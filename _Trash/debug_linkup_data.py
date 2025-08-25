#!/usr/bin/env python3
"""
Debug script to see what Linkup is actually returning
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from linkup_affiliate_research import linkup_affiliate_research

# Load environment variables
load_dotenv()

async def debug_linkup_data():
    """Debug what Linkup is actually returning"""
    
    topic = "Home Security Systems & Smart Home Technology"
    
    print("🔍 Debugging Linkup data for topic:", topic)
    
    try:
        result = await linkup_affiliate_research.search_affiliate_programs(topic)
        
        print(f"\n📊 Overall Results:")
        print(f"   Total Programs: {result.get('total_programs', 0)}")
        print(f"   Programs List: {len(result.get('programs', []))}")
        print(f"   Subtopics: {result.get('subtopics', [])}")
        
        print(f"\n📁 Detailed Program Data:")
        for i, program in enumerate(result.get('programs', [])):
            print(f"\n{i+1}. {program.get('program_name', 'N/A')}")
            print(f"   Network: {program.get('network', 'N/A')}")
            print(f"   Description: {program.get('description', 'N/A')[:100]}...")
            print(f"   Commission Rate: {program.get('commission_rate', 0)}%")
            print(f"   Commission Amount: ${program.get('commission_amount', 0)}")
            print(f"   URL: {program.get('program_url', 'N/A')}")
            print(f"   Confidence: {program.get('extraction_confidence', 0)}")
            print(f"   Approval Required: {program.get('approval_required', False)}")
        
        # Check search results for debugging
        print(f"\n🔍 Search Results Breakdown:")
        search_results = result.get('search_results', [])
        for i, search in enumerate(search_results):
            print(f"   {i+1}. Subtopic: {search.get('subtopic', 'N/A')}")
            print(f"      Programs Found: {search.get('programs_found', 0)}")
            
        # Show raw programs from search results
        print(f"\n📋 All Raw Programs Found:")
        all_programs = []
        for search in result.get('search_results', []):
            all_programs.extend(search.get('programs', []))
        
        print(f"   Total raw programs across all searches: {len(all_programs)}")
        
        # Show filtering stats
        print(f"\n📈 Filtering Statistics:")
        print(f"   Raw programs found: {len(all_programs)}")
        print(f"   After deduplication: {result.get('total_programs', 0)}")
        print(f"   After commission filter: {len([p for p in all_programs if p.get('commission_rate', 0) > 0 or p.get('commission_amount', 0) > 0])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_linkup_data())