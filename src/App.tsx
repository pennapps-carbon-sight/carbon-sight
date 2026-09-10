import React, { createContext, useContext, useEffect, useMemo, useRef, useState, useCallback } from "react";
import { BrowserRouter, Routes, Route, Link, Navigate, useNavigate } from "react-router-dom";
import {
  motion,
  useMotionValue,
  animate,
} from "framer-motion";
import { createClient } from "@supabase/supabase-js";
import type { Session, User } from "@supabase/supabase-js";
import { Menu, ChevronLeft, ChevronRight, X } from "lucide-react";
import NeuralEnergyWeb from "./NeuralEnergyWeb";
import ReactMarkdown from "react-markdown";

import {
  LogIn,
  LogOut,
  MessageSquare,
  Plus,
  BarChart3,
  Leaf,
  Zap,
  Send,
  Trash2,
  ChartLine,
  Award,
  Info
} from "lucide-react";
import {
  ResponsiveContainer,
  CartesianGrid, XAxis, YAxis, Tooltip,
  BarChart as RBarChart, Bar,
  // NEW:
  LineChart, Line,
  PieChart, Pie, Cell, Legend,
  ErrorBar,
} from "recharts";
import CarbonSightLogo from "./CarbonSightLockup";
import type { TeamAverages } from "./models/metrics";
import { fetchTeamAveragesFromView } from "./api/metrics";

// FX
import WaterBurstFX from "./WaterBurst";
import "./water-burst.css";

export default function App() {
  if (MISSING_ENV) return <MissingEnv />;
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<Protected><ChatScreen /></Protected>} />
            <Route path="/dashboard" element={<Protected><DashboardScreen /></Protected>} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { error: any }> {
  constructor(props: any) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error: any) { return { error }; }
  componentDidCatch(error: any, info: any) { console.error("[ErrorBoundary]", error, info); }
  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen bg-[#0b1115] text-slate-100 grid place-items-center p-6">
          <div className="max-w-xl w-full rounded-2xl border border-white/10 bg-white/5 p-5">
            <h1 className="text-emerald-400 font-semibold text-lg">Something went wrong</h1>
            <pre className="mt-3 whitespace-pre-wrap text-sm text-rose-300">
{String(this.state.error?.message || this.state.error)}
            </pre>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}


const SUPA_URL = (import.meta as any).env?.VITE_SUPABASE_URL as string | undefined;
const SUPA_ANON = (import.meta as any).env?.VITE_SUPABASE_ANON_KEY as string | undefined;
const MISSING_ENV = !SUPA_URL || !SUPA_ANON;

const supabase = !MISSING_ENV
  ? createClient(SUPA_URL!, SUPA_ANON!, { auth: { persistSession: true, autoRefreshToken: true } })
  : null;

/* ---------------- Auth context ---------------- */
interface AuthCtx {
  session: Session | null;
  user: User | null;
  checkEmailExists: (email: string) => Promise<boolean>;
  sendOTP: (email: string) => Promise<void>;
  verifyOTP: (email: string, token: string) => Promise<{ isNewUser: boolean }>;
  logout: () => Promise<void>;
}
const Auth = createContext<AuthCtx | null>(null);
const useAuth = () => {
  const v = useContext(Auth);
  if (!v) throw new Error("useAuth must be used inside <AuthProvider>");
  return v;
};

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const sub = supabase.auth.onAuthStateChange((_e, s) => setSession(s));
    return () => sub.data.subscription.unsubscribe();
  }, []);

  async function checkEmailExists(email: string): Promise<boolean> {
    if (!supabase) throw new Error("Supabase env vars are missing. Add .env and restart the dev server.");
    console.log("[Auth] Checking if email exists:", email);
    
    try {
      // Check in login table for existing user registration
      const { data, error } = await supabase
        .from('login')
        .select('user_email')
        .eq('user_email', email)
        .limit(1);
      
      if (error) {
        console.log("[Auth] Error checking email existence:", error);
        // If we can't check, assume it's a new user to be safe
        return false;
      }
      
      const exists = data && data.length > 0;
      console.log("[Auth] Email exists:", exists);
      return exists;
    } catch (err) {
      console.log("[Auth] Exception checking email existence:", err);
      return false;
    }
  }

  async function sendOTP(email: string) {
    if (!supabase) throw new Error("Supabase env vars are missing. Add .env and restart the dev server.");
    console.log("[Auth] Sending OTP to:", email);
    
    const { data, error } = await supabase.auth.signInWithOtp({
      email: email,
      options: {
        shouldCreateUser: true,
        emailRedirectTo: undefined, // Disable magic link redirect
      }
    });
    
    if (error) {
      console.log("[Auth] OTP send error:", error);
      throw error;
    }
    
    console.log("[Auth] OTP sent successfully:", data);
  }

  async function verifyOTP(email: string, token: string) {
    if (!supabase) throw new Error("Supabase env vars are missing. Add .env and restart the dev server.");
    console.log("[Auth] Verifying OTP for:", email);
    
    const { data, error } = await supabase.auth.verifyOtp({
      email: email,
      token: token,
      type: 'email'
    });
    
    if (error) {
      console.log("[Auth] OTP verification error:", error);
      throw error;
    }
    
    console.log("[Auth] OTP verified successfully:", data);
    
    // Check if user exists in our login table (this is the real check we should use)
    const userExists = await checkEmailExists(email);
    console.log("[Auth] User exists in login table:", userExists);
    
    if (!userExists) {
      // For new users, we need to store them in login table after team selection
      return { isNewUser: true };
    } else {
      // For existing users, they're already in our login table
      return { isNewUser: false };
    }
  }

  async function storeUserEmail(email: string, team?: string) {
    if (!supabase) return;
    
    try {
      // Store user registration in the login table
      const { data, error } = await supabase
        .from('login')
        .insert([{ 
          user_email: email,
          team: team || 'Not specified'
        }]);
      
      if (error) {
        console.log("[Auth] Error storing user data:", error);
        // Try without team field if that fails
        const { data: data2, error: error2 } = await supabase
          .from('login')
          .insert([{ 
            user_email: email
          }]);
        
        if (error2) {
          console.log("[Auth] Error storing user data without team:", error2);
        } else {
          console.log("[Auth] User data stored successfully without team:", data2);
        }
      } else {
        console.log("[Auth] User data stored successfully:", data);
      }
    } catch (err) {
      console.log("[Auth] Exception storing user data:", err);
    }
  }
  async function logout() { if (supabase) await supabase.auth.signOut(); }

  const value = useMemo(() => ({ session, user: session?.user ?? null, checkEmailExists, sendOTP, verifyOTP, logout }), [session]);
  return <Auth.Provider value={value}>{children}</Auth.Provider>;
}

/* ---------------- UI helpers ---------------- */
function Button(props: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const { className, type, ...rest } = props;
  return (
    <button
      type={type ?? "button"}
      {...rest}
      className={`inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-white hover:bg-white/10 ${className || ""}`}
    />
  );
}
function PrimaryButton(props: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const { className, type, ...rest } = props;
  return (
    <button
      type={type ?? "button"}
      {...rest}
      className={`inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-black hover:bg-emerald-400 ${className || ""}`}
    />
  );
}
function BackdropGlow() {
  return (
    <div className="pointer-events-none absolute inset-0 -z-10">
      <div className="absolute -top-32 left-1/2 h-[520px] w-[1200px] -translate-x-1/2 rounded-full bg-gradient-to-b from-emerald-500/25 via-emerald-500/10 to-transparent blur-3xl" />
    </div>
  );
}

/* ---------------- Fallback when env missing ---------------- */
function MissingEnv() {
  return (
    <div className="min-h-screen grid place-items-center bg-[#0b1115] text-slate-100 p-6">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 max-w-lg">
        <h1 className="text-xl font-semibold text-emerald-400">Supabase not configured</h1>
        <p className="mt-3 text-sm">
          Create <code>.env</code> with <code>VITE_SUPABASE_URL</code> and <code>VITE_SUPABASE_ANON_KEY</code> and restart the dev server.
        </p>
      </div>
    </div>
  );
}

/* === Gemini Analysis (from Python script) === */
const GEMINI_MODELS = {
  "gemini-2.5-pro": {"co2_per_token": 0.0025, "latency_ms": 350, "cost_per_1k_tokens": 0.03, "completion_tokens": 250},
  "gemini-2.5-flash": {"co2_per_token": 0.0018, "latency_ms": 180, "cost_per_1k_tokens": 0.02, "completion_tokens": 180},
  "gemini-2.5-flash-lite": {"co2_per_token": 0.0010, "latency_ms": 100, "cost_per_1k_tokens": 0.01, "completion_tokens": 120},
  "gemini-1.5-pro": {"co2_per_token": 0.0030, "latency_ms": 400, "cost_per_1k_tokens": 0.04, "completion_tokens": 300},
  "gemini-1.5-flash": {"co2_per_token": 0.0020, "latency_ms": 200, "cost_per_1k_tokens": 0.025, "completion_tokens": 200},
  "gemini-1.5-flash-lite": {"co2_per_token": 0.0012, "latency_ms": 120, "cost_per_1k_tokens": 0.015, "completion_tokens": 150}
};

function estimateGemini(promptText: string) {
  const charCount = promptText.length;
  const tokenCount = charCount / 4;

  const results = [];
  for (const [modelName, specs] of Object.entries(GEMINI_MODELS)) {
    const totalTokens = tokenCount + specs.completion_tokens;
    const co2 = totalTokens * specs.co2_per_token;
    const cost = totalTokens / 1000 * specs.cost_per_1k_tokens;
    const latencyMs = specs.latency_ms;
    const tokensPerSec = totalTokens / (latencyMs / 1000);

    results.push({
      model_name: modelName,
      latency: Math.round(tokensPerSec * 100) / 100,
      cost: Math.round(cost * 10000) / 10000,
      gco2_emissions: Math.round(co2 * 10000) / 10000,
      created_at: new Date().toISOString()
    });
  }

  return results;
}

async function insertGeminiToSupabase(promptText: string, userEmail: string) {
  if (!supabase) return;
  
  console.log("[Gemini] Starting analysis for user:", userEmail);
  const results = estimateGemini(promptText);
  
  // First, get user information from the login table
  let userTeam = 'Unknown';
  try {
    console.log("[Gemini] Fetching user info from login table for:", userEmail);
    const { data: loginData, error: loginError } = await supabase
      .from('login')
      .select('user_email, team')
      .eq('user_email', userEmail)
      .single();
    
    if (loginError) {
      console.log("[Gemini] Error fetching user info from login table:", loginError);
      console.log("[Gemini] LoginError details:", {
        code: loginError.code,
        message: loginError.message,
        details: loginError.details
      });
    } else if (loginData) {
      userTeam = loginData.team || 'Unknown';
      console.log("[Gemini] Found user info:", { userEmail, userTeam, loginData });
    } else {
      console.log("[Gemini] No data returned from login table for user:", userEmail);
    }
  } catch (err) {
    console.log("[Gemini] Exception fetching user info:", err);
  }
  
  const recordsWithUserInfo = results.map(result => ({
    ...result,
    user_email: userEmail,
    team: userTeam
  }));
  
  console.log("[Gemini] Prepared records for insertion:", {
    userEmail,
    userTeam,
    recordCount: recordsWithUserInfo.length,
    firstRecord: recordsWithUserInfo[0]
  });
  
  try {
    const { data: tableCheck, error: tableError } = await supabase
      .from('CarbonSight')
      .select('*')
      .limit(1);
    
    console.log("[Gemini] CarbonSight table structure check:", {
      hasData: !!tableCheck,
      columns: tableCheck?.[0] ? Object.keys(tableCheck[0]) : 'No existing data',
      tableError
    });
    
    const { data, error } = await supabase
      .from('CarbonSight')
      .insert(recordsWithUserInfo);
    
    if (error) {
      console.log("[Gemini] Error inserting metrics data:", error);
      console.log("[Gemini] Error details:", {
        code: error.code,
        message: error.message,
        details: error.details,
        hint: error.hint
      });
      
      console.log("[Gemini] Attempted to insert records:", recordsWithUserInfo);
      
      console.log("[Gemini] Trying with team field only");
      const teamOnlyRecords = results.map(result => ({
        model_name: result.model_name,
        latency: result.latency,
        cost: result.cost,
        gco2_emissions: result.gco2_emissions,
        created_at: result.created_at,
        user_email: userEmail,
        team: userTeam
      }));
      
      const { data: teamData, error: teamError } = await supabase
        .from('CarbonSight')
        .insert(teamOnlyRecords);
        
      if (teamError) {
        console.log("[Gemini] Team field also failed:", teamError);
        
        console.log("[Gemini] Final fallback without team field");
        const fallbackRecords = results.map(result => ({
          model_name: result.model_name,
          latency: result.latency,
          cost: result.cost,
          gco2_emissions: result.gco2_emissions,
          created_at: result.created_at,
          user_email: userEmail
        }));
        
        const { data: fallbackData, error: fallbackError } = await supabase
          .from('CarbonSight')
          .insert(fallbackRecords);
          
        if (fallbackError) {
          console.log("[Gemini] Final fallback also failed:", fallbackError);
        } else {
          console.log("[Gemini] Final fallback succeeded (without team):", fallbackData);
        }
      } else {
        console.log("[Gemini] Team insertion succeeded:", teamData);
      }
    } else {
      console.log("[Gemini] Metrics data inserted successfully with team:", data);
      console.log("[Gemini] Inserted records included team:", userTeam);
    }
  } catch (err) {
    console.log("[Gemini] Exception inserting metrics data:", err);
  }
  
  return results;
}

/* === Model list (used in Chat) === */
type Energy = "sustainable" | "balanced" | "intensive";
type Model = { id: string; label: string; energy: Energy };

const MODELS: Model[] = [
  { id: "eco-7b", label: "Eco (GreenAI-7B)", energy: "sustainable" },
  { id: "mix-13b", label: "Balanced (Mix-13B)", energy: "balanced" },
  { id: "xl-70b", label: "Performance (XL-70B)", energy: "intensive" },
];

// Add this near HomePage, without re-declaring Energy/Model if you already have them
const WEB_MODELS: { id: string; label: string; energy: "sustainable" | "balanced" | "intensive" }[] = [
  // your existing three:
  { id: "gemini-2.5-flash",        label: "gemini-2.5-flash (Eco)", energy: "sustainable" },
  { id: "gemini-2.5-flash-lite",       label: "gemini-2.5-flash-lite (Balanced)", energy: "balanced" },
  { id: "gemini-2.5-pro",        label: "gemini-2.5-pro (Intensive)", energy: "intensive" },

  // some extras to make the graph feel “neural”
  { id: "gpt-4o-mini",   label: "gpt-4o-mini", energy: "balanced" },
  { id: "llama-3-8b",    label: "Llama 3 8B", energy: "sustainable" },
  { id: "mistral-large", label: "Mistral Large", energy: "balanced" },
  { id: "mixtral-8x7b",  label: "Mixtral 8x7B", energy: "sustainable" },
  { id: "deepseek-70b",  label: "DeepSeek 70B", energy: "intensive" },
  { id: "phi-3-small",   label: "Phi-3 Small", energy: "sustainable" },
  { id: "qwen-14b",      label: "Qwen 14B", energy: "balanced" },
];


function HomePage() {
  const [open, setOpen] = useState(false);


  useEffect(() => {
    const handler = () => setOpen(true);
    window.addEventListener("open-login", handler);
    return () => window.removeEventListener("open-login", handler);
  }, []);

  return (
    <div className="relative min-h-screen bg-[#0b1115] text-slate-100 overflow-hidden">
      <BackdropGlow />
      <EcoWaveDeco />

      <header className="relative z-20 mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <div className="flex items-center">
          <CarbonSightLogo energy="sustainable" width={200} height={36} className="block" />
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/chat"
            className="hidden rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-white hover:bg-white/10 md:inline"
          >
            Try Chat (demo)
          </Link>
          <Button onClick={() => setOpen(true)}>
            <LogIn className="h-4 w-4" /> Login
          </Button>
        </div>
      </header>

      {/* Hero + Features + FAQ */}
      <main className="relative z-20">
        {/* HERO */}
        <section className="relative mx-auto max-w-6xl px-4 pt-12 text-center md:pt-20">
          {/* soft glow */}
          <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
            <div className="absolute left-1/2 top-[-80px] h-[520px] w-[980px] -translate-x-1/2 rounded-[50%] bg-emerald-500/15 blur-3xl" />
          </div>

          <motion.h1
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.05 }}
            className="text-5xl font-extrabold tracking-tight md:text-6xl"
          >
            Make <span className="bg-gradient-to-r from-emerald-300 via-emerald-400 to-emerald-500 bg-clip-text text-transparent">Every Token</span> Greener
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="mx-auto mt-4 max-w-2xl text-slate-300/90 md:text-lg"
          >
            Pick lower-carbon models without sacrificing quality. Track your impact and earn rewards automatically.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.18 }}
            className="mt-8 flex flex-wrap items-center justify-center gap-3"
          >
            <PrimaryButton onClick={() => setOpen(true)} className="px-5 py-2.5">
              <LogIn className="h-4 w-4" /> Start Optimizing Now
            </PrimaryButton>
          </motion.div>
        </section>

        {/* FEATURES */}
        <section className="mx-auto mt-14 max-w-6xl px-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* Greener by default */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 min-h-[220px]">
              <div className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                <Leaf className="h-5 w-5 text-emerald-300" />
                <span className="font-medium">Greener by default</span>
              </div>
              <p className="text-slate-300/90">
                Carbon-aware routing picks cleaner regions and efficient models automatically.
              </p>
              <ul className="mt-4 space-y-2 text-sm text-slate-400">
                <li>• Live grid carbon signal</li>
                <li>• Auto model/region selection</li>
                <li>• Per-request opt-out</li>
              </ul>
            </div>

            {/* Real-time signals */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 min-h-[220px]">
              <div className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                <Zap className="h-5 w-5 text-emerald-300" />
                <span className="font-medium">Real-time signals</span>
              </div>
              <p className="text-slate-300/90">
                Balance quality, latency, and energy at runtime — not at deploy time.
              </p>
              <ul className="mt-4 space-y-2 text-sm text-slate-400">
                <li>• Quality/latency/energy tradeoffs</li>
                <li>• Smart fallbacks & retries</li>
                <li>• Burst-aware throttling</li>
              </ul>
            </div>

            {/* Impact you can see */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 min-h-[220px]">
              <div className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                <BarChart3 className="h-5 w-5 text-emerald-300" />
                <span className="font-medium">Impact you can see</span>
              </div>
              <p className="text-slate-300/90">
                Track energy (Wh), CO₂e, and CSI trends across teams and models.
              </p>
              <ul className="mt-4 space-y-2 text-sm text-slate-400">
                <li>• CSI (Carbon Sensitivity Index)</li>
                <li>• Team & workspace views</li>
                <li>• Exportable reports</li>
              </ul>
            </div>

            {/* Rewards that pay back */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 min-h-[220px]">
              <div className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                <Award className="h-5 w-5 text-emerald-300" />
                <span className="font-medium">Rewards that pay back</span>
              </div>
              <p className="text-slate-300/90">
                Earn credits by choosing greener lanes without losing quality.
              </p>
              <ul className="mt-4 space-y-2 text-sm text-slate-400">
                <li>• Auto credit accrual</li>
                <li>• Payout history</li>
                <li>• Per-model incentives</li>
              </ul>
            </div>

            {/* Drop-in API & SDKs */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 min-h-[220px]">
              <div className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                <Zap className="h-5 w-5 text-emerald-300" />
                <span className="font-medium">Drop-in API & SDKs</span>
              </div>
              <p className="text-slate-300/90">
                Keep your stack; CarbonSight plugs into your existing calls.
              </p>
              <ul className="mt-4 space-y-2 text-sm text-slate-400">
                <li>• HTTP proxy or SDK</li>
                <li>• Policy & quota controls</li>
                <li>• Audit-ready logs</li>
              </ul>
            </div>

            {/* Guardrails & policies */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 min-h-[220px]">
              <div className="mb-2 flex items-center gap-2 text-sm text-slate-300">
                <Leaf className="h-5 w-5 text-emerald-300" />
                <span className="font-medium">Guardrails & policies</span>
              </div>
              <p className="text-slate-300/90">
                Define org policies for carbon budgets, models, and data regions.
              </p>
              <ul className="mt-4 space-y-2 text-sm text-slate-400">
                <li>• Carbon budget thresholds</li>
                <li>• Allow/deny model lists</li>
                <li>• Region pinning</li>
              </ul>
            </div>
          </div>
        </section>


      </main>

      {open && <LoginModal onClose={() => setOpen(false)} />}


{/* MODEL ENERGY NETWORK (full-bleed, large) */}
<section className="relative mt-14 -mx-4 md:-mx-8 lg:-mx-12">
  <div className="mx-auto w-full max-w-[1400px]">
    <h3 className="mb-2 text-center text-sm font-medium text-slate-300">
      Model Energy Network
    </h3>
    <p className="mb-6 text-center text-xs text-slate-400">
      Hover nodes to see model names. <span className="text-emerald-400">Green</span> = sustainable,&nbsp;
      <span className="text-yellow-300">Amber</span> = balanced,&nbsp;
      <span className="text-rose-400">Red</span> = intensive.
    </p>

    {/* Bigger canvas: set height here */}
    <NeuralEnergyWeb models={WEB_MODELS} height={640} />
  </div>
</section>

<br></br>
<br></br>
      {/* Footer (simple) */}
      <footer className="relative z-20 border-t border-white/10/50 px-4 py-8 text-center text-xs text-slate-500">
        © {new Date().getFullYear()} CarbonSight — Built for sustainable AI workloads.
      </footer>
    </div>
  );
}

/* ---------------- OTP Login Modal (beautiful) ---------------- */
function LoginModal({ onClose }: { onClose: () => void }) {
  const { checkEmailExists, sendOTP, verifyOTP } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [team, setTeam] = useState("");
  const [step, setStep] = useState<'email' | 'otp' | 'team'>('email');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isNewUser, setIsNewUser] = useState(false); // Track if user went through team selection

  const teams = ['HR', 'AI', 'Research', 'Engineering', 'Finance'];

  async function handleSendOTP(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    console.log("[LoginModal] Processing email:", { email, step });
    try {
      // First check if email exists
      const emailExists = await checkEmailExists(email);
      console.log("[LoginModal] Email exists check result:", { email, emailExists });
      
      if (emailExists) {
        // Email exists, send OTP for login
        console.log("[LoginModal] Existing user, sending OTP directly");
        setIsNewUser(false);
        await sendOTP(email);
        setStep('otp');
      } else {
        // Email doesn't exist, ask for team selection first
        console.log("[LoginModal] New user, showing team selection");
        setIsNewUser(true);
        setStep('team');
      }
    } catch (err: any) {
      setError(err?.message || "Failed to process login request");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerifyOTP(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    console.log("[LoginModal] Verifying OTP:", { email, team, isNewUser, step });
    try {
      const result = await verifyOTP(email, otp);
      
      // Use our tracked isNewUser flag instead of the result from verifyOTP
      if (isNewUser && team) {
        // For new users who came through team selection, store their team info
        console.log("[LoginModal] Storing new user with team:", { email, team });
        await storeUserWithTeam(email, team);
      } else if (isNewUser && !team) {
        console.log("[LoginModal] Warning: New user but no team selected");
      } else {
        console.log("[LoginModal] Existing user, no storage needed");
      }
      
      // Both new and existing users go to chat
      onClose();
      nav("/chat");
    } catch (err: any) {
      setError(err?.message || "Invalid OTP");
    } finally {
      setLoading(false);
    }
  }

  async function storeUserWithTeam(userEmail: string, userTeam: string) {
    if (!supabase || !userTeam) {
      console.log("[Auth] storeUserWithTeam called with missing data:", { userEmail, userTeam, hasSupabase: !!supabase });
      return;
    }
    
    console.log("[Auth] Storing user with team:", { userEmail, userTeam });
    
    try {
      // Store user registration in the login table
      const { data, error } = await supabase
        .from('login')
        .insert([{ 
          user_email: userEmail,
          team: userTeam
        }]);
      
      if (error) {
        console.log("[Auth] Error storing user data:", error);
        // Try without team field if that fails
        const { data: data2, error: error2 } = await supabase
          .from('login')
          .insert([{ 
            user_email: userEmail
          }]);
        
        if (error2) {
          console.log("[Auth] Error storing user data without team:", error2);
        } else {
          console.log("[Auth] User data stored successfully without team:", data2);
        }
      } else {
        console.log("[Auth] User data stored successfully with team:", data);
      }
    } catch (err) {
      console.log("[Auth] Exception storing user data:", err);
    }
  }

  async function handleTeamSelection(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    console.log("[LoginModal] Team selection:", { email, team, step });
    try {
      // For new users, send OTP after team selection
      await sendOTP(email);
      setStep('otp');
    } catch (err: any) {
      setError(err?.message || "Failed to send OTP");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4">
      <div className="relative w-full max-w-lg overflow-hidden rounded-3xl border border-white/10 bg-[#0b1115]/95 shadow-2xl">
        {/* Decorative glows */}
        <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -top-24 left-1/2 h-[420px] w-[620px] -translate-x-1/2 rounded-full bg-emerald-500/20 blur-3xl" />
          <div className="absolute bottom-[-120px] right-[-80px] h-[320px] w-[320px] rounded-full bg-emerald-400/10 blur-3xl" />
        </div>

        {/* Close */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-lg px-2 py-1 text-slate-400 hover:text-white"
          aria-label="Close"
        >
          ✕
        </button>

        {/* Header */}
        <div className="flex items-center gap-4 px-6 pt-6 sm:px-8">
          {/* Mini mark (SVG inline to avoid ID collisions) */}
          <LoginLogoMark className="h-10 w-auto shrink-0" />
          <div className="min-w-0">
            <h3 className="truncate text-base font-semibold text-white">Welcome to CarbonSight</h3>
            <p className="text-xs text-slate-400">Cut AI emissions, not quality.</p>
          </div>
        </div>

        {/* Form */}
        <div className="space-y-4 px-6 py-6 sm:px-8">
          {/* Step 1: Email */}
          {step === 'email' && (
            <form onSubmit={handleSendOTP} className="space-y-4">
              <div>
                <label htmlFor="email" className="mb-1 block text-xs text-slate-400">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-500 focus:border-emerald-400/40"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>

              {error && (
                <p className="rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-black hover:bg-emerald-400 disabled:opacity-70"
              >
                <Send className="h-4 w-4" />
                {loading ? "Processing..." : "Continue"}
              </button>
            </form>
          )}

          {/* Step 2: OTP Verification */}
          {step === 'otp' && (
            <form onSubmit={handleVerifyOTP} className="space-y-4">
              <div>
                <label htmlFor="otp" className="mb-1 block text-xs text-slate-400">
                  Enter OTP
                </label>
                <input
                  id="otp"
                  type="text"
                  placeholder="123456"
                  className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-500 focus:border-emerald-400/40 text-center text-lg tracking-widest"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  required
                  disabled={loading}
                  maxLength={6}
                />
                <p className="mt-1 text-xs text-slate-500">
                  We sent a 6-digit code to <span className="text-slate-300">{email}</span>
                </p>
              </div>

              {error && (
                <p className="rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-black hover:bg-emerald-400 disabled:opacity-70"
              >
                <LogIn className="h-4 w-4" />
                {loading ? "Verifying..." : "Verify OTP"}
              </button>

              <button
                type="button"
                onClick={() => {
                  setStep('email');
                  setOtp('');
                  setTeam('');
                  setIsNewUser(false);
                }}
                className="w-full text-xs text-slate-400 hover:text-slate-200"
              >
                ← Back to email
              </button>
            </form>
          )}

          {/* Step 3: Team Selection */}
          {step === 'team' && (
            <form onSubmit={handleTeamSelection} className="space-y-4">
              <div>
                <label htmlFor="team" className="mb-1 block text-xs text-slate-400">
                  Select Your Team
                </label>
                <select
                  id="team"
                  className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-emerald-400/40"
                  value={team}
                  onChange={(e) => setTeam(e.target.value)}
                  required
                  disabled={loading}
                >
                  <option value="">Choose your team...</option>
                  {teams.map((teamOption) => (
                    <option key={teamOption} value={teamOption} className="bg-slate-800">
                      {teamOption}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-slate-500">
                  Welcome! Since you're new, please select your team to get started.
                </p>
              </div>

              {error && (
                <p className="rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading || !team}
                className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-black hover:bg-emerald-400 disabled:opacity-70"
              >
                <Send className="h-4 w-4" />
                {loading ? "Sending OTP..." : "Send OTP"}
              </button>

              <button
                type="button"
                onClick={() => {
                  setStep('email');
                  setTeam('');
                  setIsNewUser(false);
                }}
                className="w-full text-xs text-slate-400 hover:text-slate-200"
              >
                ← Back to email
              </button>
            </form>
          )}

          <p className="text-center text-xs text-slate-400">
            By continuing, you agree to our <span className="underline">Terms</span> and{" "}
            <span className="underline">Privacy</span>.
          </p>
        </div>
      </div>
    </div>
  );
}

/* --- Small inline SVG mark for modal --- */
function LoginLogoMark(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 160 104" role="img" aria-label="CarbonSight" {...props}>
      <defs>
        <linearGradient id="csSweepLogin" x1="0" x2="1">
          <stop offset="0" stopColor="#fff" stopOpacity="0" />
          <stop offset=".5" stopColor="#fff" stopOpacity=".7" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
        <clipPath id="csEyeClipLogin">
          <path d="M0,52 C34,0 126,0 160,52 C126,104 34,104 0,52Z" />
        </clipPath>
      </defs>
      <path d="M0,52 C34,0 126,0 160,52 C126,104 34,104 0,52Z" fill="none" stroke="#10B981" strokeWidth="6" opacity=".9" />
      <circle cx="80" cy="52" r="28" fill="none" stroke="#10B981" strokeWidth="6" opacity=".55" />
      <path d="M80 33c11 9 16 19 16 29s-5 20-16 29c-11-9-16-19-16-29s5-20 16-29Z" fill="#10B981" />
      <g clipPath="url(#csEyeClipLogin)">
        <rect x="-220" y="0" width="220" height="104" fill="url(#csSweepLogin)">
          <animate attributeName="x" from="-220" to="220" dur="3.6s" repeatCount="indefinite" />
        </rect>
      </g>
    </svg>
  );
}


/* --- Background deco --- */
function EcoWaveDeco() {
  return (
    <div className="pointer-events-none absolute inset-0 -z-10">
      {/* faint radial aura */}
      <div className="absolute left-1/2 top-[-120px] h-[700px] w-[1200px] -translate-x-1/2 rounded-full bg-emerald-500/10 blur-3xl" />
      {/* animated top wave */}
      <motion.svg
        initial={{ y: -12, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="absolute left-0 top-0 h-[280px] w-full"
        viewBox="0 0 1440 280"
        preserveAspectRatio="none"
        aria-hidden
      >
        <defs>
          <linearGradient id="ecoGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10B981" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#10B981" stopOpacity="0.0" />
          </linearGradient>
        </defs>
        <motion.g animate={{ x: [0, 240, 0] }} transition={{ duration: 18, repeat: Infinity, ease: "linear" }}>
          <path d="M0,80 C240,40 480,120 720,80 C960,40 1200,120 1440,80 L1440,280 L0,280 Z" fill="url(#ecoGrad)" />
          <path d="M-1440,80 C-1200,40 -960,120 -720,80 C-480,40 -240,120 0,80 L0,280 L-1440,280 Z" fill="url(#ecoGrad)" />
        </motion.g>
      </motion.svg>
      {/* soft grid hint */}
      <div className="absolute inset-x-0 top-[260px] h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
    </div>
  );
}

/* ---------------- Screen 2: Chat (modern, polished, hideable sidebar) ---------------- */

type EstRow = {
  modelId: string;
  model: string;
  costUSD: number;
  co2kg: number;
  latencyMs: number;
  tokens: number;
};

const MODEL_FACTORS: Record<string, {
  label: string;
  costPer1K: number;     // USD / 1K tokens
  co2Per1K: number;      // kg CO2e / 1K tokens
  baseLatency: number;   // ms baseline for tiny prompt
}> = {
  "gemini-2.5-pro":        { label: "gemini-2.5-pro",        costPer1K: 0.0076, co2Per1K: 0.6313, baseLatency: 721.43 },
  "gemini-2.5-flash":      { label: "gemini-2.5-flash",      costPer1K: 0.0037, co2Per1K: 0.3285, baseLatency: 1013.89 },
  "gemini-2.5-flash-lite": { label: "gemini-2.5-flash-lite", costPer1K: 0.0012, co2Per1K: 0.1225, baseLatency: 1225.00 },
  "gemini-1.5-pro":        { label: "gemini-1.5-pro",        costPer1K: 0.0121, co2Per1K: 0.9075, baseLatency: 756.25 },
  "gemini-1.5-flash":      { label: "gemini-1.5-flash",      costPer1K: 0.0051, co2Per1K: 0.4050, baseLatency: 1012.50 },
  "gemini-1.5-flash-lite": { label: "gemini-1.5-flash-lite", costPer1K: 0.0023, co2Per1K: 0.1830, baseLatency: 1270.83 },
};

function estTokens(prompt: string) {
  const t = Math.ceil((prompt.trim().length || 1) / 4); // ~4 chars / token
  return Math.max(1, t);
}

function computeRows(prompt: string): EstRow[] {
  const tokens = estTokens(prompt);
  const k = tokens / 1000;

  return Object.entries(MODEL_FACTORS).map(([modelId, f]) => {
    // small latency growth with prompt size
    const latency = f.baseLatency + Math.sqrt(tokens) * 6; // tweakable
    return {
      modelId,
      model: f.label,
      costUSD: +(k * f.costPer1K).toFixed(4),
      co2kg: +(k * f.co2Per1K).toFixed(4),
      latencyMs: +latency.toFixed(2),
      tokens,
    };
  });
}
type BaselineRow = { model: string; costUsdPer1k: number; co2Per1k: number; latencyMsP95: number };
/** Static baseline rows to match your screenshot feel. */
const GEMINI_BASELINES: BaselineRow[] = [
  { model: "gemini-2.5-pro",       costUsdPer1k: 0.0076, co2Per1k: 0.6313, latencyMsP95: 721.43 },
  { model: "gemini-2.5-flash",     costUsdPer1k: 0.0037, co2Per1k: 0.3285, latencyMsP95: 1013.89 },
  { model: "gemini-2.5-flash-lite",costUsdPer1k: 0.0012, co2Per1k: 0.1225, latencyMsP95: 1225.00 },
  { model: "gemini-1.5-pro",       costUsdPer1k: 0.0121, co2Per1k: 0.9075, latencyMsP95: 756.25 },
  { model: "gemini-1.5-flash",     costUsdPer1k: 0.0051, co2Per1k: 0.4050, latencyMsP95: 1012.50 },
  { model: "gemini-1.5-flash-lite",costUsdPer1k: 0.0023, co2Per1k: 0.1830, latencyMsP95: 1270.83 },
];


function estimateForPrompt(_text: string): EstRow[] {
  return GEMINI_BASELINES;
}
function ChatScreen() {
  const { user, logout } = useAuth();

  // Models
  const [modelId, setModelId] = useState<string>(MODELS[0].id);
  const currentModel = useMemo(() => MODELS.find((m) => m.id === modelId)!, [modelId]);

  // FX state
  const [fx, setFx] = useState<{ show: boolean; color: "green" | "red" }>({ show: false, color: "green" });
  const playedColorsRef = useRef<Set<"green" | "red">>(new Set());
  const burstPlayedRef = useRef(false);

    const [uiAutoBest, setUiAutoBest] = useState(false);

  // Per-prompt analysis rows keyed by message index
const [analyses, setAnalyses] = useState<Record<number, EstRow[]>>({});
// Which message index is currently showing the info modal
const [infoFor, setInfoFor] = useState<number | null>(null);

  useEffect(() => {
    burstPlayedRef.current = false;
    playedColorsRef.current.clear();
  }, [modelId]);

  // Chat state (demo)
  const [convos, setConvos] = useState<{ id: string; title: string }[]>([{ id: "c1", title: "New chat" }]);
  const [activeId, setActiveId] = useState("c1");
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([
    { role: "assistant", content: "Hi! Ask me anything about CarbonSight. This is a demo UI." },
  ]);
  const [input, setInput] = useState("");
  const listRef = useRef<HTMLDivElement>(null);
  useEffect(() => { listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" }); }, [messages]);

  function newChat() {
    const id = Math.random().toString(36).slice(2);
    setConvos((c) => [{ id, title: "New chat" }, ...c]);
    setActiveId(id);
    setMessages([{ role: "assistant", content: "New conversation started." }]);
    playedColorsRef.current.clear();
  }

  function deleteChat(id: string) {
    setConvos((prev) => prev.filter((c) => c.id !== id));
    if (activeId === id && convos.length > 1) {
      const next = convos.find((c) => c.id !== id)!;
      setActiveId(next.id);
      setMessages([{ role: "assistant", content: "Switched conversation." }]);
    }
  }

  const BURST_MS = 3200;
  async function sendMessage() {
  const text = input.trim();
  if (!text) return;

  setInput("");

  // Add user message and capture its index
  setMessages((prev) => {
    const myIndex = prev.length; // this user's message will be at this index
    const next = [...prev, { role: "user", content: text }];

    // compute analysis rows for this prompt (front-end demo)
    const rows = estimateForPrompt(text);
    setAnalyses((a) => ({ ...a, [myIndex]: rows }));

    return next;
  });

  // (optional) your Supabase insert/analysis call can stay here if you have it
  // try { await insertGeminiToSupabase(text, user?.email ?? ""); } catch {}

  // Play the burst once per color
  const effectColor: "green" | "red" = currentModel.energy === "intensive" ? "red" : "green";
  if (!playedColorsRef.current.has(effectColor)) {
    requestAnimationFrame(() => {
      setFx({ show: true, color: effectColor });
      window.setTimeout(() => setFx((p) => ({ ...p, show: false })), BURST_MS);
    });
    playedColorsRef.current.add(effectColor);
  }

  try {
    // Call your backend
    const res = await fetch("http://localhost:4000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }), // match your backend
    });
  
    const data = await res.json();
    const reply = data.reply; // backend returns { reply: "..." }
  
    setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
  } catch (err) {
    console.error(err);
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "Failed to get response from Gemini API." },
    ]);
  }
}

  /* -------- Sidebar state: desktop collapse + mobile overlay -------- */
  const [collapsed, setCollapsed] = useState<boolean>(() => localStorage.getItem("cs.sidebarCollapsed") === "1");
  useEffect(() => { localStorage.setItem("cs.sidebarCollapsed", collapsed ? "1" : "0"); }, [collapsed]);

  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const key = e.key.toLowerCase();
      if ((e.ctrlKey || e.metaKey) && key === "b") { setCollapsed((v) => !v); e.preventDefault(); }
      if ((e.ctrlKey || e.metaKey) && key === "n") { newChat(); e.preventDefault(); }
      if (key === "escape") setMobileOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  /* -------- Energy chip styling -------- */
  const energyChip = {
    sustainable: { dot: "bg-emerald-400", text: "text-emerald-300", bg: "bg-emerald-500/10 ring-emerald-400/30", label: "Sustainable" },
    balanced:    { dot: "bg-amber-300",   text: "text-amber-200",   bg: "bg-amber-400/10 ring-amber-300/30",   label: "Balanced" },
    intensive:   { dot: "bg-rose-400",    text: "text-rose-300",    bg: "bg-rose-500/10 ring-rose-400/30",     label: "Energy-intensive" },
  }[currentModel.energy];

  /* -------- Sidebar content (reused for desktop + mobile) -------- */
  // Sidebar open/closed
const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);

// (optional) remember preference
useEffect(() => {
  const saved = localStorage.getItem("cs_sidebar_open");
  if (saved !== null) setIsSidebarOpen(saved === "1");
}, []);
useEffect(() => {
  localStorage.setItem("cs_sidebar_open", isSidebarOpen ? "1" : "0");
}, [isSidebarOpen]);

useEffect(() => {
  localStorage.setItem("cs_sidebar_open", isSidebarOpen ? "1" : "0");
}, [isSidebarOpen]);
  const SidebarContent: React.FC<{ collapsed: boolean; showClose?: boolean; onClose?: () => void }> = ({ collapsed, showClose, onClose }) => (
    <div className="relative flex h-full flex-col">
      {/* Decorative top wash */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-28 bg-gradient-to-b from-emerald-500/10 to-transparent" />

      {/* Title / actions row */}
      <div className="relative z-10 flex items-center justify-between">
        <PrimaryButton onClick={newChat} className={`${collapsed ? "px-2" : "px-3"} w-full`}>
          <Plus className="h-4 w-4" />
          {!collapsed && <span>New chat</span>}
        </PrimaryButton>

        {/* Desktop collapse toggle */}
        {!showClose && (
          <button
            onClick={() => setCollapsed((v) => !v)}
            className="ml-2 grid h-9 w-9 place-items-center rounded-lg border border-white/10 bg-white/5 hover:bg-white/10"
            title={collapsed ? "Expand sidebar (⌘/Ctrl+B)" : "Collapse sidebar (⌘/Ctrl+B)"}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        )}

        {/* Mobile close */}
        {showClose && (
          <button
            onClick={onClose}
            className="ml-2 grid h-9 w-9 place-items-center rounded-lg border border-white/10 bg-white/5 hover:bg-white/10"
            title="Close"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Chats list */}
      <div className="mt-3 flex-1 space-y-1 overflow-y-auto pr-1">
        {convos.map((c) => {
          const active = activeId === c.id;
          return (
            <div
              key={c.id}
              className={`group relative flex items-center justify-between rounded-lg ${collapsed ? "px-1" : "px-2"} py-2 text-sm ${
                active ? "bg-white/10" : "hover:bg-white/10"
              }`}
            >
              {/* Active indicator */}
              {active && <span className="absolute left-0 top-1/2 -translate-y-1/2 h-6 w-[3px] rounded-r bg-gradient-to-b from-emerald-400 to-emerald-300" />}

              <button
                onClick={() => setActiveId(c.id)}
                className="flex w-full items-center gap-2 text-left"
                title={c.title}
              >
                <MessageSquare className="h-4 w-4 text-emerald-300 shrink-0" />
                {!collapsed && <span className="line-clamp-1">{c.title}</span>}
              </button>

              {!collapsed && (
                <button
                  onClick={() => deleteChat(c.id)}
                  className="ml-2 hidden rounded-md p-1 text-slate-500 hover:text-rose-400 hover:bg-white/10 group-hover:block"
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className={`mt-3 rounded-xl border border-white/10 bg-white/5 ${collapsed ? "px-2" : "px-3"} py-2`}>
        <Link
          to="/dashboard"
          className={`flex items-center gap-2 rounded-lg ${collapsed ? "px-1" : "px-2"} py-2 text-sm hover:bg-white/10`}
          title="Dashboard"
        >
          <BarChart3 className="h-4 w-4" />
          {!collapsed && <span>Dashboard</span>}
        </Link>
        <button
          onClick={logout}
          className={`mt-1 flex w-full items-center gap-2 rounded-lg ${collapsed ? "px-1" : "px-2"} py-2 text-left text-sm hover:bg-white/10`}
          title="Logout"
        >
          <LogOut className="h-4 w-4" />
          {!collapsed && <span>Logout</span>}
        </button>

        {!collapsed && (
          <div className="mt-2 rounded-lg border border-white/10 bg-black/20 px-2.5 py-2 text-[11px] text-slate-400">
            <div className="truncate"><span className="text-slate-300">Signed in:</span> {user?.email ?? "guest"}</div>
            <div className="mt-1 opacity-80">Shortcuts: ⌘/Ctrl+B collapse • ⌘/Ctrl+N new chat</div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0b1115] text-slate-100 flex">
      {/* Desktop sidebar */}
     {/* Sidebar */}
<aside
  className={`relative hidden md:flex flex-col border-r border-white/10 bg-gradient-to-b from-black/40 to-black/20 transition-[width] duration-300 ease-out ${
    isSidebarOpen ? "w-[280px]" : "w-[76px]"
  }`}
>
  {/* Edge toggle */}
<button
  onClick={() => setIsSidebarOpen((v) => !v)}
  aria-label={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
  className="absolute -right-3 top-100 z-30 grid h-10 w-10 place-items-center rounded-2xl border border-white/15 bg-[#0d1418]/80 text-slate-200 backdrop-blur transition hover:bg-white/10"
  title={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
>
  {isSidebarOpen ? (
    <ChevronLeft className="h-5 w-5" />
  ) : (
    <ChevronRight className="h-5 w-5" />
  )}
</button>
  {/* Floating collapse pill */}
  <button
    onClick={() => setIsSidebarOpen((s) => !s)}
    aria-label={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
    className="group absolute top-4 -right-3 grid h-8 w-8 place-items-center rounded-full bg-black/60 ring-1 ring-white/15 backdrop-blur transition hover:bg-white/10 hover:ring-white/30"
  >
    {isSidebarOpen ? (
      <ChevronLeft className="h-4 w-4 text-slate-200" />
    ) : (
      <ChevronRight className="h-4 w-4 text-slate-200" />
    )}
  </button>

  {/* Header: New chat */}
  <div className="sticky top-0 z-10 border-b border-white/10 bg-black/30 px-2 pt-3 pb-3 backdrop-blur">
    <button
      onClick={newChat}
      className={`flex h-10 w-full items-center rounded-xl bg-emerald-500 font-semibold text-black transition hover:bg-emerald-400 ${
        isSidebarOpen ? "justify-center gap-2 px-3" : "justify-center"
      }`}
      title="New chat"
    >
      <Plus className="h-5 w-5" />
      <span className={`${isSidebarOpen ? "inline" : "hidden"}`}>New chat</span>
    </button>
  </div>

  {/* Conversations */}
  <div className="flex-1 space-y-1 overflow-y-auto p-2 pr-1">
    {convos.map((c) => {
      const active = c.id === activeId;
      return (
        <button
          key={c.id}
          onClick={() => setActiveId(c.id)}
          className={`group relative flex h-10 w-full items-center rounded-xl transition-colors ${
            isSidebarOpen ? "justify-between px-3" : "justify-center"
          } ${active ? "bg-white/10" : "hover:bg-white/5"}`}
          title={c.title}
        >
          {/* Left accent bar (active/hover only) */}
          <span
            className={`absolute left-0 top-1/2 -translate-y-1/2 h-5 w-[3px] rounded-r-full bg-emerald-400 transition-opacity ${
              isSidebarOpen ? "" : "hidden"
            } ${active ? "opacity-100" : "opacity-0 group-hover:opacity-60"}`}
          />
          <span className="flex min-w-0 items-center gap-2">
            <MessageSquare className="h-4 w-4 text-emerald-300" />
            <span className={`truncate text-left ${isSidebarOpen ? "block" : "hidden"}`}>
              {c.title}
            </span>
          </span>
          {isSidebarOpen && (
            <Trash2 className="h-4 w-4 shrink-0 text-slate-500 opacity-0 transition group-hover:opacity-100 hover:text-rose-400" />
          )}
        </button>
      );
    })}
  </div>

  {/* Footer actions */}
  <div className="border-t border-white/10 p-2">
    <Link
      to="/dashboard"
      className={`flex items-center rounded-xl px-2 py-2 text-sm transition hover:bg-white/5 ${
        isSidebarOpen ? "gap-2" : "justify-center"
      }`}
      title="Dashboard"
    >
      <BarChart3 className="h-4 w-4 text-slate-300" />
      <span className={`${isSidebarOpen ? "inline" : "hidden"}`}>Dashboard</span>
    </Link>

    <button
      onClick={logout}
      className={`mt-1 flex w-full items-center rounded-xl px-2 py-2 text-left text-sm transition hover:bg-white/5 ${
        isSidebarOpen ? "gap-2" : "justify-center"
      }`}
      title="Logout"
    >
      <LogOut className="h-4 w-4 text-slate-300" />
      <span className={`${isSidebarOpen ? "inline" : "hidden"}`}>Logout</span>
    </button>

    <div
      className={`mt-1 flex items-center rounded-xl px-2 py-2 text-sm text-slate-400 ${
        isSidebarOpen ? "gap-2" : "justify-center"
      }`}
      title="Settings"
    >
    </div>
  </div>
</aside>

      {/* Mobile sidebar overlay */}
      <div className={`md:hidden fixed inset-0 z-40 ${mobileOpen ? "" : "pointer-events-none"}`} role="dialog" aria-modal="true">
        <div
          className={`absolute inset-0 bg-black/60 transition-opacity ${mobileOpen ? "opacity-100" : "opacity-0"}`}
          onClick={() => setMobileOpen(false)}
        />
        <div
          className={`absolute left-0 top-0 h-full w-[85%] max-w-[340px] border-r border-white/10 bg-black/40 backdrop-blur transform transition-transform duration-300 ${
            mobileOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <div className="h-full p-3">
            <SidebarContent collapsed={false} showClose onClose={() => setMobileOpen(false)} />
          </div>
        </div>
      </div>

      {/* Chat pane */}
      <section className="relative isolate flex min-w-0 flex-1 flex-col">
        
        {/* Wave FX (behind content) */}
        <WaterBurstFX show={fx.show} color={fx.color} />

        {/* Header */}
        <header className="relative z-20 flex items-center justify-between border-b border-white/10 px-4 py-3">
          <div className="flex items-center gap-2">
            {/* Mobile: open sidebar */}
            <button
              onClick={() => setMobileOpen(true)}
              className="mr-1 grid h-9 w-9 place-items-center rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 md:hidden"
              title="Open sidebar"
              aria-label="Open sidebar"
            >
              <Menu className="h-5 w-5" />
            </button>

             <div className="flex items-center">
          <CarbonSightLogo energy="sustainable" width={200} height={32} className="block" />
        </div>
          </div>

          {/* Energy + model */}
          <div className="flex items-center gap-3">
            <div className={`hidden sm:flex items-center gap-2 rounded-xl ring-1 px-2 py-1.5 ${energyChip.bg}`}>
              <span className={`inline-flex h-2.5 w-2.5 rounded-full ${energyChip.dot}`} />
              <span className={`text-xs ${energyChip.text}`}>{energyChip.label}</span>
              <span className="mx-2 h-4 w-px bg-white/10" />
              <span className="text-xs text-slate-400">Model</span>
              <select
                className="rounded-lg border border-white/10 bg-black/30 px-2 py-1 text-xs outline-none hover:border-white/20"
                value={modelId}
                onChange={(e) => setModelId(e.target.value)}
                title="Choose an AI model"
              >
                {MODELS.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="text-[11px] text-slate-400">
            {user?.email ? <>Signed in as <span className="text-slate-300">{user.email}</span></> : "guest"}
          </div>
        
        </header>

         {/* Messages */}
<div
  ref={listRef as React.RefObject<HTMLDivElement>}
  className="relative z-20 flex-1 space-y-4 overflow-y-auto px-4 py-6"
>
  {messages.map((m, i) => {
    const mine = m.role === "user";
    return (
      <div key={i} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
        <div
          className={`relative max-w-[72ch] rounded-2xl px-4 py-3 text-sm shadow-[0_0_0_1px_rgba(255,255,255,0.05)] ${
            mine
              ? "bg-gradient-to-br from-emerald-500 to-emerald-400 text-black"
              : "bg-white/5 text-slate-100"
          }`}
        >
          <ReactMarkdown
            components={{
              code({ inline, className, children, ...props }) {
                return inline ? (
                  <code className={className} {...props}>
                    {children}
                  </code>
                ) : (
                  <pre
                    {...props}
                    style={{
                      background: "#272822",
                      color: "#f8f8f2",
                      padding: 8,
                      borderRadius: 6,
                      overflowX: "auto",
                    }}
                  >
                    <code className={className}>{children}</code>
                  </pre>
                );
              },
              p({ children }) {
                return (
                  <p style={{ margin: "4px 0", whiteSpace: "pre-wrap" }}>
                    {children}
                  </p>
                );
              },
            }}
          >
            {m.content}
          </ReactMarkdown>

          {/* ⓘ button only for user prompts */}
          {mine && (
            <button
              onClick={() => setInfoFor(i)}
              className="absolute -right-2 -top-2 grid h-6 w-6 place-items-center rounded-full border border-white/20 bg-black/30 text-white/80 backdrop-blur hover:bg-black/50"
              title="Show model metrics"
            >
              <Info className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>
    );
  })}
</div>


{/* Prompt info modal */}
{infoFor !== null && (
  <PromptInfoModal
    prompt={messages[infoFor]?.content ?? ""}
    rows={analyses[infoFor] ?? []}
    onClose={() => setInfoFor(null)}
  />
)}

        {/* Composer */}
        <footer className="relative z-20 border-t border-white/10 p-3">
  <div className="mx-auto max-w-4xl">
    <div className="flex items-end gap-2 rounded-2xl border border-white/10 bg-black/30 p-2">
      {/* ⬇️ inert toggle starts */}
      <div className="flex items-center gap-2 self-center px-1">
        <span className="text-[11px] text-slate-400">Auto Best</span>
        <button
          type="button"
          aria-pressed={uiAutoBest}
          onClick={() => setUiAutoBest(v => !v)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
            uiAutoBest ? "bg-emerald-500" : "bg-white/10"
          }`}
          title="Auto-select best model (UI only)"
        >
          <span
            className={`inline-block h-5 w-5 transform rounded-full bg-white transition ${
              uiAutoBest ? "translate-x-5" : "translate-x-1"
            }`}
          />
        </button>
      </div>
      {/* ⬆️ inert toggle ends */}

      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask CarbonSight…"
        rows={1}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
          }
        }}
        className="min-h-[40px] flex-1 resize-none bg-transparent px-2 py-2 text-sm outline-none placeholder:text-slate-500"
      />
      <button
        onClick={sendMessage}
        className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-3 py-2 text-sm font-semibold text-black hover:bg-emerald-400 disabled:opacity-70"
        disabled={!input.trim()}
      >
        <Send className="h-4 w-4" />
        <span className="hidden sm:inline">Send</span>
      </button>
    </div>
    <p className="mt-2 text-center text-[11px] text-slate-500">
      Burst plays once per color — <span className="text-emerald-300">green</span> for sustainable/balanced,{" "}
      <span className="text-rose-400">red</span> for intensive.
    </p>
  </div>
</footer>
        
      </section>
    </div>
  );
}
function AnimatedNumber({ value, decimals = 2 }: { value: number; decimals?: number }) {
  const mv = useMotionValue(0);
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const controls = animate(mv, value, {
      duration: 0.35,
      onUpdate: (v) => setDisplay(v),
    });
    return () => controls.stop();
  }, [value]);
  return <span>{display.toFixed(decimals)}</span>;
}

function PromptInfoModal({
  prompt,
  rows,          // optional seed rows from your `analyses[index]` map
  onClose,
}: {
  prompt: string;
  rows?: EstRow[];
  onClose: () => void;
}) {
  // Live local calc every render
  const live = useMemo(() => computeRows(prompt), [prompt]);

  // Optional: merge with realtime rows coming from Supabase (table example: "prompt_metrics")
  const [remoteRows, setRemoteRows] = useState<EstRow[]>(rows ?? []);
  useEffect(() => setRemoteRows(rows ?? []), [rows]);

  useEffect(() => {
    // Skip if you don't have supabase set up yet
    // Example realtime feed keyed by a prompt hash you store when you insert
    if (!supabase) return;

    const key = simpleHash(prompt); //  short hash for channel topic
    const channel = supabase
      .channel(`metrics_${key}`)
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'prompt_metrics', filter: `prompt_hash=eq.${key}` },
        (payload: any) => {
          // Expect rows shaped like EstRow; adapt if your table differs
          const r: EstRow = payload.new as EstRow;
          setRemoteRows((prev) => {
            const map = new Map(prev.map((x) => [x.modelId, x]));
            map.set(r.modelId, r);
            return Array.from(map.values());
          });
        }
      )
      .subscribe();

    return () => { try { supabase.removeChannel(channel); } catch {} };
  }, [prompt]);

  // Choose: remote overrides live, else live
  const merged = useMemo(() => {
    if (!remoteRows.length) return live;
    const byId = new Map(remoteRows.map(r => [r.modelId, r]));
    return live.map(r => byId.get(r.modelId) ?? r);
  }, [live, remoteRows]);

  return (
    <div className="fixed inset-0 z-[60] grid place-items-center bg-black/70 p-4">
      <div className="w-full max-w-3xl rounded-2xl border border-white/10 bg-[#0b1115] p-5 shadow-2xl">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-base font-semibold text-white">Prompt metrics</h3>
          <button onClick={onClose} className="rounded-lg px-2 py-1 text-slate-400 hover:text-white">✕</button>
        </div>

        <p className="mb-3 truncate text-sm text-slate-400">“{prompt}”</p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-slate-400">
                <th className="px-3 py-2">Model</th>
                <th className="px-3 py-2">Tokens</th>
                <th className="px-3 py-2">Cost (USD)</th>
                <th className="px-3 py-2">CO₂ (kg)</th>
                <th className="px-3 py-2">Latency (ms)</th>
              </tr>
            </thead>
            <tbody>
              {merged.map((r) => (
                <tr key={r.modelId} className="odd:bg-white/0 even:bg-white/5">
                  <td className="px-3 py-2 font-medium">{r.model}</td>
                  <td className="px-3 py-2">{r.tokens}</td>
                  <td className="px-3 py-2"><AnimatedNumber value={r.costUSD} decimals={4} /></td>
                  <td className="px-3 py-2"><AnimatedNumber value={r.co2kg} decimals={4} /></td>
                  <td className="px-3 py-2"><AnimatedNumber value={r.latencyMs} decimals={2} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        
      </div>
    </div>
  );
}

// tiny prompt hash (good enough for channel key)
function simpleHash(s: string) {
  let h = 0; for (let i = 0; i < s.length; i++) h = (h << 5) - h + s.charCodeAt(i), h |= 0;
  return Math.abs(h).toString(36);
}

function Card({
  title,
  icon,
  children,
}: {
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="mb-1 flex items-center gap-2 text-sm text-slate-300">
        {icon} {title}
      </div>
      <div className="text-2xl font-semibold">{children}</div>
    </div>
  );
}
/* Duplicate PromptInfoModal removed to fix compile error */
/* ---------------- Screen 3: Dashboard ---------------- */
// add these imports if not present:


/* ---------------- Screen 3: Dashboard ---------------- */
function DashboardScreen() {
  const nav = useNavigate();
  const { logout } = useAuth();

  // Live team averages from Supabase (computed from public.user_metrics)
  const [rows, setRows] = useState<TeamAverages[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchTeamAveragesFromView(); // <-- reads from public.user_metrics
      setRows(data);
      setErr(null);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // initial fetch
    load();

    // subscribe to realtime changes in public.user_metrics → refresh charts
    const channel = supabase
      ?.channel("realtime:user_metrics")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "user_metrics" },
        () => load()
      )
      .subscribe();

    return () => {
      channel?.unsubscribe();
    };
  }, [load]);

  // Snapshot cards (weighted by num_entries)
  const snapshot = useMemo(() => {
    if (rows.length === 0) return { csi: 78, carbon: 0, tvl: "$—" };
    const totalUsers = rows.reduce((s, r) => s + (r.num_entries ?? 0), 0) || 1;
    const weightedCarbon = rows.reduce((s, r) => s + Number(r.avg_co2_kg) * (r.num_entries ?? 0), 0) / totalUsers;

    return {
      csi: Math.round(80 + Math.random() * 10), // demo KPI for now
      carbon: Number(weightedCarbon.toFixed(2)),
      tvl: `$${(rows.length * 0.5).toFixed(1)}M`, // placeholder
    };
  }, [rows]);

  // Chart datasets
  const co2Data = rows.map((r) => ({ team: r.team, value: Number(r.avg_co2_kg) || 0 }));
  const latencyData = rows.map((r) => ({ team: r.team, value: Number(r.avg_latency_ms) || 0 }));
  const costData = rows.map((r) => ({ team: r.team, value: Number(r.avg_cost_usd) || 0 }));

  // Sort table by lowest CO2 first
  const teamBoard = [...rows].sort(
    (a, b) => Number(a.avg_co2_kg) - Number(b.avg_co2_kg)
  );

  return (
    <div className="min-h-screen bg-[#0b1115] text-slate-100">
      <BackdropGlow />
      <header className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-emerald-300" />
          <span className="font-semibold">Dashboard</span>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/chat"
            className="rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-sm hover:bg-white/10"
          >
            Chat
          </Link>
          <button
            onClick={async () => {
              await logout();
              nav("/");
            }}
            className="rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-sm hover:bg-white/10"
          >
            <LogOut className="mr-1 inline-block h-4 w-4" /> Logout
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 pb-24">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Card title="CSI Now" icon={<Zap className="h-4 w-4 text-emerald-300" />}>
            {snapshot.csi}
          </Card>
          <Card title="Avg CO₂ per Team (kg)" icon={<Leaf className="h-4 w-4 text-emerald-300" />}>
            {loading ? "…" : snapshot.carbon}
          </Card>
          <Card title="Pool TVL" icon={<Award className="h-4 w-4 text-emerald-300" />}>
            {snapshot.tvl}
          </Card>
        </div>

        {/* Charts */}
        <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
          {/* Average CO₂ by Team */}
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="mb-2 flex items-center gap-2 text-sm text-slate-300">
              <ChartLine className="h-4 w-4" /> Average CO₂ by Team (kg)
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RBarChart data={co2Data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="team" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip
                    contentStyle={{
                      background: "#0f172a",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: 12,
                      color: "#e5e7eb",
                    }}
                  />
                  <Bar dataKey="value" name="Avg CO₂ (kg)" fill="#10B981" radius={[6, 6, 0, 0]} />
                </RBarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Average Cost by Team */}
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="mb-2 text-sm text-slate-300">Average Cost by Team (USD)</div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RBarChart data={costData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="team" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip
                    contentStyle={{
                      background: "#0f172a",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: 12,
                      color: "#e5e7eb",
                    }}
                    formatter={(value) => [`$${Number(value).toFixed(4)}`, "Avg Cost (USD)"]}
                  />
                  <Bar dataKey="value" name="Avg Cost (USD)" fill="#3B82F6" radius={[6, 6, 0, 0]} />
                </RBarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Average Latency by Team */}
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="mb-2 text-sm text-slate-300">Average Latency by Team (ms)</div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RBarChart data={latencyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="team" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip
                    contentStyle={{
                      background: "#0f172a",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: 12,
                      color: "#e5e7eb",
                    }}
                  />
                  <Bar dataKey="value" name="Avg Latency (ms)" fill="#F59E0B" radius={[6, 6, 0, 0]} />
                </RBarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Team Averages Table */}
        <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="mb-3 text-sm text-slate-300">Team Averages (from public.user_metrics)</div>
          {err && <p className="text-rose-400 text-sm">{err}</p>}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-slate-400">
                  <th className="px-3 py-2">Team</th>
                  <th className="px-3 py-2">Team Size</th>
                  <th className="px-3 py-2">Avg CO₂ (kg)</th>
                  <th className="px-3 py-2">Avg Cost (USD)</th>
                  <th className="px-3 py-2">Avg Latency (ms)</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr>
                    <td className="px-3 py-4 text-slate-400" colSpan={5}>
                      Loading…
                    </td>
                  </tr>
                )}
                {!loading &&
                  teamBoard.map((r) => (
                    <tr key={r.team} className="odd:bg-white/0 even:bg-white/5">
                      <td className="px-3 py-2 font-medium">{r.team}</td>
                      <td className="px-3 py-2">{r.num_entries}</td>
                      <td className="px-3 py-2">{Number(r.avg_co2_kg).toFixed(3)}</td>
                      <td className="px-3 py-2">{Number(r.avg_cost_usd).toFixed(4)}</td>
                      <td className="px-3 py-2">{Number(r.avg_latency_ms).toFixed(0)}</td>
                    </tr>
                  ))}
                {!loading && rows.length === 0 && (
                  <tr>
                    <td className="px-3 py-4 text-slate-400" colSpan={4}>
                      No data yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}


/* ---------------- Route guard & App ---------------- */
function Protected({ children }: { children: React.ReactNode }) {
  const { session } = useAuth();
  if (!session) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export { ChatScreen };