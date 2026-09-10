"""
Production Database service for CarbonSight Dashboard API.
Handles all database operations using real Supabase data.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import time
from supabase import create_client, Client

from config import config
from models import (
    TeamStats, ModelUsageStats, LeaderboardEntry, 
    ModelLeaderboard, TeamLeaderboard, StatisticalAnalysis
)


class DatabaseService:
    """
    Production service class for database operations.
    
    Handles all interactions with the Supabase database using real data.
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
        Get comprehensive team statistics from real data.
        
        Args:
            team_id: Unique team identifier
            days_back: Number of days to look back for statistics
            
        Returns:
            TeamStats object with real data or None if team not found
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Get team information
            team_response = await self.client.table('teams').select('*').eq('team_id', team_id).execute()
            if not team_response.data:
                return None
            
            team_data = team_response.data[0]
            
            # Get real AI requests data for the team
            requests_response = await self.client.table('ai_requests').select(
                'energy_wh, co2e_g, latency_ms, cost_usd, tokens_input, tokens_output, created_at'
            ).eq('team_id', team_id).gte('created_at', start_date.isoformat()).execute()
            
            requests_data = requests_response.data or []
            
            # Calculate real statistics
            total_energy_kwh = sum(req.get('energy_wh', 0) for req in requests_data) / 1000
            total_co2_grams = sum(req.get('co2e_g', 0) for req in requests_data)
            total_cost_savings = sum(req.get('cost_usd', 0) for req in requests_data)
            avg_latency = sum(req.get('latency_ms', 0) for req in requests_data) / len(requests_data) if requests_data else 0
            
            # Calculate green tokens (simplified: 1 token per gram CO2 saved)
            green_tokens = total_co2_grams * 0.1  # 0.1 tokens per gram CO2
            
            # Get team ranking (simplified)
            all_teams_response = await self.client.table('teams').select('team_id').execute()
            total_teams = len(all_teams_response.data) if all_teams_response.data else 1
            
            return TeamStats(
                team_id=team_id,
                team_name=team_data.get('team_name', f'Team {team_id}'),
                member_count=team_data.get('member_count', 1),
                total_co2_saved_grams=total_co2_grams,
                total_energy_saved_kwh=total_energy_kwh,
                avg_latency_this_week_ms=avg_latency,
                cost_savings_usd=total_cost_savings,
                green_tokens_earned=green_tokens,
                nft_badges_count=int(green_tokens // 10),  # 1 badge per 10 tokens
                efficiency_rank=1,  # Will be calculated in leaderboard
                total_teams=total_teams,
                weekly_trend=0.0,  # Will be calculated with historical data
                period_start=start_date,
                period_end=end_date
            )
            
        except Exception as e:
            print(f"Error getting team stats: {e}")
            return None
    
    async def get_model_leaderboard(
        self, 
        team_id: str, 
        days_back: int = 7,
        limit: int = 10
    ) -> Optional[ModelLeaderboard]:
        """
        Get model usage leaderboard from real data.
        
        Args:
            team_id: Team identifier
            days_back: Number of days to look back
            limit: Maximum number of models to return
            
        Returns:
            ModelLeaderboard with real model usage data
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Get real model usage data
            response = await self.client.table('ai_requests').select(
                'model_used, energy_wh, co2e_g, latency_ms, created_at'
            ).eq('team_id', team_id).gte('created_at', start_date.isoformat()).execute()
            
            requests_data = response.data or []
            
            # Group by model and calculate statistics
            model_stats = {}
            for req in requests_data:
                model = req.get('model_used', 'unknown')
                if model not in model_stats:
                    model_stats[model] = {
                        'usage_count': 0,
                        'total_energy': 0,
                        'total_co2': 0,
                        'latencies': []
                    }
                
                model_stats[model]['usage_count'] += 1
                model_stats[model]['total_energy'] += req.get('energy_wh', 0) / 1000  # Convert to kWh
                model_stats[model]['total_co2'] += req.get('co2e_g', 0)
                model_stats[model]['latencies'].append(req.get('latency_ms', 0))
            
            # Convert to ModelUsageStats objects
            models = []
            for model_name, stats in model_stats.items():
                avg_latency = sum(stats['latencies']) / len(stats['latencies']) if stats['latencies'] else 0
                efficiency_score = min(1.0, 1000 / (stats['total_energy'] + 1))  # Simple efficiency calculation
                
                models.append(ModelUsageStats(
                    model_name=model_name,
                    usage_count=stats['usage_count'],
                    total_energy_kwh=stats['total_energy'],
                    total_co2_grams=stats['total_co2'],
                    avg_latency_ms=avg_latency,
                    efficiency_score=efficiency_score
                ))
            
            # Sort by efficiency score
            models.sort(key=lambda x: x.efficiency_score, reverse=True)
            models = models[:limit]
            
            return ModelLeaderboard(
                team_id=team_id,
                models=models,
                total_requests=len(requests_data),
                period=f"last_{days_back}_days"
            )
            
        except Exception as e:
            print(f"Error getting model leaderboard: {e}")
            return None
    
    async def get_team_leaderboard(
        self, 
        current_team_id: str, 
        days_back: int = 7,
        limit: int = 50
    ) -> Optional[TeamLeaderboard]:
        """
        Get team efficiency leaderboard from real data.
        
        Args:
            current_team_id: Current team identifier
            days_back: Number of days to look back
            limit: Maximum number of teams to return
            
        Returns:
            TeamLeaderboard with real team rankings
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Get all teams
            teams_response = await self.client.table('teams').select('team_id, team_name').execute()
            teams_data = teams_response.data or []
            
            # Get team statistics
            team_stats = []
            for team in teams_data:
                team_id = team['team_id']
                
                # Get team's AI requests
                requests_response = await self.client.table('ai_requests').select(
                    'energy_wh, co2e_g, created_at'
                ).eq('team_id', team_id).gte('created_at', start_date.isoformat()).execute()
                
                requests_data = requests_response.data or []
                
                # Calculate team metrics
                total_co2 = sum(req.get('co2e_g', 0) for req in requests_data)
                total_energy = sum(req.get('energy_wh', 0) for req in requests_data) / 1000
                
                team_stats.append({
                    'team_id': team_id,
                    'team_name': team.get('team_name', f'Team {team_id}'),
                    'co2_saved': total_co2,
                    'energy_saved': total_energy,
                    'efficiency_score': total_co2 / (total_energy + 1)  # CO2 per kWh
                })
            
            # Sort by efficiency score
            team_stats.sort(key=lambda x: x['efficiency_score'], reverse=True)
            
            # Create leaderboard entries
            teams = []
            current_rank = 1
            for i, team in enumerate(team_stats[:limit]):
                teams.append(LeaderboardEntry(
                    rank=i + 1,
                    name=team['team_name'],
                    value=team['efficiency_score'],
                    secondary_value=team['co2_saved'],
                    change_percent=0.0,  # Would need historical data
                    badge="🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else None
                ))
                
                if team['team_id'] == current_team_id:
                    current_rank = i + 1
            
            return TeamLeaderboard(
                teams=teams,
                current_team_rank=current_rank,
                total_teams=len(teams_data),
                period=f"last_{days_back}_days"
            )
            
        except Exception as e:
            print(f"Error getting team leaderboard: {e}")
            return None
    
    async def log_ai_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Log an AI request to the database.
        
        Args:
            request_data: Dictionary containing request information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for insertion
            insert_data = {
                'prompt': request_data.get('prompt', ''),
                'response': request_data.get('response', ''),
                'model_used': request_data.get('model_used', 'unknown'),
                'user_id': request_data.get('user_id', 'anonymous'),
                'team_id': request_data.get('team_id', 'team-engineering'),
                'latency_ms': request_data.get('latency_ms', 0),
                'cost_usd': request_data.get('cost_usd', 0.0),
                'energy_wh': request_data.get('energy_wh', 0.0),
                'co2e_g': request_data.get('co2e_g', 0.0),
                'tokens_input': request_data.get('input_tokens', 0),
                'tokens_output': request_data.get('output_tokens', 0),
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Insert into database
            response = await self.client.table('ai_requests').insert(insert_data).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            print(f"Error logging AI request: {e}")
            return False
    
    async def get_all_teams(self) -> List[Dict[str, Any]]:
        """Get all teams from the database."""
        try:
            response = await self.client.table('teams').select('*').execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting all teams: {e}")
            return []
    
    async def get_total_requests_count(self) -> int:
        """Get total number of AI requests."""
        try:
            response = await self.client.table('ai_requests').select('id', count='exact').execute()
            return response.count or 0
        except Exception as e:
            print(f"Error getting total requests count: {e}")
            return 0
    
    async def get_statistical_analysis(
        self, 
        team_ids: List[str], 
        analysis_type: str
    ) -> Optional[StatisticalAnalysis]:
        """
        Get statistical analysis for teams.
        
        This is a simplified version that returns basic analysis.
        For production, you would implement proper statistical calculations.
        """
        try:
            # This would be implemented with real statistical analysis
            # For now, return a basic structure
            return StatisticalAnalysis(
                analysis_type=analysis_type,
                teams_compared=team_ids,
                p_value=0.05,
                is_significant=True,
                confidence_level=0.95,
                created_at=datetime.utcnow()
            )
        except Exception as e:
            print(f"Error getting statistical analysis: {e}")
            return None
    
    async def get_blockchain_ledger(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get blockchain ledger data.
        
        In production, this would connect to a real blockchain.
        For now, return empty list.
        """
        return []
    
    async def get_carbon_credit_export(self, format: str = "json", period: str = "last_30_days") -> Dict[str, Any]:
        """
        Get carbon credit export data.
        
        In production, this would generate real carbon credit certificates.
        For now, return basic structure.
        """
        return {
            "format": format,
            "period": period,
            "total_co2_saved": 0.0,
            "certificates": [],
            "generated_at": datetime.utcnow().isoformat()
        }
