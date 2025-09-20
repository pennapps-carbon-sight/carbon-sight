"""
Pydantic models for GreenAI Dashboard API.
Defines data structures for requests, responses, and internal data.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EnergyMetrics(BaseModel):
    """Energy and carbon metrics for a model or job."""
    
    energy_kwh: float = Field(..., description="Energy consumption in kWh")
    co2_grams: float = Field(..., description="CO2 emissions in grams")
    model_name: str = Field(..., description="Name of the AI model used")
    region: str = Field("us-central1", description="Datacenter region")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the metrics were recorded")


class ModelUsageStats(BaseModel):
    """Statistics for model usage within a team."""
    
    model_name: str = Field(..., description="Name of the AI model")
    usage_count: int = Field(..., description="Number of times this model was used")
    total_energy_kwh: float = Field(..., description="Total energy consumed")
    total_co2_grams: float = Field(..., description="Total CO2 emissions")
    avg_latency_ms: float = Field(..., description="Average response latency in milliseconds")
    efficiency_score: float = Field(..., description="Energy efficiency score (0-1)")


class TeamStats(BaseModel):
    """Team-level sustainability statistics."""
    
    team_id: str = Field(..., description="Unique team identifier")
    team_name: str = Field(..., description="Display name of the team")
    member_count: int = Field(..., description="Number of team members")
    
    # Energy and sustainability metrics
    total_co2_saved_grams: float = Field(..., description="Total CO2 saved by team")
    total_energy_saved_kwh: float = Field(..., description="Total energy saved by team")
    avg_latency_this_week_ms: float = Field(..., description="Average latency this week")
    
    # Financial metrics
    cost_savings_usd: float = Field(..., description="Total cost savings in USD")
    green_tokens_earned: float = Field(..., description="Total $GREEN tokens earned")
    nft_badges_count: int = Field(..., description="Number of NFT badges earned")
    
    # Rankings and trends
    efficiency_rank: Optional[int] = Field(None, description="Team's efficiency ranking")
    total_teams: int = Field(..., description="Total number of teams")
    weekly_trend: float = Field(..., description="Weekly change in CO2 savings (%)")
    
    # Time period
    period_start: datetime = Field(..., description="Start of statistics period")
    period_end: datetime = Field(..., description="End of statistics period")


class LeaderboardEntry(BaseModel):
    """Single entry in a leaderboard."""
    
    rank: int = Field(..., description="Position in leaderboard")
    name: str = Field(..., description="Name of team or model")
    value: float = Field(..., description="Primary metric value")
    secondary_value: Optional[float] = Field(None, description="Secondary metric value")
    change_percent: Optional[float] = Field(None, description="Change from previous period (%)")
    badge: Optional[str] = Field(None, description="Badge or status indicator")


class ModelLeaderboard(BaseModel):
    """Leaderboard of most used models by team."""
    
    team_id: str = Field(..., description="Team identifier")
    models: List[ModelUsageStats] = Field(..., description="Model usage statistics")
    total_requests: int = Field(..., description="Total requests made by team")
    period: str = Field(..., description="Time period for statistics")


class TeamLeaderboard(BaseModel):
    """Leaderboard of teams by efficiency metrics."""
    
    teams: List[LeaderboardEntry] = Field(..., description="Team rankings")
    current_team_rank: int = Field(..., description="Current team's rank")
    total_teams: int = Field(..., description="Total number of teams")
    period: str = Field(..., description="Time period for statistics")


class StatisticalAnalysis(BaseModel):
    """Statistical analysis results for teams."""
    
    analysis_type: str = Field(..., description="Type of analysis performed")
    teams_compared: List[str] = Field(..., description="Teams included in analysis")
    
    # Hypothesis testing results
    p_value: Optional[float] = Field(None, description="P-value from statistical test")
    is_significant: Optional[bool] = Field(None, description="Whether difference is statistically significant")
    confidence_level: float = Field(0.95, description="Confidence level for analysis")
    
    # Forecast results
    forecast_data: Optional[Dict[str, Any]] = Field(None, description="Forecast predictions")
    forecast_accuracy: Optional[float] = Field(None, description="Forecast accuracy score")
    
    # Visualization data
    chart_data: Optional[Dict[str, Any]] = Field(None, description="Data for generating charts")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When analysis was performed")


class PromptingPanelRequest(BaseModel):
    """Request for prompting panel interaction."""
    
    user_id: str = Field(..., description="User making the request")
    team_id: str = Field(..., description="User's team")
    message: str = Field(..., description="User's prompt message")
    model_preference: Optional[str] = Field(None, description="Preferred model")
    auto_switch_enabled: bool = Field(True, description="Whether auto-switch is enabled")


class PromptingPanelResponse(BaseModel):
    """Response from prompting panel interaction."""
    
    response_message: str = Field(..., description="AI response message")
    model_used: str = Field(..., description="Model that generated the response")
    was_green_swap: bool = Field(..., description="Whether a green swap occurred")
    
    # Energy feedback
    energy_metrics: EnergyMetrics = Field(..., description="Energy consumption for this request")
    green_tokens_earned: float = Field(0.0, description="$GREEN tokens earned")
    
    # Performance metrics
    latency_ms: int = Field(..., description="Response latency in milliseconds")
    processing_time_ms: int = Field(..., description="Total processing time")
    
    # Badge/status
    efficiency_badge: str = Field(..., description="Efficiency status badge")
    recommendation: Optional[str] = Field(None, description="Recommendation for next time")


class DashboardData(BaseModel):
    """Complete dashboard data for a team."""
    
    team_stats: TeamStats = Field(..., description="Team statistics")
    model_leaderboard: ModelLeaderboard = Field(..., description="Model usage leaderboard")
    team_leaderboard: TeamLeaderboard = Field(..., description="Team efficiency leaderboard")
    statistical_analysis: Optional[StatisticalAnalysis] = Field(None, description="Statistical analysis results")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="When data was last updated")
