#!/usr/bin/env python3
"""
Simple focused test for security keyword extraction
Tests the core context-aware keyword extraction without system dependencies
"""

import re
import json
from typing import List, Dict, Any

def extract_context_aware_keywords(idea: Dict[str, Any]) -> List[str]:
    """
    Extract context-aware keywords from blog ideas focusing on security-related terms
    
    Args:
        idea: Blog idea dictionary
        
    Returns:
        List of relevant, context-aware keywords
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

def run_security_keyword_test():
    """Run comprehensive test for security keyword extraction"""
    
    print("🚀 Testing Security Keyword Extraction Improvements")
    print("=" * 60)
    
    test_cases = [
        {
            "title": "2025 Home Security Essentials: Your Checklist for Smart Upgrades",
            "description": "Complete guide to upgrading your home security system with smart technology including cameras, sensors, and automation",
            "expected_keywords": ["home security", "smart upgrades", "security", "surveillance", "smart home"],
            "unexpected_keywords": ["home guide", "home tips"]
        },
        {
            "title": "Wireless Security Camera Installation: Complete DIY Guide 2025",
            "description": "Step-by-step tutorial for installing wireless security cameras with mobile app integration and cloud storage",
            "expected_keywords": ["wireless security", "security camera", "camera installation", "surveillance", "wireless"],
            "unexpected_keywords": ["guide", "tips"]
        },
        {
            "title": "Smart Home Security Systems: AI-Powered Protection for Modern Homes",
            "description": "Explore AI-driven security solutions including facial recognition, motion detection, and automated alerts",
            "expected_keywords": ["home security", "smart home", "security systems", "surveillance", "protection"],
            "unexpected_keywords": ["smart guide", "modern tips"]
        }
    ]
    
    all_results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test Case {i}: {test_case['title']}")
        
        # Create test blog idea
        blog_idea = {
            'title': test_case['title'],
            'description': test_case['description'],
            'content_format': 'how_to_guide',
            'primary_keywords': ['security', 'smart home', 'surveillance'],
            'secondary_keywords': ['installation', 'technology', 'protection']
        }
        
        # Extract keywords using the new context-aware method
        extracted_keywords = extract_context_aware_keywords(blog_idea)
        
        # Analyze results
        found_expected = [kw for kw in extracted_keywords if any(expected in kw for expected in test_case['expected_keywords'])]
        found_unexpected = [kw for kw in extracted_keywords if kw in test_case['unexpected_keywords']]
        
        result = {
            'test_case': i,
            'title': test_case['title'],
            'extracted_keywords': extracted_keywords,
            'expected_found': len(found_expected),
            'unexpected_found': len(found_unexpected),
            'success': len(found_unexpected) == 0 and len(found_expected) > 0,
            'score': len(found_expected) / len(test_case['expected_keywords']) * 100 if test_case['expected_keywords'] else 0
        }
        
        all_results.append(result)
        
        print(f"   ✅ Extracted: {extracted_keywords}")
        print(f"   🎯 Expected matches: {len(found_expected)}/{len(test_case['expected_keywords'])}")
        print(f"   ❌ Unexpected keywords: {len(found_unexpected)}")
        print(f"   📈 Score: {result['score']:.1f}%")
    
    # Calculate overall metrics
    total_tests = len(all_results)
    passed_tests = len([r for r in all_results if r['success']])
    average_score = sum(r['score'] for r in all_results) / total_tests if total_tests > 0 else 0
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Test Cases: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests / total_tests * 100) if total_tests > 0 else 0:.1f}%")
    print(f"Average Score: {average_score:.1f}%")
    
    # Test the specific issue mentioned by user
    print("\n🔍 Testing the specific issue mentioned:")
    print("Blog Idea: '2025 Home Security Essentials: Your Checklist for Smart Upgrades'")
    
    test_idea = {
        'title': '2025 Home Security Essentials: Your Checklist for Smart Upgrades',
        'description': 'Complete guide to upgrading your home security system with smart technology including cameras, sensors, and automation',
        'content_format': 'how_to_guide'
    }
    
    keywords = extract_context_aware_keywords(test_idea)
    print(f"\n🎯 Enhanced Keywords Extracted:")
    print(f"   {keywords}")
    
    # Compare with old generic approach
    old_approach = ['home guide', 'home', 'home tips', '2025', 'checklist', 'smart', 'upgrades']
    print(f"\n❌ Old Generic Keywords: {old_approach}")
    print(f"✅ New Security Keywords: {keywords}")
    
    security_specific_count = len([k for k in keywords if 'security' in k or 'surveillance' in k or 'smart' in k])
    print(f"📈 Improvement: {security_specific_count} security-specific terms vs 0 in old approach")
    
    return all_results

if __name__ == "__main__":
    results = run_security_keyword_test()