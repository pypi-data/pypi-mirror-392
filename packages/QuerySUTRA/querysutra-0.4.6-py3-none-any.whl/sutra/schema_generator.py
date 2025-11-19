"""SQL schema generation from unstructured text using AI"""

import openai
import config

class SchemaGenerator:
    """Generate SQL schema from unstructured data using OpenAI"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
        openai.api_key = api_key
        self.model_name = model_name
        self.temperature = config.TEMPERATURE
    
    def generate_schema(self, unstructured_data: str) -> str:
        """Generate SQL schema from unstructured text"""
        
        # Truncate if too long
        if len(unstructured_data) > config.MAX_TEXT_LENGTH:
            unstructured_data = unstructured_data[:config.MAX_TEXT_LENGTH]
            print(f"⚠️ Data truncated to {config.MAX_TEXT_LENGTH} characters")
        
        prompt = f"""
Convert this unstructured text into a SQLite database:

{unstructured_data}

Requirements:
1. Create tables based on what entities you find in the text
2. Add foreign keys to connect related tables  
3. Extract ALL data from the text - don't add anything not in the text
4. Use INTEGER PRIMARY KEY AUTOINCREMENT for IDs

Return ONLY executable SQLite statements:
- DROP TABLE IF EXISTS statements
- CREATE TABLE statements with PRIMARY KEY and FOREIGN KEY
- INSERT statements with the actual data from the text

No markdown, no code blocks, just SQL.
"""
        
        print("🔄 Generating schema via OpenAI API...")
        
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        
        generated_schema = response['choices'][0]['message']['content'].strip()
        generated_schema = generated_schema.replace('```sql', '').replace('```', '').strip()
        
        print("✅ Schema generated!")
        return generated_schema