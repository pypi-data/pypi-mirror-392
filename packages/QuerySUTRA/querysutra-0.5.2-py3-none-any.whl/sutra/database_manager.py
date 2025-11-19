"""Database management for both SQLite and MySQL"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, List
from tabulate import tabulate
import config

# Add MySQL support
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("⚠️ MySQL not installed. Run: pip install mysql-connector-python")

class DatabaseManager:
    """Manage database operations (SQLite or MySQL)"""
    
    """Database management for both SQLite and MySQL"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, List
from tabulate import tabulate
import config

# Add MySQL support
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("⚠️ MySQL not installed. Run: pip install mysql-connector-python")

class DatabaseManager:
    """Manage database operations (SQLite or MySQL)"""
    
    def __init__(self, db_path: str = ':memory:', db_type: str = 'sqlite'):  # FIX: Added indentation
        self.db_type = db_type.lower()
        
        if self.db_type == 'mysql':
            if not MYSQL_AVAILABLE:
                print("❌ MySQL not available, falling back to SQLite")
                self.db_type = 'sqlite'
            else:
                # First connect without database to create it if needed
                try:
                    conn_temp = mysql.connector.connect(
                        host=config.MYSQL_HOST,
                        user=config.MYSQL_USER,
                        password=config.MYSQL_PASSWORD
                    )
                    cursor_temp = conn_temp.cursor()
                    cursor_temp.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DATABASE}")
                    conn_temp.close()
                    print(f"✅ Database {config.MYSQL_DATABASE} ready")
                except Exception as e:
                    print(f"❌ Could not create database: {e}")
                
                # Now connect to the database
                self.conn = mysql.connector.connect(
                    host=config.MYSQL_HOST,
                    user=config.MYSQL_USER,
                    password=config.MYSQL_PASSWORD,
                    database=config.MYSQL_DATABASE
                )
                self.cursor = self.conn.cursor()
                print(f"📂 Connected to MySQL: {config.MYSQL_DATABASE}")
        
        if self.db_type == 'sqlite':  # FIX: Added this block for SQLite
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            print(f"📂 SQLite {'created in memory' if db_path == ':memory:' else f'connected: {db_path}'}")
    
    # Rest of the methods stay the same...
    
    def execute_schema(self, schema_sql: str) -> bool:
        """Execute SQL schema with MySQL compatibility"""
        try:
            if self.db_type == 'mysql':
                # MySQL adjustments
                schema_sql = schema_sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 
                                                'INT PRIMARY KEY AUTO_INCREMENT')
                schema_sql = schema_sql.replace('TEXT', 'VARCHAR(255)')
                schema_sql = schema_sql.replace('REAL', 'DECIMAL(10,2)')
                
                # Execute statements one by one for MySQL
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        self.cursor.execute(statement)
                self.conn.commit()
            else:
                # SQLite can handle multiple statements
                self.cursor.executescript(schema_sql)
                self.conn.commit()
            
            print("✅ Schema executed successfully!")
            return True
        except Exception as e:
            print(f"❌ Error executing schema: {e}")
            return False
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Execute query on either database"""
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"❌ Query error: {e}")
            return None
    
    def get_tables(self):
        """Get list of all tables in database"""
        if self.db_type == 'mysql':
            cursor = self.conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            return tables
        else:  # sqlite
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            return tables

    def get_columns(self, table_name):
        """Get list of columns for a specific table"""
        if self.db_type == 'mysql':
            cursor = self.conn.cursor()
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
            columns = [col[0] for col in cursor.fetchall()]
            cursor.close()
            return columns
        else:  # sqlite
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            cursor.close()
            return columns
    
    def get_schema_context(self) -> str:
        """Get database schema"""
        if self.db_type == 'mysql':
            tables = self.get_tables()
            schema = []
            for table in tables:
                self.cursor.execute(f"SHOW CREATE TABLE {table}")
                schema.append(self.cursor.fetchone()[1])
            return '\n'.join(schema)
        else:
            self.cursor.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            )
            return '\n'.join([row[0] for row in self.cursor.fetchall()])
    
    def display_tables(self):  # FIX: Proper indentation - part of class
        """Display all tables with their structure and data"""
        tables = self.get_tables()
        print(f"\n📋 Created {len(tables)} tables:")
        
        for table in tables:
            print(f"\n  Table: {table}")
            
            # Show columns
            columns = self.get_table_info(table)
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
            
            # Show row count
            count = self.get_row_count(table)
            print(f"    Records: {count}")
    
    def get_table_info(self, table_name: str) -> List[Tuple]:  # FIX: Proper indentation
        """Get column information for a table"""
        if self.db_type == 'mysql':
            self.cursor.execute(f"DESCRIBE {table_name}")
            return [(i, row[0], row[1]) for i, row in enumerate(self.cursor.fetchall())]
        else:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            return self.cursor.fetchall()
    
    def get_row_count(self, table_name: str) -> int:  # FIX: Proper indentation
        """Get number of rows in a table"""
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return self.cursor.fetchone()[0]
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("📂 Database connection closed")

    