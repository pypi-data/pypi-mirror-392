"""NLP to SQL query processor with relevancy checking"""

import pandas as pd
from typing import Optional, Tuple
from tabulate import tabulate
from sutra.cache_manager import CacheManager
import openai
import config
from sutra.feedback import SimpleFeedback
from sutra.schema_embeddings import SchemaEmbeddings
from sutra.feedback_matcher import FeedbackMatcher

class NLPProcessor:
    """Process natural language questions to SQL queries"""
    
    def __init__(self, db_manager, openai_client=None):
        self.db = db_manager
        self.cache = CacheManager() if config.CACHE_ENABLED else None
        self.model_name = config.MODEL_NAME
        
        # Set the API key directly for openai 0.28.1
        openai.api_key = config.OPENAI_API_KEY

        # Added for feedback handling and tracking
        self.feedback = SimpleFeedback()
        self.last_question = None
        self.last_sql = None
        
        # ✅ NEW: Auto-load schema embeddings
        self.relevancy_checker = SchemaEmbeddings(db_manager)
        
        # ✅ NEW: Smart feedback matcher
        self.feedback_matcher = FeedbackMatcher()
    
    def nlp_to_sql(self, question: str) -> str:
        """Convert natural language question to SQL"""
        
        # ✅ NEW: Check feedback for similar queries first
        similar_sql, similarity = self.feedback_matcher.find_similar_query(question)
        if similar_sql:
            print(f"🎯 Found similar query in feedback (similarity: {similarity:.2f})")
            return similar_sql
        
        # Check cache next
        if self.cache:
            cached_sql = self.cache.get_cached_query(question)
            if cached_sql:
                print("⚡ Using cached query")
                return cached_sql
        
        # Only call API if no feedback match and no cache
        print("🤖 Calling OpenAI API...")
        
        # Get schema context
        schema = self.db.get_schema_context()
        
        prompt = f"""
Convert this question to a SQLite query:

Question: {question}

Database schema:
{schema}

Return ONLY the SELECT statement. No explanations, no markdown.
"""
        
        # Use openai.ChatCompletion directly for version 0.28.1
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        sql_query = response['choices'][0]['message']['content'].strip()
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        # Cache the result
        if self.cache:
            self.cache.add_to_cache(question, sql_query)
        
        return sql_query
    
    def process_question(self, question: str) -> Tuple[Optional[pd.DataFrame], str]:
        """Process a natural language question and return results"""
        
        # ✅ NEW: Check relevancy FIRST - BEFORE any API calls
        is_relevant, similarity, info = self.relevancy_checker.is_relevant(question)
        
        if not is_relevant:
            print(f"\n❌ Question not relevant to database (similarity: {similarity:.2f})")
            for item in info:
                print(f"   {item}")
            return None, ""
        
        print(f"✅ Relevant question (similarity: {similarity:.2f})")
        
        try:
            # Convert to SQL (only if relevant)
            sql_query = self.nlp_to_sql(question)
            print(f"\n🔍 Generated SQL Query:")
            print(f"   {sql_query}")
            
            # Track for feedback
            self.last_question = question
            self.last_sql = sql_query
            
            # Execute query
            result_df = self.db.execute_query(sql_query)
            
            return result_df, sql_query
            
        except Exception as e:
            print(f"❌ Error processing question: {e}")
            return None, ""
    
    def display_results(self, df: pd.DataFrame, max_rows: int = 15):
        """Display query results in a formatted table"""
        if df is None or df.empty:
            print("   No results found")
            return  # Exit early if no results
        
        # Show the table
        display_df = df.head(max_rows) if len(df) > max_rows else df
        print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))
        
        if len(df) > max_rows:
            print(f"   ... showing first {max_rows} of {len(df)} rows")
        
        # ✅ UPDATED: Only ask for feedback for relevant questions with results
        # (Irrelevant questions never reach here due to early return)
        feedback = input("\n👍 or 👎? (y/n): ").lower()
        if feedback == 'y':
            self.feedback.save(self.last_question, self.last_sql, True)
            print("✅ Saved as good")
            # Reload feedback matcher with new data
            self.feedback_matcher.reload_feedback()
        elif feedback == 'n':
            correct = input("Correct SQL: ").strip()
            self.feedback.save(self.last_question, self.last_sql, False, correct)
            if correct:
                print("✅ Learned correction")
                # Reload feedback matcher with new data
                self.feedback_matcher.reload_feedback()