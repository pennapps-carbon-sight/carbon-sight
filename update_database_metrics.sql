-- Update ai_requests table to include latency and cost metrics
-- This script adds the necessary columns for tracking performance metrics

-- Add new columns for metrics tracking
ALTER TABLE ai_requests 
ADD COLUMN IF NOT EXISTS latency_ms INTEGER,
ADD COLUMN IF NOT EXISTS cost_usd DECIMAL(10,6),
ADD COLUMN IF NOT EXISTS input_tokens INTEGER,
ADD COLUMN IF NOT EXISTS output_tokens INTEGER,
ADD COLUMN IF NOT EXISTS total_tokens INTEGER,
ADD COLUMN IF NOT EXISTS input_cost_usd DECIMAL(10,6),
ADD COLUMN IF NOT EXISTS output_cost_usd DECIMAL(10,6),
ADD COLUMN IF NOT EXISTS tokens_per_second DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS cost_per_token DECIMAL(10,6),
ADD COLUMN IF NOT EXISTS cost_per_character DECIMAL(10,6),
ADD COLUMN IF NOT EXISTS prompt_complexity DECIMAL(5,3),
ADD COLUMN IF NOT EXISTS efficiency_score DECIMAL(5,1);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_ai_requests_latency ON ai_requests(latency_ms);
CREATE INDEX IF NOT EXISTS idx_ai_requests_cost ON ai_requests(cost_usd);
CREATE INDEX IF NOT EXISTS idx_ai_requests_efficiency ON ai_requests(efficiency_score);
CREATE INDEX IF NOT EXISTS idx_ai_requests_model_latency ON ai_requests(model_used, latency_ms);
CREATE INDEX IF NOT EXISTS idx_ai_requests_model_cost ON ai_requests(model_used, cost_usd);

-- Create a view for performance analytics
CREATE OR REPLACE VIEW performance_analytics AS
SELECT 
    model_used,
    DATE(created_at) as date,
    COUNT(*) as request_count,
    AVG(latency_ms) as avg_latency_ms,
    AVG(cost_usd) as avg_cost_usd,
    SUM(cost_usd) as total_cost_usd,
    AVG(efficiency_score) as avg_efficiency_score,
    AVG(tokens_per_second) as avg_tokens_per_second,
    AVG(prompt_complexity) as avg_prompt_complexity
FROM ai_requests 
WHERE latency_ms IS NOT NULL 
    AND cost_usd IS NOT NULL 
    AND efficiency_score IS NOT NULL
GROUP BY model_used, DATE(created_at)
ORDER BY date DESC, model_used;

-- Create a view for model comparison
CREATE OR REPLACE VIEW model_comparison AS
SELECT 
    model_used,
    COUNT(*) as total_requests,
    AVG(latency_ms) as avg_latency_ms,
    MIN(latency_ms) as min_latency_ms,
    MAX(latency_ms) as max_latency_ms,
    AVG(cost_usd) as avg_cost_usd,
    SUM(cost_usd) as total_cost_usd,
    AVG(efficiency_score) as avg_efficiency_score,
    AVG(tokens_per_second) as avg_tokens_per_second,
    AVG(total_tokens) as avg_total_tokens
FROM ai_requests 
WHERE latency_ms IS NOT NULL 
    AND cost_usd IS NOT NULL 
    AND efficiency_score IS NOT NULL
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY model_used
ORDER BY avg_efficiency_score DESC;

-- Add comments for documentation
COMMENT ON COLUMN ai_requests.latency_ms IS 'Response latency in milliseconds';
COMMENT ON COLUMN ai_requests.cost_usd IS 'Total cost in USD';
COMMENT ON COLUMN ai_requests.input_tokens IS 'Number of input tokens';
COMMENT ON COLUMN ai_requests.output_tokens IS 'Number of output tokens';
COMMENT ON COLUMN ai_requests.total_tokens IS 'Total tokens used';
COMMENT ON COLUMN ai_requests.input_cost_usd IS 'Cost for input tokens in USD';
COMMENT ON COLUMN ai_requests.output_cost_usd IS 'Cost for output tokens in USD';
COMMENT ON COLUMN ai_requests.tokens_per_second IS 'Processing speed in tokens per second';
COMMENT ON COLUMN ai_requests.cost_per_token IS 'Average cost per token';
COMMENT ON COLUMN ai_requests.cost_per_character IS 'Average cost per character in response';
COMMENT ON COLUMN ai_requests.prompt_complexity IS 'Prompt complexity score (0-1)';
COMMENT ON COLUMN ai_requests.efficiency_score IS 'Overall efficiency score (0-100)';
