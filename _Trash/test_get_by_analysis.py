#!/usr/bin/env python3
"""
Test script for the new /api/v2/affiliate-research/get-by-analysis endpoint
"""

import requests
import json
import uuid

def test_get_by_analysis_endpoint():
    """Test the new endpoint"""
    
    # Base URL - adjust for your server
    base_url = "http://localhost:5000"  # Update with your actual server URL
    
    # Test parameters - use actual values from your database
    trend_analysis_id = "test-analysis-id"  # Replace with actual trend_analysis_id
    user_id = "test-user-id"  # Replace with actual user_id
    
    print("🧪 Testing /api/v2/affiliate-research/get-by-analysis endpoint")
    print(f"📊 Parameters: trend_analysis_id={trend_analysis_id}, user_id={user_id}")
    
    try:
        # Test with invalid parameters first
        response = requests.get(f"{base_url}/api/v2/affiliate-research/get-by-analysis")
        print(f"\n1️⃣ Test missing parameters: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
        # Test with invalid UUID
        response = requests.get(f"{base_url}/api/v2/affiliate-research/get-by-analysis?trend_analysis_id=invalid-uuid&user_id=invalid-uuid")
        print(f"\n2️⃣ Test invalid UUID: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
        # Test with valid but non-existent parameters
        test_uuid = str(uuid.uuid4())
        response = requests.get(f"{base_url}/api/v2/affiliate-research/get-by-analysis?trend_analysis_id={test_uuid}&user_id={test_uuid}")
        print(f"\n3️⃣ Test non-existent data: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
        # Test with valid parameters (replace with actual values)
        # response = requests.get(f"{base_url}/api/v2/affiliate-research/get-by-analysis?trend_analysis_id=YOUR_ACTUAL_ID&user_id=YOUR_ACTUAL_USER_ID")
        # print(f"\n4️⃣ Test with valid data: {response.status_code}")
        # if response.status_code == 200:
        #     data = response.json()
        #     print("✅ Success! Data structure:")
        #     print(json.dumps(data, indent=2))
        # else:
        #     print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        print("💡 Make sure your server is running and accessible")

if __name__ == "__main__":
    test_get_by_analysis_endpoint()