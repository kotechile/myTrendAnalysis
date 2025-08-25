#!/usr/bin/env python3
"""
Auto Modifier Integration for Blog Ideas
Automatically enhances blog ideas with modifier keywords during generation
"""

from keyword_modifier_enhancer import KeywordModifierEnhancer
import json
from typing import Dict, Any, List

class AutoModifierIntegrator:
    """Automatically adds modifier keywords to blog ideas"""
    
    def __init__(self):
        self.enhancer = KeywordModifierEnhancer()
    
    def enhance_blog_ideas_with_modifiers(self, blog_ideas: list) -> list:
        """
        Automatically enhance blog ideas with modifier keywords
        
        Args:
            blog_ideas: List of blog idea dictionaries from your generation
            
        Returns:
            Enhanced blog ideas with additional keywords
        """
        
        enhanced_ideas = []
        
        for idea in blog_ideas:
            # Extract keywords from the idea using context-aware extraction
            base_keywords = self._extract_context_aware_keywords(idea)
            
            if not base_keywords:
                # Fallback to topic extraction
                base_keywords = ["content marketing"]  # Default fallback
            
            # Generate enhanced keywords
            enhanced_keywords = self.enhancer.enhance_keywords_with_modifiers(
                base_keywords[:3],  # Limit to top 3 keywords for performance
                max_combinations=2
            )
            
            # Create enhanced idea
            enhanced_idea = idea.copy()
            
            # Add enhanced keywords
            enhanced_keywords_list = []
            for base_kw, combinations in enhanced_keywords['enhanced_combinations'].items():
                enhanced_keywords_list.extend([combo['enhanced_keyword'] for combo in combinations])
            
            # Update idea with enhanced keywords
            enhanced_idea.update({
                'enhanced_primary_keywords': enhanced_keywords_list[:5],
                'enhanced_secondary_keywords': enhanced_keywords_list[5:10],
                'modifier_enhanced': True,
                'total_keyword_opportunities': enhanced_keywords['total_opportunities'],
                'modifier_categories_used': list(enhanced_keywords['modifier_usage'].keys())
            })
            
            enhanced_ideas.append(enhanced_idea)
        
        return enhanced_ideas
    
    def _extract_context_aware_keywords(self, idea: Dict[str, Any]) -> List[str]:
        """
        Extract context-aware keywords from blog ideas focusing on security-related terms
        
        Args:
            idea: Blog idea dictionary
            
        Returns:
            List of relevant, context-aware keywords
        """
        import re
        
        base_keywords = []
        
        # Extract from title with security context detection
        title = idea.get('title', '')
        if title:
            title_lower = title.lower()
            
            # Security-related keyword detection
            security_patterns = [
                r'\bsecurity\b', r'\bsmart\s+home\b', r'\bhome\s+security\b',
                r'\bsurveillance\b', r'\balarm\b', r'\bcamera\b', r'\block\b',
                r'\bsensor\b', r'\bmonitor\b', r'\bprotection\b', r'\bsafety\b',
                r'\bintrusion\b', r'\baccess\s+control\b', r'\bvideo\s+doorbell\b',
                r'\bsmart\s+lock\b', r'\bmotion\s+detector\b', r'\bsecurity\s+system\b',
                r'\bwireless\s+security\b', r'\bnight\s+vision\b', r'\bcloud\s+storage\b',
                r'\bmobile\s+app\b', r'\bremote\s+monitoring\b', r'\bAI\s+security\b',
                r'\bfacial\s+recognition\b', r'\bvoice\s+control\b', r'\bautomation\b'
            ]
            
            # Extract security-related terms
            for pattern in security_patterns:
                matches = re.findall(pattern, title_lower)
                base_keywords.extend(matches)
            
            # Extract other meaningful phrases (2-3 word combinations)
            words = title.split()
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}".lower()
                if len(phrase) > 5 and not phrase.startswith(('the', 'and', 'for', 'with')):
                    base_keywords.append(phrase)
            
            # Add single important words
            important_words = [
                word.lower() for word in words 
                if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with', 'your', '2025', 'guide', 'checklist', 'complete']
            ]
            base_keywords.extend(important_words)
        
        # Extract from description
        description = idea.get('description', '')
        if description:
            desc_lower = description.lower()
            
            # Look for security-related terms in description
            security_desc_patterns = [
                r'\bwireless\b', r'\bcloud\b', r'\bmobile\b', r'\bapp\b',
                r'\bmonitoring\b', r'\brecording\b', r'\bnotification\b',
                r'\bencryption\b', r'\bprivacy\b', r'\bbackup\b', r'\bstorage\b'
            ]
            
            for pattern in security_desc_patterns:
                matches = re.findall(pattern, desc_lower)
                base_keywords.extend(matches)
        
        # Extract from existing keywords but prioritize security terms
        primary_keywords = idea.get('primary_keywords', [])
        if isinstance(primary_keywords, str):
            try:
                primary_keywords = json.loads(primary_keywords)
            except:
                primary_keywords = [primary_keywords] if primary_keywords else []
        
        # Filter existing keywords for security relevance
        security_keywords = []
        security_terms = ['security', 'smart', 'camera', 'alarm', 'lock', 'sensor', 'monitor', 'surveillance', 'protection', 'safety']
        
        for keyword in primary_keywords:
            kw_lower = str(keyword).lower()
            if any(term in kw_lower for term in security_terms):
                security_keywords.append(kw_lower)
            else:
                base_keywords.append(kw_lower)
        
        base_keywords.extend(security_keywords)
        
        # Extract from secondary keywords
        secondary_keywords = idea.get('secondary_keywords', [])
        if isinstance(secondary_keywords, str):
            try:
                secondary_keywords = json.loads(secondary_keywords)
            except:
                secondary_keywords = [secondary_keywords] if secondary_keywords else []
        
        for keyword in secondary_keywords:
            kw_lower = str(keyword).lower()
            if any(term in kw_lower for term in security_terms):
                security_keywords.append(kw_lower)
            else:
                base_keywords.append(kw_lower)
        
        # Remove duplicates and clean
        base_keywords = list(set([kw.strip().rstrip(':') for kw in base_keywords if kw.strip() and len(kw.strip()) > 2]))
        
        # Prioritize security-specific terms
        security_terms = ['security', 'surveillance', 'camera', 'alarm', 'lock', 'sensor', 'monitor', 'protection', 'safety']
        
        def security_priority(kw):
            kw_lower = kw.lower()
            if any(term in kw_lower for term in security_terms):
                return (100, len(kw), kw.count(' '))  # Security terms get highest priority
            elif kw_lower.startswith(('the', 'and', 'for', 'with', 'your', '2025')):
                return (0, len(kw), kw.count(' '))  # Generic starters get lowest
            else:
                return (50, len(kw), kw.count(' '))  # Others get medium
        
        base_keywords.sort(key=security_priority, reverse=True)
        
        return base_keywords[:10]  # Return top 10 most relevant keywords

    def generate_keyword_export_csv(self, enhanced_ideas: list) -> str:
        """Generate CSV for keyword tool upload"""
        
        csv_lines = ["Keyword,Source_Idea,Content_Type,Search_Intent"]
        
        for idea in enhanced_ideas:
            # Get enhanced keywords
            enhanced_keywords = idea.get('enhanced_primary_keywords', []) + idea.get('enhanced_secondary_keywords', [])
            
            for keyword in enhanced_keywords:
                content_type = idea.get('content_format', 'blog_post')
                search_intent = 'informational' if 'guide' in keyword.lower() or 'tips' in keyword.lower() else 'commercial'
                
                csv_lines.append(f'"{keyword}","{idea.get("title", "")}","{content_type}","{search_intent}"')
        
        return "\n".join(csv_lines)

def integrate_with_existing_workflow():
    """
    Simple integration function to add to your workflow
    
    Usage:
    1. After generating blog ideas, pass them through this function
    2. Upload the resulting keywords to your keyword tool
    3. Proceed with your normal workflow
    """
    
    integrator = AutoModifierIntegrator()
    
    return {
        'enhance_ideas': integrator.enhance_blog_ideas_with_modifiers,
        'generate_csv': integrator.generate_keyword_export_csv,
        'description': 'Automatically adds modifier keywords to blog ideas'
    }

# Usage example
if __name__ == "__main__":
    # Sample blog ideas (like what you'd get from your generation)
    sample_blog_ideas = [
        {
            'title': 'Remote Work Productivity Tips',
            'description': 'Learn how to boost productivity while working from home',
            'content_format': 'how_to_guide',
            'primary_keywords': ['remote work', 'productivity', 'work from home'],
            'secondary_keywords': ['remote work tips', 'home office setup', 'productivity hacks']
        },
        {
            'title': 'Digital Marketing Strategy Guide',
            'description': 'Complete guide to digital marketing for small businesses',
            'content_format': 'guide',
            'primary_keywords': ['digital marketing', 'strategy', 'small business'],
            'secondary_keywords': ['marketing strategy', 'digital marketing guide', 'business growth']
        }
    ]
    
    integrator = AutoModifierIntegrator()
    
    # Enhance the ideas
    enhanced_ideas = integrator.enhance_blog_ideas_with_modifiers(sample_blog_ideas)
    
    print("🚀 Enhanced Blog Ideas with Modifier Keywords")
    print("=" * 50)
    
    for i, idea in enumerate(enhanced_ideas, 1):
        print(f"\n{i}. {idea['title']}")
        print(f"   Enhanced Keywords: {', '.join(idea['enhanced_primary_keywords'][:5])}")
        print(f"   Total Opportunities: {idea['total_keyword_opportunities']}")
    
    # Generate CSV for keyword tools
    csv_data = integrator.generate_keyword_export_csv(enhanced_ideas)
    
    print(f"\n📊 CSV Generated with {len(csv_data.splitlines())-1} keywords")
    print("\nSample CSV:")
    print(csv_data[:300] + "...")
    
    # Save to file
    with open('enhanced_keywords_for_upload.csv', 'w') as f:
        f.write(csv_data)
    
    print("\n✅ Saved to 'enhanced_keywords_for_upload.csv'")
    print("\nNext steps:")
    print("1. Upload enhanced_keywords_for_upload.csv to Ahrefs/SEMrush")
    print("2. Get keyword data back")
    print("3. Use /api/v2/keyword-research/upload to process results")