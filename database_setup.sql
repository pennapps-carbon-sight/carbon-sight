-- GreenAI Dashboard Database Schema
-- Run this in your Supabase SQL editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR(255) UNIQUE NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    team_id VARCHAR(255) REFERENCES teams(team_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Energy usage tracking
CREATE TABLE IF NOT EXISTS energy_usage (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    model_name VARCHAR(255) NOT NULL,
    energy_kwh DECIMAL(10, 6) NOT NULL,
    co2_saved_grams DECIMAL(10, 4) NOT NULL,
    energy_saved_kwh DECIMAL(10, 6) NOT NULL,
    cost_savings_usd DECIMAL(10, 4) NOT NULL,
    green_tokens_earned DECIMAL(10, 4) NOT NULL,
    latency_ms INTEGER,
    nft_badge_earned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model usage tracking
CREATE TABLE IF NOT EXISTS model_usage (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    energy_kwh DECIMAL(10, 6) NOT NULL,
    co2_grams DECIMAL(10, 4) NOT NULL,
    latency_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_energy_usage_team_id ON energy_usage(team_id);
CREATE INDEX IF NOT EXISTS idx_energy_usage_created_at ON energy_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_model_usage_team_id ON model_usage(team_id);
CREATE INDEX IF NOT EXISTS idx_model_usage_created_at ON model_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_users_team_id ON users(team_id);

-- Insert sample data
INSERT INTO teams (team_id, team_name, organization) VALUES 
    ('team-engineering', 'Engineering Team', 'GreenAI Corp'),
    ('team-marketing', 'Marketing Team', 'GreenAI Corp'),
    ('team-sales', 'Sales Team', 'GreenAI Corp'),
    ('team-research', 'Research Team', 'GreenAI Corp')
ON CONFLICT (team_id) DO NOTHING;

INSERT INTO users (user_id, email, team_id) VALUES 
    ('user-alice', 'alice@greenai.com', 'team-engineering'),
    ('user-bob', 'bob@greenai.com', 'team-engineering'),
    ('user-carol', 'carol@greenai.com', 'team-marketing'),
    ('user-david', 'david@greenai.com', 'team-sales'),
    ('user-eve', 'eve@greenai.com', 'team-research')
ON CONFLICT (user_id) DO NOTHING;

-- Insert sample energy usage data
INSERT INTO energy_usage (team_id, user_id, model_name, energy_kwh, co2_saved_grams, energy_saved_kwh, cost_savings_usd, green_tokens_earned, latency_ms, nft_badge_earned) VALUES 
    ('team-engineering', 'user-alice', 'gemini-2.5-flash', 0.05, 25.0, 0.02, 0.50, 0.50, 800, true),
    ('team-engineering', 'user-bob', 'gemini-2.5-flash', 0.07, 35.0, 0.03, 0.70, 0.70, 750, true),
    ('team-marketing', 'user-carol', 'gemini-1.5-flash', 0.04, 20.0, 0.015, 0.40, 0.40, 700, true),
    ('team-sales', 'user-david', 'gemini-2.5-pro', 0.12, 60.0, 0.05, 1.20, 1.20, 1200, false),
    ('team-research', 'user-eve', 'gemini-2.5-flash', 0.06, 30.0, 0.025, 0.60, 0.60, 850, true)
ON CONFLICT DO NOTHING;

-- Insert sample model usage data
INSERT INTO model_usage (team_id, model_name, energy_kwh, co2_grams, latency_ms) VALUES 
    ('team-engineering', 'gemini-2.5-flash', 0.05, 25.0, 800),
    ('team-engineering', 'gemini-2.5-pro', 0.12, 60.0, 1200),
    ('team-marketing', 'gemini-1.5-flash', 0.04, 20.0, 700),
    ('team-sales', 'gemini-2.5-pro', 0.12, 60.0, 1200),
    ('team-research', 'gemini-2.5-flash', 0.06, 30.0, 850)
ON CONFLICT DO NOTHING;
