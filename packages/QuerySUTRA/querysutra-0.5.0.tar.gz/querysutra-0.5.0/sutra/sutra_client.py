"""
Main client interface for SUTRA library
"""

import os
from pathlib import Path
from typing import Optional, Union, List
import pandas as pd

from .data_loader import DataLoader
from .database_manager import DatabaseManager
from .schema_generator import SchemaGenerator
from .nlp_processor import NLPProcessor
from .visualizer import Visualizer
from .direct_query import DirectQueryHandler
from .cache_manager import CacheManager
from .feedback import FeedbackSystem


class SutraClient:
    """
    Main client for interacting with SUTRA - Natural Language to SQL system.
    
    Usage Example:
        ```python
        from sutra import SutraClient
        
        # Initialize client
        client = SutraClient(api_key="your-openai-key")
        
        # Upload data
        client.upload_data("sales_data.csv")
        
        # Query with natural language
        result = client.query("Show me total sales by region")
        
        # Query with visualization
        result = client.query("Show me sales trend over time", visualize=True)
        ```
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        db_path: str = "sutra_database.db",
        use_cache: bool = True
    ):
        """
        Initialize SUTRA client.
        
        Args:
            api_key: OpenAI API key. If None, will try to read from OPENAI_API_KEY env variable
            db_path: Path to SQLite database file
            use_cache: Whether to use caching for queries
        """
        # Set API key
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        elif 'OPENAI_API_KEY' not in os.environ:
            raise ValueError(
                "OpenAI API key not found. Please provide it via:\n"
                "  1. SutraClient(api_key='your-key'), or\n"
                "  2. Set OPENAI_API_KEY environment variable"
            )
        
        self.api_key = os.environ['OPENAI_API_KEY']
        self.db_path = db_path
        self.use_cache = use_cache
        
        # Initialize components
        self.db_manager = DatabaseManager(db_path)
        self.data_loader = DataLoader(self.db_manager)
        self.schema_generator = SchemaGenerator(self.db_manager)
        self.nlp_processor = NLPProcessor(self.api_key)
        self.visualizer = Visualizer()
        self.direct_query_handler = DirectQueryHandler(self.db_manager)
        
        if use_cache:
            self.cache_manager = CacheManager()
        
        self.feedback_system = FeedbackSystem(self.db_manager)
        
        print(f"✓ SUTRA initialized successfully!")
        print(f"✓ Database: {db_path}")
        print(f"✓ Cache enabled: {use_cache}")
    
    def set_api_key(self, api_key: str):
        """
        Set or update OpenAI API key.
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        os.environ['OPENAI_API_KEY'] = api_key
        self.nlp_processor = NLPProcessor(api_key)
        print("✓ API key updated successfully!")
    
    def upload_data(
        self, 
        file_path: str, 
        table_name: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> dict:
        """
        Upload data from various file formats to the database.
        
        Supported formats: CSV, Excel (.xlsx, .xls), JSON, PDF, DOCX, TXT, HTML
        
        Args:
            file_path: Path to the data file
            table_name: Name for the database table (optional, auto-generated if None)
            file_type: File type override (optional, auto-detected from extension)
        
        Returns:
            dict: Status information including table name and row count
        
        Example:
            ```python
            # Upload CSV
            client.upload_data("sales.csv")
            
            # Upload Excel with custom table name
            client.upload_data("data.xlsx", table_name="monthly_sales")
            
            # Upload JSON
            client.upload_data("products.json")
            ```
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-generate table name if not provided
        if table_name is None:
            table_name = Path(file_path).stem.lower().replace(" ", "_").replace("-", "_")
        
        print(f"📁 Uploading data from: {file_path}")
        print(f"📊 Table name: {table_name}")
        
        try:
            # Load data using DataLoader
            result = self.data_loader.load_data(file_path, table_name, file_type)
            
            # Generate schema after loading
            self.schema_generator.generate_schema()
            
            print(f"✓ Data uploaded successfully!")
            print(f"✓ Rows inserted: {result.get('rows_inserted', 'N/A')}")
            
            return {
                "status": "success",
                "table_name": table_name,
                "file_path": file_path,
                "rows_inserted": result.get('rows_inserted', 0)
            }
            
        except Exception as e:
            print(f"✗ Error uploading data: {str(e)}")
            raise
    
    def upload_dataframe(self, df: pd.DataFrame, table_name: str) -> dict:
        """
        Upload a pandas DataFrame directly to the database.
        
        Args:
            df: Pandas DataFrame
            table_name: Name for the database table
        
        Returns:
            dict: Status information
        
        Example:
            ```python
            import pandas as pd
            
            df = pd.DataFrame({
                'name': ['Alice', 'Bob'],
                'age': [25, 30]
            })
            
            client.upload_dataframe(df, "users")
            ```
        """
        print(f"📊 Uploading DataFrame to table: {table_name}")
        
        try:
            self.data_loader.load_from_dataframe(df, table_name)
            self.schema_generator.generate_schema()
            
            print(f"✓ DataFrame uploaded successfully!")
            print(f"✓ Rows inserted: {len(df)}")
            
            return {
                "status": "success",
                "table_name": table_name,
                "rows_inserted": len(df)
            }
            
        except Exception as e:
            print(f"✗ Error uploading DataFrame: {str(e)}")
            raise
    
    def list_tables(self) -> List[str]:
        """
        List all tables in the database.
        
        Returns:
            List of table names
        
        Example:
            ```python
            tables = client.list_tables()
            print("Available tables:", tables)
            ```
        """
        tables = self.db_manager.get_all_tables()
        print(f"\n📋 Available tables ({len(tables)}):")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
        return tables
    
    def get_table_info(self, table_name: str) -> dict:
        """
        Get detailed information about a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            dict: Table information including columns, types, and sample data
        """
        schema = self.db_manager.get_table_schema(table_name)
        sample = self.db_manager.execute_query(f"SELECT * FROM {table_name} LIMIT 5")
        
        print(f"\n📊 Table: {table_name}")
        print(f"Columns: {len(schema)}")
        for col in schema:
            print(f"  - {col['name']}: {col['type']}")
        
        return {
            "table_name": table_name,
            "columns": schema,
            "sample_data": sample
        }
    
    def execute_sql(self, sql_query: str, visualize: bool = False) -> dict:
        """
        Execute SQL query directly without NLP processing.
        
        Args:
            sql_query: SQL query string
            visualize: Whether to generate visualization
        
        Returns:
            dict: Query results with optional visualization
        
        Example:
            ```python
            # Direct SQL query
            result = client.execute_sql("SELECT * FROM sales WHERE amount > 1000")
            
            # With visualization
            result = client.execute_sql(
                "SELECT region, SUM(amount) FROM sales GROUP BY region",
                visualize=True
            )
            ```
        """
        print(f"\n🔍 Executing SQL query...")
        print(f"Query: {sql_query}")
        
        try:
            results = self.direct_query_handler.execute_direct_query(sql_query)
            
            print(f"✓ Query executed successfully!")
            print(f"✓ Rows returned: {len(results) if results else 0}")
            
            response = {
                "status": "success",
                "sql_query": sql_query,
                "results": results,
                "visualization": None
            }
            
            # Generate visualization if requested
            if visualize and results:
                print("📊 Generating visualization...")
                df = pd.DataFrame(results)
                viz = self.visualizer.create_visualization(df, sql_query)
                response["visualization"] = viz
                print("✓ Visualization created!")
            
            return response
            
        except Exception as e:
            print(f"✗ Error executing query: {str(e)}")
            raise
    
    def query(
        self, 
        natural_language_query: str, 
        visualize: bool = True,
        return_sql: bool = False
    ) -> dict:
        """
        Query the database using natural language.
        
        Args:
            natural_language_query: Question in natural language
            visualize: Whether to generate visualization (default: True)
            return_sql: Whether to include generated SQL in response
        
        Returns:
            dict: Query results with optional visualization and SQL
        
        Example:
            ```python
            # Simple query
            result = client.query("What are the total sales?")
            
            # Query without visualization
            result = client.query("Show me all customers", visualize=False)
            
            # Query with SQL debugging
            result = client.query("Average price by category", return_sql=True)
            ```
        """
        print(f"\n💬 Processing query: '{natural_language_query}'")
        
        # Check cache if enabled
        if self.use_cache:
            cached_result = self.cache_manager.get_cached_query(natural_language_query)
            if cached_result:
                print("✓ Retrieved from cache!")
                return cached_result
        
        try:
            # Get schema for context
            schema = self.schema_generator.get_schema()
            
            # Generate SQL from natural language
            print("🤖 Generating SQL query...")
            sql_query = self.nlp_processor.generate_sql(natural_language_query, schema)
            print(f"✓ Generated SQL: {sql_query}")
            
            # Execute query
            results = self.db_manager.execute_query(sql_query)
            print(f"✓ Query executed successfully!")
            print(f"✓ Rows returned: {len(results) if results else 0}")
            
            response = {
                "status": "success",
                "query": natural_language_query,
                "results": results,
                "visualization": None
            }
            
            if return_sql:
                response["sql_query"] = sql_query
            
            # Generate visualization if requested and results exist
            if visualize and results:
                print("📊 Generating visualization...")
                df = pd.DataFrame(results)
                viz = self.visualizer.create_visualization(df, natural_language_query)
                response["visualization"] = viz
                print("✓ Visualization created!")
            
            # Cache the result
            if self.use_cache:
                self.cache_manager.cache_query(natural_language_query, response)
            
            return response
            
        except Exception as e:
            print(f"✗ Error processing query: {str(e)}")
            return {
                "status": "error",
                "query": natural_language_query,
                "error": str(e)
            }
    
    def provide_feedback(
        self, 
        query: str, 
        generated_sql: str, 
        is_correct: bool,
        correct_sql: Optional[str] = None
    ):
        """
        Provide feedback on query results to improve future queries.
        
        Args:
            query: Original natural language query
            generated_sql: SQL that was generated
            is_correct: Whether the generated SQL was correct
            correct_sql: Correct SQL if generated one was wrong
        
        Example:
            ```python
            client.provide_feedback(
                query="Show total sales",
                generated_sql="SELECT SUM(amount) FROM sales",
                is_correct=True
            )
            ```
        """
        self.feedback_system.add_feedback(query, generated_sql, is_correct, correct_sql)
        print("✓ Feedback recorded. Thank you!")
    
    def clear_cache(self):
        """Clear the query cache."""
        if self.use_cache:
            self.cache_manager.clear_cache()
            print("✓ Cache cleared!")
        else:
            print("Cache is not enabled.")
    
    def get_schema(self) -> str:
        """
        Get the current database schema.
        
        Returns:
            str: Formatted schema description
        """
        return self.schema_generator.get_schema()
    
    def close(self):
        """Close database connection."""
        self.db_manager.close()
        print("✓ Database connection closed.")
