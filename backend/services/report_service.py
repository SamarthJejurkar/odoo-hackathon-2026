"""Business logic for Reports & Analytics (Screen 9).

Pure read/aggregation — no repo writes exist for this feature and none
should be added here.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from repositories.report_repository import ReportRepository
from schemas.report import (
    AgingAsset,
    DepartmentUtilization,
    IdleAsset,
    MaintenanceDueAsset,
    MaintenanceFrequencyPoint,
    MostUsedAsset,
    ReportSummary,
)


class ReportService:
    def __init__(self, db: Session):
        self.repo = ReportRepository(db)

    def utilization_by_department(self) -> list[DepartmentUtilization]:
        result = []
        for name, total, allocated in self.repo.utilization_by_department():
            pct = round((allocated / total) * 100, 1) if total else 0.0
            result.append(
                DepartmentUtilization(
                    department_name=name,
                    total_assets=total,
                    allocated_assets=allocated,
                    utilization_pct=pct,
                )
            )
        return result

    def maintenance_frequency(self, months: int = 6) -> list[MaintenanceFrequencyPoint]:
        return [
            MaintenanceFrequencyPoint(month=month, count=count)
            for month, count in self.repo.maintenance_frequency(months)
        ]

    def most_used_assets(self, limit: int = 5, days: int = 30) -> list[MostUsedAsset]:
        return [
            MostUsedAsset(asset_id=aid, asset_tag=tag, name=name, usage_count=count)
            for aid, tag, name, count in self.repo.most_used_assets(limit, days)
        ]

    def idle_assets(self, min_days_idle: int = 30, limit: int = 10) -> list[IdleAsset]:
        assets = self.repo.available_assets()
        last_activity = self.repo.last_activity_per_asset()
        now = datetime.utcnow()

        results = []
        for asset in assets:
            last_seen = last_activity.get(asset.id, asset.created_at)
            if last_seen is None:
                continue
            # last_seen may be naive or aware depending on the column;
            # normalize to naive UTC for a simple subtraction.
            if last_seen.tzinfo is not None:
                last_seen = last_seen.replace(tzinfo=None)
            days_idle = (now - last_seen).days
            if days_idle >= min_days_idle:
                results.append(
                    IdleAsset(
                        asset_id=asset.id,
                        asset_tag=asset.asset_tag,
                        name=asset.name,
                        days_idle=days_idle,
                    )
                )

        results.sort(key=lambda a: a.days_idle, reverse=True)
        return results[:limit]

    def maintenance_due(self, limit: int = 10) -> list[MaintenanceDueAsset]:
        requests = self.repo.open_maintenance_requests()
        now = datetime.utcnow()
        result = []
        for req in requests[:limit]:
            created = req.created_at
            if created and created.tzinfo is not None:
                created = created.replace(tzinfo=None)
            days_open = (now - created).days if created else 0
            result.append(
                MaintenanceDueAsset(
                    asset_id=req.asset_id,
                    asset_tag=req.asset.asset_tag,
                    name=req.asset.name,
                    priority=req.priority.value,
                    status=req.status.value,
                    days_open=days_open,
                )
            )
        return result

    def aging_assets(self, years: int = 4, limit: int = 10) -> list[AgingAsset]:
        assets = self.repo.aging_assets(years)
        today = datetime.utcnow().date()
        result = []
        for asset in assets[:limit]:
            age_years = round((today - asset.acquisition_date).days / 365, 1)
            result.append(
                AgingAsset(
                    asset_id=asset.id,
                    asset_tag=asset.asset_tag,
                    name=asset.name,
                    acquisition_date=asset.acquisition_date,
                    age_years=age_years,
                )
            )
        return result

    def summary(self) -> ReportSummary:
        """Single call that feeds the entire Screen 9 layout in one round trip."""
        return ReportSummary(
            utilization_by_department=self.utilization_by_department(),
            maintenance_frequency=self.maintenance_frequency(),
            most_used_assets=self.most_used_assets(),
            idle_assets=self.idle_assets(),
            maintenance_due=self.maintenance_due(),
            aging_assets=self.aging_assets(),
        )