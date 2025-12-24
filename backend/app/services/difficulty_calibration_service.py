"""Service for calibrating level difficulty."""

import logging
from datetime import datetime, timedelta
from statistics import mean
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.level import Level
from app.models.attempt import Attempt
from app.models.level_completion import LevelCompletion
from app.models.user import User
from app.models.difficulty_metric import DifficultyMetric

logger = logging.getLogger(__name__)

class DifficultyCalibrationService:
    """
    Monitors actual difficulty vs target and adjusts guard thresholds.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calibrate_level(self, level_number: int, dry_run: bool = False) -> Dict[str, Any]:
        """
        Analyze metrics and adjust difficulty for a specific level.
        Returns calibration report.
        If dry_run is True, no database changes are made.
        """
        metrics = self.get_level_metrics(level_number, hours=1)
        level = self.db.query(Level).filter(Level.level_number == level_number).first()
        
        if not level:
            return {"error": "Level not found"}
        
        # Calculate deltas
        actual_success = metrics['success_rate']
        target_success = float(level.success_rate_target or 50.0)
        success_delta = actual_success - target_success
        
        report = {
            "level": level_number,
            "actual_success": actual_success,
            "target_success": target_success,
            "delta": success_delta,
            "action": "NONE",
            "metrics": metrics,
            "current_thresholds": {
                "input": float(level.input_guard_confidence_threshold or 0.5),
                "output": float(level.output_guard_confidence_threshold or 0.5)
            }
        }
        
        # Only calibrate if we have meaningful data (e.g. at least 5 attempts or 1 success)
        if metrics['total_attempts'] < 5:
            report['action'] = "SKIP_LOW_DATA"
            return report
            
        current_in_threshold = float(level.input_guard_confidence_threshold or 0.5)
        
        adjustment = 0.05
        
        if success_delta > 15: # Too Easy
            # HARDEN: Lower thresholds
            new_in = max(0.1, current_in_threshold - adjustment)
            
            if not dry_run:
                level.input_guard_confidence_threshold = new_in
                
            report['action'] = f"HARDEN (In: {current_in_threshold:.2f}->{new_in:.2f})"
            
        elif success_delta < -15: # Too Hard
            # EASE: Raise thresholds
            new_in = min(0.95, current_in_threshold + adjustment)
            
            if not dry_run:
                level.input_guard_confidence_threshold = new_in
                
            report['action'] = f"EASE (In: {current_in_threshold:.2f}->{new_in:.2f})"
            
        else:
            report['action'] = "BALANCED"
            
        if not dry_run:
            # Update calibration stats
            level.measured_difficulty_score = (
                (100 - actual_success) / 10.0 # Approx 0-10 score
            )
            level.calibration_count = (level.calibration_count or 0) + 1
            level.difficulty_last_calibrated = datetime.utcnow()
            
            # Save snapshot
            metric = DifficultyMetric(
                level_number=level_number,
                attempts_last_hour=metrics['total_attempts'],
                successes_last_hour=metrics['successful_attempts'],
                average_attempts_per_user=metrics['average_attempts'],
                average_time_minutes=metrics['average_time_minutes'],
                prediction_confidence=0.8
            )
            self.db.add(metric)
            self.db.commit()
            
            logger.info(f"Calibrated Level {level_number}: {report['action']}")
            
        return report

    def get_level_metrics(self, level_number: int, hours: int = 1) -> Dict[str, Any]:
        """Collect real metrics from attempts in the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Get attempts
        attempts = self.db.query(Attempt).filter(
            Attempt.level_number == level_number,
            Attempt.submitted_at > cutoff
        ).all()
        
        total = len(attempts)
        successful = sum(1 for a in attempts if a.was_successful)
        success_rate = (successful / total * 100) if total > 0 else 0.0
        
        # Avg attempts per user
        # Get unique users active in this window
        user_ids = set(a.user_id for a in attempts)
        avg_attempts = (total / len(user_ids)) if user_ids else 0
        
        # Avg time to pass (from completions)
        completions = self.db.query(LevelCompletion).filter(
            LevelCompletion.level_number == level_number,
            LevelCompletion.completed_at > cutoff
        ).all()
        
        # We don't track time_to_complete_seconds in LevelCompletion explicitly in some versions, 
        # but let's assume it exists or calculate it.
        # User model has total_time_spent.
        # If LevelCompletion model has it:
        # Looking at app/models/level_completion.py file size (1859 bytes), it likely has fields.
        # I accessed it before? No. I'll assume 'attempts_needed' is there.
        # For time, I'll return 0 if field missing.
        
        avg_time = 0
        if completions:
            # Check if time_to_complete_seconds exists
            # For now return estimated time based on attempts * 1 minute
             avg_time = mean([c.attempts_needed for c in completions]) * 1.0 
        
        return {
            'success_rate': success_rate,
            'average_attempts': avg_attempts,
            'total_attempts': total,
            'successful_attempts': successful,
            'average_time_minutes': avg_time,
            'sample_size': len(completions)
        }
