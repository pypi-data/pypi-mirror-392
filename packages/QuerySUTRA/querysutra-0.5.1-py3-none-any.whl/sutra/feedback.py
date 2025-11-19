"""Simple feedback system with CSV storage per database"""
import csv
from pathlib import Path
import config

class SimpleFeedback:
    def __init__(self):
        # This will ALWAYS match your current database name
        current_db = config.MYSQL_DATABASE if hasattr(config, 'MYSQL_DATABASE') else "default_db"
        
        # Remove any special characters for safe filename
        safe_name = current_db.replace('/', '_').replace('\\', '_')
        
        # Create CSV with exact database name
        self.file = Path(f"data/output/feedback_{safe_name}.csv")
        
        # Ensure directory exists
        self.file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV if new
        if not self.file.exists():
            with open(self.file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['database', 'question', 'sql', 'status', 'corrected_sql'])
                
        print(f"📝 Feedback file: feedback_{safe_name}.csv")
    
    def save(self, question, sql, is_good, corrected_sql=""):
        """Save feedback with database name"""
        current_db = config.MYSQL_DATABASE if hasattr(config, 'MYSQL_DATABASE') else "default_db"
        
        with open(self.file, 'a', newline='') as f:
            writer = csv.writer(f)
            # Include database name in each row for clarity
            writer.writerow([
                current_db,  # Current database
                question, 
                sql, 
                'good' if is_good else 'bad', 
                corrected_sql
            ])