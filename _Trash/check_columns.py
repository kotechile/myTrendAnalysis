#!/usr/bin/env python3
"""
Check actual column structure of affiliate tables
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}'
}

def check_table_structure(table_name):
    """Check table structure"""
    print(f"\n🔍 Checking {table_name} structure...")
    
    # Try to get a sample record
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&limit=1"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            columns = list(data[0].keys())
            print(f"✅ {table_name} columns: {columns}")
            return columns
        else:
            print(f"✅ {table_name} exists but empty")
            # Try to get column info from empty table
            url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&limit=0"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"   Table accessible")
            return []
    else:
        print(f"❌ {table_name}: {response.status_code} - {response.text}")
        return []

# Check all affiliate tables
tables = [
    'affiliate_research_sessions',
    'affiliate_programs',
    'affiliate_session_programs',
    'affiliate_profitability_analysis'
]

for table in tables:
    check_table_structure(table)

print("\n📋 Summary:")
print("Make sure your session data matches exactly the columns in the tables!")