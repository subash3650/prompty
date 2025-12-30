-- Migration: Add hint system fields to levels table
-- Run this against your PostgreSQL database on Render

-- Add missing columns to levels table
ALTER TABLE levels
ADD COLUMN IF NOT EXISTS hint_revelation_stages TEXT DEFAULT '[]',
ADD COLUMN IF NOT EXISTS hint_difficulty VARCHAR(50) DEFAULT 'moderate';

-- Note: start_hint already exists in the model based on earlier analysis

-- Update existing rows with proper difficulty levels based on level number
UPDATE levels SET hint_difficulty = 'trivial' WHERE level_number = 1;
UPDATE levels SET hint_difficulty = 'subtle' WHERE level_number = 2;
UPDATE levels SET hint_difficulty = 'moderate' WHERE level_number = 3;
UPDATE levels SET hint_difficulty = 'moderate-hard' WHERE level_number = 4;
UPDATE levels SET hint_difficulty = 'hard' WHERE level_number = 5;
UPDATE levels SET hint_difficulty = 'hard' WHERE level_number = 6;
UPDATE levels SET hint_difficulty = 'very_hard' WHERE level_number = 7;
UPDATE levels SET hint_difficulty = 'expert' WHERE level_number = 8;

-- Verify migration was successful
SELECT level_number, hint, hint_difficulty, hint_revelation_stages 
FROM levels 
ORDER BY level_number;
