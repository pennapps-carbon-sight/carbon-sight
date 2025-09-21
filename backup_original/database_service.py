"""
Database service for CarbonSight Dashboard API.
Handles all database operations using Supabase.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import time
import base64
import random
from supabase import create_client, Client

from config import config
from models import (
    TeamStats, ModelUsageStats, LeaderboardEntry, 
    ModelLeaderboard, TeamLeaderboard, StatisticalAnalysis
)


class DatabaseService:
    """
    Service class for database operations.
    
    Handles all interactions with the Supabase database including
    team statistics, leaderboards, and analytical data.
    """
    
    def __init__(self):
        """Initialize database service with Supabase client."""
        if not config.is_database_configured:
            raise ValueError("Database configuration is incomplete")
        
        self.client: Client = create_client(
            config.supabase_url,
            config.supabase_key
        )
    
    async def get_team_stats(
        self, 
        team_id: str, 
        days_back: int = 7
    ) -> Optional[TeamStats]:
        """
        Get comprehensive team statistics.
        
        Args:
            team_id: Unique team identifier
            days_back: Number of days to look back for statistics
            
        Returns:
            TeamStats object with all team metrics, or None if team not found
        """
        try:
            # Get team basic info
            team_response = self.client.table("teams").select("*").eq("team_id", team_id).execute()
            if not team_response.data:
                return None
            
            team_data = team_response.data[0]
            
            # Get team members
            members_response = self.client.table("users").select("*").eq("team_id", team_id).execute()
            member_count = len(members_response.data)
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Get energy usage data for the period
            energy_response = self.client.table("energy_usage").select("*").eq(
                "team_id", team_id
            ).gte("created_at", start_date.isoformat()).execute()
            
            # Calculate aggregated metrics
            total_co2_saved = sum(record.get("co2_saved_grams", 0) for record in energy_response.data)
            total_energy_saved = sum(record.get("energy_saved_kwh", 0) for record in energy_response.data)
            total_cost_savings = sum(record.get("cost_savings_usd", 0) for record in energy_response.data)
            total_tokens = sum(record.get("green_tokens_earned", 0) for record in energy_response.data)
            
            # Calculate average latency
            latencies = [record.get("latency_ms", 0) for record in energy_response.data if record.get("latency_ms")]
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            
            # Calculate weekly trend (simplified)
            weekly_trend = 5.2  # Mock calculation - would be real in production
            
            # Get team ranking
            ranking_data = await self._get_team_ranking(team_id)
            
            return TeamStats(
                team_id=team_id,
                team_name=team_data["team_name"],
                member_count=member_count,
                total_co2_saved_grams=total_co2_saved,
                total_energy_saved_kwh=total_energy_saved,
                avg_latency_this_week_ms=avg_latency,
                cost_savings_usd=total_cost_savings,
                green_tokens_earned=total_tokens,
                nft_badges_count=len([t for t in energy_response.data if t.get("nft_badge_earned")]),
                efficiency_rank=ranking_data.get("rank"),
                total_teams=ranking_data.get("total_teams", 1),
                weekly_trend=weekly_trend,
                period_start=start_date,
                period_end=end_date
            )
            
        except Exception as e:
            print(f"Error fetching team stats: {e}")
            return None
    
    async def get_model_leaderboard(
        self, 
        team_id: str, 
        days_back: int = 7,
        limit: int = 10
    ) -> Optional[ModelLeaderboard]:
        """
        Get model usage leaderboard for a team.
        
        Args:
            team_id: Team identifier
            days_back: Number of days to analyze
            
        Returns:
            ModelLeaderboard with model usage statistics
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Get model usage data
            usage_response = self.client.table("model_usage").select("*").eq(
                "team_id", team_id
            ).gte("created_at", start_date.isoformat()).execute()
            
            # Aggregate by model
            model_stats = {}
            total_requests = 0
            
            for record in usage_response.data:
                model_name = record.get("model_name", "unknown")
                total_requests += 1
                
                if model_name not in model_stats:
                    model_stats[model_name] = {
                        "usage_count": 0,
                        "total_energy": 0,
                        "total_co2": 0,
                        "latencies": []
                    }
                
                model_stats[model_name]["usage_count"] += 1
                model_stats[model_name]["total_energy"] += record.get("energy_kwh", 0)
                model_stats[model_name]["total_co2"] += record.get("co2_grams", 0)
                model_stats[model_name]["latencies"].append(record.get("latency_ms", 0))
            
            # Convert to ModelUsageStats objects
            models = []
            for model_name, stats in model_stats.items():
                avg_latency = sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0
                efficiency_score = self._calculate_efficiency_score(stats["total_energy"], stats["total_co2"])
                
                models.append(ModelUsageStats(
                    model_name=model_name,
                    usage_count=stats["usage_count"],
                    total_energy_kwh=stats["total_energy"],
                    total_co2_grams=stats["total_co2"],
                    avg_latency_ms=avg_latency,
                    efficiency_score=efficiency_score
                ))
            
            # Sort by efficiency score
            models.sort(key=lambda x: x.efficiency_score, reverse=True)
            
            return ModelLeaderboard(
                team_id=team_id,
                models=models,
                total_requests=total_requests,
                period=f"Last {days_back} days"
            )
            
        except Exception as e:
            print(f"Error fetching model leaderboard: {e}")
            return None
    
    async def get_team_leaderboard(
        self, 
        current_team_id: str = "engineering", 
        days_back: int = 7,
        limit: int = 10
    ) -> Optional[TeamLeaderboard]:
        """
        Get team efficiency leaderboard.
        
        Args:
            current_team_id: Current team's ID for ranking
            days_back: Number of days to analyze
            
        Returns:
            TeamLeaderboard with team rankings
        """
        try:
            # Get all teams
            teams_response = self.client.table("teams").select("*").execute()
            
            # Calculate stats for each team
            team_entries = []
            current_team_rank = 1
            
            for team in teams_response.data:
                team_id = team["team_id"]
                team_stats = await self.get_team_stats(team_id, days_back)
                
                if team_stats:
                    # Calculate efficiency score
                    efficiency_score = self._calculate_team_efficiency_score(team_stats)
                    
                    entry = LeaderboardEntry(
                        rank=0,  # Will be set after sorting
                        name=team_stats.team_name,
                        value=efficiency_score,
                        secondary_value=team_stats.total_co2_saved_grams,
                        change_percent=team_stats.weekly_trend,
                        badge=self._get_team_badge(efficiency_score)
                    )
                    
                    team_entries.append(entry)
                    
                    if team_id == current_team_id:
                        current_team_rank = len(team_entries)
            
            # Sort by efficiency score
            team_entries.sort(key=lambda x: x.value, reverse=True)
            
            # Update ranks
            for i, entry in enumerate(team_entries):
                entry.rank = i + 1
                if entry.name == teams_response.data[current_team_rank - 1]["team_name"]:
                    current_team_rank = i + 1
            
            return TeamLeaderboard(
                teams=team_entries,
                current_team_rank=current_team_rank,
                total_teams=len(team_entries),
                period=f"Last {days_back} days"
            )
            
        except Exception as e:
            print(f"Error fetching team leaderboard: {e}")
            return None
    
    async def get_statistical_analysis(
        self, 
        team_ids: List[str], 
        analysis_type: str = "efficiency_comparison"
    ) -> Optional[StatisticalAnalysis]:
        """
        Perform statistical analysis on team data.
        
        Args:
            team_ids: List of team IDs to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            StatisticalAnalysis with results
        """
        try:
            # Get data for all teams
            team_data = []
            for team_id in team_ids:
                stats = await self.get_team_stats(team_id)
                if stats:
                    team_data.append(stats)
            
            if len(team_data) < 2:
                return None
            
            # Perform analysis based on type
            if analysis_type == "efficiency_comparison":
                return await self._perform_efficiency_analysis(team_data)
            elif analysis_type == "forecast":
                return await self._perform_forecast_analysis(team_data)
            else:
                return None
                
        except Exception as e:
            print(f"Error performing statistical analysis: {e}")
            return None
    
    def _calculate_efficiency_score(self, energy_kwh: float, co2_grams: float) -> float:
        """Calculate efficiency score for a model."""
        if energy_kwh == 0:
            return 0.0
        
        # Simple efficiency calculation (higher is better)
        # In production, this would be more sophisticated
        base_efficiency = 1.0 / (energy_kwh + 0.1)  # Avoid division by zero
        co2_factor = 1.0 / (co2_grams + 0.1)
        
        return min(1.0, (base_efficiency + co2_factor) / 2)
    
    def _calculate_team_efficiency_score(self, team_stats: TeamStats) -> float:
        """Calculate overall efficiency score for a team."""
        if team_stats.total_energy_saved_kwh == 0:
            return 0.0
        
        # Weighted efficiency score
        energy_efficiency = team_stats.total_energy_saved_kwh / max(1, team_stats.member_count)
        co2_efficiency = team_stats.total_co2_saved_grams / max(1, team_stats.member_count)
        token_efficiency = team_stats.green_tokens_earned / max(1, team_stats.member_count)
        
        return (energy_efficiency + co2_efficiency + token_efficiency) / 3
    
    def _get_team_badge(self, efficiency_score: float) -> str:
        """Get badge based on efficiency score."""
        if efficiency_score >= 0.8:
            return "🥇 Gold"
        elif efficiency_score >= 0.6:
            return "🥈 Silver"
        elif efficiency_score >= 0.4:
            return "🥉 Bronze"
        else:
            return "🌱 Green"
    
    async def _get_team_ranking(self, team_id: str) -> Dict[str, int]:
        """Get team's current ranking."""
        # Mock implementation - would query actual rankings
        return {"rank": 3, "total_teams": 10}
    
    async def _perform_efficiency_analysis(self, team_data: List[TeamStats]) -> StatisticalAnalysis:
        """Perform efficiency comparison analysis."""
        # Mock statistical analysis
        return StatisticalAnalysis(
            analysis_type="efficiency_comparison",
            teams_compared=[team.team_id for team in team_data],
            p_value=0.023,
            is_significant=True,
            confidence_level=0.95,
            chart_data={
                "teams": [team.team_name for team in team_data],
                "efficiency_scores": [self._calculate_team_efficiency_score(team) for team in team_data]
            }
        )
    
    # Admin Dashboard Methods
    async def get_all_teams(self) -> List[Dict[str, Any]]:
        """Get all teams in the organization."""
        try:
            response = self.client.table("teams").select("*").execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting all teams: {e}")
            return []
    
    async def get_total_requests_count(self) -> int:
        """Get total number of AI requests across all teams."""
        try:
            response = self.client.table("ai_requests").select("request_id", count="exact").execute()
            return response.count or 0
        except Exception as e:
            print(f"Error getting total requests count: {e}")
            return 0
    
    async def get_blockchain_ledger(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get blockchain ledger of $GREEN payouts for Proof-of-Green."""
        try:
            # Mock blockchain data - in real implementation, this would query blockchain
            ledger_entries = []
            for i in range(min(limit, 20)):  # Mock 20 entries
                ledger_entries.append({
                    "transaction_id": f"GREEN_{int(time.time())}_{i}",
                    "team_id": f"team-{i % 4 + 1}",
                    "user_id": f"user_{i}",
                    "amount_green": round(random.uniform(0.1, 5.0), 2),
                    "co2_saved_grams": round(random.uniform(10, 100), 2),
                    "energy_saved_kwh": round(random.uniform(0.01, 0.5), 4),
                    "timestamp": datetime.now().isoformat(),
                    "block_hash": f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
                    "status": "confirmed"
                })
            
            return {
                "entries": ledger_entries,
                "total_entries": len(ledger_entries),
                "total_green_distributed": sum(entry["amount_green"] for entry in ledger_entries),
                "total_co2_saved": sum(entry["co2_saved_grams"] for entry in ledger_entries),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting blockchain ledger: {e}")
            return {"entries": [], "total_entries": 0, "error": str(e)}
    
    async def get_carbon_credit_export(self, format: str = "json", period: str = "last_30_days") -> Dict[str, Any]:
        """Get carbon credit export data for compliance/PR."""
        try:
            # Mock carbon credit data
            export_data = {
                "organization": "CarbonSight Corp",
                "period": period,
                "total_co2_saved_grams": round(random.uniform(1000, 10000), 2),
                "total_energy_saved_kwh": round(random.uniform(100, 1000), 2),
                "certificate_id": f"CC_{int(time.time())}",
                "verification_hash": f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
                "teams_contributing": [
                    {"team_id": "engineering", "co2_saved": round(random.uniform(200, 2000), 2)},
                    {"team_id": "marketing", "co2_saved": round(random.uniform(150, 1500), 2)},
                    {"team_id": "sales", "co2_saved": round(random.uniform(100, 1000), 2)},
                    {"team_id": "research", "co2_saved": round(random.uniform(300, 3000), 2)}
                ],
                "models_used": [
                    {"model": "gemini-1.5-flash", "efficiency_score": 95, "usage_percent": 60},
                    {"model": "gemini-1.5-pro", "efficiency_score": 75, "usage_percent": 30},
                    {"model": "gemini-2.0-flash", "efficiency_score": 98, "usage_percent": 10}
                ],
                "export_formats": {
                    "json": {},
                    "csv": "",
                    "pdf": ""
                },
                "generated_at": datetime.now().isoformat(),
                "valid_until": (datetime.now() + timedelta(days=365)).isoformat()
            }
            
            # Fill export formats after data is created (avoid circular reference)
            export_data["export_formats"]["json"] = {
                "organization": export_data["organization"],
                "period": export_data["period"],
                "total_co2_saved_grams": export_data["total_co2_saved_grams"],
                "total_energy_saved_kwh": export_data["total_energy_saved_kwh"],
                "certificate_id": export_data["certificate_id"],
                "verification_hash": export_data["verification_hash"]
            }
            export_data["export_formats"]["csv"] = f"data:text/csv;base64,{base64.b64encode(str(export_data).encode()).decode()}"
            export_data["export_formats"]["pdf"] = f"data:application/pdf;base64,{base64.b64encode(b'Mock PDF Content').decode()}"
            
            return export_data
        except Exception as e:
            print(f"Error getting carbon credit export: {e}")
            return {"error": str(e), "export_data": None}
    
    async def _perform_forecast_analysis(self, team_data: List[TeamStats]) -> StatisticalAnalysis:
        """Perform forecast analysis."""
        # Mock forecast analysis
        return StatisticalAnalysis(
            analysis_type="forecast",
            teams_compared=[team.team_id for team in team_data],
            forecast_data={
                "predictions": {
                    "Marketing": {"overtake_date": "Tuesday", "confidence": 0.85}
                }
            },
            forecast_accuracy=0.78,
            chart_data={
                "trend_lines": "Mock trend data for visualization"
            }
        )
    
    async def log_job(
        self,
        job_id: str,
        user_id: str,
        model_used: str,
        tokens_input: int,
        tokens_output: int,
        energy_wh: float,
        co2e_g: float,
        processing_time_ms: int,
        was_green_swap: bool = False,
        region: str = "unknown"
    ) -> bool:
        """
        Log a job execution to the database.
        
        Args:
            job_id: Unique identifier for the job
            user_id: ID of the user who ran the job
            model_used: AI model that was used
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens
            energy_wh: Energy consumed in watt-hours
            co2e_g: CO2 emissions in grams
            processing_time_ms: Processing time in milliseconds
            was_green_swap: Whether this was a green model swap
            region: Geographic region where the job ran
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Insert into ai_requests table
            request_data = {
                "request_id": job_id,
                "user_id": user_id,
                "team_id": "engineering",  # Use clean team ID
                "model_used": model_used,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "energy_wh": energy_wh,
                "co2e_g": co2e_g,
                "processing_time_ms": processing_time_ms,
                "was_green_swap": was_green_swap,
                "was_auto_selected": True,  # Track auto vs manual selection
                "region": region,
                "created_at": "now()"
            }
            
            response = self.client.table("ai_requests").insert(request_data).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"Error logging job: {e}")
            return False
    
    async def log_ai_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Log AI request with comprehensive metrics to ai_requests table.
        
        Args:
            request_data: Dictionary containing all request and metrics data
            
        Returns:
            Boolean indicating success
        """
        try:
            # Prepare data for insertion
            insert_data = {
                "prompt": request_data.get("prompt", ""),
                "response": request_data.get("response", ""),
                "model_used": request_data.get("model_used", ""),
                "user_id": request_data.get("user_id", "anonymous"),
                "team_id": request_data.get("team_id", "team-engineering"),
                "latency_ms": request_data.get("latency_ms"),
                "cost_usd": request_data.get("cost_usd"),
                "input_tokens": request_data.get("input_tokens"),
                "output_tokens": request_data.get("output_tokens"),
                "total_tokens": request_data.get("total_tokens"),
                "input_cost_usd": request_data.get("input_cost_usd"),
                "output_cost_usd": request_data.get("output_cost_usd"),
                "tokens_per_second": request_data.get("tokens_per_second"),
                "cost_per_token": request_data.get("cost_per_token"),
                "cost_per_character": request_data.get("cost_per_character"),
                "prompt_complexity": request_data.get("prompt_complexity"),
                "efficiency_score": request_data.get("efficiency_score"),
                "created_at": "now()"
            }
            
            response = self.client.table("ai_requests").insert(insert_data).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"Error logging AI request: {e}")
            return False
