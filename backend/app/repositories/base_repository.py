"""
Generic base repository.

Backend coding standard: "Database access belongs only inside Repositories."
This generic class exists so every entity-specific repository (User now;
Asset, Booking, MaintenanceTicket, etc. later) follows the exact same
pattern instead of each engineer improvising their own CRUD shape.

Repositories NEVER contain business logic — no validation, no permission
checks, no "is this transition allowed." That all lives in the Service
layer. A repository only knows how to talk to the database.
"""

from typing import Generic, TypeVar, Type, Optional
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        self.db.commit()
        self.db.refresh(obj)
        return obj