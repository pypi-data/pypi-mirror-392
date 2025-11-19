"""
Test suite for SUTRA library
Run with: pytest test_sutra.py
"""

import pytest
import pandas as pd
import os
from sutra import SutraClient


class TestSutraClient:
    """Test cases for SutraClient"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        # Use a test database
        api_key = os.getenv('OPENAI_API_KEY', 'test-key')
        client = SutraClient(api_key=api_key, db_path="test_db.db")
        yield client
        # Cleanup
        client.close()
        if os.path.exists("test_db.db"):
            os.remove("test_db.db")
    
    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrame"""
        return pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['New York', 'London', 'Paris']
        })
    
    def test_client_initialization(self, client):
        """Test client can be initialized"""
        assert client is not None
        assert client.db_path == "test_db.db"
    
    def test_upload_dataframe(self, client, sample_data):
        """Test uploading a DataFrame"""
        result = client.upload_dataframe(sample_data, "test_table")
        assert result['status'] == 'success'
        assert result['table_name'] == 'test_table'
        assert result['rows_inserted'] == 3
    
    def test_list_tables(self, client, sample_data):
        """Test listing tables"""
        client.upload_dataframe(sample_data, "test_table")
        tables = client.list_tables()
        assert 'test_table' in tables
    
    def test_execute_sql(self, client, sample_data):
        """Test direct SQL execution"""
        client.upload_dataframe(sample_data, "test_table")
        result = client.execute_sql("SELECT * FROM test_table")
        assert result['status'] == 'success'
        assert len(result['results']) == 3
    
    def test_get_table_info(self, client, sample_data):
        """Test getting table information"""
        client.upload_dataframe(sample_data, "test_table")
        info = client.get_table_info("test_table")
        assert info['table_name'] == 'test_table'
        assert len(info['columns']) > 0


def test_import():
    """Test that the library can be imported"""
    from sutra import SutraClient
    assert SutraClient is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
