from pydantic import BaseModel, Field
from decimal import Decimal


class LotCreate(BaseModel):
    title: str
    start_price: Decimal


class LotResponse(BaseModel):
    id: int
    title: str
    start_price: Decimal = Field(100.00)
    status: str

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class BidCreate(BaseModel):
    amount: float
    bidder: str


class BidResponse(BaseModel):
    id: int
    lot_id: int
    amount: float

    class Config:
        from_attributes = True
