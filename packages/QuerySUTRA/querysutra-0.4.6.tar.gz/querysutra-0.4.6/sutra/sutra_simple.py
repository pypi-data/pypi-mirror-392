"""
SUTRA - Simple Natural Language to SQL Query System
A single-file library for converting natural language to SQL with visualization.

Author: Your Name
License: MIT
Version: 0.1.0

Installation:
    pip install sutra

Usage:
    from sutra import SUTRA
    
    # Step 1: Initialize with API key
    sutra = SUTRA(api_key="your-openai-api-key")
    
    # Step 2: Upload data
    sutra.upload_data("data.csv")
    
    # Step 3: Query with natural language
    result = sutra.query("Show me all sales data", visualize=True)
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from typing import Optional, Union, List, Dict, Any
from pathlib import Path
import json
import pickle
import hashlib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Try importing optional dependencies
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class SUTRA:
    """
    Main SUTRA class - Natural Language to SQL Query System.
    
    This class provides a simple interface for:
    1. Uploading data from various formats (CSV, Excel, JSON, SQL, DataFrame)
    2. Converting natural language questions to SQL queries
    3. Executing queries and visualizing results
    4. Direct SQL access without API
    
    Example:
        >>> sutra = SUTRA(api_key="sk-...")
        >>> sutra.upload_data("sales.csv")
        >>> result = sutra.query("What are total sales by region?", visualize=True)
        >>> print(result['data'])
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 db_path: str = "sutra_database.db",
                 cache_enabled: bool = True):
        """
        Initialize SUTRA system.
        
        Args:
            api_key: OpenAI API key. If None, looks for OPENAI_API_KEY env variable
            db_path: Path to SQLite database file
            cache_enabled: Whether to cache query results
        
        Raises:
            ValueError: If API key not provided and OPENAI_API_KEY not set
            ImportError: If required dependencies are missing
        """
        print("🚀 Initializing SUTRA...")
        
        # Set API key
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        elif "OPENAI_API_KEY" not in os.environ:
            print("⚠️  Warning: No API key provided. Only direct SQL queries will work.")
            self.api_key = None
        else:
            self.api_key = os.environ["OPENAI_API_KEY"]
        
        if self.api_key and not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key) if self.api_key and OPENAI_AVAILABLE else None
        
        # Database setup
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # State variables
        self.current_table = None
        self.schema = {}
        self.cache_enabled = cache_enabled
        self.query_cache = {}
        self.cache_file = "sutra_cache.pkl"
        
        # Load cache if exists
        if cache_enabled and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.query_cache = pickle.load(f)
            except:
                self.query_cache = {}
        
        print(f"✅ SUTRA initialized successfully!")
        print(f"   📁 Database: {self.db_path}")
        print(f"   🔑 API Key: {'Configured' if self.api_key else 'Not configured'}")
        print(f"   💾 Cache: {'Enabled' if cache_enabled else 'Disabled'}")
    
    # ========================================================================
    # STEP 2: UPLOAD DATA
    # ========================================================================
    
    def upload_data(self, 
                   data_source: Union[str, pd.DataFrame], 
                   table_name: Optional[str] = None) -> str:
        """
        Upload data from various sources to database.
        
        Supports:
        - CSV files (.csv)
        - Excel files (.xlsx, .xls)
        - JSON files (.json)
        - SQL files (.sql)
        - Pandas DataFrame
        - Multiple files at once (list of paths)
        
        Args:
            data_source: File path, DataFrame, or list of file paths
            table_name: Custom table name. Auto-generated if None
        
        Returns:
            str: Name of created table
        
        Example:
            >>> sutra.upload_data("sales.csv")
            >>> sutra.upload_data(df, table_name="my_data")
        """
        print(f"\n📤 Uploading data...")
        
        # Handle DataFrame
        if isinstance(data_source, pd.DataFrame):
            table_name = table_name or "uploaded_data"
            return self._store_dataframe(data_source, table_name)
        
        # Handle file path
        file_path = Path(data_source)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {data_source}")
        
        # Generate table name
        if table_name is None:
            table_name = file_path.stem.replace(" ", "_").replace("-", "_")
            table_name = "".join(c if c.isalnum() or c == "_" else "_" for c in table_name)
        
        # Load data based on file type
        file_ext = file_path.suffix.lower()
        
        print(f"   📄 File: {file_path.name}")
        print(f"   🏷️  Table: {table_name}")
        
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        elif file_ext == ".json":
            df = pd.read_json(file_path)
        elif file_ext == ".sql":
            # Execute SQL file
            with open(file_path, 'r') as f:
                sql_script = f.read()
            self.cursor.executescript(sql_script)
            self.conn.commit()
            print(f"✅ SQL file executed successfully!")
            self._update_schema()
            return table_name
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        return self._store_dataframe(df, table_name)
    
    def _store_dataframe(self, df: pd.DataFrame, table_name: str) -> str:
        """Store DataFrame in database."""
        # Clean column names
        df.columns = [col.strip().replace(" ", "_").replace("-", "_") for col in df.columns]
        
        # Store in database
        df.to_sql(table_name, self.conn, if_exists='replace', index=False)
        self.current_table = table_name
        
        # Update schema
        self._update_schema()
        
        print(f"✅ Data uploaded successfully!")
        print(f"   📊 Rows: {len(df)}")
        print(f"   📋 Columns: {len(df.columns)}")
        print(f"   🔤 Fields: {', '.join(df.columns.tolist()[:5])}{'...' if len(df.columns) > 5 else ''}")
        
        return table_name
    
    def _update_schema(self):
        """Update schema information."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in self.cursor.fetchall()]
        
        self.schema = {}
        for table in tables:
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            self.schema[table] = columns
    
    # ========================================================================
    # STEP 3: VIEW DATABASE
    # ========================================================================
    
    def list_tables(self) -> List[str]:
        """
        List all tables in database.
        
        Returns:
            List of table names
        
        Example:
            >>> tables = sutra.list_tables()
            >>> print(tables)
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]
    
    def show_schema(self, table_name: Optional[str] = None):
        """
        Display database schema.
        
        Args:
            table_name: Show specific table. If None, shows all tables
        
        Example:
            >>> sutra.show_schema()
            >>> sutra.show_schema("sales_data")
        """
        if not self.schema:
            self._update_schema()
        
        print("\n" + "="*70)
        print("📋 DATABASE SCHEMA")
        print("="*70)
        
        if table_name:
            if table_name in self.schema:
                self._print_table_schema(table_name)
            else:
                print(f"❌ Table '{table_name}' not found")
        else:
            for table in self.schema:
                self._print_table_schema(table)
        
        print("="*70)
    
    def _print_table_schema(self, table_name: str):
        """Print schema for a single table."""
        print(f"\n📊 Table: {table_name}")
        for col, dtype in self.schema[table_name].items():
            print(f"   • {col:<30} ({dtype})")
    
    def get_sample_data(self, table_name: Optional[str] = None, n: int = 5) -> pd.DataFrame:
        """
        Get sample rows from table.
        
        Args:
            table_name: Table name. Uses current table if None
            n: Number of rows
        
        Returns:
            DataFrame with sample data
        
        Example:
            >>> sample = sutra.get_sample_data(n=10)
            >>> print(sample)
        """
        target_table = table_name or self.current_table
        
        if not target_table:
            print("❌ No table specified")
            return pd.DataFrame()
        
        query = f"SELECT * FROM {target_table} LIMIT {n}"
        df = pd.read_sql_query(query, self.conn)
        
        print(f"\n📊 Sample data from '{target_table}' (showing {len(df)} rows):")
        print(df.to_string(index=False))
        
        return df
    
    # ========================================================================
    # STEP 4: DIRECT SQL QUERY (NO API)
    # ========================================================================
    
    def direct_query(self, sql: str, visualize: bool = False) -> Dict[str, Any]:
        """
        Execute SQL query directly without NLP processing.
        No API key required for this method.
        
        Args:
            sql: SQL query string
            visualize: Whether to create visualization
        
        Returns:
            Dictionary with keys: success, sql, data, visualization
        
        Example:
            >>> result = sutra.direct_query("SELECT * FROM sales WHERE amount > 1000")
            >>> print(result['data'])
        """
        print(f"\n⚡ Executing direct SQL query...")
        print(f"   SQL: {sql}")
        
        try:
            df = pd.read_sql_query(sql, self.conn)
            print(f"✅ Query executed! Returned {len(df)} rows")
            
            # Visualization
            viz = None
            if visualize and not df.empty:
                viz = self._create_visualization(df, "Direct Query Result")
            
            return {
                "success": True,
                "sql": sql,
                "data": df,
                "visualization": viz
            }
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sql": sql
            }
    
    # ========================================================================
    # STEP 5: NATURAL LANGUAGE QUERY
    # ========================================================================
    
    def query(self, 
             question: str, 
             visualize: bool = False,
             table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Query database using natural language.
        Requires OpenAI API key.
        
        Args:
            question: Natural language question
            visualize: Whether to create visualization
            table_name: Specific table to query. Uses current table if None
        
        Returns:
            Dictionary with keys: success, sql, data, visualization
        
        Example:
            >>> result = sutra.query("What are total sales by region?", visualize=True)
            >>> print(result['data'])
        """
        if not self.client:
            return {
                "success": False,
                "error": "API key not configured. Use direct_query() for SQL without API."
            }
        
        print(f"\n🔍 Processing query: '{question}'")
        
        target_table = table_name or self.current_table
        
        if not target_table:
            return {
                "success": False,
                "error": "No table specified. Upload data first or specify table_name."
            }
        
        # Check cache
        cache_key = self._get_cache_key(question, target_table)
        if self.cache_enabled and cache_key in self.query_cache:
            print("   💾 Retrieved from cache")
            sql_query = self.query_cache[cache_key]
        else:
            # Generate SQL using OpenAI
            sql_query = self._generate_sql(question, target_table)
            
            # Cache the query
            if self.cache_enabled:
                self.query_cache[cache_key] = sql_query
                self._save_cache()
        
        print(f"   📝 Generated SQL: {sql_query}")
        
        # Execute query
        try:
            df = pd.read_sql_query(sql_query, self.conn)
            print(f"✅ Query executed! Returned {len(df)} rows")
            
            # Visualization
            viz = None
            if visualize and not df.empty:
                viz = self._create_visualization(df, question)
            
            return {
                "success": True,
                "sql": sql_query,
                "data": df,
                "visualization": viz
            }
        
        except Exception as e:
            print(f"❌ Error executing query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sql": sql_query
            }
    
    def _generate_sql(self, question: str, table_name: str) -> str:
        """Generate SQL query using OpenAI."""
        # Get schema for the table
        schema_info = self.schema.get(table_name, {})
        schema_str = ", ".join([f"{col} ({dtype})" for col, dtype in schema_info.items()])
        
        # Create prompt
        prompt = f"""You are a SQL expert. Convert the natural language question to a SQL query.

Database: SQLite
Table: {table_name}
Columns: {schema_str}

Question: {question}

Return ONLY the SQL query, nothing else. No explanations, no markdown, just the SQL.
Use proper SQLite syntax."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Return only SQL queries, nothing else."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=500
            )
            
            sql = response.choices[0].message.content.strip()
            
            # Clean up the response
            sql = sql.replace("```sql", "").replace("```", "").strip()
            
            return sql
        
        except Exception as e:
            raise Exception(f"Failed to generate SQL: {str(e)}")
    
    def _get_cache_key(self, question: str, table_name: str) -> str:
        """Generate cache key."""
        return hashlib.md5(f"{question}:{table_name}".encode()).hexdigest()
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.query_cache, f)
        except:
            pass
    
    # ========================================================================
    # STEP 6: VISUALIZATION
    # ========================================================================
    
    def _create_visualization(self, df: pd.DataFrame, title: str):
        """Create visualization based on data."""
        if not PLOTLY_AVAILABLE and not MATPLOTLIB_AVAILABLE:
            print("⚠️  No visualization library available. Install: pip install plotly matplotlib")
            return None
        
        print("📊 Creating visualization...")
        
        # Use Plotly if available
        if PLOTLY_AVAILABLE:
            return self._create_plotly_viz(df, title)
        else:
            return self._create_matplotlib_viz(df, title)
    
    def _create_plotly_viz(self, df: pd.DataFrame, title: str):
        """Create Plotly visualization."""
        try:
            # Determine best chart type
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if len(df) == 1 or len(numeric_cols) == 0:
                # Table for single row or no numeric data
                fig = go.Figure(data=[go.Table(
                    header=dict(values=list(df.columns)),
                    cells=dict(values=[df[col] for col in df.columns])
                )])
            
            elif len(cat_cols) > 0 and len(numeric_cols) > 0:
                # Bar chart for categorical + numeric
                fig = px.bar(df, x=cat_cols[0], y=numeric_cols[0], title=title)
            
            elif len(numeric_cols) >= 2:
                # Line or scatter for multiple numeric columns
                fig = px.line(df, y=numeric_cols[0], title=title)
            
            else:
                # Default: bar chart
                fig = px.bar(df, y=df.columns[0], title=title)
            
            fig.update_layout(height=500, showlegend=True)
            fig.show()
            print("✅ Visualization created")
            
            return fig
        
        except Exception as e:
            print(f"⚠️  Could not create visualization: {str(e)}")
            return None
    
    def _create_matplotlib_viz(self, df: pd.DataFrame, title: str):
        """Create Matplotlib visualization."""
        try:
            plt.figure(figsize=(10, 6))
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) > 0:
                df[numeric_cols[0]].plot(kind='bar')
            else:
                df.iloc[:, 0].value_counts().plot(kind='bar')
            
            plt.title(title)
            plt.tight_layout()
            plt.show()
            print("✅ Visualization created")
            
            return plt.gcf()
        
        except Exception as e:
            print(f"⚠️  Could not create visualization: {str(e)}")
            return None
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def export_results(self, data: pd.DataFrame, file_path: str, format: str = "csv"):
        """
        Export query results to file.
        
        Args:
            data: DataFrame to export
            file_path: Output file path
            format: Export format (csv, excel, json)
        
        Example:
            >>> result = sutra.query("SELECT * FROM sales")
            >>> sutra.export_results(result['data'], "output.csv")
        """
        format = format.lower()
        
        if format == "csv":
            data.to_csv(file_path, index=False)
        elif format in ["excel", "xlsx"]:
            data.to_excel(file_path, index=False)
        elif format == "json":
            data.to_json(file_path, orient="records", indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"✅ Results exported to {file_path}")
    
    def clear_cache(self):
        """Clear query cache."""
        self.query_cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("✅ Cache cleared")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("✅ SUTRA closed successfully")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self):
        """String representation."""
        return f"SUTRA(db='{self.db_path}', tables={len(self.schema)}, current_table='{self.current_table}')"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_query(api_key: str, data_path: str, question: str, visualize: bool = False) -> Dict[str, Any]:
    """
    Quick one-liner for simple queries.
    
    Args:
        api_key: OpenAI API key
        data_path: Path to data file
        question: Natural language question
        visualize: Whether to visualize results
    
    Returns:
        Query result dictionary
    
    Example:
        >>> result = quick_query("sk-...", "sales.csv", "What are total sales?")
        >>> print(result['data'])
    """
    with SUTRA(api_key=api_key) as sutra:
        sutra.upload_data(data_path)
        return sutra.query(question, visualize=visualize)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                    SUTRA v0.1.0                            ║
    ║        Natural Language to SQL Query System                ║
    ╚════════════════════════════════════════════════════════════╝
    
    Quick Start:
    
    1. Install:
       pip install sutra
    
    2. Use:
       from sutra import SUTRA
       
       sutra = SUTRA(api_key="your-key")
       sutra.upload_data("data.csv")
       result = sutra.query("Show me all data", visualize=True)
    
    For more examples, see: example_usage.py
    """)
