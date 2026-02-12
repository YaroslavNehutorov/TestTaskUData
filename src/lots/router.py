from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.lots import service
from src.lots.schemas import LotCreate, LotResponse, BidCreate, BidResponse

router = APIRouter()


@router.post("", response_model=LotResponse)
async def create_lot(
    lot_data: LotCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_lot(db, lot_data)

@router.get("", response_model=list[LotResponse])
async def get_running_lots(db: AsyncSession = Depends(get_db)):
    return await service.get_running_lots(db)


@router.post("/{lot_id}/bids", response_model=BidResponse)
async def create_bid(
    lot_id: int,
    bid_data: BidCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_bid(
        db,
        lot_id,
        bid_data.amount
    )
