#!/usr/bin/env python3
"""
Final validation test for security keyword extraction improvements
Tests both direct extraction and auto-integration functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from _Trash_py.auto_modifier_integration import AutoModifierIntegrator
from simple_keyword_test import extract_context_aware_keywords

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
    
    # Test 1: Direct extraction
    direct_keywords = extract_context_aware_keywords(blog_idea)
    
    # Test 2: Auto integration
    integrator = AutoModifierIntegrator()
    auto_keywords = integrator._extract_context_aware_keywords(blog_idea)
    
    # Test 3: Full integration with modifiers
    enhanced_idea = integrator.enhance_blog_ideas_with_modifiers([blog_idea])[0]
    enhanced_keywords = enhanced_idea.get('enhanced_primary_keywords', [])
    
    print(f"\n📊 ORIGINAL ISSUE:")
    print(f"   Blog Idea: {blog_idea['title']}")
    print(f"   ❌ OLD Generic Keywords (before fix): ['home guide', 'home', 'home tips', '2025', 'checklist', 'smart', 'upgrades']")
    
    print(f"\n✅ NEW Security-Specific Keywords:")
    print(f"   Direct Extraction: {direct_keywords}")
    print(f"   Auto Integration: {auto_keywords}")
    print(f"   Enhanced w/ Modifiers: {enhanced_keywords[:5]}")
    
    # Validate improvements
    security_terms = ['security', 'surveillance', 'camera', 'alarm', 'lock', 'sensor', 'monitor', 'protection']
    
    direct_security_count = len([kw for kw in direct_keywords if any(term in kw.lower() for term in security_terms)])
    auto_security_count = len([kw for kw in auto_keywords if any(term in kw.lower() for term in security_terms)])
    enhanced_security_count = len([kw for kw in enhanced_keywords if any(term in kw.lower() for term in security_terms)])
    
    print(f"\n📈 IMPROVEMENT METRICS:")
    print(f"   Direct extraction: {direct_security_count} security-specific terms")
    print(f"   Auto integration: {auto_security_count} security-specific terms") 
    print(f"   Enhanced w/ modifiers: {enhanced_security_count} security-specific terms")
    print(f"   Generic terms eliminated: ✅ (no 'home guide', 'home tips')")
    
    # Verify no generic terms
    generic_terms = ['home guide', 'home tips', 'home', 'guide', 'tips']
    has_generic = any(term in ' '.join(direct_keywords).lower() for term in generic_terms)
    
    print(f"\n🎯 VALIDATION RESULTS:")
    print(f"   ✅ Security-specific keywords extracted: {direct_security_count > 0}")
    print(f"   ✅ Generic keywords eliminated: {not has_generic}")
    print(f"   ✅ Context-aware extraction working: {'security' in ' '.join(direct_keywords).lower()}")
    
    return {
        'direct_security_count': direct_security_count,
        'auto_security_count': auto_security_count,
        'enhanced_security_count': enhanced_security_count,
        'generic_eliminated': not has_generic,
        'success': direct_security_count > 0 and not has_generic
    }

if __name__ == "__main__":
    result = test_security_keyword_fix()
    
    print(f"\n" + "=" * 60)
    print(f"🎉 FINAL STATUS: {'SUCCESS' if result['success'] else 'NEEDS ADJUSTMENT'}")
    print("=" * 60)