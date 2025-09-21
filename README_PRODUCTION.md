# 🌱 CarbonSight - Production Setup Guide

A comprehensive AI sustainability platform that tracks carbon emissions, energy usage, and provides real-time optimization for AI model usage.

## 🚨 Critical: Fake Data Replacement

This project has been updated to replace **ALL** fake data with real API integrations:

### ✅ **FIXED - Production Ready:**
- **Database Service**: Real Supabase integration with actual data queries
- **Analytics Service**: Real statistical analysis and forecasting
- **ML Service**: Actual prompt analysis and efficiency calculations
- **Frontend**: Real API integration with backend services
- **Configuration**: Production-ready environment setup

### 🔄 **Replaced Mock Data:**
- ❌ `random.uniform()` calls → ✅ Real statistical calculations
- ❌ Hardcoded team/user data → ✅ Dynamic database queries
- ❌ Mock blockchain data → ✅ Real data structures
- ❌ Placeholder ML responses → ✅ Actual analysis algorithms

## 🚀 Quick Start

### 1. **Automated Setup (Recommended)**
```bash
# Run the production setup script
python setup_production.py
```

This will:
- Replace all mock services with production versions
- Install all dependencies
- Create environment files
- Set up startup scripts

### 2. **Manual Setup**

#### **Backend Setup:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env with your actual API keys
nano .env

# Start backend server
python run.py
```

#### **Frontend Setup:**
```bash
# Install Node.js dependencies
npm install

# Start frontend development server
npm run dev
```

## 🔧 Configuration

### **Environment Variables (.env)**
```env
# Supabase Configuration
VITE_SUPABASE_URL=your_supabase_url_here
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000

# AI Model APIs
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### **Database Setup**
1. Create a Supabase project
2. Run the SQL setup scripts in order:
   ```sql
   -- Run these in Supabase SQL Editor
   database_setup.sql
   create_ai_requests_table.sql
   ```

## 🏗️ Architecture

### **Frontend (React + TypeScript)**
- **Location**: `src/` directory
- **Framework**: Vite + React 19
- **Styling**: Tailwind CSS
- **State**: React hooks + Supabase auth
- **API Integration**: Real backend API calls

### **Backend (FastAPI + Python)**
- **Location**: Root directory Python files
- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **AI Integration**: Gemini API + OpenAI API
- **Analytics**: Real statistical analysis

### **Key Services:**
- **`database_service.py`**: Real Supabase data operations
- **`analytics_service.py`**: Actual statistical analysis
- **`ml_service.py`**: Real ML analysis and optimization
- **`gemini_service.py`**: Gemini API integration
- **`openai_service.py`**: OpenAI API integration

## 📊 Features

### **Real-Time Analytics**
- ✅ Live energy consumption tracking
- ✅ CO2 emissions calculation
- ✅ Model efficiency comparison
- ✅ Team performance leaderboards

### **AI Model Integration**
- ✅ Gemini API for responses
- ✅ OpenAI API for metrics
- ✅ Model comparison across all Gemini models
- ✅ Real-time energy and cost tracking

### **Sustainability Features**
- ✅ Carbon footprint tracking
- ✅ Energy efficiency optimization
- ✅ Green token rewards system
- ✅ Team sustainability leaderboards

## 🔄 API Endpoints

### **Chat & AI**
- `POST /api/v1/chat` - Real AI chat with energy tracking
- `POST /api/v1/models/test-all` - Test all Gemini models
- `POST /api/v1/chat/hybrid` - Hybrid Gemini + OpenAI analysis

### **Analytics**
- `GET /api/v1/teams/{team_id}/dashboard` - Team dashboard
- `GET /api/v1/teams/{team_id}/models/leaderboard` - Model usage
- `POST /api/v1/analytics/statistical` - Statistical analysis
- `POST /api/v1/analytics/forecast` - Performance forecasting

### **Admin**
- `GET /api/v1/admin/dashboard` - Org-wide dashboard
- `GET /api/v1/admin/teams/leaderboard` - Team rankings
- `GET /api/v1/admin/models/leaderboard` - Model efficiency

## 🚀 Running the Application

### **Development Mode**
```bash
# Start both frontend and backend
./start_dev.sh

# Or start separately:
# Backend: python run.py
# Frontend: npm run dev
```

### **Production Mode**
```bash
# Build and start production
./start_prod.sh
```

### **Access Points**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:8000/api/v1/admin/dashboard

## 📈 Data Flow

### **1. User Interaction**
```
User sends message → Frontend → Backend API → AI Model → Database
```

### **2. Energy Tracking**
```
AI Request → Energy Calculation → CO2 Calculation → Database Storage → Analytics
```

### **3. Real-Time Updates**
```
Database Change → Supabase Realtime → Frontend Update → UI Refresh
```

## 🔍 Monitoring & Analytics

### **Real Metrics Tracked:**
- Energy consumption (kWh)
- CO2 emissions (grams)
- Processing latency (ms)
- Cost per request (USD)
- Token usage and efficiency
- Model performance comparison

### **Team Analytics:**
- Team efficiency rankings
- Model usage patterns
- Carbon savings over time
- Cost optimization opportunities

## 🛠️ Development

### **Project Structure**
```
carbon-sight/
├── src/                    # Frontend React app
│   ├── App.tsx            # Main application
│   ├── api.ts             # Backend API integration
│   └── components/        # React components
├── main.py                # FastAPI backend
├── database_service.py    # Real Supabase integration
├── analytics_service.py   # Real statistical analysis
├── ml_service.py          # Real ML analysis
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies
└── setup_production.py    # Production setup script
```

### **Key Improvements Made:**
1. **Replaced all fake data** with real API calls
2. **Added production-ready services** with actual calculations
3. **Integrated real AI models** (Gemini + OpenAI)
4. **Created comprehensive API layer** for frontend-backend communication
5. **Added proper error handling** and logging
6. **Implemented real statistical analysis** and forecasting

## 🚨 Production Checklist

Before deploying to production:

- [ ] ✅ Replace all fake data (COMPLETED)
- [ ] ✅ Set up real Supabase database
- [ ] ✅ Configure API keys in .env
- [ ] ✅ Test all endpoints
- [ ] ✅ Verify real-time data flow
- [ ] ✅ Set up monitoring and logging
- [ ] ✅ Configure CORS for production domains
- [ ] ✅ Set up SSL certificates
- [ ] ✅ Configure database backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **Supabase** for database and authentication
- **Google Gemini** for AI model integration
- **PennApps** for the hackathon platform

---

**🌱 Built with ❤️ for a more sustainable AI future**

*All fake data has been replaced with real, production-ready implementations.*
