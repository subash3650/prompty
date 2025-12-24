"""Admin routes."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.security.jwt import get_current_admin
from app.models.user import User
from app.models.level import Level
from app.models.attempt import Attempt
from app.models.audit_log import AuditLog
from app.ai.groq_client import get_groq_client
from app.services.difficulty_calibration_service import DifficultyCalibrationService


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_admin_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get event statistics for admin dashboard.
    """
    # User stats
    total_users = db.query(User).filter(User.is_admin == False).count()
    online_users = db.query(User).filter(
        User.is_admin == False,
        User.is_online == True
    ).count()
    finished_users = db.query(User).filter(
        User.is_admin == False,
        User.is_finished == True
    ).count()
    
    # Attempt stats
    total_attempts = db.query(Attempt).count()
    successful_attempts = db.query(Attempt).filter(Attempt.was_successful == True).count()
    
    # Average latency
    avg_latency = db.query(func.avg(Attempt.ai_latency_ms)).scalar() or 0
    
    # Level distribution
    level_distribution = {}
    for level in range(1, 9):
        count = db.query(User).filter(
            User.is_admin == False,
            User.highest_level_reached == level
        ).count()
        level_distribution[level] = count
    
    # Get Groq usage
    groq_client = get_groq_client()
    groq_stats = groq_client.get_usage_stats()
    
    return {
        "users": {
            "total": total_users,
            "online": online_users,
            "finished": finished_users,
        },
        "attempts": {
            "total": total_attempts,
            "successful": successful_attempts,
            "success_rate": (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            "avg_latency_ms": round(avg_latency),
        },
        "level_distribution": level_distribution,
        "groq": groq_stats,
        "timestamp": datetime.utcnow(),
    }


@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all users with their status.
    """
    offset = (page - 1) * per_page
    
    users = db.query(User).filter(
        User.is_admin == False
    ).order_by(User.created_at.desc()).offset(offset).limit(per_page).all()
    
    total = db.query(User).filter(User.is_admin == False).count()
    
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "current_level": u.current_level,
                "highest_level_reached": u.highest_level_reached,
                "total_attempts": u.total_attempts,
                "successful_attempts": u.successful_attempts,
                "is_online": u.is_online,
                "is_finished": u.is_finished,
                "last_activity": u.last_activity,
                "created_at": u.created_at,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/attempts")
async def get_all_attempts(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    level: Optional[int] = Query(None, ge=1, le=8),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all attempts (audit trail).
    """
    offset = (page - 1) * per_page
    
    query = db.query(Attempt)
    
    if user_id:
        query = query.filter(Attempt.user_id == user_id)
    if level:
        query = query.filter(Attempt.level_number == level)
    
    total = query.count()
    attempts = query.order_by(Attempt.submitted_at.desc()).offset(offset).limit(per_page).all()
    
    return {
        "attempts": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "level_number": a.level_number,
                "user_prompt": a.user_prompt[:200] + "..." if len(a.user_prompt) > 200 else a.user_prompt,
                "was_successful": a.was_successful,
                "input_guard_triggered": a.input_guard_triggered,
                "output_guard_triggered": a.output_guard_triggered,
                "ai_latency_ms": a.ai_latency_ms,
                "submitted_at": a.submitted_at,
            }
            for a in attempts
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/levels")
async def get_level_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get statistics for all levels.
    """
    levels = db.query(Level).order_by(Level.level_number).all()
    
    return {
        "levels": [
            {
                "level_number": l.level_number,
                "defense_description": l.defense_description,
                "input_guard_type": l.input_guard_type,
                "output_guard_type": l.output_guard_type,
                "total_attempts": l.total_attempts_made,
                "successful_attempts": l.successful_attempts_made,
                "success_rate": float(l.success_rate or 0),
            }
            for l in levels
        ]
    }


@router.get("/logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    event_type: Optional[str] = Query(None),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs.
    """
    offset = (page - 1) * per_page
    
    query = db.query(AuditLog)
    
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(per_page).all()
    
    return {
        "logs": [
            {
                "id": l.id,
                "event_type": l.event_type,
                "user_id": l.user_id,
                "details": l.details,
                "severity": l.severity,
                "suspicious_flag": l.suspicious_flag,
                "created_at": l.created_at,
            }
            for l in logs
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/difficulty-analysis")
async def get_difficulty_analysis(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Real-time dashboard showing difficulty distribution and calibration status.
    """
    service = DifficultyCalibrationService(db)
    
    analysis = {
        "timestamp": datetime.utcnow(),
        "levels": []
    }
    
    for level_number in range(1, 9):
        # Run calibration in dry_run mode just to get the report/recommendation
        report = service.calibrate_level(level_number, dry_run=True)
        analysis["levels"].append(report)
    
    return analysis
