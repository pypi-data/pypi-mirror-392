"""Configuration management for WeFact CLI tool"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the WeFact CLI tool"""
    
    # Project root (where .env is located)
    PROJECT_ROOT = Path(__file__).parent.parent
    ENV_FILE = PROJECT_ROOT / ".env"
    
    # Configuration keys
    API_KEY_NAME = "WEFACT_API_KEY"
    API_URL_NAME = "WEFACT_API_URL"
    DUMMY_DATA_FLAG = "WEFACT_DUMMY_DATA_INITIALIZED"
    
    # Dummy data ID keys for each endpoint
    DUMMY_DEBTOR_IDS = "DUMMY_DEBTOR_IDS"
    DUMMY_PRODUCT_IDS = "DUMMY_PRODUCT_IDS"
    DUMMY_CREDITOR_IDS = "DUMMY_CREDITOR_IDS"
    DUMMY_GROUP_IDS = "DUMMY_GROUP_IDS"
    DUMMY_INVOICE_IDS = "DUMMY_INVOICE_IDS"
    DUMMY_QUOTE_IDS = "DUMMY_QUOTE_IDS"
    DUMMY_SUBSCRIPTION_IDS = "DUMMY_SUBSCRIPTION_IDS"
    DUMMY_INTERACTION_IDS = "DUMMY_INTERACTION_IDS"
    DUMMY_TASK_IDS = "DUMMY_TASK_IDS"
    DUMMY_TRANSACTION_IDS = "DUMMY_TRANSACTION_IDS"
    DUMMY_COST_CATEGORY_IDS = "DUMMY_COST_CATEGORY_IDS"
    
    DEFAULT_API_URL = "https://api.mijnwefact.nl/v2/"
    
    def __init__(self):
        """Initialize configuration by loading .env file"""
        self.load_env()
    
    def load_env(self) -> None:
        """Load environment variables from .env file"""
        load_dotenv(self.ENV_FILE)
    
    def get_api_key(self) -> Optional[str]:
        """Get the WeFact API key from environment"""
        return os.getenv(self.API_KEY_NAME)
    
    def get_api_url(self) -> str:
        """Get the WeFact API URL from environment or use default"""
        return os.getenv(self.API_URL_NAME, self.DEFAULT_API_URL)
    
    def is_dummy_data_initialized(self) -> bool:
        """Check if dummy data has been initialized"""
        return os.getenv(self.DUMMY_DATA_FLAG, "false").lower() == "true"
    
    def get_dummy_ids(self, endpoint: str) -> list[str]:
        """Get dummy IDs for a specific endpoint"""
        key = f"DUMMY_{endpoint.upper()}_IDS"
        ids_str = os.getenv(key, "")
        return [id.strip() for id in ids_str.split(",") if id.strip()]
    
    def has_api_key(self) -> bool:
        """Check if API key is configured"""
        api_key = self.get_api_key()
        return api_key is not None and len(api_key) > 0


# Global config instance
config = Config()
