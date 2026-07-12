"""
Reports & Analytics router (Screen 9).

ACCESS CONTROL NOTE: gated to any authenticated user via get_current_user.
If reports should be Admin/Asset Manager only, swap this for whatever
require_role(...) does for multiple roles in dependencies/auth.py — I
didn't have that file's multi-role signature confirmed, so I kept this
permissive rather than guess and lock out a role that should have access.
"""
import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from schemas.report import ReportSummary
from services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


@router.get("/summary", response_model=ReportSummary,
            dependencies=[Depends(get_current_user)])
def get_report_summary(db: Session = Depends(get_db)):
    """Single call that feeds the whole Screen 9 dashboard."""
    return ReportService(db).summary()


@router.get("/export", dependencies=[Depends(get_current_user)])
def export_report_csv(db: Session = Depends(get_db)):
    """Screen 9 'Export report' button — flat CSV of the current summary."""
    summary = ReportService(db).summary()

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["Utilization by Department"])
    writer.writerow(["Department", "Total Assets", "Allocated", "Utilization %"])
    for row in summary.utilization_by_department:
        writer.writerow([row.department_name, row.total_assets, row.allocated_assets, row.utilization_pct])
    writer.writerow([])

    writer.writerow(["Maintenance Frequency"])
    writer.writerow(["Month", "Request Count"])
    for row in summary.maintenance_frequency:
        writer.writerow([row.month, row.count])
    writer.writerow([])

    writer.writerow(["Most Used Assets"])
    writer.writerow(["Asset Tag", "Name", "Usage Count (30d)"])
    for row in summary.most_used_assets:
        writer.writerow([row.asset_tag, row.name, row.usage_count])
    writer.writerow([])

    writer.writerow(["Idle Assets"])
    writer.writerow(["Asset Tag", "Name", "Days Idle"])
    for row in summary.idle_assets:
        writer.writerow([row.asset_tag, row.name, row.days_idle])
    writer.writerow([])

    writer.writerow(["Assets Due for Maintenance (open requests)"])
    writer.writerow(["Asset Tag", "Name", "Priority", "Status", "Days Open"])
    for row in summary.maintenance_due:
        writer.writerow([row.asset_tag, row.name, row.priority, row.status, row.days_open])
    writer.writerow([])

    writer.writerow(["Assets Nearing Retirement"])
    writer.writerow(["Asset Tag", "Name", "Acquisition Date", "Age (years)"])
    for row in summary.aging_assets:
        writer.writerow([row.asset_tag, row.name, row.acquisition_date, row.age_years])

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=assetflow_report.csv"},
    )