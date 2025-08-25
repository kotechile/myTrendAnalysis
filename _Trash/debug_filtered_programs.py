#!/usr/bin/env python3
"""
Debug script to see what programs are being filtered out
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from linkup_affiliate_research import linkup_affiliate_research

# Load environment variables
load_dotenv()

async def debug_filtered_programs():
    """Debug what programs are being filtered out"""
    
    topic = "Home Security Systems"
    
    print("🔍 Debugging filtered programs for topic:", topic)
    
    try:
        result = await linkup_affiliate_research.search_affiliate_programs(topic)
        
        print(f"\n📊 Raw Search Results:")
        search_results = result.get('search_results', [])
        
        all_raw_programs = []
        for search in search_results:
            subtopic = search.get('subtopic', 'N/A')
            programs = search.get('programs', [])
            print(f"\n📋 {subtopic}: {len(programs)} programs")
            
            for i, program in enumerate(programs):
                print(f"   {i+1}. {program.get('program_name', 'N/A')[:60]}...")
                print(f"      Commission: {program.get('commission_rate', 0)}% / ${program.get('commission_amount', 0)}")
                print(f"      Confidence: {program.get('extraction_confidence', 0)}")
                print(f"      Network: {program.get('network', 'N/A')}")
                
                # Check why it might be filtered
                reasons = []
                if program.get('commission_rate', 0) == 0 and program.get('commission_amount', 0) == 0:
                    reasons.append("No commission data")
                if program.get('extraction_confidence', 0) < 0.5:
                    reasons.append("Low confidence")
                if not program.get('program_name'):
                    reasons.append("No program name")
                
                if reasons:
                    print(f"      ⚠️ Filtered out: {', '.join(reasons)}")
                else:
                    print(f"      ✅ Valid program")
                
                all_raw_programs.append(program)
        
        print(f"\n📈 Summary:")
        print(f"   Total raw programs: {len(all_raw_programs)}")
        print(f"   With commission data: {len([p for p in all_raw_programs if p.get('commission_rate', 0) > 0 or p.get('commission_amount', 0) > 0])}")
        print(f"   High confidence: {len([p for p in all_raw_programs if p.get('extraction_confidence', 0) >= 0.5])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_filtered_programs())