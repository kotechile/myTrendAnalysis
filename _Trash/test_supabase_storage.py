#!/usr/bin/env python3
"""
Test script to verify Supabase storage is working correctly
"""

import asyncio
import os
from dotenv import load_dotenv
from linkup_affiliate_research import linkup_affiliate_research
from supabase_affiliate_storage import affiliate_storage

# Load environment variables
load_dotenv()

async def test_supabase_storage():
    """Test storing affiliate research in Supabase"""
    
    topic = "Home Security Systems"
    # Use a system user ID for testing
    user_id = "system-user-123"
    
    print("🔍 Testing Supabase storage...")
    
    try:
        # 1. Run affiliate research
        print("📊 Running affiliate research...")
        research_result = await linkup_affiliate_research.search_affiliate_programs(topic)
        
        print(f"✅ Found {research_result['total_programs']} programs")
        print(f"✅ Found {len(research_result['programs'])} valid programs with commission data")
        
        # Show the valid programs
        valid_programs = [p for p in research_result['programs'] if p.get('commission_rate', 0) > 0 or p.get('commission_amount', 0) > 0]
        print(f"\n📋 Valid programs with commission data:")
        for i, program in enumerate(valid_programs, 1):
            print(f"   {i}. {program.get('program_name', 'N/A')} - {program.get('commission_rate', 0)}%")
        
        # 2. Store in Supabase
        print(f"\n💾 Storing {len(valid_programs)} programs in Supabase...")
        session_id = await affiliate_storage.store_affiliate_research(
            topic=topic,
            user_id=user_id,
            research_data=research_result
        )
        
        print(f"✅ Successfully stored research session: {session_id}")
        
        # 3. Check what programs are in Supabase
        print("\n📖 Checking stored programs...")
        
        # Simple check by querying the affiliate_programs table directly
        try:
            from working_supabase_integration import RLSSupabaseStorage
            storage = RLSSupabaseStorage()
            
            # Get all programs
            response = storage._execute_query('GET', 'affiliate_programs?select=*&order=created_at.desc&limit=20')
            if response['success']:
                programs = response['data']
                print(f"✅ Found {len(programs)} total programs in Supabase")
                
                if programs:
                    print(f"\n📋 Programs in Supabase:")
                    for i, program in enumerate(programs, 1):
                        print(f"   {i}. {program.get('program_name', 'N/A')} - Network: {program.get('network', 'N/A')}")
                        print(f"      Commission: {program.get('commission_rate', 0)}% / ${program.get('commission_amount', 0)}")
                        print(f"      URL: {program.get('program_url', 'N/A')}")
                else:
                    print("❌ No programs found in Supabase")
            else:
                print(f"❌ Error checking programs: {response.get('error')}")
                
        except Exception as e:
            print(f"❌ Error checking storage: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_supabase_storage())