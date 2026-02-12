import asyncio
from datetime import datetime
from sqlalchemy import select

from src.database import AsyncSessionLocal
from src.lots.models import Lot, LotStatus


async def auction_watcher():
    while True:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Lot).where(Lot.status == LotStatus.running)
            )
            lots = result.scalars().all()

            for lot in lots:
                if lot.end_time <= datetime.utcnow():
                    lot.status = LotStatus.ended

            await db.commit()

        await asyncio.sleep(5)
