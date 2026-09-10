"""
OpenAI API service for CarbonSight Dashboard.
Handles all OpenAI API interactions with proper error handling and response formatting.
"""

import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import openai
    import tiktoken
except ImportError:
    print("Warning: OpenAI or tiktoken package not installed. Run: pip install openai tiktoken")
    openai = None
    tiktoken = None

from config import config


class OpenAIService:
    """
    OpenAI API service for generating content and tracking metrics.
    Handles API calls, error management, and response formatting.
    """
    
    def __init__(self):
        """Initialize OpenAI service with API key."""
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI integration")
        
        if openai is None:
            raise ImportError("OpenAI package is required. Install with: pip install openai")
        
        # Initialize OpenAI client
        openai.api_key = config.openai_api_key
        
        # Model configurations with pricing (per 1k tokens) - Updated 2024
        self.model_configs = {
            "gpt-3.5-turbo": {
                "input_cost": 0.0005,    # $0.50 per 1M input tokens
                "output_cost": 0.0015,   # $1.50 per 1M output tokens
                "max_tokens": 4096,
                "description": "Fast and efficient model"
            },
            "gpt-4": {
                "input_cost": 0.03,      # $30 per 1M input tokens
                "output_cost": 0.06,     # $60 per 1M output tokens
                "max_tokens": 8192,
                "description": "Most capable model"
            },
            "gpt-4o": {
                "input_cost": 0.005,     # $5 per 1M input tokens
                "output_cost": 0.015,    # $15 per 1M output tokens
                "max_tokens": 128000,
                "description": "Latest optimized model"
            }
        }
        
        # Initialize tokenizer for accurate token counting
        self.tokenizer = None
        if tiktoken:
            try:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                print(f"Warning: Could not initialize tokenizer: {e}")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken for accurate tokenization.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback: rough estimation (4 characters ≈ 1 token)
            return len(text) // 4
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> Dict[str, float]:
        """
        Calculate exact cost based on token counts and model pricing.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name
            
        Returns:
            Dictionary with cost breakdown
        """
        if model not in self.model_configs:
            return {"input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0}
        
        model_config = self.model_configs[model]
        
        # Calculate costs (pricing is per 1k tokens)
        input_cost = (input_tokens / 1000) * model_config["input_cost"]
        output_cost = (output_tokens / 1000) * model_config["output_cost"]
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6)
        }
    
    async def generate_content(
        self, 
        prompt: str, 
        model: str = "gpt-3.5-turbo",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate content using OpenAI API.
        
        Args:
            prompt: User's input prompt
            model: OpenAI model to use
            max_tokens: Maximum tokens to generate
            temperature: Response creativity (0.0-1.0)
            
        Returns:
            Dictionary with response, metrics, and usage data
        """
        start_time = time.time()
        
        try:
            # Validate model
            if model not in self.model_configs:
                raise ValueError(f"Unsupported model: {model}")
            
            # Set max_tokens if not provided
            if max_tokens is None:
                max_tokens = min(1000, self.model_configs[model]["max_tokens"])
            
            # Make OpenAI API call
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract response content
            response_text = response.choices[0].message.content
            
            # Extract token usage from API response
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            # Calculate exact cost using our method
            cost_breakdown = self.calculate_cost(input_tokens, output_tokens, model)
            input_cost = cost_breakdown["input_cost"]
            output_cost = cost_breakdown["output_cost"]
            total_cost = cost_breakdown["total_cost"]
            
            return {
                "response_text": response_text,
                "model_used": model,
                "latency_ms": processing_time_ms,
                "cost_usd": round(total_cost, 6),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "input_cost_usd": round(input_cost, 6),
                "output_cost_usd": round(output_cost, 6),
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "response_text": f"Error generating response: {str(e)}",
                "model_used": model,
                "latency_ms": processing_time_ms,
                "cost_usd": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "input_cost_usd": 0.0,
                "output_cost_usd": 0.0,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model: Model name to get info for
            
        Returns:
            Dictionary with model configuration and pricing
        """
        if model not in self.model_configs:
            raise ValueError(f"Unsupported model: {model}")
        
        return self.model_configs[model]
    
    def get_available_models(self) -> list:
        """
        Get list of available models.
        
        Returns:
            List of model names
        """
        return list(self.model_configs.keys())
    
    def estimate_cost(self, prompt: str, model: str = "gpt-3.5-turbo", estimated_output_tokens: int = 100) -> Dict[str, Any]:
        """
        Estimate cost for a prompt without making API call.
        
        Args:
            prompt: Input prompt
            model: Model to estimate for
            estimated_output_tokens: Estimated output length
            
        Returns:
            Dictionary with cost estimates
        """
        if model not in self.model_configs:
            raise ValueError(f"Unsupported model: {model}")
        
        # Use accurate token counting
        estimated_input_tokens = self.count_tokens(prompt)
        
        # Calculate costs using our method
        cost_breakdown = self.calculate_cost(estimated_input_tokens, estimated_output_tokens, model)
        
        return {
            "model": model,
            "estimated_input_tokens": estimated_input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "estimated_total_tokens": estimated_input_tokens + estimated_output_tokens,
            "estimated_input_cost_usd": cost_breakdown["input_cost"],
            "estimated_output_cost_usd": cost_breakdown["output_cost"],
            "estimated_total_cost_usd": cost_breakdown["total_cost"],
            "character_to_token_ratio": round(len(prompt) / estimated_input_tokens, 2) if estimated_input_tokens > 0 else 0
        }
