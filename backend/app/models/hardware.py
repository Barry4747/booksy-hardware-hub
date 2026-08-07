import enum
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class HardwareStatus(str, enum.Enum):   
    AVAILABLE = "Available"
    IN_USE = "In Use"
    REPAIR = "Repair"

class Hardware(Base):
    __tablename__ = "hardware"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    purchase_date = Column(Date, nullable=True)
    status = Column(Enum(HardwareStatus), default=HardwareStatus.AVAILABLE, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

    rentals = relationship("Rental", back_populates="hardware", cascade="all, delete-orphan")
