#!/usr/bin/env python3
"""
Example usage of the Keyword Modifier Enhancement System
Shows how to integrate modifier keywords with existing workflow
"""

import asyncio
import json
from keyword_modifier_enhancer import KeywordModifierEnhancer, integrate_with_existing_system

def demo_keyword_modifiers():
    """Demonstrate keyword modifier enhancement"""
    
    print("🚀 Keyword Modifier Enhancement Demo")
    print("=" * 50)
    
    # Example base keywords from trend analysis
    base_keywords = [
        "digital marketing",
        "content strategy", 
        "social media management",
        "SEO optimization",
        "email marketing"
    ]
    
    # Initialize enhancer
    enhancer = KeywordModifierEnhancer()
    
    # Generate enhanced keywords
    print("\n📊 Generating enhanced keyword combinations...")
    enhanced_data = enhancer.enhance_keywords_with_modifiers(
        base_keywords, 
        target_audience="professional",
        max_combinations=3
    )
    
    # Display results
    print(f"\n✅ Enhanced {len(base_keywords)} base keywords")
    print(f"📈 Generated {enhanced_data['total_opportunities']} new keyword opportunities")
    
    print("\n🎯 Modifier Usage Breakdown:")
    for category, count in enhanced_data["modifier_usage"].items():
        print(f"   {category.replace('_', ' ').title()}: {count} combinations")
    
    print("\n🔍 Intent Distribution:")
    for intent, count in enhanced_data["intent_distribution"].items():
        print(f"   {intent.title()}: {count} keywords")
    
    # Show sample combinations
    print("\n📋 Sample Enhanced Keywords:")
    for base_keyword in base_keywords[:2]:
        print(f"\n📝 {base_keyword.upper()}:")
        combinations = enhanced_data["enhanced_combinations"][base_keyword][:3]
        for combo in combinations:
            print(f"   • {combo['enhanced_keyword']} ({combo['estimated_search_volume']} est. volume)")
            print(f"     Content: {combo['content_type']} | Intent: {combo['search_intent']}")
    
    # Generate tool-specific exports
    print("\n🛠️ Generating tool-specific exports...")
    
    ahrefs_keywords = enhancer.generate_tool_specific_keywords("ahrefs", base_keywords)
    semrush_keywords = enhancer.generate_tool_specific_keywords("semrush", base_keywords)
    
    print(f"   Ahrefs export: {len(ahrefs_keywords)} keywords")
    print(f"   SEMrush export: {len(semrush_keywords)} keywords")
    
    # Create CSV for direct import
    csv_data = enhancer.create_csv_export_for_tools(base_keywords)
    
    # Save to file
    with open("enhanced_keywords_for_tools.csv", "w") as f:
        f.write(csv_data)
    
    print("\n💾 Saved enhanced keywords to 'enhanced_keywords_for_tools.csv'")
    
    return enhanced_data

def create_ahrefs_import_list():
    """Create specific import list for Ahrefs"""
    
    enhancer = KeywordModifierEnhancer()
    
    # Core topics from your trend analysis
    core_topics = [
        "remote work",
        "productivity tips",
        "digital collaboration",
        "work from home",
        "team management",
        "online business",
        "freelance work",
        "digital tools"
    ]
    
    # Generate comprehensive keyword list
    ahrefs_keywords = enhancer.generate_tool_specific_keywords("ahrefs", core_topics)
    
    # Filter and prioritize
    prioritized_keywords = []
    for keyword in ahrefs_keywords:
        # Prioritize informational and commercial intent
        if any(word in keyword.lower() for word in ["guide", "tips", "best", "tool", "software"]):
            prioritized_keywords.append(keyword)
    
    # Save to CSV
    csv_content = "Keyword\n" + "\n".join(f'"{kw}"' for kw in prioritized_keywords[:200])
    
    with open("ahrefs_import_keywords.csv", "w") as f:
        f.write(csv_content)
    
    print(f"🎯 Created Ahrefs import list with {len(prioritized_keywords)} keywords")
    return prioritized_keywords[:200]

def create_semrush_import_list():
    """Create specific import list for SEMrush"""
    
    enhancer = KeywordModifierEnhancer()
    
    # High-value topics
    topics = [
        "content marketing",
        "social media strategy", 
        "email automation",
        "lead generation",
        "conversion optimization",
        "customer retention",
        "brand awareness",
        "marketing automation"
    ]
    
    # Generate SEMrush-specific combinations
    semrush_keywords = enhancer.generate_tool_specific_keywords("semrush", topics)
    
    # Create CSV with additional context
    rows = ["Keyword,Category,Intent,Content Type"]
    
    for keyword in semrush_keywords[:150]:
        # Determine category and intent
        category = "Unknown"
        intent = "informational"
        content_type = "blog_post"
        
        keyword_lower = keyword.lower()
        
        # Categorize
        for cat_name, modifier_obj in enhancer.modifier_categories.items():
            if any(mod in keyword_lower for mod in modifier_obj.modifiers):
                category = cat_name.replace('_', ' ').title()
                intent = modifier_obj.intent
                break
        
        rows.append(f'"{keyword}","{category}","{intent}","{content_type}"')
    
    csv_content = "\n".join(rows)
    
    with open("semrush_import_keywords.csv", "w") as f:
        f.write(csv_content)
    
    print(f"🔍 Created SEMrush import list with {len(rows)-1} keywords")
    return rows[1:]

async def full_workflow_demo():
    """Demonstrate full workflow integration"""
    
    print("🔄 Full Workflow Integration Demo")
    print("=" * 50)
    
    # Step 1: Start with trend analysis keywords
    trend_keywords = [
        "artificial intelligence",
        "machine learning",
        "data analytics",
        "business automation",
        "digital transformation"
    ]
    
    # Step 2: Enhance with modifiers
    enhancer = KeywordModifierEnhancer()
    enhanced = enhancer.enhance_keywords_with_modifiers(
        trend_keywords, 
        max_combinations=5
    )
    
    # Step 3: Create tool exports
    integrations = integrate_with_existing_system(trend_keywords)
    
    print("\n📊 Workflow Results:")
    print(f"   Original keywords: {len(trend_keywords)}")
    print(f"   Enhanced opportunities: {enhanced['total_opportunities']}")
    print(f"   Tool exports ready: Ahrefs ({len(integrations['tool_specific_exports']['ahrefs'])}), SEMrush ({len(integrations['tool_specific_exports']['semrush'])})")
    
    # Save integration results
    with open("keyword_workflow_results.json", "w") as f:
        json.dump(integrations, f, indent=2)
    
    print("\n💾 Saved workflow results to 'keyword_workflow_results.json'")
    
    return integrations

if __name__ == "__main__":
    # Run demo
    demo_keyword_modifiers()
    
    # Create tool-specific lists
    create_ahrefs_import_list()
    create_semrush_import_list()
    
    # Run full workflow
    asyncio.run(full_workflow_demo())
    
    print("\n✅ Demo complete! Check the generated files:")
    print("   • enhanced_keywords_for_tools.csv")
    print("   • ahrefs_import_keywords.csv") 
    print("   • semrush_import_keywords.csv")
    print("   • keyword_workflow_results.json")