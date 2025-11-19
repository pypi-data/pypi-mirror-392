"""
SUTRA - Quick Start Example

This script demonstrates the basic usage of SUTRA library.
"""

from sutra import SutraClient
import pandas as pd

def main():
    print("=" * 60)
    print("SUTRA - Natural Language to SQL Query System")
    print("=" * 60)
    
    # Step 1: Get API key from user
    api_key = input("\n Enter your OpenAI API key: ").strip()
    
    # Step 2: Initialize client
    print("\n🚀 Initializing SUTRA...")
    client = SutraClient(api_key=api_key)
    
    # Step 3: Create sample data
    print("\n📊 Creating sample sales data...")
    sales_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=50),
        'product': ['Laptop', 'Mouse', 'Keyboard'] * 16 + ['Laptop', 'Mouse'],
        'amount': [1200, 25, 75] * 16 + [1200, 25],
        'region': ['North', 'South', 'East', 'West'] * 12 + ['North', 'South'],
        'quantity': [1, 2, 1] * 16 + [1, 2]
    })
    
    # Step 4: Upload data
    print("\n📁 Uploading data to database...")
    client.upload_dataframe(sales_data, "sales")
    
    # Step 5: List tables
    print("\n📋 Checking database...")
    client.list_tables()
    
    # Step 6: Run example queries
    print("\n" + "=" * 60)
    print("EXAMPLE QUERIES")
    print("=" * 60)
    
    queries = [
        "What are the total sales?",
        "Show me sales by product",
        "Which region has the highest revenue?",
        "What's the average order value?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: '{query}'")
        result = client.query(query, visualize=False)
        
        if result['status'] == 'success':
            df = pd.DataFrame(result['results'])
            print("\nResults:")
            print(df.to_string(index=False))
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Step 7: Example with visualization
    print("\n" + "=" * 60)
    print("QUERY WITH VISUALIZATION")
    print("=" * 60)
    print("\nQuery: 'Show sales by region'")
    result = client.query("Show sales by region", visualize=True)
    
    if result['status'] == 'success':
        df = pd.DataFrame(result['results'])
        print("\nResults:")
        print(df.to_string(index=False))
        if result['visualization']:
            print("\n✓ Visualization created!")
    
    # Step 8: Direct SQL example
    print("\n" + "=" * 60)
    print("DIRECT SQL QUERY")
    print("=" * 60)
    sql = "SELECT product, COUNT(*) as order_count FROM sales GROUP BY product"
    print(f"\nSQL: {sql}")
    result = client.execute_sql(sql)
    
    if result['status'] == 'success':
        df = pd.DataFrame(result['results'])
        print("\nResults:")
        print(df.to_string(index=False))
    
    # Step 9: Interactive mode
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("=" * 60)
    print("\nYou can now ask your own questions!")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_query = input("Your question: ").strip()
        
        if user_query.lower() in ['exit', 'quit', 'q']:
            break
        
        if not user_query:
            continue
        
        # Ask if user wants visualization
        viz_input = input("Do you want visualization? (y/n): ").strip().lower()
        visualize = viz_input in ['y', 'yes']
        
        result = client.query(user_query, visualize=visualize)
        
        if result['status'] == 'success':
            df = pd.DataFrame(result['results'])
            print("\nResults:")
            print(df.to_string(index=False))
            print()
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}\n")
    
    # Close
    print("\n✓ Closing connection...")
    client.close()
    print("✓ Thank you for using SUTRA!")

if __name__ == "__main__":
    main()
