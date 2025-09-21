"""
Main FastAPI application for CarbonSight Dashboard API.
Provides comprehensive dashboard data and analytics for teams and admins.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime
import time

from config import config
from models import (
    DashboardData, TeamStats, ModelLeaderboard, 
    TeamLeaderboard, StatisticalAnalysis, PromptingPanelRequest, PromptingPanelResponse
)
from database_service import DatabaseService
from analytics_service import AnalyticsService
from gemini_service import GeminiService
from openai_service import OpenAIService
from metrics_service import MetricsService
from ml_service import MLService

# Initialize FastAPI app
app = FastAPI(
    title=config.api_title,
    version=config.api_version,
    description="CarbonSight Dashboard API - Team and Admin analytics for sustainable AI usage"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
database_service = DatabaseService()
analytics_service = AnalyticsService()
gemini_service = GeminiService()
openai_service = OpenAIService()
metrics_service = MetricsService()
ml_service = MLService()


def get_database_service() -> DatabaseService:
    """Dependency to get database service instance."""
    return database_service


def get_analytics_service() -> AnalyticsService:
    """Dependency to get analytics service instance."""
    return analytics_service


def get_openai_service() -> OpenAIService:
    """Dependency to get OpenAI service instance."""
    return openai_service


def get_metrics_service() -> MetricsService:
    """Dependency to get metrics service instance."""
    return metrics_service


def get_ml_service() -> MLService:
    """Dependency to get ML service instance."""
    return ml_service


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "CarbonSight Dashboard API",
        "version": config.api_version,
        "description": "Team and Admin dashboards for sustainable AI usage",
        "endpoints": {
            "team_dashboard": "/api/v1/teams/{team_id}/dashboard",
            "model_leaderboard": "/api/v1/teams/{team_id}/models/leaderboard",
            "team_leaderboard": "/api/v1/teams/leaderboard",
            "statistical_analysis": "/api/v1/analytics/statistical",
            "forecast": "/api/v1/analytics/forecast",
            "visualization": "/api/v1/analytics/visualization"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database_configured": config.is_database_configured
    }


# Team Dashboard Endpoints
@app.get("/api/v1/teams/{team_id}/dashboard", response_model=DashboardData)
async def get_team_dashboard(
    team_id: str,
    days_back: int = 7,
    include_analytics: bool = True,
    db: DatabaseService = Depends(get_database_service),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get comprehensive dashboard data for a team.
    
    This endpoint provides all the data needed for the team dashboard including:
    - Team statistics and metrics
    - Model usage leaderboard
    - Team efficiency ranking
    - Optional statistical analysis
    """
    try:
        # Get team statistics
        team_stats = await db.get_team_stats(team_id, days_back)
        if not team_stats:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Get model leaderboard
        model_leaderboard = await db.get_model_leaderboard(team_id, days_back)
        if not model_leaderboard:
            raise HTTPException(status_code=500, detail="Failed to load model leaderboard")
        
        # Get team leaderboard
        team_leaderboard = await db.get_team_leaderboard(team_id, days_back)
        if not team_leaderboard:
            raise HTTPException(status_code=500, detail="Failed to load team leaderboard")
        
        # Get statistical analysis if requested
        statistical_analysis = None
        if include_analytics:
            # Get all teams for comparison
            all_teams = await db.get_team_leaderboard(team_id, days_back)
            if all_teams and len(all_teams.teams) > 1:
                team_ids = [f"team_{i}" for i in range(len(all_teams.teams))]
                statistical_analysis = await db.get_statistical_analysis(team_ids, "efficiency_comparison")
        
        return DashboardData(
            team_stats=team_stats,
            model_leaderboard=model_leaderboard,
            team_leaderboard=team_leaderboard,
            statistical_analysis=statistical_analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")


@app.get("/api/v1/teams/{team_id}/models/leaderboard", response_model=ModelLeaderboard)
async def get_model_leaderboard(
    team_id: str,
    days_back: int = 7,
    db: DatabaseService = Depends(get_database_service)
):
    """
    Get model usage leaderboard for a specific team.
    
    Shows which models the team uses most frequently, ranked by efficiency
    and output quality tradeoffs.
    """
    try:
        leaderboard = await db.get_model_leaderboard(team_id, days_back)
        if not leaderboard:
            raise HTTPException(status_code=404, detail="Team not found or no data available")
        
        return leaderboard
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model leaderboard: {str(e)}")


@app.get("/api/v1/teams/leaderboard", response_model=TeamLeaderboard)
async def get_team_leaderboard(
    current_team_id: str,
    days_back: int = 7,
    db: DatabaseService = Depends(get_database_service)
):
    """
    Get team efficiency leaderboard.
    
    Shows where teams rank in energy savings and $GREEN tokens earned.
    """
    try:
        leaderboard = await db.get_team_leaderboard(current_team_id, days_back)
        if not leaderboard:
            raise HTTPException(status_code=500, detail="Failed to load team leaderboard")
        
        return leaderboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load team leaderboard: {str(e)}")


# Analytics Endpoints
@app.post("/api/v1/analytics/statistical")
async def perform_statistical_analysis(
    team_ids: List[str],
    analysis_type: str = "efficiency_comparison",
    metric: str = "co2_saved",
    db: DatabaseService = Depends(get_database_service),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Perform statistical analysis between teams.
    
    Provides hypothesis testing, ANOVA analysis, and significance testing
    to identify differences in team efficiency.
    """
    try:
        # Get team data
        teams_data = []
        for team_id in team_ids:
            team_stats = await db.get_team_stats(team_id)
            if team_stats:
                teams_data.append(team_stats)
        
        if len(teams_data) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 teams for statistical analysis")
        
        # Perform analysis
        if analysis_type == "hypothesis_testing":
            result = await analytics.perform_hypothesis_testing(teams_data, metric)
        else:
            result = await db.get_statistical_analysis(team_ids, analysis_type)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistical analysis failed: {str(e)}")


@app.post("/api/v1/analytics/forecast")
async def generate_forecast(
    team_ids: List[str],
    metric: str = "co2_saved",
    days_ahead: int = 7,
    db: DatabaseService = Depends(get_database_service),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Generate regression-based forecasts for team metrics.
    
    Provides predictions about future performance and identifies potential
    team overtakes based on current trends.
    """
    try:
        # Get team data
        teams_data = []
        for team_id in team_ids:
            team_stats = await db.get_team_stats(team_id)
            if team_stats:
                teams_data.append(team_stats)
        
        if not teams_data:
            raise HTTPException(status_code=400, detail="No team data available for forecasting")
        
        # Generate forecast
        result = await analytics.generate_forecast(teams_data, metric, days_ahead)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")


@app.post("/api/v1/analytics/visualization")
async def generate_visualization_data(
    team_ids: List[str],
    chart_type: str = "boxplot",
    db: DatabaseService = Depends(get_database_service),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Generate data for various chart visualizations.
    
    Provides data for boxplots, trend lines, scatter plots, and radar charts
    to visualize team performance and efficiency metrics.
    """
    try:
        # Get team data
        teams_data = []
        for team_id in team_ids:
            team_stats = await db.get_team_stats(team_id)
            if team_stats:
                teams_data.append(team_stats)
        
        if not teams_data:
            raise HTTPException(status_code=400, detail="No team data available for visualization")
        
        # Generate visualization data
        result = await analytics.generate_visualization_data(teams_data, chart_type)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization data generation failed: {str(e)}")


# Real AI Chat Endpoints
@app.post("/api/v1/chat")
async def real_chat(
    message: str,
    model: str = "gemini-2.5-flash",
    user_id: str = "anonymous",
    team_id: str = "team-engineering",
    gemini: GeminiService = Depends(lambda: gemini_service),
    db: DatabaseService = Depends(get_database_service)
):
    """
    Real chat completion using Gemini API with energy tracking.
    
    This endpoint:
    1. Calls actual Gemini API
    2. Measures real energy usage
    3. Saves real data to database
    4. Returns real energy metrics
    """
    try:
        # Call real Gemini API
        result = await gemini.generate_content(
            prompt=message,
            model=model
        )
        
        if result["success"]:
            # Save real usage data to database
            await db.log_ai_request({
                "prompt": message,
                "response": result["response_text"],
                "model_used": model,
                "user_id": user_id,
                "team_id": team_id,
                "latency_ms": int(result["processing_time_ms"]),
                "cost_usd": 0.0,  # TODO: Calculate real cost
                "energy_kwh": result["energy_metrics"].energy_kwh,
                "co2_grams": result["energy_metrics"].co2_grams,
                "tokens_input": int(result["tokens_used"]["input"]),
                "tokens_output": int(result["tokens_used"]["output"])
            })
        
        return {
            "message": result["response_text"],
            "model_used": model,
            "energy_metrics": result["energy_metrics"],
            "tokens_used": result["tokens_used"],
            "processing_time_ms": result["processing_time_ms"],
            "success": result["success"]
        }
        
    except Exception as e:
        return {
            "message": f"Error: {str(e)}",
            "model_used": model,
            "error": str(e),
            "success": False
        }


# Prompting Panel Endpoints
@app.post("/api/v1/prompting/chat", response_model=PromptingPanelResponse)
async def chat_completion(
    request: PromptingPanelRequest,
    db: DatabaseService = Depends(get_database_service)
):
    """
    Handle chat completion with energy feedback.
    
    This endpoint processes user prompts and provides inline energy bar
    and badge feedback for each interaction.
    """
    try:
        # Mock implementation - in production this would integrate with AI models
        response_message = f"Mock response to: {request.message}"
        
        # Mock energy metrics
        energy_kwh = 0.05 if "flash" in (request.model_preference or "").lower() else 0.12
        co2_grams = energy_kwh * config.base_co2_per_kwh
        was_green_swap = "flash" in (request.model_preference or "").lower()
        
        # Calculate rewards
        green_tokens_earned = co2_grams * config.reward_rate_per_gram_co2 if was_green_swap else 0.0
        
        # Determine efficiency badge
        if was_green_swap:
            efficiency_badge = "🔵 Efficient Model (Flash) — Green Choice."
        else:
            efficiency_badge = "🔴 High Energy Model (Pro) — consider switching."
        
        return PromptingPanelResponse(
            response_message=response_message,
            model_used=request.model_preference or "gemini-2.5-flash",
            was_green_swap=was_green_swap,
            energy_metrics={
                "energy_kwh": energy_kwh,
                "co2_grams": co2_grams,
                "model_name": request.model_preference or "gemini-2.5-flash",
                "region": "us-central1"
            },
            green_tokens_earned=green_tokens_earned,
            latency_ms=800 if was_green_swap else 1200,
            processing_time_ms=1000,
            efficiency_badge=efficiency_badge,
            recommendation="Consider using Flash model for better efficiency" if not was_green_swap else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


# Hybrid Chat: Gemini Response + OpenAI Metrics
@app.post("/api/v1/chat/hybrid")
async def hybrid_chat(
    message: str,
    gemini_model: str = "gemini-1.5-flash",
    openai_model: str = "gpt-3.5-turbo",
    user_id: str = "anonymous",
    team_id: str = "team-engineering",
    gemini: GeminiService = Depends(lambda: gemini_service),
    openai_service: OpenAIService = Depends(get_openai_service),
    metrics_service: MetricsService = Depends(get_metrics_service),
    db: DatabaseService = Depends(get_database_service)
):
    """
    Hybrid chat: Gemini for response + OpenAI for metrics.
    
    This endpoint:
    1. Calls Gemini API for actual response (what user sees)
    2. Calls OpenAI API for latency/cost metrics (background)
    3. Combines both for comprehensive tracking
    4. Saves detailed metrics to database
    """
    try:
        # Call Gemini for actual response
        gemini_result = await gemini.generate_content(
            prompt=message,
            model=gemini_model
        )
        
        # Call OpenAI for metrics (in parallel)
        openai_result = await openai_service.generate_content(
            prompt=message,
            model=openai_model
        )
        
        if gemini_result["success"] and openai_result["success"]:
            # Track metrics using OpenAI data
            metrics = metrics_service.track_request_metrics(
                prompt=message,
                response=gemini_result["response_text"],  # Use Gemini response
                model=f"{gemini_model}+{openai_model}",  # Combined model name
                latency_ms=openai_result["latency_ms"],  # Use OpenAI latency
                cost_usd=openai_result["cost_usd"],  # Use OpenAI cost
                input_tokens=openai_result["input_tokens"],
                output_tokens=openai_result["output_tokens"],
                total_tokens=openai_result["total_tokens"]
            )
            
            # Save to database with detailed metrics
            await db.log_ai_request({
                "prompt": message,
                "response": gemini_result["response_text"],  # Gemini response
                "model_used": f"{gemini_model}+{openai_model}",
                "user_id": user_id,
                "team_id": team_id,
                "latency_ms": openai_result["latency_ms"],
                "cost_usd": openai_result["cost_usd"],
                "input_tokens": openai_result["input_tokens"],
                "output_tokens": openai_result["output_tokens"],
                "total_tokens": openai_result["total_tokens"],
                "input_cost_usd": openai_result["input_cost_usd"],
                "output_cost_usd": openai_result["output_cost_usd"],
                "tokens_per_second": metrics["tokens_per_second"],
                "cost_per_token": metrics["cost_per_token"],
                "cost_per_character": metrics["cost_per_character"],
                "prompt_complexity": metrics["prompt_complexity"],
                "efficiency_score": metrics["efficiency_score"]
            })
        
        return {
            "message": gemini_result["response_text"],  # User gets Gemini response
            "response_model": gemini_model,
            "metrics_model": openai_model,
            "latency_ms": openai_result["latency_ms"],
            "cost_usd": openai_result["cost_usd"],
            "tokens_used": {
                "input": openai_result["input_tokens"],
                "output": openai_result["output_tokens"],
                "total": openai_result["total_tokens"]
            },
            "efficiency_score": metrics.get("efficiency_score", 0),
            "success": gemini_result["success"]
        }
        
    except Exception as e:
        return {
            "message": f"Error: {str(e)}",
            "success": False,
            "error": str(e)
        }


# Metrics and Performance Endpoints
@app.get("/api/v1/metrics/performance")
async def get_performance_metrics(
    model: Optional[str] = None,
    hours: int = 24,
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get performance metrics summary for recent requests."""
    try:
        summary = metrics_service.get_performance_summary(model=model, hours=hours)
        return {"metrics": summary, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


@app.get("/api/v1/metrics/model-comparison")
async def get_model_comparison(
    hours: int = 24,
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Compare performance across different models."""
    try:
        comparison = metrics_service.get_model_comparison(hours=hours)
        return {"comparison": comparison, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


@app.post("/api/v1/metrics/efficiency-recommendations")
async def get_efficiency_recommendations(
    current_model: str,
    prompt: str,
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get efficiency recommendations for a specific prompt and model."""
    try:
        recommendations = metrics_service.get_efficiency_recommendations(current_model, prompt)
        return {"recommendations": recommendations, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


@app.get("/api/v1/openai/models")
async def get_available_models(
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """Get available OpenAI models and their configurations."""
    try:
        models = openai_service.get_available_models()
        model_info = {}
        for model in models:
            model_info[model] = openai_service.get_model_info(model)
        return {"models": model_info, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


@app.post("/api/v1/openai/estimate-cost")
async def estimate_cost(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    estimated_output_tokens: int = 100,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """Estimate cost for a prompt without making API call."""
    try:
        estimate = openai_service.estimate_cost(prompt, model, estimated_output_tokens)
        return {"estimate": estimate, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


# Model Comparison Endpoints
@app.post("/api/v1/models/test-all")
async def test_all_gemini_models(
    message: str,
    user_id: str = "anonymous",
    team_id: str = "team-engineering",
    gemini: GeminiService = Depends(lambda: gemini_service),
    db: DatabaseService = Depends(get_database_service)
):
    """
    Test a prompt against all 6 Gemini models and store results.
    
    This endpoint:
    1. Tests the prompt against all 6 Gemini models
    2. Stores all results in Supabase
    3. Returns comparison and best model recommendation
    """
    try:
        # Test all models
        comparison_result = await gemini.test_all_models(message)
        
        # Store all successful results in database
        stored_models = []
        for model_name, result in comparison_result["results"].items():
            if result.get("success", False):
                # Store each model result
                await db.log_ai_request({
                    "prompt": message,
                    "response": result["response_text"],
                    "model_used": model_name,
                    "user_id": user_id,
                    "team_id": team_id,
                    "latency_ms": result.get("processing_time_ms", 0),
                    "cost_usd": 0.0,  # Gemini doesn't provide cost
                    "input_tokens": result.get("tokens_used", {}).get("input", 0),
                    "output_tokens": result.get("tokens_used", {}).get("output", 0),
                    "total_tokens": result.get("tokens_used", {}).get("total", 0),
                    "efficiency_score": 0.0,  # Will be calculated by metrics service
                    "is_model_comparison": True  # Flag for comparison requests
                })
                stored_models.append(model_name)
        
        return {
            "prompt": message,
            "best_model": comparison_result["best_model"],
            "recommendation": comparison_result["recommendation"],
            "total_models_tested": comparison_result["total_models_tested"],
            "successful_models": comparison_result["successful_models"],
            "stored_models": stored_models,
            "model_comparison": comparison_result["model_comparison"],
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


# Admin Dashboard Endpoints
@app.get("/api/v1/admin/test")
async def admin_test():
    """Simple admin test endpoint."""
    return {"message": "Admin endpoint working", "success": True}

@app.get("/api/v1/admin/dashboard")
async def get_admin_dashboard(
    db: DatabaseService = Depends(get_database_service),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get org-wide admin dashboard with all teams and models.
    Includes leaderboards, statistical reports, and blockchain data.
    """
    try:
        # Get org-wide team leaderboard
        org_teams = await db.get_all_teams()
        team_leaderboard = await db.get_team_leaderboard(limit=50)  # Top 50 teams
        
        # Get org-wide model leaderboard
        model_leaderboard = await db.get_model_leaderboard(team_id="engineering", limit=20)  # Top 20 models
        
        # Get org-wide statistical analysis
        statistical_analysis = await analytics.perform_org_wide_analysis(org_teams)
        
        # Get blockchain ledger data
        blockchain_ledger = await db.get_blockchain_ledger()
        
        # Get carbon credit export data
        carbon_export = await db.get_carbon_credit_export()
        
        return {
            "org_team_leaderboard": team_leaderboard,
            "org_model_leaderboard": model_leaderboard,
            "statistical_analysis": statistical_analysis,
            "blockchain_ledger": blockchain_ledger,
            "carbon_credit_export": carbon_export,
            "total_teams": len(org_teams),
            "total_requests": await db.get_total_requests_count(),
            "last_updated": datetime.now().isoformat(),
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}

@app.get("/api/v1/admin/teams/leaderboard")
async def get_org_team_leaderboard(
    limit: int = 50,
    period: str = "last_7_days",
    db: DatabaseService = Depends(get_database_service)
):
    """Get org-wide team leaderboard ranked by efficiency and CO2 savings."""
    try:
        leaderboard = await db.get_team_leaderboard(limit=limit, period=period)
        return {"leaderboard": leaderboard, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.get("/api/v1/admin/models/leaderboard")
async def get_org_model_leaderboard(
    limit: int = 20,
    period: str = "last_7_days",
    db: DatabaseService = Depends(get_database_service)
):
    """Get org-wide model leaderboard showing which models drain the most energy."""
    try:
        leaderboard = await db.get_model_leaderboard(limit=limit, period=period)
        return {"leaderboard": leaderboard, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.get("/api/v1/admin/statistical-reports")
async def get_org_statistical_reports(
    report_type: str = "comprehensive",
    db: DatabaseService = Depends(get_database_service),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """Get org-wide statistical inference reports."""
    try:
        all_teams = await db.get_all_teams()
        reports = await analytics.generate_org_wide_reports(all_teams, report_type)
        return {"reports": reports, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.get("/api/v1/admin/blockchain-ledger")
async def get_blockchain_ledger(
    limit: int = 100,
    offset: int = 0,
    db: DatabaseService = Depends(get_database_service)
):
    """Get blockchain ledger of $GREEN payouts for transparent Proof-of-Green."""
    try:
        ledger = await db.get_blockchain_ledger(limit=limit, offset=offset)
        return {"ledger": ledger, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.get("/api/v1/admin/carbon-credit-export")
async def get_carbon_credit_export(
    format: str = "json",  # json, csv, pdf
    period: str = "last_30_days",
    db: DatabaseService = Depends(get_database_service)
):
    """Get carbon credit export data for compliance/PR."""
    try:
        export_data = await db.get_carbon_credit_export(format=format, period=period)
        return {"export_data": export_data, "format": format, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


# ML Analysis Endpoints
@app.post("/api/v1/ml/analyze-prompt")
async def analyze_prompt_complexity(
    prompt: str,
    ml: MLService = Depends(lambda: ml_service)
):
    """Analyze prompt complexity and predict efficiency metrics."""
    try:
        analysis = await ml.analyze_prompt_complexity(prompt)
        return {"analysis": analysis, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.post("/api/v1/ml/predict-efficiency")
async def predict_efficiency_metrics(
    prompt: str,
    model: str = "gemini-1.5-flash",
    user_history: Optional[List[Dict]] = None,
    ml: MLService = Depends(lambda: ml_service)
):
    """Predict efficiency metrics for a prompt-model combination."""
    try:
        predictions = await ml.predict_efficiency_metrics(prompt, model, user_history)
        return {"predictions": predictions, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.post("/api/v1/ml/generate-formulas")
async def generate_regression_formulas(
    historical_data: List[Dict],
    ml: MLService = Depends(lambda: ml_service)
):
    """Generate regression formulas for sustainability metrics."""
    try:
        formulas = await ml.generate_regression_formulas(historical_data)
        return {"formulas": formulas, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.post("/api/v1/ml/generate-charts")
async def generate_chart_data(
    data: List[Dict],
    chart_type: str = "efficiency_trend",
    ml: MLService = Depends(lambda: ml_service)
):
    """Generate data for various chart visualizations."""
    try:
        chart_data = await ml.generate_chart_data(data, chart_type)
        return {"chart_data": chart_data, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.post("/api/v1/ml/optimize-prompt")
async def optimize_prompt_for_efficiency(
    prompt: str,
    ml: MLService = Depends(lambda: ml_service)
):
    """Suggest prompt optimizations for better efficiency."""
    try:
        optimization = await ml.optimize_prompt_for_efficiency(prompt)
        return {"optimization": optimization, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.post("/api/v1/ml/calculate-efficiency-score")
async def calculate_prompt_efficiency_score(
    prompt: str,
    response: str,
    energy_used: float,
    processing_time: int,
    ml: MLService = Depends(lambda: ml_service)
):
    """Calculate comprehensive efficiency score for a prompt-response pair."""
    try:
        score = await ml.calculate_prompt_efficiency_score(
            prompt, response, energy_used, processing_time
        )
        return {"efficiency_score": score, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=config.debug
    )
