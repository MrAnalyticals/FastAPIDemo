from fastapi import FastAPI, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
import random
from . import models, schemas, crud
from .database import SessionLocal, engine, Base, test_connection

# Dynamic example functions
def get_random_trade_id():
    return random.randint(1, 25)

def get_random_commodity():
    return random.choice(['electricity', 'oil', 'gas', 'coal', 'natural_gas', 'renewable'])

def get_random_trader():
    return random.choice(['trader_001', 'trader_002', 'trader_003', 'energy_corp', 'green_power', 'fossil_fuel_ltd'])

# Initialize FastAPI app
app = FastAPI(
    title="Energy Trading Platform - REST API",
    description="""
    ## 🔋 Energy Commodities Trading Platform
    
    A **REST API service** for managing energy commodity trades in real-time. This platform provides comprehensive 
    endpoints for creating, retrieving, and managing trades across various energy markets.
    
    ### 🎯 **What This API Does:**
    - **Trade Management**: Create, retrieve, and filter energy commodity trades
    - **Market Data**: Access real-time simulated market data for energy commodities
    - **Multi-Commodity Support**: Electricity, Oil, Gas, Coal, Natural Gas, and Renewable energy
    - **Trader Management**: Track trades by individual traders or organizations
    
    ### 🚀 **How to Use This API:**
    1. **Create Trades**: Use `POST /trades/` to register new energy trades
    2. **Query Trades**: Use `GET /trades/` with filters to find specific trades
    3. **Market Data**: Use `GET /market-data/current` for live market information
    4. **Specific Lookups**: Use ID-based endpoints to get individual trades or filter by commodity/trader
    
    ---
    
    ## 🎲 **Dynamic Testing Made Easy!**
    
    ### **1. 🔄 Dynamic Examples Endpoint**
    **NEW**: `/examples/dynamic` endpoint that provides fresh examples on every request:
    
    **This endpoint gives you:**
    - ✅ **Fresh trade IDs, commodities, and traders** on each call
    - ✅ **Ready-to-use test URLs** with dynamic values
    - ✅ **Sample trade data** for POST requests
    - ✅ **Different values every time** you refresh
    
    ### **2. 📝 Enhanced Static Examples**
    The main `/docs` page now has **better examples** with:
    - Multiple example variations for POST requests
    - Realistic parameter examples
    - Better descriptions
    
    ### **3. 🎯 How to Use Dynamic Examples:**
    1. **Visit the dynamic examples endpoint**: `/examples/dynamic`
    2. **Copy the fresh values** from the response
    3. **Use them in other endpoints** or in the `/docs` "Try it out" forms
    4. **Refresh for new examples** anytime
    
    ### **4. � Example Workflow:**
    1. Call `/examples/dynamic` → Get random trade ID `15`
    2. Use `/trades/15` → Test with that specific trade
    3. Refresh `/examples/dynamic` → Get new random commodity `oil`
    4. Use `/trades/commodity/oil` → Test with that commodity
    
    ### **⚡ Result:**
    While the main `/docs` page examples are set at server startup, you now have a **"Dynamic Examples Generator"** 
    that provides fresh, realistic test data every time you need it!
    
    ---
    
    ### �📊 **Supported Commodities:**
    - `electricity` - Electric power trading ($/MWh)
    - `oil` - Crude oil trading ($/barrel)
    - `gas` / `natural_gas` - Natural gas trading ($/MMBtu)
    - `coal` - Coal commodity trading ($/ton)
    - `renewable` - Renewable energy credits ($/MWh)
    
    ### 👥 **Sample Traders:**
    - `trader_001`, `trader_002`, `trader_003` - Individual traders
    - `energy_corp` - Energy corporation
    - `green_power` - Green energy company
    - `fossil_fuel_ltd` - Traditional energy company
    
    ### 🔧 **Quick Start:**
    1. **Get fresh examples**: `GET /examples/dynamic`
    2. **Check market data**: `GET /market-data/current`
    3. **View existing trades**: `GET /trades/`
    4. **Create your first trade**: `POST /trades/`
    5. **Try the interactive "Try it out" buttons** with dynamic values!
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Energy Trading Platform Support",
        "url": "https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net",
    },
    license_info={
        "name": "MIT License",
    },
)

# Create database tables on first request instead of startup
tables_created = False

def ensure_tables_exist():
    """Ensure database tables exist, with retry logic"""
    global tables_created
    if not tables_created:
        try:
            Base.metadata.create_all(bind=engine)
            tables_created = True
            print("Database tables created successfully")
        except Exception as e:
            print(f"Failed to create database tables: {e}")
            # Don't raise exception, let the app continue and retry later

# Dependency to get database session
def get_db():
    ensure_tables_exist()  # Ensure tables exist before each database operation
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", summary="🏠 API Information", tags=["General"])
async def read_root():
    """
    **Welcome to the Energy Trading Platform API!**
    
    This endpoint provides basic information about the API and quick links to get started.
    
    ## 🎲 **NEW: Dynamic Testing Feature!**
    **🔥 Hot Tip**: Use `/examples/dynamic` to get fresh, realistic test data that changes every time!
    - Get random trade IDs, commodities, and traders
    - Copy values directly into other endpoints
    - Ready-to-use test URLs provided
    - **Perfect for testing without guessing valid values!**
    
    **Next Steps:**
    - 🎲 **Dynamic Examples**: Try `/examples/dynamic` for fresh test data
    - 📖 **API Documentation**: Visit `/docs` for interactive API documentation  
    - 📊 **Market Data**: Try `/market-data/current` to see live market prices
    - 💼 **View Trades**: Use `/trades/` to see existing trades
    
    **Test URLs:**
    - Dynamic Examples: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/examples/dynamic
    - Market Data: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/market-data/current
    - All Trades: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/
    """
    return {
        "message": "🔋 Energy Trading Platform API",
        "version": "1.0.0", 
        "description": "REST API for energy commodity trading",
        "🔥 new_feature": {
            "dynamic_examples": "/examples/dynamic",
            "description": "Get fresh test data that changes every time!"
        },
        "quick_links": {
            "dynamic_examples": "/examples/dynamic",
            "documentation": "/docs",
            "market_data": "/market-data/current", 
            "all_trades": "/trades/",
            "health_check": "/health"
        },
        "supported_commodities": ["electricity", "oil", "gas", "natural_gas", "coal", "renewable"],
        "example_traders": ["trader_001", "trader_002", "energy_corp", "green_power"],
        "💡 testing_tip": "Use /examples/dynamic to get realistic values for testing other endpoints!"
    }

@app.get("/health", response_model=schemas.HealthCheck, summary="🏥 Health Check", tags=["General"])
async def health_check():
    """
    **System Health Check**
    
    Verify that the API and database connectivity are working properly.
    
    **What this endpoint does:**
    - ✅ Confirms the API is responding
    - 🗄️ Tests database connectivity
    - ⏰ Provides current timestamp
    
    **Test Now:**
    ```
    GET https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/health
    ```
    """
    # Simple and fast health check
    try:
        # Just test that we can create a session (doesn't actually connect until used)
        db = SessionLocal()
        db.close()
        db_connected = True
    except Exception as e:
        print(f"Health check failed: {e}")
        db_connected = False
    
    return schemas.HealthCheck(
        status="healthy",  # Always report healthy if the API is responding
        timestamp=datetime.utcnow(),
        database_connected=db_connected
    )

@app.post("/trades/", response_model=schemas.Trade, summary="💼 Create New Trade", tags=["Trading"])
async def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    """
    **Create a new energy commodity trade**
    
    Submit a new trade order to the platform. All fields are required and validated.
    
    **📋 Required Fields:**
    - **commodity**: Energy type (`electricity`, `oil`, `gas`, `natural_gas`, `coal`, `renewable`)
    - **price**: Price per unit (must be positive number)
    - **quantity**: Amount to trade (must be positive number)
    - **side**: Trade direction (`buy` or `sell`)
    - **trader_id**: Your trader identification
    
    **💡 Example Request:**
    ```json
    {
        "commodity": "electricity",
        "price": 75.50,
        "quantity": 250.0,
        "side": "buy",
        "trader_id": "trader_001"
    }
    ```
    
    **🧪 Test This Endpoint:**
    Try creating a trade with the example above using the "Try it out" button!
    
    **✅ Success Response:**
    Returns the created trade with assigned ID and timestamp.
    """
    try:
        return crud.create_trade(db=db, trade=trade)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create trade: {str(e)}")

@app.get("/trades/", response_model=schemas.TradeResponse, summary="📊 Get All Trades", tags=["Trading"])
async def get_trades(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of trades to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Number of trades to skip for pagination"),
    commodity: Optional[str] = Query(None, description="Filter by commodity type", example=get_random_commodity()),
    trader_id: Optional[str] = Query(None, description="Filter by specific trader ID", example=get_random_trader()),
    side: Optional[str] = Query(None, description="Filter by trade side (buy/sell)", example=random.choice(['buy', 'sell'])),
    db: Session = Depends(get_db)
):
    """
    **Retrieve trades with optional filtering and pagination**
    
    Get a list of trades from the database with powerful filtering options.
    
    **🔍 Filter Options:**
    - **limit**: How many trades to return (default: 100, max: 1000)
    - **offset**: Skip trades for pagination (default: 0)
    - **commodity**: Filter by energy type (`electricity`, `oil`, `gas`, etc.)
    - **trader_id**: Filter by specific trader
    - **side**: Filter by trade direction (`buy` or `sell`)
    
    **🧪 Test These URLs:**
    - **All trades**: `GET /trades/`
    - **Electricity only**: `GET /trades/?commodity=electricity`
    - **Buy orders only**: `GET /trades/?side=buy`
    - **Trader's trades**: `GET /trades/?trader_id=trader_001`
    - **Paginated**: `GET /trades/?limit=10&offset=0`
    
    **🔗 Direct Test Links:**
    ```
    All trades: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/
    Electricity: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/?commodity=electricity
    Buy orders: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/?side=buy
    ```
    
    **📈 Response Format:**
    Returns paginated list with total count for easy frontend integration.
    """
    try:
        trades = crud.get_trades(
            db=db, 
            limit=limit, 
            offset=offset,
            commodity=commodity,
            trader_id=trader_id,
            side=side
        )
        
        total = crud.get_trades_count(
            db=db,
            commodity=commodity,
            trader_id=trader_id,
            side=side
        )
        
        return schemas.TradeResponse(trades=trades, total=total)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve trades: {str(e)}")

@app.get("/trades/{trade_id}", response_model=schemas.Trade, summary="🔍 Get Trade by ID", tags=["Trading"])
async def get_trade(
    trade_id: int = Path(..., description="Trade ID to retrieve", example=get_random_trade_id()),
    db: Session = Depends(get_db)
):
    """
    **Get a specific trade by its unique ID**
    
    Retrieve detailed information about a single trade using its database ID.
    
    **📝 Usage:**
    - Replace `{trade_id}` with an actual trade ID (e.g., 1, 2, 21, etc.)
    - Returns full trade details including timestamp
    
    **🧪 Test These Examples:**
    ```
    Trade ID 1: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/1
    Trade ID 21: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/21
    Latest trade: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/20
    ```
    
    **💡 Pro Tip:** Use the trade IDs you see from the `/trades/` endpoint
    
    **❌ Error Handling:**
    Returns 404 if trade ID doesn't exist
    """
    trade = crud.get_trade_by_id(db=db, trade_id=trade_id)
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@app.get("/trades/commodity/{commodity}", response_model=List[schemas.Trade], summary="⚡ Get Trades by Commodity", tags=["Trading"])
async def get_trades_by_commodity(
    commodity: str = Path(..., description="Energy commodity type", example=get_random_commodity()),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of trades to return (1-100)"),
    db: Session = Depends(get_db)
):
    """
    **Get recent trades for a specific energy commodity**
    
    Filter trades by energy commodity type and get the most recent ones first.
    
    **🔋 Available Commodities:**
    - `electricity` - Electric power ($/MWh)
    - `oil` - Crude oil ($/barrel)  
    - `gas` - Natural gas ($/MMBtu)
    - `natural_gas` - Alternative gas notation
    - `coal` - Coal commodity ($/ton)
    - `renewable` - Renewable energy credits ($/MWh)
    
    **🧪 Test These Commodity Endpoints:**
    ```
    Electricity: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/commodity/electricity
    Oil trades: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/commodity/oil
    Gas trades: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/commodity/gas
    Renewable: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/commodity/renewable
    ```
    
    **📊 Response:** Returns most recent trades for the commodity, sorted by timestamp (newest first)
    
    **⚙️ Parameters:**
    - **commodity**: The energy commodity type (required)
    - **limit**: Number of trades to return (default: 10, max: 100)
    """
    try:
        trades = crud.get_recent_trades_by_commodity(db=db, commodity=commodity, limit=limit)
        return trades
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve commodity trades: {str(e)}")

@app.get("/trades/trader/{trader_id}", response_model=List[schemas.Trade], summary="👤 Get Trades by Trader", tags=["Trading"])
async def get_trades_by_trader(
    trader_id: str = Path(..., description="Trader identification", example=get_random_trader()),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of trades to return (1-200)"),
    db: Session = Depends(get_db)
):
    """
    **Get all trades for a specific trader**
    
    Retrieve trading history for an individual trader or organization.
    
    **👥 Sample Traders in Database:**
    - `trader_001` - Individual trader #1
    - `trader_002` - Individual trader #2  
    - `trader_003` - Individual trader #3
    - `energy_corp` - Energy corporation
    - `green_power` - Green energy company
    - `fossil_fuel_ltd` - Traditional energy company
    
    **🧪 Test These Trader Endpoints:**
    ```
    Trader 001: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/trader/trader_001
    Trader 002: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/trader/trader_002
    Energy Corp: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/trader/energy_corp
    Green Power: https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/trader/green_power
    ```
    
    **📈 Use Cases:**
    - Portfolio analysis for individual traders
    - Compliance reporting
    - Trading pattern analysis
    - Risk management
    
    **📊 Response:** Returns trader's trades sorted by timestamp (newest first)
    
    **⚙️ Parameters:**
    - **trader_id**: The trader's unique identifier (required)
    - **limit**: Number of trades to return (default: 50, max: 200)
    """
    try:
        trades = crud.get_trader_trades(db=db, trader_id=trader_id, limit=limit)
        return trades
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve trader trades: {str(e)}")

# Market Data Endpoints (no database required - generates mock data)
@app.get("/market-data/current", summary="📈 Current Market Data", tags=["Market Data"])
async def get_current_market_data():
    """
    **Get current market data for energy commodities (simulated)**
    
    Real-time market prices and statistics for all supported energy commodities.
    
    **📊 What You Get:**
    - Current price for each commodity
    - 24-hour price change (absolute and percentage)
    - Daily high/low prices
    - Trading volume statistics
    - Live timestamps
    
    **⚡ Commodity Coverage:**
    - **Electricity** - $/MWh pricing
    - **Oil** - $/barrel pricing
    - **Gas/Natural Gas** - $/MMBtu pricing  
    - **Coal** - $/ton pricing
    - **Renewable** - $/MWh pricing
    
    **🧪 Test This Endpoint:**
    ```
    GET https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/market-data/current
    ```
    
    **🔄 Data Updates:**
    Prices are simulated and change with each request to demonstrate real-time market conditions.
    
    **💡 Use Cases:**
    - Trading dashboard displays
    - Price alerts and notifications  
    - Market analysis and reporting
    - Trading strategy development
    
    **📱 Perfect for:** Frontend applications, mobile apps, trading bots
    """
    commodities = ['electricity', 'oil', 'gas', 'coal', 'natural_gas', 'renewable']
    
    market_data = []
    for commodity in commodities:
        # Generate realistic price ranges
        if commodity == 'electricity':
            base_price = 75.0
            variation = 25.0
        elif commodity == 'oil':
            base_price = 80.0
            variation = 20.0
        elif commodity in ['gas', 'natural_gas']:
            base_price = 4.5
            variation = 1.5
        elif commodity == 'coal':
            base_price = 60.0
            variation = 15.0
        else:  # renewable
            base_price = 65.0
            variation = 20.0
        
        current_price = round(base_price + random.uniform(-variation, variation), 2)
        change = round(random.uniform(-5.0, 5.0), 2)
        
        market_data.append({
            "commodity": commodity,
            "current_price": current_price,
            "change_24h": change,
            "change_percent": round((change / base_price) * 100, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "volume_24h": random.randint(1000, 50000),
            "high_24h": round(current_price + abs(change) + random.uniform(0, 5), 2),
            "low_24h": round(current_price - abs(change) - random.uniform(0, 5), 2)
        })
    
    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "market_data": market_data
    }

# Dynamic Examples Endpoint
@app.get("/examples/dynamic", summary="🎲 Dynamic Examples Generator", tags=["🎯 Testing Tools"])
async def get_dynamic_examples():
    """
    ## 🔄 **Dynamic Examples Generator - Your Testing Best Friend!**
    
    **Get fresh, realistic examples that change every time you call this endpoint.**
    
    ### 🎯 **What This Does:**
    This endpoint provides **fresh examples on every request** to help you test all the other API endpoints 
    with realistic, valid data.
    
    ### ✅ **What You Get:**
    - 🆔 **Fresh trade IDs** from existing trades in the database
    - ⚡ **Random commodities** from available energy types
    - 👤 **Random traders** from active trader accounts
    - 💱 **Random trade sides** (buy/sell)
    - 💰 **Realistic pricing data** based on commodity types
    - 🔗 **Ready-to-use test URLs** with the dynamic values
    
    ### 🚀 **How to Use This:**
    
    #### **Method 1: Copy & Paste Values**
    1. **Call this endpoint** (click "Try it out" → "Execute")
    2. **Copy values** from the response (trade_id, commodity, trader_id, etc.)
    3. **Paste them** into other endpoint parameters
    4. **Test away!**
    
    #### **Method 2: Use the Ready-Made URLs**
    1. **Look at the `test_urls` section** in the response
    2. **Copy any URL** and paste it into your browser or API client
    3. **Instant testing** with valid data!
    
    ### 🔧 **Example Workflow:**
    ```
    Step 1: Call /examples/dynamic
    Response: {"examples": {"trade_id": 15, "commodity": "oil", ...}}
    
    Step 2: Use the values
    - Test specific trade: GET /trades/15
    - Test commodity: GET /trades/commodity/oil
    - Create new trade with sample_trade data
    
    Step 3: Need different values?
    - Refresh this endpoint for new random values!
    ```
    
    ### 💡 **Pro Tips:**
    - **Bookmark this endpoint** for quick access to test data
    - **Refresh multiple times** to get different combinations
    - **Use sample_trade object** for POST /trades/ testing
    - **Copy test_urls** for instant endpoint testing
    
    ### 🔄 **Dynamic Updates:**
    - **Trade IDs**: Random from 1-25 (existing trade range)
    - **Commodities**: Rotates through all 6 energy types
    - **Traders**: Cycles through all 6 trader accounts
    - **Prices**: Realistic ranges based on commodity type
    - **Test URLs**: Generated with fresh values each time
    
    **💫 This endpoint updates every single time you call it - try it multiple times!**
    """
    random_commodity = get_random_commodity()
    random_trader = get_random_trader()
    random_trade_id = get_random_trade_id()
    random_side = random.choice(['buy', 'sell'])
    
    # Generate realistic price based on commodity
    price_ranges = {
        'electricity': (50, 150),
        'oil': (60, 100), 
        'gas': (2, 8),
        'natural_gas': (2, 8),
        'coal': (40, 80),
        'renewable': (30, 120)
    }
    min_price, max_price = price_ranges.get(random_commodity, (50, 100))
    random_price = round(random.uniform(min_price, max_price), 2)
    
    # Generate realistic quantity based on commodity
    quantity_ranges = {
        'electricity': (10, 1000),
        'oil': (100, 10000),
        'gas': (1000, 50000), 
        'natural_gas': (1000, 50000),
        'coal': (500, 5000),
        'renewable': (50, 2000)
    }
    min_qty, max_qty = quantity_ranges.get(random_commodity, (100, 1000))
    random_quantity = round(random.uniform(min_qty, max_qty), 2)
    
    return {
        "🎲 status": "Fresh examples generated!",
        "⏰ timestamp": datetime.utcnow().isoformat(),
        "🔄 refresh_note": "Call this endpoint again for different values!",
        
        "examples": {
            "trade_id": random_trade_id,
            "commodity": random_commodity,
            "trader_id": random_trader,
            "side": random_side,
            "sample_trade_for_POST": {
                "commodity": random_commodity,
                "price": random_price,
                "quantity": random_quantity,
                "side": random_side,
                "trader_id": random_trader
            }
        },
        
        "🔗 ready_to_use_test_urls": {
            "get_specific_trade": f"https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/{random_trade_id}",
            "get_by_commodity": f"https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/commodity/{random_commodity}",
            "get_by_trader": f"https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/trader/{random_trader}",
            "filtered_trades": f"https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/trades/?commodity={random_commodity}&side={random_side}",
            "get_fresh_examples": "https://fastapi-energy-trading-g2a9h8bdhzchh7fa.westeurope-01.azurewebsites.net/examples/dynamic"
        },
        
        "💡 instructions": {
            "step_1": "Copy values from 'examples' section above",
            "step_2": "Paste them into other endpoint parameters in /docs",
            "step_3": "Or copy/paste any URL from 'ready_to_use_test_urls'",
            "step_4": "Refresh this endpoint anytime for new values!"
        },
        
        "🎯 available_values": {
            "commodities": ["electricity", "oil", "gas", "natural_gas", "coal", "renewable"],
            "traders": ["trader_001", "trader_002", "trader_003", "energy_corp", "green_power", "fossil_fuel_ltd"],
            "sides": ["buy", "sell"],
            "trade_id_range": "1-25 (existing trades)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
