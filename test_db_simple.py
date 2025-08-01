#!/usr/bin/env python3
"""Simple database connection test without retry logic"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def simple_db_test():
    """Simple database connection test"""
    try:
        # Get the DATABASE_URL
        database_url = os.getenv("DATABASE_URL")
        print(f"Using DATABASE_URL: {database_url[:50]}...")
        
        if not database_url:
            print("ERROR: DATABASE_URL not found in environment")
            return False
        
        # Create engine with minimal settings
        engine = create_engine(database_url, echo=True)
        
        # Test connection
        print("Attempting database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test, GETDATE() as current_time"))
            row = result.fetchone()
            print(f"SUCCESS: Connected to database!")
            print(f"Test query result: {row}")
            return True
            
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("=== Simple Database Connection Test ===")
    success = simple_db_test()
    print(f"Connection test {'PASSED' if success else 'FAILED'}")
