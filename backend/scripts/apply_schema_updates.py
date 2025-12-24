"""
Apply schema updates for Difficulty Scaling Engine.
Adds columns to 'levels' table and creates new tables.
Idempotent script (safe to run multiple times).
"""

import sys
import os
import sqlalchemy
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine

def apply_updates():
    print("Connecting to database...")
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # 1. Add columns to LEVELS table
        # We run each ALTER individually and catch error if column exists
        columns = [
            # Difficulty calibration
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS difficulty_base_score NUMERIC(4,1) CHECK (difficulty_base_score >= 1 AND difficulty_base_score <= 10)",
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS measured_difficulty_score NUMERIC(4,1)",
            
            # Guard configuration
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS input_guard_confidence_threshold NUMERIC(3,2) DEFAULT 0.5",
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS output_guard_confidence_threshold NUMERIC(3,2) DEFAULT 0.5",
            
            # Metrics
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS success_rate_target NUMERIC(5,2) DEFAULT 50.0",
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS average_attempts_target INTEGER DEFAULT 5",
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS time_to_pass_target_minutes INTEGER DEFAULT 5",
            
            # Tracking
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS difficulty_last_calibrated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS calibration_count INTEGER DEFAULT 0",
            
            # Password learning
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS discovered_bypass_techniques TEXT",
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS password_variations_count INTEGER DEFAULT 0",
            
            # New fields for level definitions
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS start_hint VARCHAR",
            "ALTER TABLE levels ADD COLUMN IF NOT EXISTS defense_description VARCHAR",
        ]

        print("Updating LEVELS table schema...")
        for query in columns:
            try:
                conn.execute(text(query))
                print(f"Executed: {query[:60]}...")
            except Exception as e:
                # If "column already exists" or duplicate, we can ignore (IF NOT EXISTS usually handles it in PG 9.6+)
                if "already exists" in str(e):
                    print(f"Skipped (exists): {query[:60]}...")
                else:
                    print(f"Error executing {query}: {e}")
        
        # 2. Create GUARD_RULES table
        print("Creating GUARD_RULES table...")
        create_rules_query = """
        CREATE TABLE IF NOT EXISTS guard_rules (
            id UUID PRIMARY KEY,
            level_number INTEGER NOT NULL REFERENCES levels(level_number),
            rule_type VARCHAR(50) NOT NULL,
            rule_name VARCHAR(100) NOT NULL,
            rule_expression TEXT NOT NULL,
            confidence_weight NUMERIC(3,2) DEFAULT 1.0,
            enabled BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(level_number, rule_name)
        );
        """
        try:
            conn.execute(text(create_rules_query))
            print("Guard Rules table checked/created.")
        except Exception as e:
            print(f"Error creating guard_rules: {e}")

        # 3. Create DIFFICULTY_METRICS table
        print("Creating DIFFICULTY_METRICS table...")
        create_metrics_query = """
        CREATE TABLE IF NOT EXISTS difficulty_metrics (
            id UUID PRIMARY KEY,
            level_number INTEGER NOT NULL REFERENCES levels(level_number),
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            
            attempts_last_hour INTEGER DEFAULT 0,
            successes_last_hour INTEGER DEFAULT 0,
            average_attempts_per_user NUMERIC(5,2),
            average_time_minutes NUMERIC(6,2),
            
            prediction_confidence NUMERIC(3,2)
        );
        """
        # Note: Index creation usually separate
        try:
            conn.execute(text(create_metrics_query))
            print("Difficulty Metrics table checked/created.")
            
            # Index
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_metrics_level_time ON difficulty_metrics (level_number, timestamp DESC)"))
            print("Index created.")
            
        except Exception as e:
            print(f"Error creating difficulty_metrics: {e}")
            
        print("✅ Schema updates applied successfully.")

if __name__ == "__main__":
    apply_updates()
