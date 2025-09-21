# Carbonsight Documentation  

## 1. Introduction  
Carbonsight is an enterprise-focused platform that makes AI usage both sustainable and rewarding.  
Every AI prompt generates carbon emissions, and enterprises today lack visibility into this impact.  

**Carbonsight solves this by:**  
- Tracking carbon costs per prompt  
- Dynamically routing queries to the most efficient Gemini model  
- Allowing employees to control quality vs. energy trade-offs  
- Incentivizing sustainable choices with $GREEN tokens + NFT badges  
- Providing managers with dashboards to track team/organization-wide savings  

---

## 2. System Architecture  

### 2.1 Core Agentic Framework (Google ADK)  
The backbone of Carbonsight is built using Google ADK agents:  
- **Root Agent** – orchestrates requests between sub-agents  
- **Routing Agent** – decides which Gemini model to use (Flash, Pro, Flash-Lite)  
- **Embedding Agent** – generates embeddings to:  
  - Compare semantic similarity across prompts (caching & reuse)  
  - Optimize model routing based on prompt type  
- **Thinking Agent** – allocates thinking budgets dynamically to balance reasoning power with energy usage  

**Repo Structure**  

carbon_agent/
│── agent.py # Entrypoint
│── root_agent.py # Routes queries
│── routing_agent.py # Model selection
│── embedding_agent.py # Semantic embeddings + caching
│── thinking_agent.py # Thinking budget allocation
│── tools/
│ ├── gemini_client.py # Gemini API wrapper
│ ├── routing_tools.py # Model routing + inference
│ ├── embedding_tools.py # Embedding + similarity + cache
│ ├── thinking_tools.py # Budget allocation logic
│── .env # GEMINI_API_KEY


---

### 2.2 Model Routing Logic  
**Auto-switch ON (default):**  
- Queries dynamically routed based on CO₂ + latency thresholds  
- User sees energy bar feedback:
  
Used: Gemini Flash | 0.05 kWh | 20g CO₂ | 0.002 $GREEN earned


**Auto-switch OFF (manual):**  
- Employee selects model from dropdown  
- Visual feedback:  
- 🔴 High Energy (Pro)  
- 🔵 Efficient (Flash)  

---

### 2.3 Embeddings  
Using **Gemini Embedding-001** for:  
- Semantic similarity → detect duplicate/near-duplicate prompts  
- Caching → avoid recompute for repeated queries  

**Benefit:** Cuts redundant compute → lowers energy + cost.  

---

### 2.4 Thinking Budgets  
Automatically assigned by the Thinking Agent:  
- Easy tasks → low budget (0)  
- Medium tasks → moderate budget (~2048)  
- Hard tasks → high budget (~8192)  

**Employee Control:**  
- Error tolerance % (baseline 3%)  
- Lower tolerance → higher thinking budget (accuracy > efficiency)  
- Higher tolerance → smaller budget (efficiency > accuracy)  

---

## 3. Frontend  

### 3.1 Prompting Panel  
- Chatbot-like interface  
- Toggle: Auto-Switch ON/OFF  
- Energy bar or badge shown per response  

### 3.2 Employee Controls  
- **Tolerance Slider** – set acceptable quality loss (e.g., 5%)  
- **Model Picker** – if auto-switch OFF  

---

## 4. Dashboards  

### 4.1 Team Dashboard  
- **Prompting Panel** with inline feedback  
- **Leaderboards**  
  - Models used by team (Flash vs Pro)  
  - Team standing vs others in carbon savings  
- **Team Stats**  
  - Avg latency  
  - CO₂ saved vs baseline  
  - Cost savings in $  
  - Tokens/NFTs earned  
  - Trendlines + daily/weekly reports  
- **Advanced Analytics (optional)**  
  - Hypothesis tests, regression forecasts, ANOVA comparisons  
  - Visualizations: boxplots, confidence bands  

### 4.2 Admin Dashboard  
  - Org-wide leaderboards  
  - Model usage heatmap (“carbon hog” models)  
  - Blockchain ledger of $GREEN payouts → Proof-of-Green  
  - Exportable CO₂ certificates for compliance/PR  

---

## 5. Blockchain Incentivization  

### 5.1 Proof-of-Green  
Each green swap (Flash instead of Pro) triggers a blockchain log.  

The system mints:  
- **ERC-721 NFTs** – unique badges (Bronze, Silver, Gold)  
- **ERC-20 $GREEN tokens** – fungible credits tied to CO₂ savings  

### 5.2 Reward Logic  

tokens = CO₂_saved_in_grams / 10

Example: Saving 50g CO₂ → 5 $GREEN tokens  

### 5.3 Transparency  
- Rewards managed by smart contracts on Polygon testnet  
- Enterprises get verifiable Proof-of-Green ledger  
- Employees get wallet-linked rewards for sustainability  

---

## 6. Enterprise Value  

**For Managers:**  
- Track how project teams reduce carbon cost  
- Benchmark teams against each other  
- Export CO₂ savings reports for compliance & ESG reporting  

**For Teams/Employees:**  
- See real-time impact of their AI usage  
- Earn tokens and recognition for efficient AI practices  
- Compete with other teams in a friendly way  

---

## 7. Future Roadmap  
- Integration with vector DBs (Pinecone, Weaviate, Qdrant) for enterprise-scale embeddings  
- Integration with enterprise auth (SSO)  
- Marketplace for redeeming $GREEN tokens  
- “Carbon Offsetting” option → tokens fund certified carbon credits  

---

## Built With  
- **Python** – Backend logic, Google ADK agent framework  
- **React.js** – Frontend chatbot and dashboard  
- **Google ADK** – Agentic framework for model routing, embeddings, and thinking budget allocation  
- **Google Gemini API** – Generative AI and embeddings  
- **FastAPI (via ADK)** – API serving layer
- **Supabase**
- **Polygon (Testnet)** – Blockchain, NFT, and $GREEN token incentives  
