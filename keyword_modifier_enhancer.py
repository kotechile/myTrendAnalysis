#!/usr/bin/env python3
"""
Keyword Modifier Enhancement System
Extends keyword research by adding non-niche specific modifier words to increase search volume opportunities
"""

import logging
from typing import Dict, Any, List, Set
from dataclasses import dataclass
from keyword_research_api import generate_keyword_suggestions  # Import from existing system

@dataclass
class KeywordModifier:
    """Represents a keyword modifier category"""
    category: str
    modifiers: List[str]
    intent: str  # 'informational', 'commercial', 'transactional'
    use_case: str

class KeywordModifierEnhancer:
    """Enhances keywords with non-niche specific modifier words"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define modifier categories based on user input
        self.modifier_categories = {
            "security_tools": KeywordModifier(
                category="Security Tools",
                modifiers=[
                    "control-panel", "mobile-app", "web-interface", "dashboard",
                    "monitoring-station", "alert-system", "sensor-network", "camera-setup"
                ],
                intent="commercial",
                use_case="Security system tools and interfaces"
            ),
            
            "services": KeywordModifier(
                category="Services",
                modifiers=[
                    "consultation", "coaching", "training", "course", "workshop",
                    "service", "repair", "installation", "maintenance", "cleaning"
                ],
                intent="commercial",
                use_case="Service offerings and professional help"
            ),
            
            "information_learning": KeywordModifier(
                category="Information & Learning",
                modifiers=[
                    "advice", "tips", "tutorial", "review", "comparison",
                    "analysis", "strategy", "method", "technique", "solution"
                ],
                intent="informational",
                use_case="Educational content and knowledge sharing"
            ),
            
            "commercial_intent": KeywordModifier(
                category="Commercial Intent",
                modifiers=[
                    "kit", "supplies", "equipment", "accessories", "parts",
                    "rental", "subscription", "membership", "package", "bundle"
                ],
                intent="commercial",
                use_case="Product-focused and purchase-oriented content"
            ),
            
            "problem_solving": KeywordModifier(
                category="Problem-Solving",
                modifiers=[
                    "problem", "issue", "fix", "troubleshooting", "optimization",
                    "improvement", "upgrade", "replacement", "alternative", "workaround"
                ],
                intent="informational",
                use_case="Solution-focused content addressing pain points"
            ),
            
            "planning_organization": KeywordModifier(
                category="Planning & Organization",
                modifiers=[
                    "planning", "management", "organization", "scheduling",
                    "budget", "cost", "pricing", "estimate", "forecast", "preparation"
                ],
                intent="informational",
                use_case="Strategic and organizational content"
            ),
            
            "security_specific": KeywordModifier(
                category="Security-Specific",
                modifiers=[
                    "surveillance", "monitoring", "alarm", "detection", "protection",
                    "access", "control", "wireless", "smart", "automated", "AI",
                    "night", "vision", "cloud", "mobile", "remote", "real-time",
                    "encrypted", "secure", "24/7", "HD", "4K", "weatherproof", "battery"
                ],
                intent="commercial",
                use_case="Security and smart home technology content"
            ),
            
            "home_automation": KeywordModifier(
                category="Home Automation",
                modifiers=[
                    "smart", "automated", "voice", "app", "mobile", "wireless",
                    "integrated", "connected", "IoT", "Alexa", "Google", "Siri",
                    "schedule", "timer", "notification", "geofence", "IFTTT"
                ],
                intent="commercial",
                use_case="Smart home and automation technology content"
            ),
            
            "installation_setup": KeywordModifier(
                category="Installation & Setup",
                modifiers=[
                    "setup", "installation", "configuration", "mounting", "wiring",
                    "DIY", "professional", "setup", "sync", "pairing", "calibration",
                    "positioning", "placement", "adjustment", "fine-tuning"
                ],
                intent="informational",
                use_case="Installation and configuration guidance"
            )
        }
    
    def enhance_keywords_with_modifiers(self, base_keywords: List[str], 
                                      target_audience: str = "professional",
                                      max_combinations: int = 5) -> Dict[str, Any]:
        """
        Enhance base keywords with modifier combinations
        
        Args:
            base_keywords: List of core topic keywords
            target_audience: Target audience type
            max_combinations: Maximum modifier combinations per keyword
            
        Returns:
            Enhanced keyword dictionary with modifier combinations
        """
        
        self.logger.info(f"🔍 Enhancing {len(base_keywords)} keywords with modifier combinations")
        
        enhanced_keywords = {
            "original_keywords": base_keywords,
            "enhanced_combinations": {},
            "modifier_usage": {},
            "intent_distribution": {},
            "total_opportunities": 0
        }
        
        for base_keyword in base_keywords:
            combinations = self._generate_modifier_combinations(base_keyword, max_combinations)
            enhanced_keywords["enhanced_combinations"][base_keyword] = combinations
            enhanced_keywords["total_opportunities"] += len(combinations)
            
            # Track modifier usage
            for combo in combinations:
                modifier_type = combo["modifier_category"]
                enhanced_keywords["modifier_usage"][modifier_type] = \
                    enhanced_keywords["modifier_usage"].get(modifier_type, 0) + 1
                    
                # Track intent distribution
                intent = combo["search_intent"]
                enhanced_keywords["intent_distribution"][intent] = \
                    enhanced_keywords["intent_distribution"].get(intent, 0) + 1
        
        return enhanced_keywords
    
    def _generate_modifier_combinations(self, base_keyword: str, max_combinations: int) -> List[Dict[str, Any]]:
        """Generate modifier combinations for a single base keyword"""
        
        combinations = []
        
        for category_name, modifier_obj in self.modifier_categories.items():
            for modifier in modifier_obj.modifiers:
                # Generate different combination patterns
                patterns = self._create_combination_patterns(base_keyword, modifier)
                
                for pattern in patterns:
                    if len(combinations) >= max_combinations * len(self.modifier_categories):
                        break
                        
                    combination = {
                        "original_keyword": base_keyword,
                        "enhanced_keyword": pattern,
                        "modifier": modifier,
                        "modifier_category": category_name,
                        "search_intent": modifier_obj.intent,
                        "use_case": modifier_obj.use_case,
                        "estimated_search_volume": self._estimate_volume(pattern),
                        "competition_level": self._estimate_competition(pattern),
                        "content_type": self._suggest_content_type(pattern, modifier_obj.intent)
                    }
                    
                    combinations.append(combination)
        
        # Sort by estimated volume and relevance
        combinations.sort(key=lambda x: x["estimated_search_volume"], reverse=True)
        return combinations[:max_combinations * len(self.modifier_categories)]
    
    def _create_combination_patterns(self, base_keyword: str, modifier: str) -> List[str]:
        """Create different keyword combination patterns"""
        
        patterns = [
            f"{base_keyword} {modifier}",
            f"{modifier} for {base_keyword}",
            f"enterprise {base_keyword} {modifier}",
            f"{base_keyword} {modifier} system",
            f"{base_keyword} {modifier} solution",
            f"advanced {base_keyword} {modifier}",
            f"{base_keyword} {modifier} integration",
            f"{base_keyword} {modifier} optimization"
        ]
        
        # Remove duplicates and clean up
        patterns = list(set(patterns))
        return [p.strip() for p in patterns if p.strip()]
    
    def _estimate_volume(self, keyword: str) -> int:
        """Estimate search volume for enhanced keyword (simplified estimation)"""
        
        base_volume = 100  # Base assumption
        
        # Volume multipliers based on patterns (context-aware)
        volume_multipliers = {
            "implementation": 1.8,
            "methodology": 1.7,
            "framework": 1.6,
            "system": 1.5,
            "solution": 1.4,
            "enterprise": 1.9,
            "integration": 1.6,
            "optimization": 1.7,
            "platform": 1.5,
            "deployment": 1.8
        }
        
        multiplier = 1.0
        for pattern, mult in volume_multipliers.items():
            if pattern in keyword.lower():
                multiplier = max(multiplier, mult)
        
        # Adjust based on keyword length (long-tail usually lower volume)
        word_count = len(keyword.split())
        if word_count > 5:
            multiplier *= 0.7
        elif word_count > 3:
            multiplier *= 0.85
            
        return int(base_volume * multiplier)
    
    def _estimate_competition(self, keyword: str) -> str:
        """Estimate competition level for enhanced keyword"""
        
        # Competition indicators
        high_competition_words = ["best", "top", "review", "comparison", "2025"]
        medium_competition_words = ["guide", "tips", "tool", "software"]
        low_competition_words = ["free", "template", "checklist", "planner"]
        
        keyword_lower = keyword.lower()
        
        # Check for competition indicators
        if any(word in keyword_lower for word in high_competition_words):
            return "high"
        elif any(word in keyword_lower for word in medium_competition_words):
            return "medium"
        elif any(word in keyword_lower for word in low_competition_words):
            return "low"
        else:
            return "medium"
    
    def _suggest_content_type(self, keyword: str, intent: str) -> str:
        """Suggest content type based on keyword and intent"""
        
        keyword_lower = keyword.lower()
        
        content_mapping = {
            "calculator": "interactive_tool",
            "tool": "interactive_tool",
            "software": "enterprise_solution",
            "platform": "enterprise_platform",
            "system": "integrated_system",
            "solution": "enterprise_solution",
            "framework": "implementation_framework",
            "methodology": "implementation_methodology",
            "template": "implementation_template",
            "workflow": "process_workflow",
            "integration": "system_integration",
            "deployment": "enterprise_deployment",
            "implementation": "strategic_implementation",
            "architecture": "enterprise_architecture",
            "consultation": "strategic_consultation",
            "coaching": "executive_coaching",
            "training": "professional_training",
            "course": "professional_course",
            "workshop": "strategy_workshop",
            "service": "enterprise_service",
            "analysis": "strategic_analysis",
            "strategy": "business_strategy",
            "optimization": "performance_optimization",
            "planning": "strategic_planning",
            "management": "enterprise_management",
            "organization": "organizational_design",
            "scheduling": "project_scheduling",
            "budget": "resource_planning",
            "forecast": "business_forecasting"
        }
        
        for key, content_type in content_mapping.items():
            if key in keyword_lower:
                return content_type
        
        # Default based on intent
        intent_mapping = {
            "informational": "blog_post",
            "commercial": "product_review",
            "transactional": "product_page"
        }
        
        return intent_mapping.get(intent, "blog_post")
    
    def generate_tool_specific_keywords(self, tool_name: str, base_keywords: List[str]) -> List[str]:
        """Generate tool-specific keyword lists for Ahrefs, SEMrush, etc."""
        
        tool_keywords = []
        
        for base_keyword in base_keywords:
            for category_name, modifier_obj in self.modifier_categories.items():
                for modifier in modifier_obj.modifiers:
                    # Create search-friendly combinations
                    combinations = [
                        f"{base_keyword} {modifier}",
                        f"{modifier} {base_keyword}",
                        f"best {base_keyword} {modifier}",
                        f"{base_keyword} {modifier} 2025"
                    ]
                    
                    tool_keywords.extend(combinations)
        
        # Remove duplicates and return
        unique_keywords = list(set(tool_keywords))
        return sorted(unique_keywords)
    
    def create_csv_export_for_tools(self, base_keywords: List[str]) -> str:
        """Create CSV export for direct import into keyword tools"""
        
        rows = []
        headers = ["Keyword", "Category", "Intent", "Use Case", "Content Type"]
        rows.append(",".join(headers))
        
        for base_keyword in base_keywords:
            for category_name, modifier_obj in self.modifier_categories.items():
                for modifier in modifier_obj.modifiers:
                    enhanced_keyword = f"{base_keyword} {modifier}"
                    content_type = self._suggest_content_type(enhanced_keyword, modifier_obj.intent)
                    
                    row = [
                        f'"{enhanced_keyword}"',
                        f'"{category_name}"',
                        f'"{modifier_obj.intent}"',
                        f'"{modifier_obj.use_case}"',
                        f'"{content_type}"'
                    ]
                    rows.append(",".join(row))
        
        return "\n".join(rows)

def integrate_with_existing_system(base_keywords: List[str], 
                                 existing_keywords: List[str] = None) -> Dict[str, Any]:
    """
    Integration function to work with existing keyword research system
    
    Args:
        base_keywords: Core topic keywords from trend analysis
        existing_keywords: Already researched keywords to avoid duplicates
        
    Returns:
        Enhanced keyword data ready for tool import
    """
    
    enhancer = KeywordModifierEnhancer()
    
    # Generate enhanced combinations
    enhanced_data = enhancer.enhance_keywords_with_modifiers(base_keywords)
    
    # Generate tool-specific exports
    ahrefs_keywords = enhancer.generate_tool_specific_keywords("ahrefs", base_keywords)
    semrush_keywords = enhancer.generate_tool_specific_keywords("semrush", base_keywords)
    moz_keywords = enhancer.generate_tool_specific_keywords("moz", base_keywords)
    
    # Create CSV export
    csv_export = enhancer.create_csv_export_for_tools(base_keywords)
    
    return {
        "enhanced_keywords": enhanced_data,
        "tool_specific_exports": {
            "ahrefs": ahrefs_keywords,
            "semrush": semrush_keywords,
            "moz": moz_keywords
        },
        "csv_export": csv_export,
        "total_new_opportunities": len([kw for kw in ahrefs_keywords if not existing_keywords or kw not in existing_keywords])
    }

# Example usage
if __name__ == "__main__":
    # Test the system
    test_keywords = ["digital marketing", "content strategy", "social media"]
    
    enhancer = KeywordModifierEnhancer()
    result = enhancer.enhance_keywords_with_modifiers(test_keywords, max_combinations=3)
    
    print("Enhanced Keywords:")
    for base, combos in result["enhanced_combinations"].items():
        print(f"\n{base}:")
        for combo in combos[:3]:
            print(f"  - {combo['enhanced_keyword']} ({combo['estimated_search_volume']} est. volume)")
    
    # Generate CSV for tools
    csv_data = enhancer.create_csv_export_for_tools(test_keywords)
    print("\nCSV Export Sample:")
    print(csv_data[:500] + "...")