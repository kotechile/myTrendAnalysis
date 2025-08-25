#!/usr/bin/env python3
"""
Keyword Research API Integration for Noodl Server
Extends the existing noodl_server.py with manual keyword research functionality
"""

from typing import Dict, Any, List

# Import the manual keyword research system
from manual_keyword_integration import ManualKeywordResearchIntegration, KeywordData

def generate_keyword_suggestions(base_keywords: List[str], topic: str, target_audience: str) -> Dict[str, List[str]]:
    """Generate additional keyword suggestions"""
    
    suggestions = {
        "informational_keywords": [],
        "commercial_keywords": [], 
        "long_tail_keywords": [],
        "question_keywords": [],
        "comparison_keywords": [],
        "location_based_keywords": []
    }
    
    # Base terms from keywords and topic
    base_terms = set()
    for keyword in base_keywords:
        base_terms.update(keyword.lower().split())
    if topic:
        base_terms.update(topic.lower().split())
    
    # Remove common words
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why', 'who'}
    base_terms = [term for term in base_terms if term not in common_words and len(term) > 2]
    
    # Generate suggestions
    for term in base_terms[:5]:  # Limit to top 5 terms
        # Informational
        suggestions["informational_keywords"].extend([
            f"what is {term}",
            f"{term} methodology",
            f"{term} implementation process",
            f"how to implement {term}",
            f"{term} optimization techniques",
            f"{term} strategic approach"
        ])
        
        # Commercial
        suggestions["commercial_keywords"].extend([
            f"enterprise {term}",
            f"{term} platform",
            f"{term} solution",
            f"{term} system",
            f"{term} infrastructure",
            f"{term} deployment"
        ])
        
        # Long-tail
        suggestions["long_tail_keywords"].extend([
            f"{term} implementation workflow",
            f"{term} enterprise deployment", 
            f"{term} strategic framework",
            f"{term} integration methodology",
            f"{term} optimization process"
        ])
        
        # Questions
        suggestions["question_keywords"].extend([
            f"how does {term} work",
            f"why use {term}",
            f"when to use {term}",
            f"what are {term} benefits"
        ])
        
        # Comparisons
        suggestions["comparison_keywords"].extend([
            f"{term} vs alternatives",
            f"{term} pros and cons",
            f"difference between {term}"
        ])
    
    # Audience-specific suggestions
    if target_audience == 'small_business':
        for term in base_terms[:3]:
            suggestions["informational_keywords"].extend([
                f"{term} workflow optimization",
                f"{term} resource planning",
                f"{term} implementation strategy"
            ])
    elif target_audience == 'enterprise':
        for term in base_terms[:3]:
            suggestions["informational_keywords"].extend([
                f"enterprise {term} architecture",
                f"{term} enterprise integration",
                f"{term} organizational deployment"
            ])
    
    # Remove duplicates and limit results
    for category in suggestions:
        suggestions[category] = list(set(suggestions[category]))[:10]
    
    return suggestions