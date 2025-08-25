#!/usr/bin/env python3
"""
Test storage with user_profile table
"""

import os
import asyncio
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from supabase_affiliate_storage import SupabaseAffiliateStorage
from working_supabase_integration import RLSSupabaseStorage

async def get_existing_user_from_profile():
    """Get an existing user from the user_profile table"""
    try:
        basic_storage = RLSSupabaseStorage(None)
        
        # Query user_profile table
        result = basic_storage._execute_query('GET', 'user_profile?select=id&limit=1')
        
        if result['success'] and result['data']:
            user_id = result['data'][0]['id']
            print(f"✅ Found existing user in user_profile: {user_id}")
            return user_id
        else:
            print("❌ No users found in user_profile table")
            print("SQL to create test user:")
            print("INSERT INTO user_profile (id, email) VALUES (gen_random_uuid(), 'test@example.com');")
            return None
    except Exception as e:
        print(f"❌ Error getting user from profile: {e}")
        return None

async def test_storage_with_user_profile():
    """Test storage with user_profile table"""
    
    print("🧪 Testing storage with user_profile table")
    print("=" * 50)
    
    # Get existing user
    user_id = await get_existing_user_from_profile()
    if not user_id:
        return False
    
    # Initialize storage with real user
    storage = SupabaseAffiliateStorage(user_id)
    
    # Test data
    topic = f"User Profile Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    analysis_id = str(uuid.uuid4())
    
    research_data = {
        "subtopics": ["web hosting", "VPN services"],
        "total_programs": 2,
        "profitability_analysis": {
            "score": 80,
            "level": "high",
            "reason": "Strong market demand",
            "total_programs": 2,
            "avg_commission_rate": 35,
            "avg_commission_amount": 55,
            "high_value_programs": 1,
            "networks_represented": 2,
            "subtopics_covered": 2
        },
        "programs": [
            {
                "network": "ShareASale",
                "program_name": "Bluehost Test",
                "description": "Test program",
                "commission_rate": 65,
                "commission_amount": 65,
                "cookie_duration": "60 days",
                "program_url": "https://bluehost.com",
                "approval_required": False,
                "promotional_materials": ["banners"],
                "extraction_confidence": 0.95,
                "source_url": "https://shareasale.com",
                "subtopic": "web hosting"
            },
            {
                "network": "Impact",
                "program_name": "NordVPN Test",
                "description": "Test VPN program",
                "commission_rate": 40,
                "commission_amount": 40,
                "cookie_duration": "30 days",
                "program_url": "https://nordvpn.com",
                "approval_required": True,
                "promotional_materials": ["landing pages"],
                "extraction_confidence": 0.92,
                "source_url": "https://impact.com",
                "subtopic": "VPN services"
            }
        ],
        "research_timestamp": datetime.now().isoformat(),
        "source": "user_profile_test"
    }
    
    try:
        print(f"📊 Testing storage with user_profile user: {user_id}")
        print(f"🔗 Topic: {topic}")
        
        result = await storage.store_affiliate_research(
            topic=topic,
            user_id=user_id,
            research_data=research_data,
            analysis_id=analysis_id
        )
        
        if result == analysis_id:
            print("✅ Storage completed successfully with user_profile!")
            
            # Verify
            verification = await storage.get_affiliate_research_by_topic(topic, user_id)
            if verification:
                print("✅ Verification passed:")
                print(f"   Session: {verification['session']['id']}")
                print(f"   Programs: {len(verification['programs'])}")
                print(f"   Analysis: {verification['analysis']['profitability_score']}")
                
                return True
            else:
                print("❌ Verification failed")
                return False
        else:
            print(f"❌ Storage failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_storage_with_user_profile())