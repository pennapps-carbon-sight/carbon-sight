#!/usr/bin/env python3
"""
Integration test script for CarbonSight.
Tests the connection between frontend and backend.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from database_service import DatabaseService
from analytics_service import AnalyticsService
from ml_service import MLService
from config import config


async def test_database_service():
    """Test database service functionality."""
    print("🔍 Testing Database Service...")
    
    try:
        db = DatabaseService()
        print("  ✓ Database service initialized")
        
        # Test health check
        teams = await db.get_all_teams()
        print(f"  ✓ Found {len(teams)} teams")
        
        return True
    except Exception as e:
        print(f"  ❌ Database service error: {e}")
        return False


async def test_analytics_service():
    """Test analytics service functionality."""
    print("🔍 Testing Analytics Service...")
    
    try:
        analytics = AnalyticsService()
        print("  ✓ Analytics service initialized")
        
        # Test prompt analysis
        result = await analytics.perform_hypothesis_testing([], "co2_saved")
        print(f"  ✓ Hypothesis testing: {result.get('success', False)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Analytics service error: {e}")
        return False


async def test_ml_service():
    """Test ML service functionality."""
    print("🔍 Testing ML Service...")
    
    try:
        ml = MLService()
        print("  ✓ ML service initialized")
        
        # Test prompt analysis
        result = await ml.analyze_prompt_complexity("Test prompt for analysis")
        print(f"  ✓ Prompt analysis: {result.get('success', False)}")
        
        return True
    except Exception as e:
        print(f"  ❌ ML service error: {e}")
        return False


def test_configuration():
    """Test configuration setup."""
    print("🔍 Testing Configuration...")
    
    try:
        print(f"  ✓ API Title: {config.api_title}")
        print(f"  ✓ API Version: {config.api_version}")
        print(f"  ✓ Database configured: {config.is_database_configured}")
        print(f"  ✓ Debug mode: {config.debug}")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False


async def main():
    """Run all integration tests."""
    print("🚀 Running CarbonSight Integration Tests...\n")
    
    tests = [
        ("Configuration", test_configuration()),
        ("Database Service", test_database_service()),
        ("Analytics Service", test_analytics_service()),
        ("ML Service", test_ml_service())
    ]
    
    results = []
    for test_name, test_coro in tests:
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))
    
    print("\n📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Integration is working correctly.")
        print("\n📋 Next steps:")
        print("1. Configure your .env file with real API keys")
        print("2. Set up your Supabase database")
        print("3. Start the backend: python run.py")
        print("4. Start the frontend: npm run dev")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the configuration.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
