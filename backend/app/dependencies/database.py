"""
Database session dependency.

Deliberately placed in app/dependencies/ rather than app/database/database.py:
`database.py` is Tanmay's file (engine/session/Base construction — the
Database Architect's territory). Wiring that session into FastAPI's
dependency-injection system is a backend/DI concern, so it lives here
instead of adding to his file.

Every router/service that needs DB access takes `db: Session = Depends(get_db)`.
"""

from typing import Generator
from sqlalchemy.orm import Session
from app.database.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
