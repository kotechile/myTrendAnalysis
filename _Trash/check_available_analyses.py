#!/usr/bin/env python3
"""
Check available trend analyses in Supabase
"""

import os
import sys
import json
from datetime import datetime

# Add this directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the RLS Supabase storage
from working_supabase_integration import RLSSupabaseStorage

# Set environment variables
os.environ['SUPABASE_URL'] = 'https://dgcsqiaciyqvprtpopxg.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRnY3NxaWFjaXlxdnBydHBvcHhnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxNTQ3NTk5MywiZXhwIjoyMDMxMDUxOTkzfQ.wXVY743o8sX2waD03EenpvTjAdmrwT4eEt6lgWIMaC0'

def check_available_analyses():
    """Check what trend analyses are available"""
    
    print("🔍 Checking available trend analyses...")
    print("=" * 60)
    
    try:
        storage = RLSSupabaseStorage()
        
        # Get all trend analyses (without user filtering to see all)
        result = storage._execute_query('GET', 'trend_analyses?select=*&order=created_at.desc&limit=20')
        
        if result['success'] and result['data']:
            analyses = result['data']
            print(f"✅ Found {len(analyses)} trend analyses")
            
            for i, analysis in enumerate(analyses):
                print(f"\n📊 Analysis {i+1}:")
                print(f"   ID: {analysis['id']}")
                print(f"   Topic: {analysis['topic']}")
                print(f"   User ID: {analysis['user_id']}")
                print(f"   Success: {analysis['analysis_success']}")
                print(f"   Created: {analysis['created_at']}")
                
                # Check metadata
                metadata = analysis.get('metadata', {})
                if metadata:
                    print(f"   ✅ Has metadata")
                    print(f"   Confidence: {metadata.get('confidence_score', 'N/A')}")
                    print(f"   Has PyTrends: {'pytrends_analysis' in metadata}")
                    
                    if 'pytrends_analysis' in metadata:
                        pytrends = metadata['pytrends_analysis']
                        print(f"   PyTrends keys: {list(pytrends.keys())}")
                        
                        seasonal = pytrends.get('seasonal_patterns', {})
                        print(f"   Seasonal success: {seasonal.get('analysis_success', False)}")
                        print(f"   Seasonal data points: {seasonal.get('data_points', 0)}")
                else:
                    print(f"   ❌ No metadata")
                    
            return analyses
        else:
            print(f"❌ No analyses found or error: {result.get('error', 'Unknown')}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    analyses = check_available_analyses()
    
    if analyses:
        print(f"\n" + "=" * 60)
        print("RECOMMENDATION: Use one of these analysis IDs in your Noodl frontend")
        print("=" * 60)
        for analysis in analyses[:3]:
            print(f"   ID: {analysis['id']} (Topic: {analysis['topic']})")