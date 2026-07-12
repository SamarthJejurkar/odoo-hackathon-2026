"""
User repository — DB access only, no business logic.

Note: built against UserDraft (app/models/user_draft.py). The day Tanmay's
real User model lands, this file changes its import and possibly its
field names — nothing outside this file (the service layer) needs to change.
"""

from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.user_draft import UserDraft


class UserRepository(BaseRepository[UserDraft]):
    def __init__(self, db: Session):
        super().__init__(UserDraft, db)

    def get_by_email(self, email: str) -> UserDraft | None:
        return self.db.query(UserDraft).filter(UserDraft.email == email).first()