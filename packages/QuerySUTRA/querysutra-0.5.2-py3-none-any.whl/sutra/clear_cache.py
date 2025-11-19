# Create a file called clear_cache.py
import os
cache_file = "data/output/query_history.json"
if os.path.exists(cache_file):
    os.remove(cache_file)
    print("✅ Cache cleared!")