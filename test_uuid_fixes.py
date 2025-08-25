#!/usr/bin/env python3
"""
Test script to verify UUID fixes in EnhancedSupabaseAffiliateStorage
"""

import asyncio
import uuid
import os
from datetime import datetime
from supabase_affiliate_storage_enhanced import EnhancedSupabaseAffiliateStorage

async def test_uuid_generation():
    """Test UUID generation and validation"""
    
    # Test with a short string that would cause UUID errors
    storage = EnhancedSupabaseAffiliateStorage()
    
    # Test _ensure_uuid method
    test_strings = [
        "short_id",
        "another_short",
        "1234567890",
        str(uuid.uuid4()),  # Already UUID
    ]
    
    print("Testing UUID generation from short strings:")
    for test_str in test_strings:
        uuid_result = storage._ensure_uuid(test_str)
        print(f"  '{test_str}' -> '{uuid_result}' (valid UUID: {len(uuid_result) == 36})")
    
    # Test program hash generation
    test_program = {
        'program_name': 'Test Affiliate Program',
        'company_name': 'Test Company',
        'signup_url': 'https://test.com/affiliate'
    }
    
    program_hash = storage._generate_program_hash(test_program)
    print(f"\nProgram hash: {program_hash}")
    print(f"Hash length: {len(program_hash)}")
    
    return True

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not installed. Make sure environment variables are set manually.")
    
    print("🧪 Testing UUID fixes...")
    print("=" * 50)
    
    asyncio.run(test_uuid_generation())
    print("✅ UUID generation test completed!")