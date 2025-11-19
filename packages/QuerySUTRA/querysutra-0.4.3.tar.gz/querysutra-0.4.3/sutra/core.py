"""
Core SUTRA class - Main interface for the library
"""
import os
import pandas as pd
from typing import Optional, Union, Dict, Any
from pathlib import Path

from .data_loader import DataLoader
from .database_manager import DatabaseManager
from .schema_generator import SchemaGenerator
from .nlp_processor import NLPProcessor
from .visualizer import Visualizer
from .cache_manager import CacheManager
from .feedback import FeedbackSystem
from .direct_query import DirectQueryHandler


class Sutra:
    """
    Main SUTRA class for natural language to SQL queries with visualization.
    
    Example:
        >>> from sutra import Sutra
        >>> sutra = Sutra(api_key="your-openai-api-key")
        >>> sutra.upload_data("sales_data.csv")
        >>> result = sutra.query("What are the top 5 products by revenue?", visualize=True)
    """
    
    def __init__(self, api_key: Optional[str] = None, db_path: Optional[str] = None):
        """
        Initialize SUTRA system.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY in environment.
            db_path: Path to SQLite database. If not provided, creates 'sutra_data.db' in current directory.
        """
        # Set API key
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        elif 'OPENAI_API_KEY' not in os.environ:
            raise ValueError(
                "OpenAI API key required. Either pass api_key parameter or set OPENAI_API_KEY environment variable."
            )
        
        self.api_key = os.environ['OPENAI_API_KEY']
        
        # Set database path
        self.db_path = db_path or "sutra_data.db"
        
        # Initialize components
        self.data_loader = DataLoader()
        self.db_manager = DatabaseManager(self.db_path)
        self.schema_generator = SchemaGenerator()
        self.nlp_processor = NLPProcessor(api_key=self.api_key)
        self.visualizer = Visualizer()
        self.cache_manager = CacheManager()
        self.feedback_system = FeedbackSystem()
        self.direct_query = DirectQueryHandler(self.db_manager)
        
        self.uploaded_tables = []
        
        print(f"✓ SUTRA initialized successfully!")
        print(f"✓ Database: {self.db_path}")
    
    def upload_data(self, file_path: str, table_name: Optional[str] = None) -> str:
        """
        Upload data from various file formats (CSV, Excel, JSON, etc.) to the database.
        
        Args:
            file_path: Path to the data file (supports .csv, .xlsx, .json, .parquet, etc.)
            table_name: Optional custom table name. If not provided, uses filename.
        
        Returns:
            Table name where data was stored
            
        Example:
            >>> sutra.upload_data("sales_data.csv")
            >>> sutra.upload_data("products.xlsx", table_name="products")
        """
        print(f"\n📂 Loading data from: {file_path}")
        
        # Load data using DataLoader
        df = self.data_loader.load(file_path)
        
        # Determine table name
        if table_name is None:
            table_name = Path(file_path).stem.lower().replace(" ", "_")
        
        # Store in database
        self.db_manager.store_dataframe(df, table_name)
        
        # Generate schema
        schema = self.schema_generator.generate_schema(df, table_name)
        
        # Store schema for NLP processing
        self.nlp_processor.add_schema(table_name, schema)
        
        self.uploaded_tables.append(table_name)
        
        print(f"✓ Data uploaded successfully to table: '{table_name}'")
        print(f"✓ Rows: {len(df)}, Columns: {len(df.columns)}")
        
        return table_name
    
    def list_tables(self) -> list:
        """
        List all tables in the database.
        
        Returns:
            List of table names
        """
        tables = self.db_manager.list_tables()
        print("\n📊 Available tables:")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
        return tables
    
    def show_table_info(self, table_name: str):
        """
        Display information about a specific table.
        
        Args:
            table_name: Name of the table
        """
        info = self.db_manager.get_table_info(table_name)
        print(f"\n📋 Table: {table_name}")
        print(info)
    
    def direct_sql(self, sql_query: str, visualize: bool = False) -> Dict[str, Any]:
        """
        Execute a direct SQL query on the database (without NLP processing).
        
        Args:
            sql_query: SQL query string
            visualize: Whether to create visualizations
            
        Returns:
            Dictionary with results and optional visualization
            
        Example:
            >>> result = sutra.direct_sql("SELECT * FROM sales LIMIT 10")
            >>> print(result['data'])
        """
        print(f"\n🔍 Executing SQL query...")
        
        # Execute query
        df = self.direct_query.execute(sql_query)
        
        result = {
            'query': sql_query,
            'data': df,
            'success': True
        }
        
        # Visualize if requested
        if visualize and not df.empty:
            print("\n📊 Generating visualization...")
            viz = self.visualizer.create_visualization(df, sql_query)
            result['visualization'] = viz
        
        print(f"✓ Query executed successfully! Returned {len(df)} rows.")
        
        return result
    
    def query(self, natural_language_query: str, visualize: bool = True) -> Dict[str, Any]:
        """
        Query the database using natural language.
        
        Args:
            natural_language_query: Your question in plain English
            visualize: Whether to automatically create visualizations (default: True)
            
        Returns:
            Dictionary containing:
                - 'query': Natural language query
                - 'sql': Generated SQL query
                - 'data': Results as pandas DataFrame
                - 'visualization': Plotly figure (if visualize=True)
                - 'success': Boolean indicating if query was successful
                
        Example:
            >>> result = sutra.query("What are the top 10 products by sales?")
            >>> print(result['data'])
            >>> result['visualization'].show()  # Display the chart
        """
        print(f"\n💬 Query: {natural_language_query}")
        
        # Check cache
        cached_result = self.cache_manager.get(natural_language_query)
        if cached_result:
            print("✓ Retrieved from cache!")
            return cached_result
        
        # Generate SQL from natural language
        print("🔄 Generating SQL query...")
        sql_query = self.nlp_processor.generate_sql(
            natural_language_query, 
            self.uploaded_tables
        )
        
        print(f"📝 Generated SQL: {sql_query}")
        
        # Execute query
        try:
            df = self.db_manager.execute_query(sql_query)
            
            result = {
                'query': natural_language_query,
                'sql': sql_query,
                'data': df,
                'success': True
            }
            
            # Create visualization if requested
            if visualize and not df.empty:
                print("📊 Creating visualization...")
                viz = self.visualizer.create_visualization(df, natural_language_query)
                result['visualization'] = viz
                print("✓ Visualization created!")
            
            # Cache the result
            self.cache_manager.set(natural_language_query, result)
            
            print(f"✓ Query successful! Returned {len(df)} rows.")
            
            return result
            
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
            return {
                'query': natural_language_query,
                'sql': sql_query,
                'error': str(e),
                'success': False
            }
    
    def provide_feedback(self, query: str, sql: str, is_correct: bool, correct_sql: Optional[str] = None):
        """
        Provide feedback on query results to improve future queries.
        
        Args:
            query: The natural language query
            sql: The generated SQL
            is_correct: Whether the SQL was correct
            correct_sql: The correct SQL (if is_correct=False)
            
        Example:
            >>> sutra.provide_feedback(
            ...     query="Show me sales",
            ...     sql="SELECT * FROM sales",
            ...     is_correct=False,
            ...     correct_sql="SELECT SUM(amount) FROM sales"
            ... )
        """
        self.feedback_system.add_feedback(query, sql, is_correct, correct_sql)
        print("✓ Feedback recorded. Thank you!")
    
    def get_schema(self) -> str:
        """
        Get the complete database schema.
        
        Returns:
            Formatted schema string
        """
        return self.db_manager.get_full_schema()
    
    def export_results(self, result: Dict[str, Any], output_path: str, format: str = 'csv'):
        """
        Export query results to a file.
        
        Args:
            result: Query result dictionary
            output_path: Path to save the file
            format: Output format ('csv', 'excel', 'json')
            
        Example:
            >>> result = sutra.query("SELECT * FROM sales")
            >>> sutra.export_results(result, "sales_export.csv")
        """
        if not result.get('success') or result.get('data') is None:
            print("❌ No data to export")
            return
        
        df = result['data']
        
        if format.lower() == 'csv':
            df.to_csv(output_path, index=False)
        elif format.lower() in ['excel', 'xlsx']:
            df.to_excel(output_path, index=False)
        elif format.lower() == 'json':
            df.to_json(output_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"✓ Results exported to: {output_path}")
    
    def close(self):
        """Close database connection."""
        self.db_manager.close()
        print("✓ SUTRA closed successfully!")
