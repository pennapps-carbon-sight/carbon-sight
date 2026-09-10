-- Create ai_requests table for logging real API calls
CREATE TABLE IF NOT EXISTS ai_requests (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    model_used VARCHAR(255) NOT NULL,
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    energy_wh DECIMAL(10,6) NOT NULL,
    co2e_g DECIMAL(10,6) NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    was_green_swap BOOLEAN DEFAULT FALSE,
    region VARCHAR(100) DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add some indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ai_requests_user_id ON ai_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_requests_model_used ON ai_requests(model_used);
CREATE INDEX IF NOT EXISTS idx_ai_requests_created_at ON ai_requests(created_at);

-- Enable RLS (Row Level Security)
ALTER TABLE ai_requests ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (for now)
CREATE POLICY "Allow all operations on ai_requests" ON ai_requests
    FOR ALL USING (true);
