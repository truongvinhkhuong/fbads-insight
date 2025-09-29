"""
Budget Cache Manager
Handles caching of Facebook campaign budget data to avoid rate limiting
"""
import json
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class BudgetCache:
    def __init__(self, cache_file: str = "budget_cache.json"):
        self.cache_file = cache_file
        self.cache_duration = 3600  # 1 hour cache duration
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading budget cache: {e}")
        return {"campaigns": {}, "last_updated": None}
    
    def _save_cache(self, cache_data: Dict[str, Any]) -> bool:
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving budget cache: {e}")
            return False
    
    def _is_cache_valid(self, cache_data: Dict[str, Any]) -> bool:
        """Check if cache is still valid"""
        if not cache_data.get("last_updated"):
            return False
        
        try:
            last_updated = datetime.fromisoformat(cache_data["last_updated"])
            return datetime.now() - last_updated < timedelta(seconds=self.cache_duration)
        except:
            return False
    
    def get_campaign_budget(self, campaign_id: str) -> Optional[Dict[str, float]]:
        """Get cached budget data for a campaign"""
        cache_data = self._load_cache()
        
        if not self._is_cache_valid(cache_data):
            return None
        
        return cache_data.get("campaigns", {}).get(campaign_id)
    
    def set_campaign_budget(self, campaign_id: str, budget_data: Dict[str, float]) -> bool:
        """Cache budget data for a campaign"""
        cache_data = self._load_cache()
        
        if "campaigns" not in cache_data:
            cache_data["campaigns"] = {}
        
        cache_data["campaigns"][campaign_id] = budget_data
        cache_data["last_updated"] = datetime.now().isoformat()
        
        return self._save_cache(cache_data)
    
    def get_all_budgets(self) -> Dict[str, Dict[str, float]]:
        """Get all cached budget data"""
        cache_data = self._load_cache()
        
        if not self._is_cache_valid(cache_data):
            return {}
        
        return cache_data.get("campaigns", {})
    
    def clear_cache(self) -> bool:
        """Clear the cache"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            return True
        except Exception as e:
            print(f"Error clearing budget cache: {e}")
            return False
    
    def is_cache_available(self) -> bool:
        """Check if cache is available and valid"""
        cache_data = self._load_cache()
        return self._is_cache_valid(cache_data)

# Global cache instance
budget_cache = BudgetCache()
