"""
Metrics service for CarbonSight Dashboard.
Handles latency tracking, cost analysis, and performance metrics calculation.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics

from models import EnergyMetrics


class MetricsService:
    """
    Service for tracking and analyzing performance metrics.
    Handles latency, cost, efficiency calculations, and trend analysis.
    """
    
    def __init__(self):
        """Initialize metrics service."""
        self.metrics_history = []
        self.performance_thresholds = {
            "latency_ms": {
                "excellent": 500,
                "good": 1000,
                "acceptable": 2000,
                "poor": 5000
            },
            "cost_usd": {
                "excellent": 0.001,
                "good": 0.005,
                "acceptable": 0.01,
                "poor": 0.05
            },
            "tokens_per_second": {
                "excellent": 50,
                "good": 25,
                "acceptable": 10,
                "poor": 5
            }
        }
    
    def track_request_metrics(
        self,
        prompt: str,
        response: str,
        model: str,
        latency_ms: int,
        cost_usd: float,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int
    ) -> Dict[str, Any]:
        """
        Track metrics for a single request.
        
        Args:
            prompt: Input prompt
            response: Generated response
            model: Model used
            latency_ms: Response latency in milliseconds
            cost_usd: Cost in USD
            input_tokens: Input token count
            output_tokens: Output token count
            total_tokens: Total token count
            
        Returns:
            Dictionary with calculated metrics
        """
        # Calculate efficiency metrics
        tokens_per_second = (total_tokens / (latency_ms / 1000)) if latency_ms > 0 else 0
        cost_per_token = cost_usd / total_tokens if total_tokens > 0 else 0
        cost_per_character = cost_usd / len(response) if len(response) > 0 else 0
        
        # Calculate prompt complexity (rough estimation)
        prompt_complexity = self._calculate_prompt_complexity(prompt)
        
        # Create metrics record
        metrics_record = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "tokens_per_second": round(tokens_per_second, 2),
            "cost_per_token": round(cost_per_token, 6),
            "cost_per_character": round(cost_per_character, 6),
            "prompt_complexity": prompt_complexity,
            "efficiency_score": self._calculate_efficiency_score(
                latency_ms, cost_usd, tokens_per_second, prompt_complexity
            )
        }
        
        # Add to history
        self.metrics_history.append(metrics_record)
        
        # Keep only last 1000 records to prevent memory issues
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics_record
    
    def _calculate_prompt_complexity(self, prompt: str) -> float:
        """
        Calculate prompt complexity score (0-1).
        
        Args:
            prompt: Input prompt
            
        Returns:
            Complexity score between 0 and 1
        """
        # Simple complexity calculation based on length and content
        length_factor = min(len(prompt) / 1000, 1.0)  # Normalize to 0-1
        
        # Count special characters and numbers
        special_chars = sum(1 for c in prompt if not c.isalnum() and not c.isspace())
        special_factor = min(special_chars / len(prompt), 1.0) if len(prompt) > 0 else 0
        
        # Count question marks and exclamation marks (indicates complexity)
        question_marks = prompt.count('?')
        exclamation_marks = prompt.count('!')
        question_factor = min((question_marks + exclamation_marks) / 10, 1.0)
        
        # Combine factors
        complexity = (length_factor * 0.4 + special_factor * 0.3 + question_factor * 0.3)
        return round(complexity, 3)
    
    def _calculate_efficiency_score(
        self, 
        latency_ms: int, 
        cost_usd: float, 
        tokens_per_second: float, 
        complexity: float
    ) -> float:
        """
        Calculate overall efficiency score (0-100).
        
        Args:
            latency_ms: Response latency
            cost_usd: Cost in USD
            tokens_per_second: Tokens processed per second
            complexity: Prompt complexity score
            
        Returns:
            Efficiency score between 0 and 100
        """
        # Normalize metrics to 0-1 scale
        latency_score = max(0, 1 - (latency_ms / 5000))  # Better if < 5s
        cost_score = max(0, 1 - (cost_usd / 0.1))  # Better if < $0.1
        speed_score = min(1, tokens_per_second / 100)  # Better if > 100 tokens/s
        
        # Weighted average with complexity adjustment
        base_score = (latency_score * 0.3 + cost_score * 0.4 + speed_score * 0.3)
        
        # Adjust for complexity (more complex prompts get slight bonus)
        complexity_bonus = complexity * 0.1
        
        efficiency = (base_score + complexity_bonus) * 100
        return round(max(0, min(100, efficiency)), 1)
    
    def get_performance_summary(self, model: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """
        Get performance summary for recent requests.
        
        Args:
            model: Filter by specific model (optional)
            hours: Time window in hours
            
        Returns:
            Dictionary with performance statistics
        """
        # Filter by time window
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"]) >= cutoff_time
        ]
        
        # Filter by model if specified
        if model:
            recent_metrics = [m for m in recent_metrics if m["model"] == model]
        
        if not recent_metrics:
            return {"error": "No metrics available for the specified period"}
        
        # Calculate statistics
        latencies = [m["latency_ms"] for m in recent_metrics]
        costs = [m["cost_usd"] for m in recent_metrics]
        efficiency_scores = [m["efficiency_score"] for m in recent_metrics]
        tokens_per_second = [m["tokens_per_second"] for m in recent_metrics]
        
        return {
            "period_hours": hours,
            "total_requests": len(recent_metrics),
            "model_filter": model,
            "latency_stats": {
                "avg_ms": round(statistics.mean(latencies), 2),
                "median_ms": round(statistics.median(latencies), 2),
                "min_ms": min(latencies),
                "max_ms": max(latencies),
                "p95_ms": round(sorted(latencies)[int(len(latencies) * 0.95)], 2)
            },
            "cost_stats": {
                "total_usd": round(sum(costs), 6),
                "avg_usd": round(statistics.mean(costs), 6),
                "median_usd": round(statistics.median(costs), 6),
                "min_usd": min(costs),
                "max_usd": max(costs)
            },
            "efficiency_stats": {
                "avg_score": round(statistics.mean(efficiency_scores), 1),
                "median_score": round(statistics.median(efficiency_scores), 1),
                "min_score": min(efficiency_scores),
                "max_score": max(efficiency_scores)
            },
            "performance_stats": {
                "avg_tokens_per_second": round(statistics.mean(tokens_per_second), 2),
                "median_tokens_per_second": round(statistics.median(tokens_per_second), 2)
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def get_model_comparison(self, hours: int = 24) -> Dict[str, Any]:
        """
        Compare performance across different models.
        
        Args:
            hours: Time window in hours
            
        Returns:
            Dictionary with model comparison data
        """
        # Filter by time window
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"]) >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No metrics available for comparison"}
        
        # Group by model
        model_groups = {}
        for metric in recent_metrics:
            model = metric["model"]
            if model not in model_groups:
                model_groups[model] = []
            model_groups[model].append(metric)
        
        # Calculate stats for each model
        comparison = {}
        for model, metrics in model_groups.items():
            latencies = [m["latency_ms"] for m in metrics]
            costs = [m["cost_usd"] for m in metrics]
            efficiency_scores = [m["efficiency_score"] for m in metrics]
            
            comparison[model] = {
                "request_count": len(metrics),
                "avg_latency_ms": round(statistics.mean(latencies), 2),
                "avg_cost_usd": round(statistics.mean(costs), 6),
                "total_cost_usd": round(sum(costs), 6),
                "avg_efficiency_score": round(statistics.mean(efficiency_scores), 1),
                "avg_tokens_per_second": round(
                    statistics.mean([m["tokens_per_second"] for m in metrics]), 2
                )
            }
        
        return {
            "period_hours": hours,
            "model_comparison": comparison,
            "best_performing_model": max(
                comparison.keys(), 
                key=lambda x: comparison[x]["avg_efficiency_score"]
            ),
            "most_cost_effective_model": min(
                comparison.keys(), 
                key=lambda x: comparison[x]["avg_cost_usd"]
            ),
            "fastest_model": min(
                comparison.keys(), 
                key=lambda x: comparison[x]["avg_latency_ms"]
            ),
            "generated_at": datetime.now().isoformat()
        }
    
    def get_efficiency_recommendations(self, current_model: str, prompt: str) -> Dict[str, Any]:
        """
        Get efficiency recommendations for a specific prompt and model.
        
        Args:
            current_model: Currently selected model
            prompt: Input prompt
            
        Returns:
            Dictionary with efficiency recommendations
        """
        # Get recent performance data for current model
        recent_metrics = [
            m for m in self.metrics_history 
            if m["model"] == current_model
        ][-50:]  # Last 50 requests
        
        if not recent_metrics:
            return {"error": "Insufficient data for recommendations"}
        
        # Calculate current model performance
        current_latency = statistics.mean([m["latency_ms"] for m in recent_metrics])
        current_cost = statistics.mean([m["cost_usd"] for m in recent_metrics])
        current_efficiency = statistics.mean([m["efficiency_score"] for m in recent_metrics])
        
        # Get all models performance
        model_performance = self.get_model_comparison(hours=24)
        
        recommendations = {
            "current_model": current_model,
            "current_performance": {
                "avg_latency_ms": round(current_latency, 2),
                "avg_cost_usd": round(current_cost, 6),
                "avg_efficiency_score": round(current_efficiency, 1)
            },
            "recommendations": [],
            "alternative_models": []
        }
        
        # Find better alternatives
        if "model_comparison" in model_performance:
            for model, stats in model_performance["model_comparison"].items():
                if model != current_model:
                    if stats["avg_efficiency_score"] > current_efficiency:
                        recommendations["alternative_models"].append({
                            "model": model,
                            "efficiency_improvement": round(
                                stats["avg_efficiency_score"] - current_efficiency, 1
                            ),
                            "cost_difference": round(
                                stats["avg_cost_usd"] - current_cost, 6
                            ),
                            "latency_difference": round(
                                stats["avg_latency_ms"] - current_latency, 2
                            )
                        })
        
        # Sort by efficiency improvement
        recommendations["alternative_models"].sort(
            key=lambda x: x["efficiency_improvement"], reverse=True
        )
        
        # Generate recommendations
        if recommendations["alternative_models"]:
            best_alternative = recommendations["alternative_models"][0]
            recommendations["recommendations"].append(
                f"Consider switching to {best_alternative['model']} for "
                f"{best_alternative['efficiency_improvement']}% efficiency improvement"
            )
        
        return recommendations
