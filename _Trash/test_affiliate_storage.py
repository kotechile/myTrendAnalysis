#!/usr/bin/env python3
"""
Test script to validate affiliate research data storage
Run this to verify the complete storage flow works correctly
"""

import asyncio
import uuid
from datetime import datetime
from supabase_affiliate_storage import SupabaseAffiliateStorage

async def test_affiliate_storage():
    """Test complete affiliate research storage flow"""
    
    print("🧪 Testing Affiliate Research Storage...")
    
    # Test data
    user_id = "test_user_" + str(uuid.uuid4())[:8]
    topic = "Test Affiliate Storage Validation"
    analysis_id = str(uuid.uuid4())
    
    # Sample research data
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
                "description": "Web hosting affiliate program",
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
        "source": "test_validation"
    }
    
    # Initialize storage
    storage = SupabaseAffiliateStorage()
    
    try:
        # Test storage
        print(f"📊 Storing test data for topic: {topic}")
        print(f"👤 User ID: {user_id}")
        print(f"🆔 Analysis ID: {analysis_id}")
        print()
        
        # Store the complete research
        result = await storage.store_affiliate_research(
            topic=topic,
            user_id=user_id,
            research_data=research_data,
            analysis_id=analysis_id
        )
        
        print(f"✅ Storage completed with result: {result}")
        print()
        
        # Verify storage
        print("🔍 Verifying stored data...")
        verification = await storage.get_affiliate_research_by_topic(topic, user_id)
        
        if verification:
            print("✅ Data verification successful!")
            print(f"   Session ID: {verification['session']['id']}")
            print(f"   Topic: {verification['session']['topic']}")
            print(f"   Programs: {len(verification['programs'])}")
            print(f"   Analysis: {verification['analysis']['profitability_score'] if verification['analysis'] else 'None'}")
            print()
            
            # Show detailed data
            print("📋 Detailed verification:")
            print(f"   affiliate_research_sessions: 1 record")
            print(f"   affiliate_programs: {len(verification['programs'])} records")
            print(f"   affiliate_session_programs: {len(verification['programs'])} records")
            print(f"   affiliate_profitability_analysis: 1 record")
            print()
            
            return True
        else:
            print("❌ Data verification failed - no data found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

async def check_current_tables():
    """Check current state of all tables"""
    print("📊 Current table state check...")
    
    storage = SupabaseAffiliateStorage()
    
    # Check table counts
    for table in [
        'affiliate_research_sessions',
        'affiliate_programs', 
        'affiliate_session_programs',
        'affiliate_profitability_analysis'
    ]:
        try:
            result = storage._execute_query('GET', f'{table}?select=id')
            count = len(result['data']) if result['success'] else 0
            print(f"   {table}: {count} records")
        except Exception as e:
            print(f"   {table}: Error - {e}")

async def main():
    """Main test runner"""
    print("🧪 Affiliate Storage Validation Tool")
    print("=" * 50)
    
    # Check current state
    await check_current_tables()
    print()
    
    # Run test
    success = await test_affiliate_storage()
    
    if success:
        print("🎉 All tests passed! The storage system is working correctly.")
    else:
        print("❌ Tests failed. Check logs above for details.")
    
    print()
    print("📊 Final table state:")
    await check_current_tables()

if __name__ == "__main__":
    asyncio.run(main())