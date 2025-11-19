"""Direct query existing MySQL databases without API calls"""

import mysql.connector
import pandas as pd
from tabulate import tabulate
import config

def list_databases():
    """Show all available databases"""
    conn = mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall()]
    
    # Filter your NLP databases
    nlp_dbs = [db for db in databases if '_db' in db or db == 'sample']
    conn.close()
    return nlp_dbs

def query_database(db_name, query):
    """Run SQL query on specific database"""
    conn = mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=db_name
    )
    
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        conn.close()

def main():
    print("="*60)
    print("DIRECT DATABASE QUERY (No API Calls)")
    print("="*60)
    
    # List available databases
    databases = list_databases()
    print("\n📂 Available databases:")
    for i, db in enumerate(databases, 1):
        print(f"  {i}. {db}")
    
    # Select database
    choice = input("\nSelect database number: ")
    db_name = databases[int(choice)-1]
    
    print(f"\n✅ Connected to: {db_name}")
    
    # Show tables
    conn = mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=db_name
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"📋 Tables: {', '.join(tables)}")
    conn.close()
    
    # Interactive SQL queries
    while True:
        print("\n" + "="*60)
        query = input("Enter SQL query (or 'exit'): ").strip()
        
        if query.lower() == 'exit':
            break
        
        # Quick shortcuts
        if query.lower() == 'show tables':
            query = "SHOW TABLES"
        elif query.lower().startswith('describe '):
            table = query.split()[1]
            query = f"DESCRIBE {table}"
        
        df = query_database(db_name, query)
        if df is not None and not df.empty:
            print(f"\n📊 Results ({len(df)} rows):")
            print(tabulate(df.head(20), headers='keys', tablefmt='grid', showindex=False))
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main()