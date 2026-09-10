/**
 * API service for communicating with the CarbonSight backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  model?: string;
  user_id?: string;
  team_id?: string;
}

export interface ChatResponse {
  message: string;
  model_used: string;
  energy_metrics: {
    energy_kwh: number;
    co2_grams: number;
    model_name: string;
    region: string;
  };
  tokens_used: {
    input: number;
    output: number;
    total: number;
  };
  processing_time_ms: number;
  success: boolean;
}

export interface ModelComparisonResponse {
  prompt: string;
  best_model: string;
  recommendation: string;
  total_models_tested: number;
  successful_models: string[];
  stored_models: string[];
  model_comparison: Record<string, any>;
  success: boolean;
}

export interface TeamStats {
  team_id: string;
  team_name: string;
  member_count: number;
  total_co2_saved_grams: number;
  total_energy_saved_kwh: number;
  avg_latency_this_week_ms: number;
  cost_savings_usd: number;
  green_tokens_earned: number;
  nft_badges_count: number;
  efficiency_rank?: number;
  total_teams: number;
  weekly_trend: number;
  period_start: string;
  period_end: string;
}

export interface ModelUsageStats {
  model_name: string;
  usage_count: number;
  total_energy_kwh: number;
  total_co2_grams: number;
  avg_latency_ms: number;
  efficiency_score: number;
}

export interface DashboardData {
  team_stats: TeamStats;
  model_leaderboard: {
    team_id: string;
    models: ModelUsageStats[];
    total_requests: number;
    period: string;
  };
  team_leaderboard: {
    teams: Array<{
      rank: number;
      name: string;
      value: number;
      secondary_value?: number;
      change_percent?: number;
      badge?: string;
    }>;
    current_team_rank: number;
    total_teams: number;
    period: string;
  };
  statistical_analysis?: any;
  last_updated: string;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Chat endpoints
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const params = new URLSearchParams({
      message: request.message,
      model: request.model || 'gemini-2.5-flash',
      user_id: request.user_id || 'anonymous',
      team_id: request.team_id || 'team-engineering'
    });
    
    return this.request<ChatResponse>(`/api/v1/chat?${params.toString()}`, {
      method: 'POST',
    });
  }

  async testAllModels(message: string, user_id: string = 'anonymous', team_id: string = 'team-engineering'): Promise<ModelComparisonResponse> {
    const params = new URLSearchParams({
      message,
      user_id,
      team_id
    });
    
    return this.request<ModelComparisonResponse>(`/api/v1/models/test-all?${params.toString()}`, {
      method: 'POST',
    });
  }

  // Dashboard endpoints
  async getTeamDashboard(team_id: string, days_back: number = 7): Promise<DashboardData> {
    return this.request<DashboardData>(`/api/v1/teams/${team_id}/dashboard?days_back=${days_back}`);
  }

  async getModelLeaderboard(team_id: string, days_back: number = 7) {
    return this.request(`/api/v1/teams/${team_id}/models/leaderboard?days_back=${days_back}`);
  }

  async getTeamLeaderboard(current_team_id: string, days_back: number = 7) {
    return this.request(`/api/v1/teams/leaderboard?current_team_id=${current_team_id}&days_back=${days_back}`);
  }

  // Analytics endpoints
  async performStatisticalAnalysis(team_ids: string[], analysis_type: string = 'efficiency_comparison') {
    return this.request('/api/v1/analytics/statistical', {
      method: 'POST',
      body: JSON.stringify({ team_ids, analysis_type }),
    });
  }

  async generateForecast(team_ids: string[], metric: string = 'co2_saved', days_ahead: number = 7) {
    return this.request('/api/v1/analytics/forecast', {
      method: 'POST',
      body: JSON.stringify({ team_ids, metric, days_ahead }),
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Admin endpoints
  async getAdminDashboard() {
    return this.request('/api/v1/admin/dashboard');
  }

  async getOrgTeamLeaderboard(limit: number = 50) {
    return this.request(`/api/v1/admin/teams/leaderboard?limit=${limit}`);
  }

  async getOrgModelLeaderboard(limit: number = 20) {
    return this.request(`/api/v1/admin/models/leaderboard?limit=${limit}`);
  }
}

export const apiService = new ApiService();
export default apiService;
