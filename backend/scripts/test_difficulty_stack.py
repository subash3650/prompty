"""Test the Difficulty Scaling Engine stack."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.services.difficulty_calibration_service import DifficultyCalibrationService

def test_stack():
    db = SessionLocal()
    try:
        service = DifficultyCalibrationService(db)
        print("✅ Service initialized")
        
        # Test calibration analysis (dry run)
        report = service.calibrate_level(1, dry_run=True)
        print(f"✅ Level 1 Analysis: {report['action']}")
        print(f"   Success Rate: {report['actual_success']}%")
        
        # Test models exist using SQL check implicitly done by query
        print("✅ Database connection works")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_stack()
