#!/usr/bin/env python3
"""
Complete Supabase validation guide for trend analysis data
Shows exactly what tables to check and how to verify data storage
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def validate_supabase_structure():
    """Validate all Supabase tables and data structure for trend analysis"""
    
    print("🔍 SUPABASE TREND ANALYSIS VALIDATION GUIDE")
    print("=" * 60)
    
    try:
        from working_supabase_integration import RLSSupabaseStorage
        storage = RLSSupabaseStorage()
        
        # 1. CHECK TABLE STRUCTURE
        print("\n📊 TABLE STRUCTURE VERIFICATION:")
        print("-" * 40)
        
        # Main tables to check
        tables = [
            'trend_analyses',
            'trending_topics', 
            'content_opportunities',
            'keyword_intelligence',
            'affiliate_programs'
        ]
        
        for table in tables:
            try:
                response = storage._execute_query('GET', f'{table}?limit=1')
                if response['success']:
                    print(f"✅ {table}: EXISTS ({len(response['data'])} records)")
                else:
                    print(f"❌ {table}: ERROR - {response.get('error')}")
            except Exception as e:
                print(f"❌ {table}: FAILED - {str(e)}")
        
        # 2. CHECK TREND ANALYSES TABLE DETAILS
        print("\n📈 TREND_ANALYSES TABLE DETAILS:")
        print("-" * 40)
        
        response = storage._execute_query('GET', 'trend_analyses?limit=5&order=created_at.desc')
        if response['success'] and response['data']:
            for i, record in enumerate(response['data'][:3], 1):
                print(f"\nRecord {i}:")
                print(f"  ID: {record.get('id')}")
                print(f"  Topic: {record.get('topic')}")
                print(f"  Status: {record.get('status')}")
                print(f"  User ID: {record.get('user_id')}")
                print(f"  Created: {record.get('created_at')}")
                
                # Check metadata structure
                metadata = record.get('metadata', {})
                if metadata:
                    print(f"  Has PyTrends: {'pytrends_analysis' in metadata}")
                    print(f"  Has Affiliate: 'affiliate_research_data' in metadata")
                    print(f"  Metadata keys: {list(metadata.keys())}")
        
        # 3. CHECK RELATED TABLES
        print("\n🔗 RELATED TABLE VERIFICATION:")
        print("-" * 40)
        
        # Get latest trend analysis ID
        latest_response = storage._execute_query('GET', 'trend_analyses?limit=1&order=created_at.desc')
        if latest_response['success'] and latest_response['data']:
            latest_id = latest_response['data'][0]['id']
            print(f"Latest Analysis ID: {latest_id}")
            
            # Check related data for this ID
            related_checks = [
                ('trending_topics', f'trending_topics?trend_analysis_id=eq.{latest_id}'),
                ('content_opportunities', f'content_opportunities?trend_analysis_id=eq.{latest_id}'),
                ('keyword_intelligence', f'keyword_intelligence?trend_analysis_id=eq.{latest_id}')
            ]
            
            for table_name, query in related_checks:
                response = storage._execute_query('GET', query)
                if response['success']:
                    count = len(response['data'])
                    print(f"  {table_name}: {count} records")
                    if count > 0 and table_name == 'trending_topics':
                        print(f"    Sample: {response['data'][0].get('title', 'N/A')}")
                    elif count > 0 and table_name == 'content_opportunities':
                        print(f"    Sample: {response['data'][0].get('title', 'N/A')}")
        
        # 4. SHOW EXAMPLE QUERIES FOR VALIDATION
        print("\n📝 EXAMPLE SUPABASE QUERIES:")
        print("-" * 40)
        
        user_id_example = "f248b7ed-b8df-4464-8544-8304d7ae4c30"  # From your logs
        
        queries = [
            # Basic trend analysis check
            f"SELECT id, topic, created_at FROM trend_analyses WHERE user_id = '{user_id_example}' ORDER BY created_at DESC LIMIT 10",
            
            # Detailed trend analysis with metadata
            f"SELECT id, topic, metadata->'pytrends_analysis' as pytrends FROM trend_analyses WHERE user_id = '{user_id_example}' ORDER BY created_at DESC LIMIT 5",
            
            # Trending topics for specific analysis
            f"SELECT tt.* FROM trending_topics tt JOIN trend_analyses ta ON tt.trend_analysis_id = ta.id WHERE ta.user_id = '{user_id_example}' ORDER BY tt.created_at DESC LIMIT 10",
            
            # Content opportunities check
            f"SELECT co.* FROM content_opportunities co JOIN trend_analyses ta ON co.trend_analysis_id = ta.id WHERE ta.user_id = '{user_id_example}' ORDER BY co.created_at DESC LIMIT 5",
            
            # Keyword intelligence check
            f"SELECT ki.* FROM keyword_intelligence ki JOIN trend_analyses ta ON ki.trend_analysis_id = ta.id WHERE ta.user_id = '{user_id_example}' ORDER BY ki.created_at DESC LIMIT 5",
            
            # Affiliate programs check
            f"SELECT program_name, commission_rate, network FROM affiliate_programs ORDER BY created_at DESC LIMIT 10"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nQuery {i}:")
            print(f"  {query}")
        
        # 5. CREATE VALIDATION CHECKLIST
        print("\n✅ VALIDATION CHECKLIST:")
        print("-" * 40)
        
        checklist = [
            "1. Check trend_analyses table exists",
            "2. Verify records have metadata field with pytrends_analysis",
            "3. Confirm trending_topics has data linked to trend_analysis_id",
            "4. Verify content_opportunities has data linked to trend_analysis_id", 
            "5. Check keyword_intelligence has data linked to trend_analysis_id",
            "6. Validate RLS policies allow user to see their data",
            "7. Confirm affiliate_programs has commission data",
            "8. Check that user_id matches records in all tables"
        ]
        
        for item in checklist:
            print(f"  {item}")
        
        # 6. SHOW DIRECT SQL QUERIES FOR SUPABASE DASHBOARD
        print("\n🎯 DIRECT SQL QUERIES FOR SUPABASE DASHBOARD:")
        print("-" * 40)
        
        sql_queries = [
            "-- Get all trend analyses for user",
            f"SELECT * FROM trend_analyses WHERE user_id = '{user_id_example}' ORDER BY created_at DESC;",
            
            "-- Get trend analysis with PyTrends data",
            f"SELECT id, topic, created_at, (metadata->'pytrends_analysis'->>'pytrends_enhanced')::boolean as has_pytrends FROM trend_analyses WHERE user_id = '{user_id_example}';",
            
            "-- Get trending topics with analysis context",
            f"SELECT ta.topic, tt.title, tt.viral_potential, tt.created_at FROM trend_analyses ta JOIN trending_topics tt ON ta.id = tt.trend_analysis_id WHERE ta.user_id = '{user_id_example}';",
            
            "-- Get content opportunities with monetization",
            f"SELECT ta.topic, co.title, co.format, co.difficulty, co.created_at FROM trend_analyses ta JOIN content_opportunities co ON ta.id = co.trend_analysis_id WHERE ta.user_id = '{user_id_example}';",
            
            "-- Get affiliate programs with commission data",
            "SELECT program_name, commission_rate || '%' as commission, network, created_at FROM affiliate_programs ORDER BY created_at DESC LIMIT 20;",
            
            "-- Get comprehensive analysis summary",
            f"SELECT ta.id, ta.topic, ta.created_at, (SELECT COUNT(*) FROM trending_topics WHERE trend_analysis_id = ta.id) as topics_count, (SELECT COUNT(*) FROM content_opportunities WHERE trend_analysis_id = ta.id) as opportunities_count, (SELECT COUNT(*) FROM keyword_intelligence WHERE trend_analysis_id = ta.id) as keywords_count FROM trend_analyses ta WHERE ta.user_id = '{user_id_example}' ORDER BY ta.created_at DESC;"
        ]
        
        for query in sql_queries:
            print(f"\n{query}")
        
        # 7. SHOW HOW TO ACCESS PYTRENDS DATA
        print("\n🔍 HOW TO ACCESS PYTRENDS DATA:")
        print("-" * 40)
        print("PyTrends data is stored in the 'metadata' JSONB field of trend_analyses table")
        print("Access it with JSON queries:")
        print()
        print("# Get PyTrends insights:")
        print("SELECT metadata->'pytrends_analysis'->'actionable_insights' FROM trend_analyses WHERE id = 'analysis_id';")
        print()
        print("# Get geographic hotspots:")
        print("SELECT metadata->'pytrends_analysis'->'geographic_insights'->'global_hotspots' FROM trend_analyses WHERE id = 'analysis_id';")
        print()
        print("# Get trend direction:")
        print("SELECT metadata->'pytrends_analysis'->'main_topic_analysis'->>'trend_direction' FROM trend_analyses WHERE id = 'analysis_id';")
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(validate_supabase_structure())