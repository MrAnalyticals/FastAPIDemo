from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Literal

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
    """Schema for creating a new trade"""
    pass

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
