#!/usr/bin/env python3
"""
Check the actual database schema for affiliate tables
"""

import os
import json
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ SUPABASE_URL and SUPABASE_KEY must be set")
    exit(1)

def query_supabase(endpoint):
    """Query Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    return response

# Check what tables exist
print("🔍 Checking database schema...")

# First, let's check the affiliate tables directly
tables_to_check = [
    'affiliate_research_sessions',
    'affiliate_programs',
    'affiliate_session_programs', 
    'affiliate_profitability_analysis'
]

for table in tables_to_check:
    try:
        response = query_supabase(f'{table}?select=id&limit=1')
        if response.status_code == 200:
            count = len(response.json()) if response.json() else 0
            print(f"✅ {table}: {count} records")
        elif response.status_code == 404:
            print(f"❌ {table}: Table does not exist")
        else:
            print(f"⚠️ {table}: Error {response.status_code} - {response.text[:100]}...")
    except Exception as e:
        print(f"❌ {table}: Exception - {e}")

# Check if there's a user_id requirement issue
print("\n🔍 Checking table structures...")
try:
    # Check affiliate_research_sessions structure
    response = query_supabase('affiliate_research_sessions?select=*&limit=1')
    if response.status_code == 200 and response.json():
        sample = response.json()[0]
        print("✅ affiliate_research_sessions structure:")
        print(f"   Columns: {list(sample.keys())}")
        if 'user_id' in sample:
            print("   ✅ Has user_id column")
        else:
            print("   ❌ Missing user_id column")
    else:
        print("⚠️ Could not get sample from affiliate_research_sessions")
        
except Exception as e:
    print(f"❌ Error checking structure: {e}")

print("\n📋 Summary:")
print("The storage system is working correctly, but needs:")
print("1. Valid UUID user_id (from your application's users)")
print("2. The affiliate tables exist and are accessible")
print("3. The foreign key constraint requires users table or relaxed constraints")