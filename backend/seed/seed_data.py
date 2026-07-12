"""
Seed data for local development / demo.

INSERT ORDER MATTERS here more than in most seed scripts, because of two
structural dependencies baked into the schema on purpose:

1. Departments and Users are circularly linked (Department.department_head_id
   -> Users.id, User.department_id -> Departments.id). Resolution: insert
   departments WITHOUT a head, insert users WITH a department, then UPDATE
   departments to set department_head_id. This is exactly the two-phase
   pattern any real onboarding flow (Admin promotes an employee to Dept
   Head) will also follow - the seed script isn't a hack, it mirrors the
   real workflow.

2. AssetAllocation's partial unique index (one active allocation per
   asset) means seed data for "already allocated" demo assets must each
   get exactly one active allocation row - trying to seed two active
   allocations for the same asset will raise IntegrityError by design.

Run with: python -m app.seed.seed_data
"""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from database.database import SessionLocal
from models import (
    Asset,
    AssetAllocation,
    AssetCategory,
    Booking,
    Department,
    MaintenanceRequest,
    User,
)
from models.enums import (
    ActiveStatusEnum,
    AllocationStatusEnum,
    AssetConditionEnum,
    AssetStatusEnum,
    BookingStatusEnum,
    MaintenancePriorityEnum,
    MaintenanceStatusEnum,
    RoleEnum,
)


def seed(session: Session) -> None:
    # --- Phase 1: departments, no head yet (breaks the circular dependency) ---
    engineering = Department(name="Engineering", code="ENG", status=ActiveStatusEnum.ACTIVE)
    operations = Department(name="Operations", code="OPS", status=ActiveStatusEnum.ACTIVE)
    session.add_all([engineering, operations])
    session.flush()  # need real IDs before users can reference department_id

    # --- Phase 2: users, referencing departments ---
    admin = User(
        employee_code="EMP-0001",
        full_name="Aditi Sharma",
        email="admin@assetflow.io",
        password_hash="$2b$12$replace-with-real-bcrypt-hash",
        role=RoleEnum.ADMIN,
        status=ActiveStatusEnum.ACTIVE,
    )
    priya = User(
        employee_code="EMP-0002",
        full_name="Priya Nair",
        email="priya.nair@assetflow.io",
        password_hash="$2b$12$replace-with-real-bcrypt-hash",
        department_id=engineering.id,
        role=RoleEnum.DEPARTMENT_HEAD,
        status=ActiveStatusEnum.ACTIVE,
    )
    raj = User(
        employee_code="EMP-0003",
        full_name="Raj Verma",
        email="raj.verma@assetflow.io",
        password_hash="$2b$12$replace-with-real-bcrypt-hash",
        department_id=engineering.id,
        role=RoleEnum.EMPLOYEE,
        status=ActiveStatusEnum.ACTIVE,
    )
    asset_manager = User(
        employee_code="EMP-0004",
        full_name="Kabir Singh",
        email="kabir.singh@assetflow.io",
        password_hash="$2b$12$replace-with-real-bcrypt-hash",
        department_id=operations.id,
        role=RoleEnum.ASSET_MANAGER,
        status=ActiveStatusEnum.ACTIVE,
    )
    session.add_all([admin, priya, raj, asset_manager])
    session.flush()  # need user IDs before setting department heads

    # --- Phase 3: close the loop ---
    engineering.department_head_id = priya.id
    operations.department_head_id = asset_manager.id

    # --- Categories ---
    electronics = AssetCategory(
        name="Electronics",
        description="Laptops, monitors, phones",
        custom_fields_schema=[
            {"key": "warranty_months", "label": "Warranty (months)", "type": "integer"}
        ],
    )
    furniture = AssetCategory(name="Furniture", description="Desks, chairs, cabinets")
    rooms = AssetCategory(name="Meeting Rooms", description="Bookable shared spaces")
    session.add_all([electronics, furniture, rooms])
    session.flush()

    # --- Assets ---
    laptop = Asset(
        asset_tag="AF-0114",
        name="Dell Latitude 5440",
        category_id=electronics.id,
        department_id=engineering.id,
        serial_number="SN-DL5440-001",
        acquisition_date=date(2025, 1, 15),
        acquisition_cost=1200.00,
        condition=AssetConditionEnum.GOOD,
        status=AssetStatusEnum.ALLOCATED,  # matches the seeded active allocation below
        location="Engineering Floor 2",
        is_bookable=False,
        custom_fields={"warranty_months": 24},
    )
    room_b2 = Asset(
        asset_tag="AF-0201",
        name="Room B2",
        category_id=rooms.id,
        acquisition_date=date(2024, 6, 1),
        condition=AssetConditionEnum.GOOD,
        status=AssetStatusEnum.AVAILABLE,
        location="Building B, Floor 2",
        is_bookable=True,
    )
    spare_monitor = Asset(
        asset_tag="AF-0305",
        name="Dell 27-inch Monitor",
        category_id=electronics.id,
        acquisition_date=date(2024, 11, 1),
        acquisition_cost=250.00,
        condition=AssetConditionEnum.NEW,
        status=AssetStatusEnum.AVAILABLE,
        location="IT Storage",
        is_bookable=False,
    )
    session.add_all([laptop, room_b2, spare_monitor])
    session.flush()

    # --- The "Priya has AF-0114" scenario from the brief ---
    session.add(
        AssetAllocation(
            asset_id=laptop.id,
            employee_id=priya.id,
            allocated_by_id=asset_manager.id,
            allocated_at=datetime.now(timezone.utc) - timedelta(days=30),
            expected_return_date=date.today() + timedelta(days=60),
            status=AllocationStatusEnum.ACTIVE,
        )
    )

    # --- A booking on Room B2, to demonstrate the overlap window from the brief ---
    start = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
    session.add(
        Booking(
            asset_id=room_b2.id,
            booked_by_id=raj.id,
            start_time=start,
            end_time=start + timedelta(hours=1),  # 9:00-10:00
            status=BookingStatusEnum.UPCOMING,
            purpose="Sprint planning",
        )
    )

    # --- A pending maintenance request ---
    session.add(
        MaintenanceRequest(
            asset_id=spare_monitor.id,
            raised_by_id=raj.id,
            issue_description="Flickering display on power-on",
            priority=MaintenancePriorityEnum.LOW,
            status=MaintenanceStatusEnum.PENDING,
        )
    )

    session.commit()
    print("Seed complete.")


if __name__ == "__main__":
    # Uses YOUR engine/settings.DATABASE_URL from app/core/config.py + .env -
    # no separate connection string to keep in sync.
    # NOTE: since you're using Alembic (you have alembic.ini + versions/),
    # don't call Base.metadata.create_all() against a real dev/prod DB -
    # that bypasses migration history. Run `alembic upgrade head` first,
    # then run this script purely to insert data.
    with SessionLocal() as session:
        seed(session)
