from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.lots import service
from src.lots.models import Bid
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
    lots = await service.get_running_lots(db)
    if not lots:
        return []
    lot_ids = [lot.id for lot in lots]
    result = await db.execute(
        select(Bid.lot_id, func.max(Bid.amount).label("max_amount"))
        .where(Bid.lot_id.in_(lot_ids))
        .group_by(Bid.lot_id)
    )
    max_by_lot = {row.lot_id: float(row.max_amount) for row in result.all()}
    return [
        LotResponse(
            id=lot.id,
            title=lot.title,
            start_price=lot.start_price,
            status=lot.status,
            current_price=max_by_lot.get(lot.id) or float(lot.start_price),
        )
        for lot in lots
    ]


@router.post("/{lot_id}/bids", response_model=BidResponse)
async def create_bid(
    lot_id: int,
    bid_data: BidCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_bid(db, lot_id, bid_data.amount, bid_data.bidder)
