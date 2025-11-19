"""Query caching and similarity matching"""

import json
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
from difflib import SequenceMatcher
import config

class CacheManager:
    """Manage query cache with semantic similarity"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.similarity_threshold = config.SIMILARITY_THRESHOLD
        self.save_to_disk_enabled = config.SAVE_QUERIES
        self.cache_file = config.QUERY_LOG_FILE
        
        if self.save_to_disk_enabled:
            self.load_from_disk()
    
    def load_from_disk(self):
        """Load saved queries from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                print(f"📂 Loaded {len(self.cache)} cached queries")
            except Exception as e:
                print(f"⚠️ Could not load cache: {e}")
                self.cache = {}
    
    def save_to_disk(self):
        """Save cache to disk"""
        if not self.save_to_disk_enabled:
            return
        
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save cache: {e}")
    
    def compute_similarity(self, query1: str, query2: str) -> float:
        """Compute similarity between two queries"""
        return SequenceMatcher(None, query1.lower(), query2.lower()).ratio()
    
    def find_similar_query(self, question: str) -> Tuple[Optional[str], float]:
        """Find most similar cached query"""
        best_match = None
        best_similarity = 0
        
        for cached_q in self.cache:
            similarity = self.compute_similarity(question, cached_q)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = cached_q
        
        return best_match, best_similarity
    
    def get_cached_query(self, question: str) -> Optional[str]:
        """Get cached SQL for a question if similar enough"""
        similar_q, similarity = self.find_similar_query(question)
        
        if similarity >= self.similarity_threshold and similar_q:
            print(f"📊 Found similar query (similarity: {similarity:.1%})")
            return self.cache[similar_q]['sql']
        
        return None
    
    def add_to_cache(self, question: str, sql: str):
        """Add query to cache"""
        self.cache[question] = {
            'sql': sql,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.save_to_disk_enabled:
            self.save_to_disk()
    
    def clear_cache(self):
        """Clear all cached queries"""
        self.cache = {}
        if self.save_to_disk_enabled and self.cache_file.exists():
            self.cache_file.unlink()
        print("🗑️ Cache cleared")