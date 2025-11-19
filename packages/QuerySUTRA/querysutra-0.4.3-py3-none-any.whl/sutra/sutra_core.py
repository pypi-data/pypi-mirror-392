"""
SUTRA Core - Single interface for all operations
"""

import os
import sqlite3
import pandas as pd
from typing import Optional, Union, List, Dict, Any
from pathlib import Path
import json

# Import existing modules
from .data_loader import DataLoader
from .database_manager import DatabaseManager
from .schema_generator import SchemaGenerator
from .nlp_processor import NLPProcessor
from .visualizer import Visualizer
from .cache_manager import CacheManager
from .feedback import FeedbackSystem


class SUTRA:
    """
    Main SUTRA class for natural language to SQL operations.
    
    Usage:
        from sutra import SUTRA
        
        # Step 1: Initialize with OpenAI API key
        sutra = SUTRA(api_key="your-openai-api-key")
        
        # Step 2: Upload data
        sutra.upload_data("data.csv")
        
        # Step 3: Query using natural language
        result = sutra.query("Show me all sales data", visualize=True)
    """
    
    def __init__(self, api_key: Optional[str] = None, db_path: str = "sutra_database.db"):
        """
        Initialize SUTRA system.
        
        Args:
            api_key: OpenAI API key. If None, will look for OPENAI_API_KEY env variable
            db_path: Path to SQLite database file
        """
        # Set API key
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        elif "OPENAI_API_KEY" not in os.environ:
            raise ValueError(
                "OpenAI API key required. Either pass api_key parameter or set OPENAI_API_KEY environment variable."
            )
        
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.db_path = db_path
        
        # Initialize components
        self.data_loader = DataLoader()
        self.db_manager = DatabaseManager(self.db_path)
        self.schema_generator = SchemaGenerator(self.db_manager)
        self.nlp_processor = NLPProcessor(self.api_key)
        self.visualizer = Visualizer()
        self.cache_manager = CacheManager()
        self.feedback_system = FeedbackSystem()
        
        self.current_table = None
        self.schema = None
        
        print("✓ SUTRA initialized successfully!")
        print(f"✓ Database: {self.db_path}")
    
    def upload_data(self, file_path: Union[str, pd.DataFrame], table_name: Optional[str] = None):
        """
        Upload data from various sources to database.
        
        Args:
            file_path: Path to data file (CSV, Excel, JSON, SQL, PDF, DOCX) or pandas DataFrame
            table_name: Name for the table. If None, will use filename
        
        Returns:
            str: Name of created table
        """
        print(f"\n📤 Uploading data...")
        
        # Handle DataFrame
        if isinstance(file_path, pd.DataFrame):
            if table_name is None:
                table_name = "uploaded_data"
            df = file_path
        else:
            # Load data using DataLoader
            df = self.data_loader.load_data(file_path)
            
            if table_name is None:
                # Generate table name from filename
                table_name = Path(file_path).stem.replace(" ", "_").replace("-", "_")
        
        # Clean table name
        table_name = "".join(c if c.isalnum() or c == "_" else "_" for c in table_name)
        
        # Store in database
        self.db_manager.store_dataframe(df, table_name)
        self.current_table = table_name
        
        # Generate schema
        self.schema = self.schema_generator.generate_schema()
        
        print(f"✓ Data uploaded successfully to table: {table_name}")
        print(f"✓ Rows: {len(df)}, Columns: {len(df.columns)}")
        print(f"✓ Columns: {', '.join(df.columns.tolist())}")
        
        return table_name
    
    def list_tables(self) -> List[str]:
        """
        List all tables in the database.
        
        Returns:
            List of table names
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return tables
    
    def show_schema(self, table_name: Optional[str] = None):
        """
        Display database schema.
        
        Args:
            table_name: Specific table name. If None, shows all tables
        """
        if self.schema is None:
            self.schema = self.schema_generator.generate_schema()
        
        print("\n📋 Database Schema:")
        print("=" * 60)
        
        if table_name:
            if table_name in self.schema:
                print(f"\nTable: {table_name}")
                for col, dtype in self.schema[table_name].items():
                    print(f"  - {col}: {dtype}")
            else:
                print(f"Table '{table_name}' not found")
        else:
            for table, columns in self.schema.items():
                print(f"\nTable: {table}")
                for col, dtype in columns.items():
                    print(f"  - {col}: {dtype}")
        
        print("=" * 60)
    
    def query(self, question: str, visualize: bool = False, table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Query database using natural language.
        
        Args:
            question: Natural language question
            visualize: Whether to create visualization
            table_name: Specific table to query. If None, uses current table
        
        Returns:
            Dictionary containing:
                - sql: Generated SQL query
                - data: Query results as DataFrame
                - visualization: Plotly figure (if visualize=True)
                - success: Boolean indicating success
        """
        print(f"\n🔍 Processing query: '{question}'")
        
        # Use specified table or current table
        target_table = table_name or self.current_table
        
        if target_table is None:
            return {
                "success": False,
                "error": "No table specified. Please upload data first or specify table_name parameter."
            }
        
        # Check cache
        cached_result = self.cache_manager.get_cached_query(question)
        if cached_result:
            print("✓ Retrieved from cache")
            sql_query = cached_result
        else:
            # Generate SQL using NLP
            if self.schema is None:
                self.schema = self.schema_generator.generate_schema()
            
            sql_query = self.nlp_processor.generate_sql(question, self.schema)
            
            # Cache the query
            self.cache_manager.cache_query(question, sql_query)
        
        print(f"✓ Generated SQL: {sql_query}")
        
        # Execute query
        try:
            result_df = self.db_manager.execute_query(sql_query)
            print(f"✓ Query executed successfully! Returned {len(result_df)} rows")
            
            # Create visualization if requested
            viz_figure = None
            if visualize and not result_df.empty:
                print("📊 Creating visualization...")
                viz_figure = self.visualizer.create_visualization(result_df, question)
                if viz_figure:
                    print("✓ Visualization created")
                    viz_figure.show()
            
            return {
                "success": True,
                "sql": sql_query,
                "data": result_df,
                "visualization": viz_figure
            }
            
        except Exception as e:
            print(f"✗ Error executing query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sql": sql_query
            }
    
    def direct_query(self, sql: str, visualize: bool = False) -> Dict[str, Any]:
        """
        Execute SQL query directly without NLP processing.
        
        Args:
            sql: SQL query string
            visualize: Whether to create visualization
        
        Returns:
            Dictionary containing query results
        """
        print(f"\n⚡ Executing direct SQL query...")
        print(f"SQL: {sql}")
        
        try:
            result_df = self.db_manager.execute_query(sql)
            print(f"✓ Query executed successfully! Returned {len(result_df)} rows")
            
            # Create visualization if requested
            viz_figure = None
            if visualize and not result_df.empty:
                print("📊 Creating visualization...")
                viz_figure = self.visualizer.create_visualization(result_df, "Direct Query")
                if viz_figure:
                    print("✓ Visualization created")
                    viz_figure.show()
            
            return {
                "success": True,
                "sql": sql,
                "data": result_df,
                "visualization": viz_figure
            }
            
        except Exception as e:
            print(f"✗ Error executing query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sql": sql
            }
    
    def get_sample_data(self, table_name: Optional[str] = None, n: int = 5) -> pd.DataFrame:
        """
        Get sample rows from a table.
        
        Args:
            table_name: Table name. If None, uses current table
            n: Number of rows to return
        
        Returns:
            DataFrame with sample data
        """
        target_table = table_name or self.current_table
        
        if target_table is None:
            print("No table specified")
            return pd.DataFrame()
        
        sql = f"SELECT * FROM {target_table} LIMIT {n}"
        result = self.db_manager.execute_query(sql)
        
        print(f"\n📊 Sample data from '{target_table}':")
        print(result)
        
        return result
    
    def provide_feedback(self, question: str, sql: str, is_correct: bool, correct_sql: Optional[str] = None):
        """
        Provide feedback on query results.
        
        Args:
            question: Original natural language question
            sql: Generated SQL query
            is_correct: Whether the query was correct
            correct_sql: Correct SQL if the generated one was wrong
        """
        self.feedback_system.add_feedback(question, sql, is_correct, correct_sql)
        print("✓ Feedback recorded")
    
    def export_results(self, data: pd.DataFrame, file_path: str, format: str = "csv"):
        """
        Export query results to file.
        
        Args:
            data: DataFrame to export
            file_path: Output file path
            format: Export format (csv, excel, json)
        """
        if format.lower() == "csv":
            data.to_csv(file_path, index=False)
        elif format.lower() in ["excel", "xlsx"]:
            data.to_excel(file_path, index=False)
        elif format.lower() == "json":
            data.to_json(file_path, orient="records", indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"✓ Results exported to {file_path}")
    
    def close(self):
        """Close database connection."""
        self.db_manager.close()
        print("✓ SUTRA closed successfully")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
