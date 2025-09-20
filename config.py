"""
Configuration management for GreenAI Dashboard API.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """
    Application configuration class.
    
    Manages all configuration settings including database connections,
    API keys, and application parameters.
    """
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Database configuration
        self.supabase_url: str = os.getenv("SUPABASE_URL", "")
        self.supabase_key: str = os.getenv("SUPABASE_KEY", "")
        
        # Cerebras API configuration
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        
        # Application settings
        self.debug: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # API configuration
        self.api_title: str = "GreenAI Dashboard API"
        self.api_version: str = "1.0.0"
        
        # Energy calculation constants
        self.base_co2_per_kwh: float = float(os.getenv("BASE_CO2_PER_KWH", "500.0"))
        self.reward_rate_per_gram_co2: float = float(os.getenv("REWARD_RATE_PER_GRAM_CO2", "0.02"))
        self.csi_surge_threshold: int = int(os.getenv("CSI_SURGE_THRESHOLD", "70"))
    
    @property
    def is_database_configured(self) -> bool:
        """Check if database configuration is valid."""
        return bool(self.supabase_url and self.supabase_key)
    
    @property
    def is_valid(self) -> bool:
        """Check if all required configuration is present."""
        return self.is_database_configured


# Global configuration instance
config = Config()
