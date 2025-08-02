from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Literal
import random

# Dynamic example generators
def get_random_commodity():
    return random.choice(['electricity', 'oil', 'gas', 'coal', 'natural_gas', 'renewable'])

def get_random_trader():
    return random.choice(['trader_001', 'trader_002', 'trader_003', 'energy_corp', 'green_power', 'fossil_fuel_ltd'])

def get_random_side():
    return random.choice(['buy', 'sell'])

def get_random_price(commodity):
    price_ranges = {
        'electricity': (50, 150),
        'oil': (60, 100),
        'gas': (2, 8),
        'natural_gas': (2, 8),
        'coal': (40, 80),
        'renewable': (30, 120)
    }
    min_price, max_price = price_ranges.get(commodity, (50, 100))
    return round(random.uniform(min_price, max_price), 2)

def get_random_quantity(commodity):
    quantity_ranges = {
        'electricity': (10, 1000),
        'oil': (100, 10000),
        'gas': (1000, 50000),
        'natural_gas': (1000, 50000),
        'coal': (500, 5000),
        'renewable': (50, 2000)
    }
    min_qty, max_qty = quantity_ranges.get(commodity, (100, 1000))
    return round(random.uniform(min_qty, max_qty), 2)

class TradeBase(BaseModel):
    """Base trade schema with common fields"""
    commodity: str = Field(..., min_length=1, max_length=50, description="Energy commodity type (e.g., electricity, oil, gas)")
    price: float = Field(..., gt=0, description="Price per unit (must be positive)")
    quantity: float = Field(..., gt=0, description="Quantity to trade (must be positive)")
    side: Literal["buy", "sell"] = Field(..., description="Trade side: buy or sell")
    trader_id: str = Field(..., min_length=1, max_length=100, description="Trader identification")
    
    @validator('commodity')
    def validate_commodity(cls, v):
        """Validate commodity type"""
        allowed_commodities = ['electricity', 'oil', 'gas', 'coal', 'natural_gas', 'renewable']
        if v.lower() not in allowed_commodities:
            raise ValueError(f'Commodity must be one of: {", ".join(allowed_commodities)}')
        return v.lower()
    
    @validator('trader_id')
    def validate_trader_id(cls, v):
        """Validate trader ID format"""
        if not v.isalnum() and '_' not in v and '-' not in v:
            raise ValueError('Trader ID must contain only alphanumeric characters, underscores, or hyphens')
        return v

class TradeCreate(TradeBase):
    """Schema for creating a new trade with dynamic examples"""
    
    class Config:
        schema_extra = {
            "examples": [
                {
                    "commodity": get_random_commodity(),
                    "price": get_random_price(get_random_commodity()),
                    "quantity": get_random_quantity(get_random_commodity()),
                    "side": get_random_side(),
                    "trader_id": get_random_trader()
                },
                {
                    "commodity": "electricity",
                    "price": 85.75,
                    "quantity": 500.0,
                    "side": "buy",
                    "trader_id": "energy_corp"
                },
                {
                    "commodity": "oil",
                    "price": 78.50,
                    "quantity": 2500.0,
                    "side": "sell",
                    "trader_id": "fossil_fuel_ltd"
                },
                {
                    "commodity": "renewable",
                    "price": 65.25,
                    "quantity": 750.0,
                    "side": "buy",
                    "trader_id": "green_power"
                }
            ]
        }

class Trade(TradeBase):
    """Schema for trade response including database fields"""
    id: int = Field(..., description="Unique trade identifier")
    timestamp: datetime = Field(..., description="Trade execution timestamp")

    class Config:
        from_attributes = True  # Updated for Pydantic v2
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TradeResponse(BaseModel):
    """Response schema for multiple trades"""
    trades: list[Trade]
    total: int
    
class HealthCheck(BaseModel):
    """Health check response schema"""
    status: str
    timestamp: datetime
    database_connected: bool
