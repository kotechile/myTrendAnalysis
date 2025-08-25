#!/usr/bin/env python3
"""
Production test script for affiliate research storage
Tests the complete storage flow with a valid user from the users table
"""

import os
import asyncio
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import after environment is loaded
from supabase_affiliate_storage import SupabaseAffiliateStorage
from working_supabase_integration import RLSSupabaseStorage

async def get_existing_user():
    """Get an existing user from the users table"""
    try:
        # Create a basic storage instance to query users
        basic_storage = RLSSupabaseStorage(None)
        
        # Query for any existing user
        result = basic_storage._execute_query('GET', 'users?select=id&limit=1')
        
        if result['success'] and result['data']:
            user_id = result['data'][0]['id']
            print(f"✅ Found existing user: {user_id}")
            return user_id
        else:
            print("❌ No users found in table. Please create a user first.")
            print("SQL to create test user:")
            print("INSERT INTO users (id, email) VALUES (gen_random_uuid(), 'test@example.com');")
            return None
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return None

async def test_storage_with_real_user():
    """Test storage with a real user from the database"""
    
    print("🧪 Production Test: Affiliate Research Storage")
    print("=" * 50)
    
    # Get existing user
    user_id = await get_existing_user()
    if not user_id:
        return False
    
    # Initialize storage with real user
    storage = SupabaseAffiliateStorage(user_id)
    
    # Test data
    topic = f"Production Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    analysis_id = str(uuid.uuid4())
    
    research_data = {
        "subtopics": ["web hosting", "VPN services", "email marketing"],
        "total_programs": 3,
        "profitability_analysis": {
            "score": 85,
            "level": "high",
            "reason": "High commission rates and strong market demand",
            "total_programs": 3,
            "avg_commission_rate": 25.0,
            "avg_commission_amount": 75.0,
            "high_value_programs": 2,
            "networks_represented": 2,
            "subtopics_covered": 3
        },
        "programs": [
            {
                "network": "ShareASale",
                "program_name": "Bluehost Affiliate",
                "description": "Web hosting affiliate program with high commissions",
                "commission_rate": 65,
                "commission_amount": 65.0,
                "cookie_duration": "60 days",
                "program_url": "https://bluehost.com",
                "approval_required": False,
                "promotional_materials": ["banners", "text links"],
                "extraction_confidence": 0.95,
                "source_url": "https://shareasale.com",
                "subtopic": "web hosting"
            },
            {
                "network": "Impact",
                "program_name": "NordVPN Affiliate",
                "description": "VPN service affiliate program",
                "commission_rate": 40,
                "commission_amount": 40.0,
                "cookie_duration": "30 days",
                "program_url": "https://nordvpn.com",
                "approval_required": True,
                "promotional_materials": ["banners", "landing pages"],
                "extraction_confidence": 0.92,
                "source_url": "https://impact.com",
                "subtopic": "VPN services"
            },
            {
                "network": "CJ Affiliate",
                "program_name": "ConvertKit Affiliate",
                "description": "Email marketing affiliate program",
                "commission_rate": 30,
                "commission_amount": 30.0,
                "cookie_duration": "90 days",
                "program_url": "https://convertkit.com",
                "approval_required": False,
                "promotional_materials": ["email templates", "social media assets"],
                "extraction_confidence": 0.90,
                "source_url": "https://cj.com",
                "subtopic": "email marketing"
            }
        ],
        "research_timestamp": datetime.now().isoformat(),
        "source": "production_test"
    }
    
    try:
        print(f"📊 Testing storage with topic: {topic}")
        print(f"👤 User ID: {user_id}")
        print(f"🆔 Analysis ID: {analysis_id}")
        print()
        
        # Store the research
        result = await storage.store_affiliate_research(
            topic=topic,
            user_id=user_id,
            research_data=research_data,
            analysis_id=analysis_id
        )
        
        if result == analysis_id:
            print("✅ Storage completed successfully!")
            
            # Verify
            print("🔍 Verifying stored data...")
            verification = await storage.get_affiliate_research_by_topic(topic, user_id)
            
            if verification:
                print("✅ Verification passed!")
                print(f"   Session ID: {verification['session']['id']}")
                print(f"   Topic: {verification['session']['topic']}")
                print(f"   Programs: {len(verification['programs'])}")
                print(f"   Analysis Score: {verification['analysis']['profitability_score']}")
                print(f"   Analysis Level: {verification['analysis']['profitability_level']}")
                
                # Show table counts
                print("\n📊 Table counts after storage:")
                tables = [
                    'affiliate_research_sessions',
                    'affiliate_programs',
                    'affiliate_session_programs',
                    'affiliate_profitability_analysis'
                ]
                
                for table in tables:
                    try:
                        count_result = storage._execute_query('GET', f'{table}?select=id')
                        count = len(count_result['data']) if count_result['success'] else 0
                        print(f"   {table}: {count} records")
                    except Exception as e:
                        print(f"   {table}: Error - {e}")
                
                return True
            else:
                print("❌ Verification failed - no data found")
                return False
        else:
            print(f"❌ Storage failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner"""
    success = await test_storage_with_real_user()
    
    if success:
        print("\n🎉 Production test passed! Storage system is working correctly.")
        print("\n💡 The endpoint /api/v2/enhanced-trend-research will now properly:")
        print("   1. Store research sessions in affiliate_research_sessions")
        print("   2. Store individual programs in affiliate_programs") 
        print("   3. Create links in affiliate_session_programs")
        print("   4. Store analysis in affiliate_profitability_analysis")
    else:
        print("\n❌ Test failed. Check the logs above.")

if __name__ == "__main__":
    asyncio.run(main())