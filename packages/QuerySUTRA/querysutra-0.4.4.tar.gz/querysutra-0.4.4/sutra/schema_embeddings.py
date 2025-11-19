"""Strict schema and data validation for relevancy checking"""

import pickle
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import config
import re

class SchemaEmbeddings:
    def __init__(self, db_manager):
        self.db = db_manager
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.strict_threshold = 0.85  # Higher threshold to prevent false positives
        
        # Auto-generate embeddings path
        db_name = config.MYSQL_DATABASE
        self.embed_file = Path(f"data/output/schema_embeddings_{db_name}.pkl")
        self.embed_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create embeddings automatically
        self.data_inventory = self._load_or_create()
    
    def _load_or_create(self):
        """Load existing or create new data inventory"""
        if self.embed_file.exists():
            print(f"⚡ Loading cached data inventory for {config.MYSQL_DATABASE}")
            with open(self.embed_file, 'rb') as f:
                return pickle.load(f)
        else:
            print(f"🔨 Building data inventory for {config.MYSQL_DATABASE} (one-time)")
            return self._create_inventory()
    
    def _create_inventory(self):
        """Create complete inventory of ALL data values in database - NO HARDCODING"""
        inventory = {
            'tables': [],
            'columns': {},
            'all_values': set(),  # Use set to avoid duplicates
            'values_by_column': {},
            'embeddings': [],
            'embedded_texts': []
        }
        
        # Get tables
        tables = self.db.get_tables()
        inventory['tables'] = tables
        
        print(f"   Scanning {len(tables)} tables for ALL data...")
        
        for table in tables:
            # Get columns
            columns = self.db.get_columns(table)
            inventory['columns'][table] = columns
            
            # Get ALL data from EVERY column
            for col in columns:
                try:
                    # Get ALL unique values - no limits, no filters
                    query = f"SELECT DISTINCT `{col}` FROM `{table}` WHERE `{col}` IS NOT NULL"
                    cursor = self.db.conn.cursor()
                    cursor.execute(query)
                    values = cursor.fetchall()
                    cursor.close()
                    
                    column_values = set()
                    for val in values:
                        if val[0] is not None:
                            val_str = str(val[0]).strip()
                            
                            # Add the complete value in lowercase
                            val_lower = val_str.lower()
                            column_values.add(val_lower)
                            inventory['all_values'].add(val_lower)
                            
                            # Extract all possible substrings that might be queried
                            # Split by common delimiters
                            delimiters = [',', ';', '|', '/', '\\', '-', '_', '.', ':', '\n', '\t']
                            parts = [val_lower]
                            
                            for delimiter in delimiters:
                                new_parts = []
                                for part in parts:
                                    new_parts.extend(part.split(delimiter))
                                parts = new_parts
                            
                            # Add all non-empty, cleaned parts
                            for part in parts:
                                cleaned = part.strip()
                                if cleaned and len(cleaned) > 1:  # Skip single characters
                                    inventory['all_values'].add(cleaned)
                                    
                                    # Also add individual words from each part
                                    words = cleaned.split()
                                    for word in words:
                                        if len(word) > 1:  # Skip single letters
                                            inventory['all_values'].add(word)
                                    
                                    # Add consecutive word pairs (for things like "new york")
                                    for i in range(len(words) - 1):
                                        pair = f"{words[i]} {words[i+1]}"
                                        inventory['all_values'].add(pair)
                    
                    if column_values:
                        inventory['values_by_column'][f"{table}.{col}"] = list(column_values)
                        print(f"      Found {len(column_values)} unique values in {table}.{col}")
                    
                except Exception as e:
                    print(f"      Could not read {table}.{col}: {e}")
        
        # Convert set to list for final storage
        inventory['all_values'] = list(inventory['all_values'])
        
        # Create texts for embedding - include everything
        texts_to_embed = []
        
        # Add table and column names
        for table in inventory['tables']:
            texts_to_embed.append(f"table {table}")
            for col in inventory['columns'][table]:
                texts_to_embed.append(f"column {col}")
        
        # Add ALL extracted data values
        texts_to_embed.extend(inventory['all_values'])
        
        # Generate embeddings
        print(f"   Generating embeddings for {len(texts_to_embed)} items...")
        if texts_to_embed:
            inventory['embeddings'] = self.model.encode(texts_to_embed)
            inventory['embedded_texts'] = texts_to_embed
        else:
            inventory['embeddings'] = []
            inventory['embedded_texts'] = []
        
        # Save
        with open(self.embed_file, 'wb') as f:
            pickle.dump(inventory, f)
        
        print(f"✅ Data inventory complete: {len(inventory['all_values'])} unique values indexed")
        return inventory
    
    def is_relevant(self, question: str) -> tuple:
        """Check if question refers to actual data in database"""
        question_lower = question.lower().strip()
        
        # Block obviously inappropriate content
        if any(word in question_lower for word in ['fuck', 'shit', 'damn', 'hell', 'ass']):
            return False, 0.0, ["Inappropriate question"]
        
        # Check for exact or partial matches with actual data
        exact_matches = []
        partial_matches = []
        
        # Split question into potential search terms
        question_words = question_lower.split()
        question_pairs = [f"{question_words[i]} {question_words[i+1]}" 
                         for i in range(len(question_words)-1) if i+1 < len(question_words)]
        
        # Check all possible terms from question
        search_terms = [question_lower] + question_words + question_pairs
        
        for term in search_terms:
            if len(term) > 1:  # Skip single characters
                for value in self.data_inventory['all_values']:
                    # Exact match
                    if term == value:
                        exact_matches.append(value)
                    # Partial match (term in value or value in term)
                    elif term in value or value in term:
                        partial_matches.append(value)
        
        # Check for table/column references
        schema_matches = []
        for table in self.data_inventory['tables']:
            if table.lower() in question_lower:
                schema_matches.append(f"table:{table}")
        
        for col_list in self.data_inventory['columns'].values():
            for col in col_list:
                if col.lower() in question_lower:
                    schema_matches.append(f"column:{col}")
        
        # Decision logic
        if exact_matches:
            return True, 1.0, [f"Found exact match: {', '.join(list(set(exact_matches))[:3])}"]
        
        if partial_matches and schema_matches:
            # Both partial data match and schema reference
            return True, 0.8, [f"Found: {', '.join(list(set(partial_matches))[:3])}"]
        
        if schema_matches:
            # Only schema mentioned, use semantic similarity
            question_embedding = self.model.encode([question_lower])[0]
            
            similarities = []
            for emb in self.data_inventory['embeddings']:
                sim = np.dot(question_embedding, emb) / (np.linalg.norm(question_embedding) * np.linalg.norm(emb))
                similarities.append(sim)
            
            if similarities:
                max_similarity = max(similarities)
                best_idx = np.argmax(similarities)
                best_match = self.data_inventory['embedded_texts'][best_idx]
                
                if max_similarity >= self.strict_threshold:
                    return True, max_similarity, [f"Semantically similar to: {best_match}"]
        
        # Nothing matched - not relevant
        sample_values = self.data_inventory['all_values'][:10] if self.data_inventory['all_values'] else []
        return False, 0.0, [
            "Data not found in database.",
            f"Sample available data: {', '.join(sample_values)}" if sample_values else "No data available"
        ]