from typing import Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from app.models.rental import Rental

class RentalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Rental | None:
        return self.db.query(Rental).options(joinedload(Rental.hardware)).filter(Rental.id == id).first()

    def list(self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None, sort_by: str | None = None, sort_desc: bool = False) -> list[Rental]:
        query = self.db.query(Rental).options(joinedload(Rental.hardware))
        
        if filters:
            for key, value in filters.items():
                if hasattr(Rental, key) and value is not None:
                    query = query.filter(getattr(Rental, key) == value)
                    
        if sort_by and hasattr(Rental, sort_by):
            order_func = desc if sort_desc else asc
            query = query.order_by(order_func(getattr(Rental, sort_by)))
            
        return query.offset(skip).limit(limit).all()

    def create(self, **kwargs) -> Rental:
        rental = Rental(**kwargs)
        self.db.add(rental)
        self.db.flush()
        return rental

    def update(self, rental: Rental, updates: dict[str, Any]) -> Rental:
        for key, value in updates.items():
            if hasattr(rental, key):
                setattr(rental, key, value)
        self.db.flush()
        return rental

    def delete(self, rental: Rental) -> None:
        self.db.delete(rental)
        self.db.flush()
