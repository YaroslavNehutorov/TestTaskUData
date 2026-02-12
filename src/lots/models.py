from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    Enum as SqlEnum,
    Numeric,
    DateTime,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.models import Base
from src.lots.enums import LotStatus



class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    start_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[LotStatus] = mapped_column(
        SqlEnum(LotStatus, name="lot_status"),
        default=LotStatus.running,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    bids: Mapped[list["Bid"]] = relationship(
        back_populates="lot",
        cascade="all, delete-orphan",
    )

    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    bidder: Mapped[str] = mapped_column(String(255), nullable=False)

    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    lot: Mapped["Lot"] = relationship(back_populates="bids")
