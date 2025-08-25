#!/usr/bin/env python3
"""
Check what trend analysis data is stored in Supabase for a specific analysis ID
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_trend_analysis_storage():
    """Verify trend analysis data is properly stored"""
    
    # Analysis ID from your logs
    analysis_id = "2ec896ae-bdfc-4e64-b3ab-697bce742cad"
    user_id = "f248b7ed-b8df-4464-8544-8304d7ae4c30"
    
    print("🔍 Checking trend analysis storage...")
    print(f"Analysis ID: {analysis_id}")
    print(f"User ID: {user_id}")
    
    try:
        from working_supabase_integration import RLSSupabaseStorage
        storage = RLSSupabaseStorage()
        
        # 1. Check main trend analysis record
        print("\n📊 Main trend analysis record:")
        response = storage._execute_query(
            'GET', 
            f'trend_analyses?id=eq.{analysis_id}&user_id=eq.{user_id}'
        )
        
        if response['success'] and response['data']:
            record = response['data'][0]
            print(f"✅ Found trend analysis record")
            print(f"   Topic: {record.get('topic')}")
            print(f"   Status: {record.get('status')}")
            print(f"   Created: {record.get('created_at')}")
            
            # Check PyTrends data in metadata
            metadata = record.get('metadata', {})
            pytrends = metadata.get('pytrends_analysis', {})
            
            print(f"\n📈 PyTrends data found:")
            print(f"   Enhanced: {pytrends.get('pytrends_enhanced', False)}")
            print(f"   Topic analyzed: {pytrends.get('topic_analyzed')}")
            print(f"   Timestamp: {pytrends.get('analysis_timestamp')}")
            
            # Insights count
            insights = pytrends.get('actionable_insights', [])
            print(f"   Actionable insights: {len(insights)}")
            
            # Geographic data
            geo = pytrends.get('geographic_insights', {})
            hotspots = geo.get('global_hotspots', [])
            print(f"   Geographic hotspots: {len(hotspots)}")
            
            if insights:
                print(f"\n💡 Top insights:")
                for i, insight in enumerate(insights[:3], 1):
                    print(f"   {i}. {insight.get('title', 'N/A')}")
                    print(f"      {insight.get('action', 'N/A')}")
                    
        else:
            print("❌ No trend analysis record found")
            return
            
        # 2. Check related trending topics
        print(f"\n🔥 Trending topics:")
        topics_response = storage._execute_query(
            'GET', 
            f'trending_topics?trend_analysis_id=eq.{analysis_id}'
        )
        
        if topics_response['success'] and topics_response['data']:
            topics = topics_response['data']
            print(f"✅ Found {len(topics)} trending topics")
            for i, topic in enumerate(topics[:5], 1):
                print(f"   {i}. {topic.get('topic', 'N/A')} - Trend: {topic.get('trend_score', 'N/A')}")
        
        # 3. Check content opportunities
        print(f"\n🎯 Content opportunities:")
        opportunities_response = storage._execute_query(
            'GET', 
            f'content_opportunities?trend_analysis_id=eq.{analysis_id}'
        )
        
        if opportunities_response['success'] and opportunities_response['data']:
            opportunities = opportunities_response['data']
            print(f"✅ Found {len(opportunities)} content opportunities")
            for i, opp in enumerate(opportunities[:5], 1):
                print(f"   {i}. {opp.get('title', 'N/A')}")
                
        # 4. Check keyword intelligence
        print(f"\n🔍 Keyword intelligence:")
        keywords_response = storage._execute_query(
            'GET', 
            f'keyword_intelligence?trend_analysis_id=eq.{analysis_id}'
        )
        
        if keywords_response['success'] and keywords_response['data']:
            keywords = keywords_response['data']
            print(f"✅ Found {len(keywords)} keyword insights")
            for i, kw in enumerate(keywords[:3], 1):
                print(f"   {i}. {kw.get('keyword', 'N/A')} - Volume: {kw.get('search_volume', 'N/A')}")
        
        # 5. Show actual database query for verification
        print(f"\n📋 Database verification:")
        print("You can run these queries in Supabase SQL editor:")
        print(f"""
-- Check trend analysis with PyTrends data
SELECT 
    id,
    topic,
    created_at,
    (metadata->'pytrends_analysis'->>'pytrends_enhanced')::boolean as pytrends_available,
    json_array_length(metadata->'pytrends_analysis'->'actionable_insights') as insights_count
FROM trend_analyses 
WHERE id = '{analysis_id}';

-- Check all related data
SELECT 'trending_topics' as table_name, count(*) as count
FROM trending_topics WHERE trend_analysis_id = '{analysis_id}'
UNION ALL
SELECT 'content_opportunities', count(*) 
FROM content_opportunities WHERE trend_analysis_id = '{analysis_id}'
UNION ALL
SELECT 'keyword_intelligence', count(*) 
FROM keyword_intelligence WHERE trend_analysis_id = '{analysis_id}';
        """)
        
    except Exception as e:
        print(f"❌ Error checking storage: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_trend_analysis_storage())