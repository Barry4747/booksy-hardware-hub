import enum
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base

class RentalStatus(str, enum.Enum):
    ACTIVE = "Active"
    RETURNED = "Returned"

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    hardware_id = Column(Integer, ForeignKey("hardware.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rented_at = Column(DateTime, default=func.now(), nullable=False)
    returned_at = Column(DateTime, nullable=True)
    status = Column(Enum(RentalStatus), default=RentalStatus.ACTIVE, nullable=False)

    hardware = relationship("Hardware", back_populates="rentals")
    user = relationship("User", back_populates="rentals")
