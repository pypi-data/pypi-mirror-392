"""Smart feedback matching using semantic similarity"""

import csv
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import config

class FeedbackMatcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.85  # High threshold for SQL reuse
        
        # Load feedback for current database
        db_name = config.MYSQL_DATABASE if hasattr(config, 'MYSQL_DATABASE') else "default_db"
        self.feedback_file = Path(f"data/output/feedback_{db_name}.csv")
        
        # Load and embed all good queries
        self.good_queries = self._load_good_queries()
    
    def _load_good_queries(self):
        """Load and embed all good queries from feedback"""
        good_queries = {}
        
        if not self.feedback_file.exists():
            return good_queries
        
        with open(self.feedback_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('status') == 'good':
                    question = row['question'].lower().strip()
                    sql = row['sql'].strip()
                    
                    # Skip if we already have this question with different SQL
                    if question not in good_queries:
                        good_queries[question] = {
                            'sql': sql,
                            'embedding': self.model.encode([question])[0]
                        }
        
        print(f"📚 Loaded {len(good_queries)} good queries from feedback")
        return good_queries
    
    def find_similar_query(self, question: str):
        """Find similar query from feedback"""
        if not self.good_queries:
            return None, 0
        
        question_lower = question.lower().strip()
        question_embedding = self.model.encode([question_lower])[0]
        
        best_match = None
        best_similarity = 0
        
        for stored_question, data in self.good_queries.items():
            # Calculate cosine similarity
            similarity = np.dot(question_embedding, data['embedding']) / (
                np.linalg.norm(question_embedding) * np.linalg.norm(data['embedding'])
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = data['sql']
        
        # Only return if similarity is high enough
        if best_similarity >= self.similarity_threshold:
            return best_match, best_similarity
        
        return None, best_similarity
    
    def reload_feedback(self):
        """Reload feedback (call after new feedback is saved)"""
        self.good_queries = self._load_good_queries()