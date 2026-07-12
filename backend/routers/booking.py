"""Thin router — validation, DI, response shaping only."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.enums import BookingStatusEnum
from models.user import User
from schemas.booking import BookingCancel, BookingCreate, BookingRead, SuggestedSlot
from services.booking_service import BookingService
from utils.response import success_envelope

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])


@router.post("", response_model=dict, status_code=201)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    booking = BookingService(db).create_booking(payload, actor)
    return success_envelope(BookingRead.model_validate(booking).model_dump())


@router.get("", response_model=dict)
def list_bookings(
    asset_id: Optional[int] = None,
    booked_by_id: Optional[int] = None,
    department_id: Optional[int] = None,
    status: Optional[BookingStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    bookings = BookingService(db).list_bookings(asset_id, booked_by_id, department_id, status, skip, limit)
    return success_envelope([BookingRead.model_validate(b).model_dump() for b in bookings])


@router.get("/suggest-slot", response_model=dict)
def suggest_slot(
    asset_id: int,
    desired_start: datetime,
    duration_minutes: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    suggestion = BookingService(db).suggest_slot(asset_id, desired_start, duration_minutes)
    return success_envelope(suggestion.model_dump() if suggestion else None)


@router.get("/{booking_id}", response_model=dict)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    booking = BookingService(db).get_booking(booking_id)
    return success_envelope(BookingRead.model_validate(booking).model_dump())


@router.post("/{booking_id}/cancel", response_model=dict)
def cancel_booking(
    booking_id: int,
    payload: BookingCancel,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    booking = BookingService(db).cancel_booking(booking_id, payload.cancellation_reason, actor)
    return success_envelope(BookingRead.model_validate(booking).model_dump())