#!/usr/bin/env python3
"""
Database setup script for GreenAI Dashboard.
Creates the ai_requests table and cleans up fake data.
"""

import asyncio
from supabase import create_client, Client
from config import config

async def setup_database():
    """Set up the database with proper tables and clean data."""
    
    # Initialize Supabase client
    supabase: Client = create_client(config.supabase_url, config.supabase_key)
    
    print("🔧 Setting up GreenAI Database...")
    
    # Create ai_requests table
    print("📊 Creating ai_requests table...")
    create_table_sql = """
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
    """
    
    try:
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print("✅ ai_requests table created successfully!")
    except Exception as e:
        print(f"⚠️  Note: Table might already exist or need manual creation: {e}")
    
    # Clean up fake data
    print("🧹 Cleaning up fake data...")
    
    # Delete fake energy usage records
    try:
        supabase.table("energy_usage").delete().in_("user_id", [
            "user-alice", "user-bob", "user-carol", "user-david", "user-eve"
        ]).execute()
        print("✅ Removed fake energy usage records")
    except Exception as e:
        print(f"⚠️  Error cleaning energy_usage: {e}")
    
    # Delete fake users
    try:
        supabase.table("users").delete().in_("user_id", [
            "user-alice", "user-bob", "user-carol", "user-david", "user-eve"
        ]).execute()
        print("✅ Removed fake users")
    except Exception as e:
        print(f"⚠️  Error cleaning users: {e}")
    
    # Add a real user for testing
    try:
        supabase.table("users").upsert({
            "user_id": "real-user-1",
            "email": "you@yourcompany.com",
            "team_id": "team-engineering"
        }).execute()
        print("✅ Added real test user")
    except Exception as e:
        print(f"⚠️  Error adding test user: {e}")
    
    print("🎉 Database setup complete!")
    print("\n📋 Next steps:")
    print("1. Run: python3 run.py")
    print("2. Test: curl -X POST 'http://localhost:8000/api/v1/chat?message=Hello&model=cerebras-llama-3.1-8b'")
    print("3. Check data: Visit your Supabase dashboard to see real data!")

if __name__ == "__main__":
    asyncio.run(setup_database())
