#!/usr/bin/env python3
"""
Debug script to test Noodl frontend data access and validate PyTrends integration
"""

import os
import sys
import json
import asyncio
from datetime import datetime

# Add this directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed, using environment variables")

# Import the RLS Supabase storage
from working_supabase_integration import RLSSupabaseStorage

def test_noodl_data_access():
    """Test Noodl frontend data access patterns"""
    
    print("🧪 Testing Noodl Frontend Data Access...")
    print("=" * 60)
    
    # Test data - using your actual analysis ID
    analysis_id = "9ff218cc-f27a-4f3e-8267-5f1f88d887b8"
    user_id = "00000000-0000-0000-0000-000000000000"  # Use a dummy user ID for testing
    
    try:
        # Initialize storage
        storage = RLSSupabaseStorage()
        
        # Test the get_trend_analysis_for_phase2 method
        async def fetch_data():
            return await storage.get_trend_analysis_for_phase2(analysis_id, user_id)
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            data = loop.run_until_complete(fetch_data())
            loop.close()
            
            print("✅ Successfully retrieved data from Supabase")
            
            # Analyze the structure
            print(f"\n📊 Data Structure Analysis:")
            print(f"   Analysis ID: {data.get('trend_analysis_id')}")
            print(f"   Has analysis_info: {bool(data.get('analysis_info'))}")
            print(f"   Has trending_topics: {bool(data.get('trending_topics'))}")
            print(f"   Has content_opportunities: {bool(data.get('content_opportunities'))}")
            print(f"   Has keyword_intelligence: {bool(data.get('keyword_intelligence'))}")
            
            # Check for PyTrends data
            analysis_info = data.get('analysis_info', {})
            metadata = analysis_info.get('metadata', {})
            
            print(f"\n🔍 PyTrends Data Check:")
            print(f"   Analysis_info keys: {list(analysis_info.keys()) if analysis_info else 'None'}")
            print(f"   Metadata keys: {list(metadata.keys()) if metadata else 'None'}")
            
            pytrends_analysis = metadata.get('pytrends_analysis', {})
            print(f"   Has pytrends_analysis: {bool(pytrends_analysis)}")
            
            if pytrends_analysis:
                print(f"   PyTrends keys: {list(pytrends_analysis.keys())}")
                seasonal = pytrends_analysis.get('seasonal_patterns', {})
                print(f"   Seasonal success: {seasonal.get('analysis_success', False)}")
                print(f"   Seasonal data points: {seasonal.get('data_points', 0)}")
                print(f"   Has seasonal pattern: {seasonal.get('has_seasonal_pattern', False)}")
            else:
                print("   ❌ No PyTrends data found in metadata")
            
            # Check data completeness
            trending_topics = data.get('trending_topics', [])
            content_opportunities = data.get('content_opportunities', [])
            
            print(f"\n📈 Content Summary:")
            print(f"   Trending topics: {len(trending_topics)}")
            print(f"   Content opportunities: {len(content_opportunities)}")
            
            if trending_topics:
                print(f"   First topic: {trending_topics[0].get('title', 'No title')}")
            
            # Check if this structure matches Noodl expectations
            print(f"\n🎯 Noodl Compatibility Check:")
            
            # Expected structure for Noodl overview
            expected_keys = [
                'analysis_info', 'trending_topics', 'content_opportunities', 
                'keyword_intelligence', 'pytrends_analysis'
            ]
            
            for key in expected_keys:
                if key in data:
                    print(f"   ✅ {key}: present")
                else:
                    print(f"   ❌ {key}: missing")
            
            # Save debug output
            debug_output = {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "data_summary": {
                    "analysis_info_keys": list(analysis_info.keys()) if analysis_info else [],
                    "metadata_keys": list(metadata.keys()) if metadata else [],
                    "trending_topics_count": len(trending_topics),
                    "content_opportunities_count": len(content_opportunities),
                    "has_pytrends": bool(pytrends_analysis),
                    "pytrends_keys": list(pytrends_analysis.keys()) if pytrends_analysis else []
                },
                "sample_data": {
                    "first_trending_topic": trending_topics[0] if trending_topics else None,
                    "metadata_sample": {k: str(v)[:100] + "..." if len(str(v)) > 100 else v 
                                      for k, v in metadata.items()} if metadata else None
                }
            }
            
            with open('debug_noodl_output.json', 'w') as f:
                json.dump(debug_output, f, indent=2, default=str)
            
            print(f"\n💾 Debug output saved to debug_noodl_output.json")
            
            return data
            
        except Exception as e:
            loop.close()
            raise e
            
    except Exception as e:
        print(f"❌ Error retrieving data: {e}")
        return None

def test_api_endpoint():
    """Test the actual API endpoint"""
    import requests
    
    print("\n🌐 Testing API Endpoint...")
    print("=" * 60)
    
    analysis_id = "9ff218cc-f27a-4f3e-8267-5f1f88d887b8"
    user_id = "00000000-0000-0000-0000-000000000000"
    
    try:
        # Test the API endpoint
        response = requests.get(
            f"http://localhost:5000/api/v2/trend-analysis/{analysis_id}",
            params={"user_id": user_id}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint working")
            print(f"   Response keys: {list(data.keys())}")
            
            if 'trend_analysis' in data:
                analysis = data['trend_analysis']
                print(f"   Analysis keys: {list(analysis.keys())}")
                
                # Check PyTrends in API response
                analysis_info = analysis.get('analysis_info', {})
                metadata = analysis_info.get('metadata', {})
                pytrends = metadata.get('pytrends_analysis', {})
                
                print(f"   API has PyTrends: {bool(pytrends)}")
                
            return data
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python noodl_server.py")
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    # Test direct Supabase access
    data = test_noodl_data_access()
    
    # Test API endpoint (optional, requires server running)
    # test_api_endpoint()
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)