# 🌱 GreenAI Dashboard API

A comprehensive FastAPI backend for tracking AI model energy consumption, CO2 emissions, and sustainability metrics across teams and organizations.

## 🚀 Features

### Team Dashboard
- **Prompting Panel**: Real-time AI chat with energy tracking
- **Dual Leaderboards**: 
  - Top Models Used (by team efficiency)
  - Team Standing (energy savings + $GREEN earned)
- **Team Stats**: Average latency, CO2 saved, cost savings, tokens/NFTs earned
- **Statistical Inference**: Hypothesis testing, regression forecasting, ANOVA analysis

### Admin Dashboard
- **Org-wide Team Leaderboard**: All teams ranked by efficiency
- **Org-wide Model Leaderboard**: Which models drain the most energy
- **Statistical Reports**: Comprehensive org-wide analysis
- **Blockchain Ledger**: Transparent $GREEN payouts (Proof-of-Green)
- **Carbon Credit Export**: Compliance certificates for PR/regulatory use

### ML Integration
- **Prompt Analysis**: Complexity scoring and efficiency prediction
- **Model Optimization**: Auto-switching between efficient models
- **Sustainability Formulas**: Real-time energy and CO2 calculations
- **Chart Data Generation**: Ready for frontend visualizations

## 🛠️ Tech Stack

- **FastAPI**: Modern Python web framework
- **Supabase**: Database and authentication
- **Gemini API**: Real AI model integration
- **Python 3.13**: Core runtime
- **Pydantic**: Data validation
- **ML Libraries**: scikit-learn, tensorflow, transformers, torch

## 📋 Prerequisites

- Python 3.13+
- Supabase account
- Gemini API key

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Irapathak/CarbonSight.git
   cd CarbonSight
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example .env
   # Edit .env with your Supabase and Gemini credentials
   ```

4. **Set up database**
   ```bash
   # Run the SQL scripts in Supabase SQL editor:
   # - database_setup.sql
   # - create_ai_requests_table.sql
   ```

5. **Start the server**
   ```bash
   python3 run.py
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Admin Dashboard: http://localhost:8000/api/v1/admin/dashboard

## 📊 API Endpoints

### Team Dashboard
- `GET /api/v1/teams/{team_id}/dashboard` - Team dashboard data
- `GET /api/v1/teams/{team_id}/leaderboard` - Team leaderboard
- `GET /api/v1/teams/{team_id}/stats` - Team statistics
- `POST /api/v1/chat` - Real-time AI chat with energy tracking

### Admin Dashboard
- `GET /api/v1/admin/dashboard` - Complete admin dashboard
- `GET /api/v1/admin/teams/leaderboard` - Org-wide team rankings
- `GET /api/v1/admin/models/leaderboard` - Model efficiency rankings
- `GET /api/v1/admin/statistical-reports` - Statistical analysis
- `GET /api/v1/admin/blockchain-ledger` - $GREEN payout history
- `GET /api/v1/admin/carbon-credit-export` - Compliance certificates

### ML Analysis
- `POST /api/v1/ml/analyze-prompt` - Analyze prompt complexity
- `POST /api/v1/ml/predict-efficiency` - Predict efficiency metrics
- `POST /api/v1/ml/generate-formulas` - Generate regression formulas
- `POST /api/v1/ml/generate-charts` - Generate chart data
- `POST /api/v1/ml/optimize-prompt` - Suggest prompt optimizations

## 🏗️ Project Structure

```
CarbonSight/
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── models.py              # Pydantic data models
├── database_service.py    # Supabase database operations
├── analytics_service.py   # Statistical analysis
├── gemini_service.py      # AI model integration
├── ml_service.py          # ML analysis interface
├── requirements.txt       # Python dependencies
├── run.py                 # Server startup script
├── .env                   # Environment variables
└── README.md             # This file
```

## 🌍 Sustainability Features

### Real Energy Tracking
- **System Monitoring**: CPU, memory usage via psutil
- **Model Efficiency**: Different energy profiles per AI model
- **Regional Factors**: Carbon intensity by geographic region
- **Time-based Optimization**: More efficient during off-peak hours

### Sample Sustainability Formulas
```python
# Energy calculation with multiple factors
energy_wh = base_energy * system_energy_factor * model_efficiency * time_efficiency * complexity_factor
co2_grams = base_co2 * system_energy_factor * model_efficiency * time_efficiency * complexity_factor * regional_carbon_intensity
```

### Blockchain Integration
- **$GREEN Tokens**: Reward system for sustainable AI usage
- **Proof-of-Green**: Transparent blockchain ledger
- **Carbon Credits**: Exportable certificates for compliance

## 🔧 Configuration

### Environment Variables
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Database Schema
- **teams**: Team information and metadata
- **users**: User profiles and team associations
- **ai_requests**: AI usage tracking with energy metrics
- **energy_usage**: Historical energy consumption data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **Supabase** for database and authentication
- **Google Gemini** for AI model integration
- **PennApps** for the hackathon platform

## 📞 Contact

- **Repository**: [CarbonSight](https://github.com/Irapathak/CarbonSight)
- **Issues**: [GitHub Issues](https://github.com/Irapathak/CarbonSight/issues)

---

**Built with ❤️ for a more sustainable AI future** 🌱