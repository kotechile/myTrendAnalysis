#!/usr/bin/env python3
"""
Standalone test for UUID generation functionality
"""

import uuid
import hashlib
from datetime import datetime

def ensure_uuid(id_str: str) -> str:
    """Ensure proper UUID format - standalone version"""
    try:
        # If it's already a UUID, return it
        uuid.UUID(id_str)
        return id_str
    except ValueError:
        # Convert short string to UUID by hashing and creating a deterministic UUID
        hash_obj = hashlib.md5(id_str.encode())
        return str(uuid.UUID(hash_obj.hexdigest()))

def generate_program_hash(program_data: dict) -> str:
    """Generate program hash for deduplication"""
    key_fields = [
        program_data.get('program_name', ''),
        program_data.get('company_name', ''),
        program_data.get('signup_url', '')
    ]
    key_string = '|'.join([str(f).lower().strip() for f in key_fields])
    return hashlib.md5(key_string.encode()).hexdigest()

def main():
    """Test UUID generation and validation"""
    
    print("🧪 Testing UUID Generation and Validation")
    print("=" * 50)
    
    # Test _ensure_uuid method
    test_strings = [
        "short_id",
        "another_short",
        "1234567890",
        str(uuid.uuid4()),  # Already UUID
    ]
    
    print("Testing UUID generation from short strings:")
    for test_str in test_strings:
        uuid_result = ensure_uuid(test_str)
        is_valid = len(uuid_result) == 36 and uuid_result.count('-') == 4
        print(f"  '{test_str}' -> '{uuid_result}' (valid UUID: {is_valid})")
    
    # Test program hash generation
    test_program = {
        'program_name': 'Test Affiliate Program',
        'company_name': 'Test Company',
        'signup_url': 'https://test.com/affiliate'
    }
    
    program_hash = generate_program_hash(test_program)
    print(f"\nProgram hash: {program_hash}")
    print(f"Hash length: {len(program_hash)}")
    
    # Test consistency - same input should generate same UUID
    test_id = "amazon_affiliate"
    uuid1 = ensure_uuid(test_id)
    uuid2 = ensure_uuid(test_id)
    print(f"\nConsistency test:")
    print(f"  '{test_id}' -> Same UUID twice: {uuid1 == uuid2}")
    
    # Test with actual program data structure
    test_program_data = {
        'program_name': 'Amazon Associates',
        'company_name': 'Amazon',
        'signup_url': 'https://affiliate-program.amazon.com',
        'commission_rate': '4%',
        'description': 'Amazon affiliate program',
        'cookie_duration': '24 hours'
    }
    
    # Test complete flow
    program_hash = generate_program_hash(test_program_data)
    program_uuid = ensure_uuid(f"program_{program_hash}")
    
    print(f"\nComplete flow test:")
    print(f"  Program: {test_program_data['program_name']}")
    print(f"  Hash: {program_hash}")
    print(f"  UUID: {program_uuid}")
    print(f"  Valid UUID: {len(program_uuid) == 36 and program_uuid.count('-') == 4}")
    
    return True

if __name__ == "__main__":
    main()
    print("\n✅ UUID generation test completed successfully!")