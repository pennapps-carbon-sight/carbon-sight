-- Fix Supabase security and clean up fake data
-- Run this in your Supabase SQL Editor

-- 1. DELETE ALL FAKE DATA
DELETE FROM energy_usage;
DELETE FROM model_usage;
DELETE FROM users;
DELETE FROM teams;

-- 2. ENABLE ROW LEVEL SECURITY (RLS) for all tables
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE energy_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_usage ENABLE ROW LEVEL SECURITY;

-- 3. CREATE SECURITY POLICIES
-- Teams: Allow all operations for now (you can restrict later)
CREATE POLICY "Allow all operations on teams" ON teams
    FOR ALL USING (true);

-- Users: Allow all operations for now
CREATE POLICY "Allow all operations on users" ON users
    FOR ALL USING (true);

-- Energy usage: Allow all operations for now
CREATE POLICY "Allow all operations on energy_usage" ON energy_usage
    FOR ALL USING (true);

-- Model usage: Allow all operations for now
CREATE POLICY "Allow all operations on model_usage" ON model_usage
    FOR ALL USING (true);

-- 4. INSERT ONLY REAL DATA
-- Add your actual teams
INSERT INTO teams (team_id, team_name, organization) VALUES
('engineering', 'Engineering', 'Your Company'),
('marketing', 'Marketing', 'Your Company'),
('sales', 'Sales', 'Your Company'),
('research', 'Research', 'Your Company');

-- Add yourself as a real user
INSERT INTO users (user_id, email, team_id) VALUES
('you', 'your-email@company.com', 'engineering');

-- 5. CREATE AI_REQUESTS TABLE (if it doesn't exist)
CREATE TABLE IF NOT EXISTS ai_requests (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    team_id VARCHAR(255) NOT NULL,
    model_used VARCHAR(255) NOT NULL,
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    energy_wh DECIMAL(10,6) NOT NULL,
    co2e_g DECIMAL(10,6) NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    was_green_swap BOOLEAN DEFAULT FALSE,
    was_auto_selected BOOLEAN DEFAULT TRUE,
    region VARCHAR(100) DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS for ai_requests
ALTER TABLE ai_requests ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations on ai_requests" ON ai_requests
    FOR ALL USING (true);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_ai_requests_user_id ON ai_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_requests_team_id ON ai_requests(team_id);
CREATE INDEX IF NOT EXISTS idx_ai_requests_created_at ON ai_requests(created_at);
