import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:    
    api_base: str
    copilot_api_key: Optional[str] = None
    copilot_id: Optional[str] = None
    webhook_api_key: Optional[str] = None
    webhook_recipe_id: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            api_base=os.getenv("KARINI_API_BASE"),
            copilot_id=os.getenv("KARINI_COPILOT_ID"),
            copilot_api_key=os.getenv("KARINI_API_KEY"),
            webhook_api_key=os.getenv("WEBHOOK_API_KEY"),
            webhook_recipe_id=os.getenv("WEBHOOK_RECIPE_ID"),
        )
    
    def validate_copilot_config(self) -> bool:
        """Validate that required copilot configuration is present."""
        return all([
            self.api_base,
            self.copilot_id,
            self.copilot_api_key,
        ])
    
    def validate_webhook_config(self) -> bool:
        """Validate that required webhook configuration is present."""
        return all([
            self.api_base,
            self.webhook_api_key,
            self.webhook_recipe_id,
        ])