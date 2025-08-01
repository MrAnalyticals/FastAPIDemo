#!/usr/bin/env python3
"""
Script to populate the Azure SQL Database with sample energy trading data
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal, test_connection, Base, engine
from app.models import Trade

def create_sample_trades():
    """Create sample energy trading data"""
    
    # Test database connection first
    if not test_connection():
        print("❌ Database connection failed. Please check your connection string and Azure SQL Database.")
        return False
    
    print("✅ Database connection successful")
    
    # Ensure tables exist
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        return False
    
    # Sample data
    commodities = ['electricity', 'oil', 'gas', 'coal', 'natural_gas', 'renewable']
    traders = ['trader_001', 'trader_002', 'trader_003', 'energy_corp', 'green_power', 'fossil_fuel_ltd']
    sides = ['buy', 'sell']
    
    # Generate sample trades
    sample_trades = []
    base_time = datetime.utcnow() - timedelta(days=30)  # Start 30 days ago
    
    for i in range(50):  # Create 50 sample trades
        trade_time = base_time + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        commodity = random.choice(commodities)
        
        # Set realistic price ranges based on commodity
        if commodity == 'electricity':
            price = round(random.uniform(50, 150), 2)  # $/MWh
            quantity = round(random.uniform(10, 1000), 2)  # MWh
        elif commodity == 'oil':
            price = round(random.uniform(60, 100), 2)  # $/barrel
            quantity = round(random.uniform(100, 10000), 2)  # barrels
        elif commodity in ['gas', 'natural_gas']:
            price = round(random.uniform(2, 8), 2)  # $/MMBtu
            quantity = round(random.uniform(1000, 50000), 2)  # MMBtu
        elif commodity == 'coal':
            price = round(random.uniform(40, 80), 2)  # $/ton
            quantity = round(random.uniform(500, 5000), 2)  # tons
        else:  # renewable
            price = round(random.uniform(30, 120), 2)  # $/MWh
            quantity = round(random.uniform(50, 2000), 2)  # MWh
        
        trade = Trade(
            commodity=commodity,
            price=price,
            quantity=quantity,
            side=random.choice(sides),
            trader_id=random.choice(traders),
            timestamp=trade_time
        )
        sample_trades.append(trade)
    
    # Insert sample trades into database
    db = SessionLocal()
    try:
        # Clear existing data first (optional)
        existing_count = db.query(Trade).count()
        print(f"📊 Current trades in database: {existing_count}")
        
        if existing_count > 0:
            response = input("Database already contains trades. Clear existing data? (y/N): ")
            if response.lower() == 'y':
                db.query(Trade).delete()
                db.commit()
                print("🗑️ Existing trades cleared")
        
        # Add sample trades
        for trade in sample_trades:
            db.add(trade)
        
        db.commit()
        print(f"✅ Successfully inserted {len(sample_trades)} sample trades")
        
        # Verify insertion
        total_trades = db.query(Trade).count()
        print(f"📊 Total trades in database: {total_trades}")
        
        # Show some statistics
        print("\n📈 Sample Data Summary:")
        for commodity in commodities:
            count = db.query(Trade).filter(Trade.commodity == commodity).count()
            if count > 0:
                print(f"  - {commodity.title()}: {count} trades")
        
        print("\n🔄 Trade Sides:")
        for side in sides:
            count = db.query(Trade).filter(Trade.side == side).count()
            print(f"  - {side.title()}: {count} trades")
        
        print("\n👥 Traders:")
        for trader in traders:
            count = db.query(Trade).filter(Trade.trader_id == trader).count()
            if count > 0:
                print(f"  - {trader}: {count} trades")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to insert sample data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main function"""
    print("🚀 Energy Trading Platform - Sample Data Population")
    print("=" * 60)
    
    success = create_sample_trades()
    
    if success:
        print("\n✅ Sample data population completed successfully!")
        print("\n🌐 You can now test the API endpoints:")
        print("  - GET /trades/ - List all trades")
        print("  - POST /trades/ - Create new trade")
        print("  - GET /trades/{id} - Get specific trade")
        print("  - GET /trades/commodity/{commodity} - Get trades by commodity")
        print("  - GET /trades/trader/{trader_id} - Get trades by trader")
        print("\n🔗 API Documentation: https://your-app-name.azurewebsites.net/docs")
    else:
        print("\n❌ Sample data population failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
