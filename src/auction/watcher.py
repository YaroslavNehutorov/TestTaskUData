import asyncio
from datetime import datetime, timezone
from sqlalchemy import select

from src.database import AsyncSessionLocal
from src.lots.models import Lot, LotStatus
from src.websocket.manager import manager


async def auction_watcher():
    while True:
        ended_lot_ids = []
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Lot).where(Lot.status == LotStatus.running)
            )
            lots = result.scalars().all()

            for lot in lots:
                if lot.end_time <= datetime.now(timezone.utc):
                    lot.status = LotStatus.ended
                    ended_lot_ids.append(lot.id)

            await db.commit()

        for lot_id in ended_lot_ids:
            await manager.broadcast(
                lot_id,
                {"type": "lot_ended", "lot_id": lot_id},
            )

        await asyncio.sleep(5)
