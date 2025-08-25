#!/usr/bin/env python3
"""
Debug test script for affiliate research storage with proper environment loading
"""

import os
import asyncio
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test environment setup first
print("🔍 Checking environment variables...")
required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {value[:20]}...")
    else:
        print(f"❌ {var}: NOT SET")

print()

# Only proceed if environment is set
if all(os.getenv(var) for var in required_vars):
    print("✅ Environment ready, testing storage...")
    
    from supabase_affiliate_storage import SupabaseAffiliateStorage
    
    async def test_storage():
        try:
            # Generate proper UUID for user_id
            user_id = str(uuid.uuid4())
            storage = SupabaseAffiliateStorage(user_id)
            topic = "Debug Test Topic"
            
            # Simple test data
            research_data = {
                "subtopics": ["test1", "test2"],
                "total_programs": 1,
                "profitability_analysis": {
                    "score": 75,
                    "level": "medium",
                    "reason": "Test analysis"
                },
                "programs": [
                    {
                        "network": "TestNetwork",
                        "program_name": "Test Program",
                        "description": "Test description",
                        "commission_rate": 20,
                        "commission_amount": 50,
                        "cookie_duration": "30 days",
                        "program_url": "https://test.com",
                        "approval_required": False,
                        "promotional_materials": [],
                        "extraction_confidence": 0.95,
                        "source_url": "https://test.com",
                        "subtopic": "test"
                    }
                ],
                "research_timestamp": datetime.now().isoformat(),
                "source": "debug_test"
            }
            
            print("🧪 Testing storage...")
            result = await storage.store_affiliate_research(
                topic=topic,
                user_id=user_id,
                research_data=research_data
            )
            
            print(f"✅ Storage test completed: {result}")
            
            # Verify
            verification = await storage.get_affiliate_research_by_topic(topic, user_id)
            if verification:
                print(f"✅ Verification passed:")
                print(f"   Session: {verification['session']['id']}")
                print(f"   Programs: {len(verification['programs'])}")
                print(f"   Analysis: {verification['analysis']['profitability_score']}")
            else:
                print("❌ Verification failed")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Run the test
    asyncio.run(test_storage())
    
else:
    print("❌ Environment variables not properly set")
    print("Please ensure .env file exists with SUPABASE_URL and SUPABASE_KEY")

print("\n📊 Manual verification - check tables directly:")
print("Run these SQL queries in Supabase:")
print("SELECT COUNT(*) FROM affiliate_research_sessions;")
print("SELECT COUNT(*) FROM affiliate_programs;") 
print("SELECT COUNT(*) FROM affiliate_session_programs;")
print("SELECT COUNT(*) FROM affiliate_profitability_analysis;")