#!/usr/bin/env python3
"""
Test script to validate enhanced security keyword extraction
Tests the fixes applied to improve context-aware keyword generation
"""

import sys
import os
import json
from typing import List, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _Trash_py.auto_modifier_integration import AutoModifierIntegrator
from keyword_modifier_enhancer import KeywordModifierEnhancer

class SecurityKeywordTester:
    """Test suite for security keyword extraction improvements"""
    
    def __init__(self):
        self.test_cases = [
            {
                "title": "2025 Home Security Essentials: Your Checklist for Smart Upgrades",
                "description": "Complete guide to upgrading your home security system with smart technology including cameras, sensors, and automation",
                "expected_keywords": ["home security", "smart upgrades", "security checklist", "surveillance systems", "smart locks", "security cameras"],
                "unexpected_keywords": ["home guide", "home", "home tips"]
            },
            {
                "title": "Wireless Security Camera Installation: Complete DIY Guide 2025",
                "description": "Step-by-step tutorial for installing wireless security cameras with mobile app integration and cloud storage",
                "expected_keywords": ["wireless security camera", "DIY installation", "mobile app integration", "cloud storage", "surveillance cameras"],
                "unexpected_keywords": ["guide", "tips", "wireless guide"]
            },
            {
                "title": "Smart Home Security Systems: AI-Powered Protection for Modern Homes",
                "description": "Explore AI-driven security solutions including facial recognition, motion detection, and automated alerts",
                "expected_keywords": ["smart home security", "AI-powered protection", "facial recognition", "motion detection", "automated alerts"],
                "unexpected_keywords": ["smart guide", "modern tips", "AI guide"]
            }
        ]
    
    def test_context_aware_extraction(self) -> Dict[str, Any]:
        """Test the new context-aware keyword extraction"""
        print("🧪 Testing context-aware keyword extraction...")
        
        integrator = AutoModifierIntegrator()
        results = []
        
        for i, test_case in enumerate(self.test_cases, 1):
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
            extracted_keywords = integrator._extract_context_aware_keywords(blog_idea)
            
            # Analyze results
            found_expected = [kw for kw in test_case['expected_keywords'] if any(expected in kw for expected in test_case['expected_keywords'])]
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
            
            results.append(result)
            
            print(f"   ✅ Extracted: {extracted_keywords}")
            print(f"   🎯 Expected matches: {len(found_expected)}/{len(test_case['expected_keywords'])}")
            print(f"   ❌ Unexpected keywords: {len(found_unexpected)}")
            print(f"   📈 Score: {result['score']:.1f}%")
        
        return results
    
    def test_security_modifier_enhancement(self) -> Dict[str, Any]:
        """Test security-specific keyword enhancement"""
        print("\n🔒 Testing security modifier enhancement...")
        
        enhancer = KeywordModifierEnhancer()
        
        # Test base keywords that should get security enhancements
        base_keywords = ["home security", "surveillance cameras", "smart locks"]
        
        enhanced = enhancer.enhance_keywords_with_modifiers(base_keywords, max_combinations=3)
        
        # Check for security-specific modifiers
        security_modifiers = [
            "surveillance", "monitoring", "alarm", "detection", "protection",
            "wireless", "smart", "automated", "night vision", "cloud storage"
        ]
        
        found_security_modifiers = []
        for base_kw, combinations in enhanced['enhanced_combinations'].items():
            for combo in combinations:
                modifier = combo.get('modifier', '').lower()
                if any(sec_mod in modifier for sec_mod in security_modifiers):
                    found_security_modifiers.append(modifier)
        
        return {
            'base_keywords': base_keywords,
            'enhanced_combinations': enhanced['enhanced_combinations'],
            'security_modifiers_found': list(set(found_security_modifiers)),
            'total_opportunities': enhanced['total_opportunities']
        }
    
    def test_integration_pipeline(self) -> Dict[str, Any]:
        """Test the complete integration pipeline"""
        print("\n🔗 Testing complete integration pipeline...")
        
        integrator = AutoModifierIntegrator()
        
        # Test blog idea with security focus
        blog_ideas = [{
            'title': '2025 Home Security Essentials: Your Checklist for Smart Upgrades',
            'description': 'Complete guide to upgrading your home security system with smart technology including cameras, sensors, and automation',
            'content_format': 'how_to_guide',
            'primary_keywords': ['home security', 'smart home', 'surveillance'],
            'secondary_keywords': ['installation guide', 'security cameras', 'smart locks']
        }]
        
        # Process through the enhanced pipeline
        enhanced_ideas = integrator.enhance_blog_ideas_with_modifiers(blog_ideas)
        
        if enhanced_ideas:
            enhanced_idea = enhanced_ideas[0]
            return {
                'original_keywords': blog_ideas[0]['primary_keywords'],
                'enhanced_primary': enhanced_idea.get('enhanced_primary_keywords', []),
                'enhanced_secondary': enhanced_idea.get('enhanced_secondary_keywords', []),
                'total_opportunities': enhanced_idea.get('total_keyword_opportunities', 0),
                'modifier_categories': enhanced_idea.get('modifier_categories_used', [])
            }
        
        return {}
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and provide comprehensive report"""
        print("🚀 Starting comprehensive security keyword extraction test")
        print("=" * 60)
        
        # Test 1: Context-aware extraction
        extraction_results = self.test_context_aware_extraction()
        
        # Test 2: Security modifier enhancement
        modifier_results = self.test_security_modifier_enhancement()
        
        # Test 3: Integration pipeline
        integration_results = self.test_integration_pipeline()
        
        # Calculate overall metrics
        total_tests = len(extraction_results)
        passed_tests = len([r for r in extraction_results if r['success']])
        average_score = sum(r['score'] for r in extraction_results) / total_tests if total_tests > 0 else 0
        
        report = {
            'summary': {
                'total_test_cases': total_tests,
                'passed': passed_tests,
                'failed': total_tests - passed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'average_score': average_score
            },
            'extraction_results': extraction_results,
            'modifier_results': modifier_results,
            'integration_results': integration_results,
            'recommendations': self._generate_recommendations(extraction_results, integration_results)
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Test Cases: {report['summary']['total_test_cases']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Average Score: {report['summary']['average_score']:.1f}%")
        
        return report
    
    def _generate_recommendations(self, extraction_results: List[Dict], integration_results: Dict) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        avg_extraction_score = sum(r['score'] for r in extraction_results) / len(extraction_results) if extraction_results else 0
        
        if avg_extraction_score < 80:
            recommendations.append("Consider adding more security-specific regex patterns for better context detection")
        
        if any(r['unexpected_found'] > 0 for r in extraction_results):
            recommendations.append("Review keyword filtering logic to reduce generic terms")
        
        if integration_results.get('total_opportunities', 0) < 20:
            recommendations.append("Increase modifier combination limits for more keyword opportunities")
        
        recommendations.extend([
            "Test with additional security blog topics to validate robustness",
            "Consider adding domain-specific keyword weighting",
            "Monitor keyword performance in actual SEO tools"
        ])
        
        return recommendations

def main():
    """Main test execution"""
    tester = SecurityKeywordTester()
    results = tester.run_comprehensive_test()
    
    # Save results to file
    with open('security_keyword_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to security_keyword_test_results.json")
    
    # Test the specific issue mentioned by user
    print("\n🔍 Testing the specific issue mentioned:")
    print("Blog Idea: '2025 Home Security Essentials: Your Checklist for Smart Upgrades'")
    
    integrator = AutoModifierIntegrator()
    test_idea = {
        'title': '2025 Home Security Essentials: Your Checklist for Smart Upgrades',
        'description': 'Complete guide to upgrading your home security system with smart technology including cameras, sensors, and automation',
        'content_format': 'how_to_guide'
    }
    
    keywords = integrator._extract_context_aware_keywords(test_idea)
    print(f"\n🎯 Enhanced Keywords Extracted:")
    print(f"   {keywords}")
    
    # Compare with old generic approach
    old_approach = ['home guide', 'home', 'home tips', '2025', 'checklist', 'smart', 'upgrades']
    print(f"\n❌ Old Generic Keywords: {old_approach}")
    print(f"✅ New Security Keywords: {keywords}")
    print(f"📈 Improvement: {len([k for k in keywords if 'security' in k or 'surveillance' in k or 'smart' in k])} security-specific terms vs 0 in old approach")

if __name__ == "__main__":
    main()