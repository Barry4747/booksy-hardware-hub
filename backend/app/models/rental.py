from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    hardware_id = Column(Integer, ForeignKey("hardware.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rented_at = Column(DateTime, default=func.now(), nullable=False)
    returned_at = Column(DateTime, nullable=True)

    hardware = relationship("Hardware", back_populates="rentals")
    user = relationship("User", back_populates="rentals")
