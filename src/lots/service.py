from datetime import datetime, timedelta

from src.lots.models import Lot, LotStatus, Bid
from src.lots.schemas import LotCreate
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.websocket.manager import manager


async def create_lot(db: AsyncSession, lot_data: LotCreate):
    lot = Lot(
        title=lot_data.title,
        start_price=lot_data.start_price,
        status=LotStatus.running.value,
        end_time=datetime.now() + timedelta(minutes=5)

    )

    db.add(lot)
    await db.commit()
    await db.refresh(lot)

    return lot


async def get_running_lots(db: AsyncSession):
    result = await db.execute(
        select(Lot).where(Lot.status == LotStatus.running.value)
    )
    return result.scalars().all()

from datetime import datetime, timedelta
from sqlalchemy import select, func
from fastapi import HTTPException


async def create_bid(db: AsyncSession, lot_id: int, amount: float, bidder: str):
    result = await db.execute(
        select(Lot).where(Lot.id == lot_id)
    )
    lot = result.scalar_one_or_none()

    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    if lot.status != LotStatus.running:
        raise HTTPException(status_code=400, detail="Lot is not running")

    if lot.end_time <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Auction ended")

    result = await db.execute(
        select(func.max(Bid.amount)).where(Bid.lot_id == lot_id)
    )
    max_bid = result.scalar()

    current_price = max_bid if max_bid else lot.start_price

    if amount <= current_price:
        raise HTTPException(
            status_code=400,
            detail="Bid must be greater than current price"
        )

    bid = Bid(
        lot_id=lot_id,
        amount=amount,
        bidder=bidder
    )

    db.add(bid)

    remaining_time = (lot.end_time - datetime.utcnow()).total_seconds()

    extended = False

    if remaining_time <= 30:
        lot.end_time += timedelta(seconds=60)
        extended = True

    await db.commit()
    await db.refresh(bid)

    await manager.broadcast(
        lot_id,
        {
            "type": "bid_placed",
            "lot_id": lot_id,
            "bidder": bidder,
            "amount": amount
        }
    )

    if extended:
        await manager.broadcast(
            lot_id,
            {
                "type": "time_extended",
                "lot_id": lot_id,
                "new_end_time": lot.end_time.isoformat()
            }
        )

    return bid


