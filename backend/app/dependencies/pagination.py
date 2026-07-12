"""
Reusable pagination dependency.

Every list endpoint across every module (Assets, Employees, Bookings,
Maintenance tickets, Audit logs, ...) needs the same page/page_size/sort
handling. Defining it once here means no engineer re-invents (or
subtly diverges on) pagination semantics.

Usage in a router:

    @router.get("/assets")
    def list_assets(pagination: PaginationParams = Depends(get_pagination_params)):
        ...
"""

from dataclasses import dataclass
from fastapi import Query

# NOTE: Tanmay's current Settings class (app/core/config.py) doesn't yet
# expose DEFAULT_PAGE_SIZE / MAX_PAGE_SIZE. Rather than reach into a field
# that doesn't exist, these are plain constants for now. If we want these
# configurable per-environment later, that's an additive field to propose
# to Tanmay (never a rename of what's already there).
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@dataclass
class PaginationParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_pagination_params(
    page: int = Query(1, ge=1, description="1-indexed page number"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, description="Items per page"),
) -> PaginationParams:
    # Cap page_size defensively so a client can't request page_size=100000
    # and force a full table scan / huge payload.
    if page_size > MAX_PAGE_SIZE:
        page_size = MAX_PAGE_SIZE
    return PaginationParams(page=page, page_size=page_size)
