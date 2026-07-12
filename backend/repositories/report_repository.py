"""Repository layer for Reports & Analytics — raw DB queries only.

No writes here, ever — this whole feature is read-only aggregation
over existing tables (Asset, MaintenanceRequest, Booking,
AssetAllocation, Department). No new table required.
"""
from datetime import datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from models.allocation import AssetAllocation
from models.asset import Asset
from models.booking import Booking
from models.department import Department
from models.enums import AssetStatusEnum, MaintenanceStatusEnum
from models.maintenance import MaintenanceRequest


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Screen 9: "Utilization by department" bar chart ---
    def utilization_by_department(self):
        """One row per department: total assets vs. currently allocated."""
        rows = self.db.execute(
            select(
                Department.name,
                func.count(Asset.id),
                func.count(
                    case((Asset.status == AssetStatusEnum.ALLOCATED, 1), else_=None)
                ),
            )
            .select_from(Department)
            .outerjoin(Asset, Asset.department_id == Department.id)
            .group_by(Department.name)
            .order_by(Department.name)
        ).all()
        return rows

    # --- Screen 9: "Maintenance Frequency" line chart ---
    def maintenance_frequency(self, months: int = 6):
        cutoff = datetime.utcnow() - timedelta(days=30 * months)
        rows = self.db.execute(
            select(
                func.to_char(MaintenanceRequest.created_at, "YYYY-MM"),
                func.count(MaintenanceRequest.id),
            )
            .where(MaintenanceRequest.created_at >= cutoff)
            .group_by(func.to_char(MaintenanceRequest.created_at, "YYYY-MM"))
            .order_by(func.to_char(MaintenanceRequest.created_at, "YYYY-MM"))
        ).all()
        return rows

    # --- Screen 9: "Most used assets" ---
    def most_used_assets(self, limit: int = 5, days: int = 30):
        cutoff = datetime.utcnow() - timedelta(days=days)
        rows = self.db.execute(
            select(
                Asset.id,
                Asset.asset_tag,
                Asset.name,
                func.count(Booking.id).label("usage_count"),
            )
            .join(Booking, Booking.asset_id == Asset.id)
            .where(Booking.start_time >= cutoff)
            .group_by(Asset.id, Asset.asset_tag, Asset.name)
            .order_by(func.count(Booking.id).desc())
            .limit(limit)
        ).all()
        return rows

    # --- Screen 9: "Idle assets" — supports the derived days_idle calc ---
    def available_assets(self):
        return list(
            self.db.scalars(
                select(Asset).where(Asset.status == AssetStatusEnum.AVAILABLE)
            ).all()
        )

    def last_activity_per_asset(self) -> dict[int, datetime]:
        """asset_id -> most recent of (last booking start, last allocation).
        Combined in Python rather than a single SQL UNION to keep this
        readable under time pressure — table sizes here are hackathon-scale.
        """
        combined: dict[int, datetime] = {}

        for asset_id, ts in self.db.execute(
            select(Booking.asset_id, func.max(Booking.start_time)).group_by(Booking.asset_id)
        ).all():
            if ts is not None:
                combined[asset_id] = ts

        for asset_id, ts in self.db.execute(
            select(AssetAllocation.asset_id, func.max(AssetAllocation.allocated_at)).group_by(
                AssetAllocation.asset_id
            )
        ).all():
            if ts is not None and (asset_id not in combined or ts > combined[asset_id]):
                combined[asset_id] = ts

        return combined

    # --- Screen 9: "Assets due for maintenance" (see schema docstring re: proxy) ---
    def open_maintenance_requests(self):
        return list(
            self.db.scalars(
                select(MaintenanceRequest)
                .where(MaintenanceRequest.status != MaintenanceStatusEnum.RESOLVED)
                .order_by(MaintenanceRequest.priority.desc(), MaintenanceRequest.created_at.asc())
            ).all()
        )

    # --- Screen 9: "...nearing retirement" ---
    def aging_assets(self, years: int = 4):
        cutoff = datetime.utcnow().date() - timedelta(days=365 * years)
        return list(
            self.db.scalars(
                select(Asset).where(
                    Asset.acquisition_date.is_not(None),
                    Asset.acquisition_date <= cutoff,
                    Asset.status.notin_(
                        [AssetStatusEnum.RETIRED, AssetStatusEnum.DISPOSED]
                    ),
                )
            ).all()
        )