#!/usr/bin/env python3
"""
Final validation test for security keyword extraction improvements
Tests the core extraction functionality
"""

import re
from typing import List, Dict, Any

def extract_context_aware_keywords(idea: Dict[str, Any]) -> List[str]:
    """
    Extract context-aware keywords from blog ideas focusing on security-related terms
    """
    
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

def test_security_keyword_fix():
    """Test the specific issue mentioned by user"""
    
    print("🔍 VALIDATION: Security Keyword Extraction Fix")
    print("=" * 60)
    
    # Test the exact case mentioned by user
    blog_idea = {
        'title': '2025 Home Security Essentials: Your Checklist for Smart Upgrades',
        'description': 'Complete guide to upgrading your home security system with smart technology including cameras, sensors, and automation',
        'content_format': 'how_to_guide'
    }
    
    # Test enhanced extraction
    keywords = extract_context_aware_keywords(blog_idea)
    
    print(f"\n📊 ORIGINAL ISSUE:")
    print(f"   Blog Idea: {blog_idea['title']}")
    print(f"   ❌ OLD Generic Keywords: ['home guide', 'home', 'home tips', '2025', 'checklist', 'smart', 'upgrades']")
    
    print(f"\n✅ NEW Security-Specific Keywords:")
    print(f"   Enhanced Keywords: {keywords}")
    
    # Validate improvements
    security_terms = ['security', 'surveillance', 'camera', 'alarm', 'lock', 'sensor', 'monitor', 'protection']
    
    security_count = len([kw for kw in keywords if any(term in kw.lower() for term in security_terms)])
    
    # Verify elimination of standalone generic terms (but allow compound terms)
    standalone_generics = ['home guide', 'home tips', 'guide', 'tips']
    has_generic = any(term in ' '.join(keywords).lower() for term in standalone_generics)
    
    print(f"\n📈 IMPROVEMENT METRICS:")
    print(f"   Security-specific terms: {security_count}")
    print(f"   Generic terms eliminated: {'✅' if not has_generic else '❌'}")
    print(f"   Context-aware extraction: {'✅' if 'security' in ' '.join(keywords).lower() else '❌'}")
    
    # Test additional security blog ideas
    test_cases = [
        {
            "title": "Wireless Security Camera Installation Guide",
            "description": "DIY installation of wireless security cameras for home surveillance"
        },
        {
            "title": "Smart Home Security Systems 2025",
            "description": "Latest AI-powered security systems with automation features"
        },
        {
            "title": "Home Surveillance Setup Tips",
            "description": "Professional setup guide for home surveillance and monitoring"
        }
    ]
    
    print(f"\n🎯 ADDITIONAL TESTS:")
    for i, test in enumerate(test_cases, 1):
        keywords = extract_context_aware_keywords(test)
        security_count = len([kw for kw in keywords if any(term in kw.lower() for term in security_terms)])
        print(f"   {i}. {test['title'][:30]}...: {security_count} security terms")
    
    return {
        'security_count': security_count,
        'generic_eliminated': not has_generic,
        'success': security_count > 0 and not has_generic,
        'keywords': keywords
    }

if __name__ == "__main__":
    result = test_security_keyword_fix()
    
    print(f"\n" + "=" * 60)
    print(f"🎉 FINAL STATUS: {'SUCCESS' if result['success'] else 'NEEDS ADJUSTMENT'}")
    print("=" * 60)