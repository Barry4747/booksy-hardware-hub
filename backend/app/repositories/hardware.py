from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models.hardware import Hardware

class HardwareRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Hardware | None:
        return self.db.query(Hardware).filter(Hardware.id == id).first()

    def list(self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None, search: str | None = None, sort_by: str | None = None, sort_desc: bool = False) -> list[Hardware]:
        from sqlalchemy import or_
        query = self.db.query(Hardware)
        
        if filters:
            for key, value in filters.items():
                if hasattr(Hardware, key) and value is not None:
                    query = query.filter(getattr(Hardware, key) == value)
                    
        if search:
            query = query.filter(or_(
                Hardware.name.ilike(f'%{search}%'),
                Hardware.serial_number.ilike(f'%{search}%')
            ))
                    
        if sort_by and hasattr(Hardware, sort_by):
            order_func = desc if sort_desc else asc
            query = query.order_by(order_func(getattr(Hardware, sort_by)))
            
        return query.offset(skip).limit(limit).all()

    def create(self, **kwargs) -> Hardware:
        hardware = Hardware(**kwargs)
        self.db.add(hardware)
        self.db.flush()
        return hardware

    def update(self, hardware: Hardware, updates: dict[str, Any]) -> Hardware:
        for key, value in updates.items():
            if hasattr(hardware, key):
                setattr(hardware, key, value)
        self.db.flush()
        return hardware

    def delete(self, hardware: Hardware) -> None:
        self.db.delete(hardware)
        self.db.flush()
