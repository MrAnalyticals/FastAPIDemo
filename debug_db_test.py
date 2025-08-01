#!/usr/bin/env python3
"""Database connection test that saves output to file"""

import os
import sys
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Redirect all output to both console and file
class TeeOutput:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Set up logging
sys.stdout = TeeOutput('db_test_output.txt')

print(f"=== Database Connection Test - {datetime.now()} ===")

try:
    # Load environment variables
    print("Loading environment variables...")
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL found: {bool(database_url)}")
    if database_url:
        print(f"DATABASE_URL (first 80 chars): {database_url[:80]}...")
    
    print(f"USE_MANAGED_IDENTITY: {os.getenv('USE_MANAGED_IDENTITY')}")
    print(f"AZURE_SQL_SERVER: {os.getenv('AZURE_SQL_SERVER')}")
    print(f"AZURE_SQL_DATABASE: {os.getenv('AZURE_SQL_DATABASE')}")
    
    # Test SQLAlchemy import
    print("\nTesting imports...")
    from sqlalchemy import create_engine, text
    print("SQLAlchemy imported successfully")
    
    # Test pyodbc
    import pyodbc
    print("pyodbc imported successfully")
    print(f"Available ODBC drivers: {pyodbc.drivers()}")
    
    # Test connection
    print(f"\nTesting database connection...")
    if not database_url:
        print("ERROR: No DATABASE_URL found!")
        sys.exit(1)
    
    engine = create_engine(database_url, echo=True)
    print("Engine created successfully")
    
    print("Attempting to connect...")
    with engine.connect() as conn:
        print("Connection established!")
        result = conn.execute(text("SELECT 1 as test, GETDATE() as current_datetime"))
        row = result.fetchone()
        print(f"Query executed successfully: {row}")
        print("SUCCESS: Database connection working!")

except Exception as e:
    print(f"\nERROR: Database connection failed!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print(f"\nFull traceback:")
    traceback.print_exc()

print(f"\n=== Test completed at {datetime.now()} ===")
