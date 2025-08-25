#!/usr/bin/env python3
"""
Debug script to check affiliate storage and data structure
"""

import asyncio
import os
import json
from working_supabase_integration import RLSSupabaseStorage

async def check_affiliate_storage():
    """Check what affiliate data is actually stored"""
    
    # Use environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase environment variables")
        return
    
    storage = RLSSupabaseStorage()
    
    # Test user ID from logs
    user_id = "f248b7ed-b8df-4464-8544-8304d7ae4c30"
    storage.set_user_context(user_id)
    
    print("🔍 Checking affiliate storage for user:", user_id)
    
    # Check affiliate_programs table
    print("\n📋 Checking affiliate_programs table...")
    programs = storage._execute_query('GET', 'affiliate_programs?select=*')
    if programs['success']:
        print(f"✅ Found {len(programs['data'])} programs")
        for i, program in enumerate(programs['data'][:3]):  # Show first 3
            print(f"  {i+1}. {program.get('program_name', 'N/A')}")
            print(f"     Network: {program.get('network', 'N/A')}")
            print(f"     Description: {program.get('description', 'N/A')[:100]}...")
            print(f"     Commission: {program.get('commission_rate', 0)}% / ${program.get('commission_amount', 0)}")
            print()
    else:
        print(f"❌ Error: {programs.get('error')}")
    
    # Check affiliate_research_sessions
    print("\n📊 Checking affiliate_research_sessions...")
    sessions = storage._execute_query('GET', f'affiliate_research_sessions?user_id=eq.{user_id}&select=*')
    if sessions['success']:
        print(f"✅ Found {len(sessions['data'])} research sessions")
        for session in sessions['data']:
            print(f"  Session: {session.get('topic', 'N/A')}")
            print(f"  Programs: {session.get('total_programs', 0)}")
            print(f"  Score: {session.get('profitability_score', 0)}")
            print()
    else:
        print(f"❌ Error: {sessions.get('error')}")
    
    # Check affiliate_session_programs (links)
    print("\n🔗 Checking affiliate_session_programs...")
    links = storage._execute_query('GET', f'affiliate_session_programs?select=*,affiliate_programs(*)')
    if links['success']:
        print(f"✅ Found {len(links['data'])} program-session links")
        for link in links['data'][:3]:
            program = link.get('affiliate_programs', {})
            print(f"  - {program.get('program_name', 'N/A')} (relevance: {link.get('relevance_score', 0)})")
    else:
        print(f"❌ Error: {links.get('error')}")

if __name__ == "__main__":
    asyncio.run(check_affiliate_storage())