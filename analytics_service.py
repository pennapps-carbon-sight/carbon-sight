"""
Analytics service for CarbonSight Dashboard API.
Handles statistical analysis, forecasting, and data visualization.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import random
import numpy as np

from models import TeamStats, StatisticalAnalysis, ModelUsageStats


class AnalyticsService:
    """
    Service class for advanced analytics and statistical analysis.
    
    Provides statistical testing, forecasting, and data visualization
    capabilities for the dashboard.
    """
    
    def __init__(self):
        """Initialize analytics service."""
        self.confidence_level = 0.95
        self.forecast_days = 7
    
    async def perform_hypothesis_testing(
        self, 
        teams_data: List[TeamStats], 
        metric: str = "co2_saved"
    ) -> Dict[str, Any]:
        """
        Perform hypothesis testing between teams.
        
        Args:
            teams_data: List of team statistics
            metric: Metric to test (co2_saved, energy_saved, efficiency)
            
        Returns:
            Dictionary with test results including p-value and significance
        """
        if len(teams_data) < 2:
            return {"error": "Need at least 2 teams for hypothesis testing"}
        
        try:
            # Extract metric values
            metric_values = self._extract_metric_values(teams_data, metric)
            
            if len(metric_values) < 2:
                return {"error": "Insufficient data for testing"}
            
            # Perform ANOVA test
            f_statistic, p_value = stats.f_oneway(*metric_values)
            
            # Calculate effect size (eta squared)
            effect_size = self._calculate_effect_size(metric_values)
            
            # Determine significance
            is_significant = p_value < (1 - self.confidence_level)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(metric_values)
            
            return {
                "test_type": "ANOVA",
                "f_statistic": float(f_statistic),
                "p_value": float(p_value),
                "is_significant": is_significant,
                "effect_size": effect_size,
                "confidence_level": self.confidence_level,
                "confidence_intervals": confidence_intervals,
                "teams_compared": [team.team_name for team in teams_data],
                "interpretation": self._interpret_test_results(p_value, is_significant, effect_size)
            }
            
        except Exception as e:
            return {"error": f"Hypothesis testing failed: {str(e)}"}
    
    async def generate_forecast(
        self, 
        team_data: List[TeamStats], 
        metric: str = "co2_saved",
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """
        Generate regression-based forecasts for team metrics.
        
        Args:
            team_data: Historical team data
            metric: Metric to forecast
            days_ahead: Number of days to forecast ahead
            
        Returns:
            Dictionary with forecast results and predictions
        """
        try:
            forecasts = {}
            
            for team in team_data:
                # Generate historical time series data (mock for now)
                historical_data = self._generate_historical_data(team, metric)
                
                if len(historical_data) < 3:
                    continue
                
                # Prepare data for regression
                X = np.array(range(len(historical_data))).reshape(-1, 1)
                y = np.array(historical_data)
                
                # Fit linear regression model
                model = LinearRegression()
                model.fit(X, y)
                
                # Generate forecast
                future_X = np.array(range(len(historical_data), len(historical_data) + days_ahead)).reshape(-1, 1)
                forecast_values = model.predict(future_X)
                
                # Calculate R-squared for model quality
                r2 = r2_score(y, model.predict(X))
                
                # Calculate confidence intervals
                confidence_intervals = self._calculate_forecast_confidence(
                    forecast_values, r2, len(historical_data)
                )
                
                forecasts[team.team_name] = {
                    "forecast_values": forecast_values.tolist(),
                    "r_squared": float(r2),
                    "confidence_intervals": confidence_intervals,
                    "trend": "increasing" if model.coef_[0] > 0 else "decreasing",
                    "slope": float(model.coef_[0]),
                    "next_week_prediction": float(forecast_values[-1])
                }
            
            # Find potential overtakes
            overtakes = self._find_potential_overtakes(forecasts)
            
            return {
                "forecasts": forecasts,
                "overtakes": overtakes,
                "forecast_accuracy": self._calculate_overall_accuracy(forecasts),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Forecast generation failed: {str(e)}"}
    
    async def generate_visualization_data(
        self, 
        teams_data: List[TeamStats],
        chart_type: str = "boxplot"
    ) -> Dict[str, Any]:
        """
        Generate data for various chart visualizations.
        
        Args:
            teams_data: Team statistics data
            chart_type: Type of chart (boxplot, trend, scatter, etc.)
            
        Returns:
            Dictionary with chart data and configuration
        """
        try:
            if chart_type == "boxplot":
                return self._generate_boxplot_data(teams_data)
            elif chart_type == "trend":
                return self._generate_trend_data(teams_data)
            elif chart_type == "scatter":
                return self._generate_scatter_data(teams_data)
            elif chart_type == "efficiency_radar":
                return self._generate_radar_data(teams_data)
            else:
                return {"error": f"Unsupported chart type: {chart_type}"}
                
        except Exception as e:
            return {"error": f"Visualization data generation failed: {str(e)}"}
    
    def _extract_metric_values(self, teams_data: List[TeamStats], metric: str) -> List[List[float]]:
        """Extract metric values for statistical testing."""
        values = []
        
        for team in teams_data:
            if metric == "co2_saved":
                # Generate sample data points for each team (mock)
                team_values = np.random.normal(
                    team.total_co2_saved_grams, 
                    team.total_co2_saved_grams * 0.1, 
                    10
                ).tolist()
            elif metric == "energy_saved":
                team_values = np.random.normal(
                    team.total_energy_saved_kwh,
                    team.total_energy_saved_kwh * 0.1,
                    10
                ).tolist()
            elif metric == "efficiency":
                efficiency_score = self._calculate_team_efficiency_score(team)
                team_values = np.random.normal(
                    efficiency_score,
                    efficiency_score * 0.05,
                    10
                ).tolist()
            else:
                team_values = [0.0]
            
            values.append(team_values)
        
        return values
    
    def _calculate_effect_size(self, metric_values: List[List[float]]) -> float:
        """Calculate eta squared (effect size) for ANOVA."""
        try:
            # Flatten all values
            all_values = [val for team_values in metric_values for val in team_values]
            
            # Calculate between-group and within-group variance
            grand_mean = np.mean(all_values)
            
            between_group_ss = 0
            within_group_ss = 0
            
            for team_values in metric_values:
                team_mean = np.mean(team_values)
                between_group_ss += len(team_values) * (team_mean - grand_mean) ** 2
                
                for value in team_values:
                    within_group_ss += (value - team_mean) ** 2
            
            total_ss = between_group_ss + within_group_ss
            
            if total_ss == 0:
                return 0.0
            
            return between_group_ss / total_ss
            
        except Exception:
            return 0.0
    
    def _calculate_confidence_intervals(self, metric_values: List[List[float]]) -> Dict[str, List[float]]:
        """Calculate confidence intervals for each team."""
        intervals = {}
        
        for i, team_values in enumerate(metric_values):
            if len(team_values) > 1:
                mean_val = np.mean(team_values)
                std_err = stats.sem(team_values)
                margin_error = std_err * stats.t.ppf((1 + self.confidence_level) / 2, len(team_values) - 1)
                
                intervals[f"team_{i}"] = [
                    float(mean_val - margin_error),
                    float(mean_val + margin_error)
                ]
            else:
                intervals[f"team_{i}"] = [float(team_values[0]), float(team_values[0])]
        
        return intervals
    
    def _interpret_test_results(self, p_value: float, is_significant: bool, effect_size: float) -> str:
        """Interpret statistical test results."""
        if not is_significant:
            return f"No significant difference found (p={p_value:.3f})"
        
        if effect_size < 0.01:
            effect_desc = "negligible"
        elif effect_size < 0.06:
            effect_desc = "small"
        elif effect_size < 0.14:
            effect_desc = "medium"
        else:
            effect_desc = "large"
        
        return f"Significant difference found (p={p_value:.3f}) with {effect_desc} effect size (η²={effect_size:.3f})"
    
    def _generate_historical_data(self, team: TeamStats, metric: str) -> List[float]:
        """Generate historical time series data for forecasting."""
        # Mock historical data generation
        base_value = getattr(team, f"total_{metric}_grams" if metric == "co2_saved" else f"total_{metric}_kwh", 100)
        
        # Generate 30 days of historical data with trend
        days = 30
        trend = np.random.uniform(-0.02, 0.02)  # Random trend
        noise = np.random.normal(0, 0.1, days)
        
        historical = []
        for i in range(days):
            value = base_value * (1 + trend * i + noise[i])
            historical.append(max(0, value))  # Ensure non-negative
        
        return historical
    
    def _calculate_forecast_confidence(
        self, 
        forecast_values: np.ndarray, 
        r_squared: float, 
        n_samples: int
    ) -> List[List[float]]:
        """Calculate confidence intervals for forecasts."""
        # Simplified confidence interval calculation
        confidence_intervals = []
        
        for value in forecast_values:
            # Standard error based on R-squared and sample size
            se = value * np.sqrt((1 - r_squared) / max(1, n_samples - 2))
            margin = se * 1.96  # 95% confidence
            
            confidence_intervals.append([
                float(value - margin),
                float(value + margin)
            ])
        
        return confidence_intervals
    
    def _find_potential_overtakes(self, forecasts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find potential team overtakes based on forecasts."""
        overtakes = []
        
        team_names = list(forecasts.keys())
        
        for i, team1 in enumerate(team_names):
            for team2 in team_names[i+1:]:
                forecast1 = forecasts[team1]["next_week_prediction"]
                forecast2 = forecasts[team2]["next_week_prediction"]
                
                # Check if team1 will overtake team2
                if forecast1 > forecast2:
                    overtakes.append({
                        "overtaking_team": team1,
                        "overtaken_team": team2,
                        "predicted_date": "Tuesday",  # Mock date
                        "confidence": min(0.95, forecasts[team1]["r_squared"])
                    })
        
        return overtakes
    
    def _calculate_overall_accuracy(self, forecasts: Dict[str, Any]) -> float:
        """Calculate overall forecast accuracy."""
        r_squared_values = [forecast["r_squared"] for forecast in forecasts.values()]
        return float(np.mean(r_squared_values)) if r_squared_values else 0.0
    
    def _generate_boxplot_data(self, teams_data: List[TeamStats]) -> Dict[str, Any]:
        """Generate data for boxplot visualization."""
        return {
            "chart_type": "boxplot",
            "data": {
                "teams": [team.team_name for team in teams_data],
                "co2_saved": [team.total_co2_saved_grams for team in teams_data],
                "energy_saved": [team.total_energy_saved_kwh for team in teams_data],
                "efficiency_scores": [self._calculate_team_efficiency_score(team) for team in teams_data]
            },
            "title": "Team Efficiency Distribution",
            "x_label": "Teams",
            "y_label": "Values"
        }
    
    def _generate_trend_data(self, teams_data: List[TeamStats]) -> Dict[str, Any]:
        """Generate data for trend line visualization."""
        return {
            "chart_type": "trend",
            "data": {
                "teams": [team.team_name for team in teams_data],
                "trends": [team.weekly_trend for team in teams_data],
                "values": [team.total_co2_saved_grams for team in teams_data]
            },
            "title": "Weekly CO2 Savings Trends",
            "x_label": "Time",
            "y_label": "CO2 Saved (grams)"
        }
    
    def _generate_scatter_data(self, teams_data: List[TeamStats]) -> Dict[str, Any]:
        """Generate data for scatter plot visualization."""
        return {
            "chart_type": "scatter",
            "data": {
                "x": [team.total_energy_saved_kwh for team in teams_data],
                "y": [team.total_co2_saved_grams for team in teams_data],
                "teams": [team.team_name for team in teams_data],
                "sizes": [team.member_count * 10 for team in teams_data]  # Bubble size
            },
            "title": "Energy vs CO2 Savings",
            "x_label": "Energy Saved (kWh)",
            "y_label": "CO2 Saved (grams)"
        }
    
    def _generate_radar_data(self, teams_data: List[TeamStats]) -> Dict[str, Any]:
        """Generate data for radar chart visualization."""
        return {
            "chart_type": "radar",
            "data": {
                "teams": [team.team_name for team in teams_data],
                "metrics": ["Efficiency", "CO2 Savings", "Energy Savings", "Cost Savings", "Tokens Earned"],
                "values": [
                    [
                        self._calculate_team_efficiency_score(team),
                        team.total_co2_saved_grams / 1000,  # Normalize
                        team.total_energy_saved_kwh / 100,   # Normalize
                        team.cost_savings_usd / 100,         # Normalize
                        team.green_tokens_earned / 100       # Normalize
                    ] for team in teams_data
                ]
            },
            "title": "Team Performance Radar",
            "max_values": [1.0, 5.0, 2.0, 5.0, 2.0]  # Max values for normalization
        }
    
    def _calculate_team_efficiency_score(self, team: TeamStats) -> float:
        """Calculate efficiency score for a team."""
        if team.member_count == 0:
            return 0.0
        
        # Weighted efficiency calculation
        energy_per_member = team.total_energy_saved_kwh / team.member_count
        co2_per_member = team.total_co2_saved_grams / team.member_count
        tokens_per_member = team.green_tokens_earned / team.member_count
        
        # Normalize and combine metrics
        efficiency = (energy_per_member + co2_per_member + tokens_per_member) / 3
        return min(1.0, efficiency / 100)  # Cap at 1.0
    
    # Admin Dashboard Analytics Methods
    async def perform_org_wide_analysis(self, teams: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform org-wide statistical analysis across all teams."""
        try:
            # Mock org-wide analysis
            analysis = {
                "analysis_type": "org_wide_efficiency",
                "total_teams": len(teams),
                "summary_stats": {
                    "avg_efficiency_score": round(random.uniform(75, 95), 1),
                    "total_co2_saved_grams": round(random.uniform(5000, 50000), 2),
                    "total_energy_saved_kwh": round(random.uniform(500, 5000), 2),
                    "most_efficient_team": teams[0]["team_name"] if teams else "Engineering",
                    "least_efficient_team": teams[-1]["team_name"] if teams else "Sales"
                },
                "team_rankings": [
                    {
                        "rank": i + 1,
                        "team_id": team["team_id"],
                        "team_name": team["team_name"],
                        "efficiency_score": round(random.uniform(70, 100), 1),
                        "co2_saved": round(random.uniform(100, 2000), 2),
                        "energy_saved": round(random.uniform(10, 200), 2)
                    }
                    for i, team in enumerate(teams[:10])  # Top 10 teams
                ],
                "model_analysis": {
                    "most_efficient_model": "gemini-2.0-flash",
                    "least_efficient_model": "gemini-1.5-pro",
                    "model_usage_distribution": {
                        "gemini-1.5-flash": 60,
                        "gemini-1.5-pro": 30,
                        "gemini-2.0-flash": 10
                    }
                },
                "trends": {
                    "weekly_efficiency_trend": round(random.uniform(-5, 15), 1),
                    "monthly_co2_reduction": round(random.uniform(10, 50), 1),
                    "quarterly_energy_savings": round(random.uniform(20, 80), 1)
                },
                "recommendations": [
                    "Consider migrating more teams to gemini-2.0-flash for better efficiency",
                    "Sales team shows potential for 25% efficiency improvement",
                    "Implement auto-switching for teams with <80% efficiency score"
                ],
                "generated_at": datetime.now().isoformat()
            }
            
            return analysis
        except Exception as e:
            print(f"Error performing org-wide analysis: {e}")
            return {"error": str(e), "analysis": None}
    
    async def generate_org_wide_reports(self, teams: List[Dict[str, Any]], report_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate comprehensive org-wide statistical reports."""
        try:
            reports = {
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "executive_summary": {
                    "total_teams_analyzed": len(teams),
                    "overall_efficiency_score": round(random.uniform(80, 95), 1),
                    "total_savings": {
                        "co2_grams": round(random.uniform(10000, 100000), 2),
                        "energy_kwh": round(random.uniform(1000, 10000), 2),
                        "cost_usd": round(random.uniform(5000, 50000), 2)
                    },
                    "key_insights": [
                        "Engineering team leads in efficiency with 94% score",
                        "Marketing team shows 15% improvement this month",
                        "Auto-switching adoption increased efficiency by 23%"
                    ]
                },
                "detailed_analysis": {
                    "hypothesis_testing": {
                        "test": "ANOVA - Team Efficiency Comparison",
                        "f_statistic": round(random.uniform(2.5, 8.0), 3),
                        "p_value": round(random.uniform(0.001, 0.05), 4),
                        "is_significant": True,
                        "conclusion": "Significant differences exist between team efficiency scores"
                    },
                    "regression_analysis": {
                        "model": "CO2 Savings ~ Team Size + Model Usage + Time",
                        "r_squared": round(random.uniform(0.7, 0.95), 3),
                        "coefficients": {
                            "team_size": round(random.uniform(0.1, 0.5), 3),
                            "model_usage": round(random.uniform(0.3, 0.8), 3),
                            "time": round(random.uniform(0.05, 0.2), 3)
                        }
                    },
                    "forecasting": {
                        "next_month_co2_savings": round(random.uniform(15000, 25000), 2),
                        "confidence_interval": [12000, 28000],
                        "trend_direction": "increasing",
                        "forecast_accuracy": round(random.uniform(85, 98), 1)
                    }
                },
                "team_breakdown": [
                    {
                        "team_id": team["team_id"],
                        "team_name": team["team_name"],
                        "efficiency_metrics": {
                            "score": round(random.uniform(70, 100), 1),
                            "rank": i + 1,
                            "improvement_this_month": round(random.uniform(-5, 20), 1)
                        },
                        "sustainability_metrics": {
                            "co2_saved_grams": round(random.uniform(500, 5000), 2),
                            "energy_saved_kwh": round(random.uniform(50, 500), 2),
                            "green_tokens_earned": round(random.uniform(10, 100), 2)
                        },
                        "recommendations": [
                            f"Consider {random.choice(['auto-switching', 'model optimization', 'usage patterns'])}",
                            f"Potential {round(random.uniform(10, 30), 1)}% efficiency improvement"
                        ]
                    }
                    for i, team in enumerate(teams)
                ],
                "export_options": {
                    "formats": ["json", "csv", "pdf", "excel"],
                    "sections": ["executive_summary", "detailed_analysis", "team_breakdown", "all"]
                }
            }
            
            return reports
        except Exception as e:
            print(f"Error generating org-wide reports: {e}")
            return {"error": str(e), "reports": None}
