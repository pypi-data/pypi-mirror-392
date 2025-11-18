"""Configuration management for Neuron CLI"""

import json
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manages Neuron CLI configuration"""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".neuron"
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_FILE
        self.data: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.data = json.load(f)
        else:
            # Create default config
            self.data = {
                "api_url": "https://api.support.nexuscore.cloud/api/v1",
                "device_id": "",
                "jwt_token": "",
                "brand_key": ""
            }
    
    def save(self) -> None:
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.data[key] = value
    
    def is_configured(self) -> bool:
        """Check if device is configured"""
        return bool(self.data.get("device_id") and self.data.get("jwt_token"))
    
    @property
    def device_id(self) -> str:
        return self.data.get("device_id", "")
    
    @property
    def jwt_token(self) -> str:
        return self.data.get("jwt_token", "")
    
    @property
    def api_url(self) -> str:
        return self.data.get("api_url", "https://api.support.nexuscore.cloud/api/v1")
    
    @property
    def brand_key(self) -> str:
        return self.data.get("brand_key", "")
    
    def get_auto_update_config(self) -> Dict[str, Any]:
        """Get auto-update configuration"""
        return self.data.get("auto_update", {
            "enabled": False,
            "auto_install": False,
            "check_interval": "daily",
            "last_check": None
        })
    
    def set_auto_update(self, enabled: bool, auto_install: bool = False) -> None:
        """Enable/disable auto-updates"""
        auto_update = self.get_auto_update_config()
        auto_update["enabled"] = enabled
        auto_update["auto_install"] = auto_install
        self.data["auto_update"] = auto_update
        self.save()
    
    def update_last_check(self) -> None:
        """Update last check timestamp"""
        from datetime import datetime
        auto_update = self.get_auto_update_config()
        auto_update["last_check"] = datetime.utcnow().isoformat() + 'Z'
        self.data["auto_update"] = auto_update
        self.save()
    
    def should_check_for_updates(self) -> bool:
        """Check if we should check for updates based on interval"""
        from datetime import datetime, timedelta
        
        auto_update = self.get_auto_update_config()
        
        if not auto_update.get("enabled"):
            return False
        
        last_check = auto_update.get("last_check")
        if not last_check:
            return True
        
        try:
            last_check_dt = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            now = datetime.utcnow()
            
            interval = auto_update.get("check_interval", "daily")
            if interval == "daily":
                return (now - last_check_dt) > timedelta(days=1)
            elif interval == "weekly":
                return (now - last_check_dt) > timedelta(weeks=1)
            else:
                return True
        except:
            return True
