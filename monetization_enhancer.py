#!/usr/bin/env python3
"""
Monetization Enhancement Module
Adds monetization scoring and revenue potential analysis to blog ideas
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import re


class MonetizationEnhancer:
    """Enhanced monetization analysis for blog ideas"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Monetization scoring weights
        self.MONETIZATION_WEIGHTS = {
            "affiliate_potential": 0.35,
            "digital_product_potential": 0.25,
            "service_potential": 0.20,
            "lead_generation_potential": 0.20
        }
        
        # Commercial intent keywords
        self.COMMERCIAL_KEYWORDS = {
            "high_intent": [
                "buy", "purchase", "price", "cost", "discount", "deal", "coupon",
                "review", "best", "top", "compare", "vs", "alternative", "cheap",
                "affordable", "premium", "professional", "enterprise"
            ],
            "medium_intent": [
                "how to", "guide", "tutorial", "tips", "strategies", "methods",
                "tools", "software", "platform", "service", "solution", "system"
            ],
            "product_research": [
                "features", "benefits", "pros and cons", "specifications", "demo",
                "trial", "free", "comparison", "test", "results", "case study"
            ]
        }
        
        # Affiliate program categories and typical commission rates
        self.AFFILIATE_CATEGORIES = {
            "saas": {"commission": "20-30%", "cookie_duration": "30-90 days"},
            "ecommerce": {"commission": "3-10%", "cookie_duration": "24-30 days"},
            "digital_products": {"commission": "30-70%", "cookie_duration": "30-60 days"},
            "online_courses": {"commission": "20-50%", "cookie_duration": "30-365 days"},
            "software_tools": {"commission": "15-40%", "cookie_duration": "30-90 days"},
            "web_hosting": {"commission": "50-200%", "cookie_duration": "30-60 days"},
            "marketing_tools": {"commission": "20-40%", "cookie_duration": "30-90 days"}
        }

    async def enhance_ideas_with_monetization(self, blog_ideas: List[Dict[str, Any]], 
                                            context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Add comprehensive monetization analysis to blog ideas"""
        
        self.logger.info(f"🔍 Enhancing {len(blog_ideas)} ideas with monetization analysis")
        
        enhanced_ideas = []
        
        for idea in blog_ideas:
            try:
                # Calculate monetization scores
                monetization_analysis = await self._analyze_monetization_potential(idea, context)
                
                # Add monetization data to idea
                enhanced_idea = idea.copy()
                enhanced_idea.update({
                    "monetization_analysis": monetization_analysis,
                    "monetization_score": monetization_analysis["overall_monetization_score"],
                    "revenue_potential": monetization_analysis["estimated_annual_revenue"],
                    "monetization_priority": monetization_analysis["monetization_priority"]
                })
                
                enhanced_ideas.append(enhanced_idea)
                
            except Exception as e:
                self.logger.warning(f"Failed to enhance idea {idea.get('title', 'Unknown')}: {e}")
                enhanced_ideas.append(idea)
        
        # Sort by monetization score
        enhanced_ideas.sort(key=lambda x: x.get("monetization_score", 0), reverse=True)
        
        self.logger.info(f"✅ Enhanced {len(enhanced_ideas)} ideas with monetization analysis")
        return enhanced_ideas

    async def _analyze_monetization_potential(self, idea: Dict[str, Any], 
                                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive monetization potential analysis"""
        
        # Analyze different monetization channels
        affiliate_analysis = self._analyze_affiliate_potential(idea, context)
        product_analysis = self._analyze_digital_product_potential(idea, context)
        service_analysis = self._analyze_service_potential(idea, context)
        lead_analysis = self._analyze_lead_generation_potential(idea, context)
        
        # Calculate overall monetization score
        overall_score = (
            affiliate_analysis["score"] * self.MONETIZATION_WEIGHTS["affiliate_potential"] +
            product_analysis["score"] * self.MONETIZATION_WEIGHTS["digital_product_potential"] +
            service_analysis["score"] * self.MONETIZATION_WEIGHTS["service_potential"] +
            lead_analysis["score"] * self.MONETIZATION_WEIGHTS["lead_generation_potential"]
        )
        
        # Estimate revenue potential
        revenue_potential = self._estimate_revenue_potential(
            idea, affiliate_analysis, product_analysis, service_analysis, lead_analysis
        )
        
        # Determine monetization priority
        priority = self._determine_monetization_priority(overall_score, revenue_potential)
        
        # Generate monetization strategy
        strategy = self._generate_monetization_strategy(
            idea, affiliate_analysis, product_analysis, service_analysis, lead_analysis
        )
        
        return {
            "overall_monetization_score": int(overall_score),
            "estimated_annual_revenue": revenue_potential,
            "monetization_priority": priority,
            "affiliate_opportunities": affiliate_analysis,
            "digital_product_opportunities": product_analysis,
            "service_opportunities": service_analysis,
            "lead_generation_opportunities": lead_analysis,
            "monetization_strategy": strategy,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def _analyze_affiliate_potential(self, idea: Dict[str, Any], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze affiliate marketing potential"""
        
        title = idea.get("title", "").lower()
        keywords = idea.get("primary_keywords", []) + idea.get("secondary_keywords", [])
        content_format = idea.get("content_format", "")
        
        # Score based on commercial intent
        commercial_score = self._calculate_commercial_intent_score(title, keywords)
        
        # Identify relevant affiliate categories
        relevant_categories = self._identify_affiliate_categories(title, keywords)
        
        # Estimate affiliate revenue potential
        traffic_estimate = idea.get("performance_estimates", {}).get("estimated_monthly_traffic", 500)
        conversion_rate = 0.03  # Conservative 3% conversion rate
        avg_order_value = 150  # Conservative AOV
        commission_rate = 0.20  # Conservative 20% commission
        
        estimated_affiliate_revenue = traffic_estimate * conversion_rate * avg_order_value * commission_rate * 12
        
        # Identify specific affiliate opportunities
        affiliate_opportunities = self._generate_affiliate_opportunities(title, keywords, relevant_categories)
        
        return {
            "score": min(100, commercial_score + len(relevant_categories) * 10),
            "estimated_annual_revenue": int(estimated_affiliate_revenue),
            "relevant_categories": relevant_categories,
            "opportunities": affiliate_opportunities,
            "recommended_approach": self._get_affiliate_recommendation(content_format)
        }

    def _analyze_digital_product_potential(self, idea: Dict[str, Any], 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential for digital products"""
        
        title = idea.get("title", "")
        keywords = idea.get("primary_keywords", [])
        difficulty = idea.get("difficulty_level", "intermediate")
        
        # Product type opportunities
        product_types = self._identify_digital_product_types(title, keywords, difficulty)
        
        # Market size estimation
        traffic_estimate = idea.get("performance_estimates", {}).get("estimated_monthly_traffic", 500)
        
        # Revenue calculation for each product type
        product_revenue = 0
        for product in product_types:
            if product["type"] == "ebook":
                product_revenue += traffic_estimate * 0.02 * 29  # 2% conversion at $29
            elif product["type"] == "course":
                product_revenue += traffic_estimate * 0.015 * 199  # 1.5% conversion at $199
            elif product["type"] == "template":
                product_revenue += traffic_estimate * 0.03 * 49  # 3% conversion at $49
            elif product["type"] == "tool":
                product_revenue += traffic_estimate * 0.01 * 99  # 1% conversion at $99
        
        estimated_product_revenue = int(product_revenue * 12)
        
        return {
            "score": min(100, len(product_types) * 20 + 30),
            "estimated_annual_revenue": estimated_product_revenue,
            "product_types": product_types,
            "development_complexity": self._assess_product_complexity(product_types),
            "market_validation": self._validate_product_market(product_types, keywords)
        }

    def _analyze_service_potential(self, idea: Dict[str, Any], 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential for service offerings"""
        
        title = idea.get("title", "")
        keywords = idea.get("primary_keywords", [])
        target_audience = context.get("research_context", {}).get("target_audience", "professional")
        
        # Identify service opportunities
        service_types = self._identify_service_types(title, keywords, target_audience)
        
        # Calculate service revenue potential
        traffic_estimate = idea.get("performance_estimates", {}).get("estimated_monthly_traffic", 500)
        
        service_revenue = 0
        for service in service_types:
            if service["type"] == "consulting":
                service_revenue += traffic_estimate * 0.005 * 500  # 0.5% conversion at $500
            elif service["type"] == "coaching":
                service_revenue += traffic_estimate * 0.003 * 1000  # 0.3% conversion at $1000
            elif service["type"] == "done_for_you":
                service_revenue += traffic_estimate * 0.001 * 5000  # 0.1% conversion at $5000
        
        estimated_service_revenue = int(service_revenue * 12)
        
        return {
            "score": min(100, len(service_types) * 25 + 20),
            "estimated_annual_revenue": estimated_service_revenue,
            "service_types": service_types,
            "target_audience_fit": self._assess_audience_service_fit(target_audience, service_types),
            "scalability": self._assess_service_scalability(service_types)
        }

    def _analyze_lead_generation_potential(self, idea: Dict[str, Any], 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze lead generation potential"""
        
        title = idea.get("title", "")
        keywords = idea.get("primary_keywords", [])
        content_format = idea.get("content_format", "")
        
        # Lead magnet opportunities
        lead_magnets = self._identify_lead_magnet_opportunities(title, keywords, content_format)
        
        # Calculate lead value
        traffic_estimate = idea.get("performance_estimates", {}).get("estimated_monthly_traffic", 500)
        conversion_rate = 0.05  # 5% lead conversion
        lead_value = 25  # Conservative lead value
        
        estimated_lead_revenue = int(traffic_estimate * conversion_rate * lead_value * 12)
        
        return {
            "score": min(100, len(lead_magnets) * 15 + 40),
            "estimated_annual_revenue": estimated_lead_revenue,
            "lead_magnet_opportunities": lead_magnets,
            "email_sequence_potential": self._assess_email_sequence_potential(title, keywords),
            "nurturing_strategy": self._generate_lead_nurturing_strategy(lead_magnets)
        }

    def _calculate_commercial_intent_score(self, title: str, keywords: List[str]) -> int:
        """Calculate commercial intent score based on keywords"""
        
        title_lower = title.lower()
        keywords_lower = [kw.lower() for kw in keywords]
        
        score = 0
        
        # High intent keywords
        for word in self.COMMERCIAL_KEYWORDS["high_intent"]:
            if word in title_lower:
                score += 15
            for kw in keywords_lower:
                if word in kw:
                    score += 8
        
        # Medium intent keywords
        for word in self.COMMERCIAL_KEYWORDS["medium_intent"]:
            if word in title_lower:
                score += 10
            for kw in keywords_lower:
                if word in kw:
                    score += 5
        
        # Product research keywords
        for word in self.COMMERCIAL_KEYWORDS["product_research"]:
            if word in title_lower:
                score += 8
            for kw in keywords_lower:
                if word in kw:
                    score += 4
        
        return min(100, score)

    def _identify_affiliate_categories(self, title: str, keywords: List[str]) -> List[str]:
        """Identify relevant affiliate categories"""
        
        text = (title + " " + " ".join(keywords)).lower()
        categories = []
        
        category_keywords = {
            "saas": ["software", "platform", "tool", "app", "saas", "cloud"],
            "ecommerce": ["product", "buy", "shop", "store", "amazon", "ecommerce"],
            "digital_products": ["course", "ebook", "template", "download", "digital"],
            "online_courses": ["learn", "course", "training", "education", "tutorial"],
            "software_tools": ["software", "tool", "plugin", "extension", "app"],
            "web_hosting": ["hosting", "domain", "website", "wordpress", "server"],
            "marketing_tools": ["marketing", "seo", "social media", "email", "analytics"]
        }
        
        for category, kw_list in category_keywords.items():
            if any(kw in text for kw in kw_list):
                categories.append(category)
        
        return categories[:3]  # Return top 3 categories

    def _generate_affiliate_opportunities(self, title: str, keywords: List[str], 
                                      categories: List[str]) -> List[Dict[str, Any]]:
        """Generate specific affiliate opportunities"""
        
        opportunities = []
        
        for category in categories:
            if category in self.AFFILIATE_CATEGORIES:
                opportunities.append({
                    "category": category,
                    "commission_rate": self.AFFILIATE_CATEGORIES[category]["commission"],
                    "cookie_duration": self.AFFILIATE_CATEGORIES[category]["cookie_duration"],
                    "recommended_programs": self._get_recommended_programs(category),
                    "content_integration": self._suggest_content_integration(title, category)
                })
        
        return opportunities

    def _get_affiliate_recommendation(self, content_format: str) -> str:
        """Get affiliate recommendation strategy based on content format"""
        
        recommendations = {
            "how_to_guide": "Include tool tutorials and step-by-step implementations",
            "listicle": "Create comparison tables with pros/cons for each tool",
            "comparison": "Detailed feature comparisons with clear winner recommendations",
            "case_study": "Show real results achieved with specific tools",
            "tool_review": "In-depth analysis with hands-on testing and screenshots",
            "beginner_guide": "Start with free tools and suggest upgrades when ready"
        }
        
        return recommendations.get(content_format, "Natural product mentions within educational content")

    def _identify_digital_product_types(self, title: str, keywords: List[str], 
                                      difficulty: str) -> List[Dict[str, Any]]:
        """Identify suitable digital product types"""
        
        products = []
        text = (title + " " + " ".join(keywords)).lower()
        
        product_mappings = {
            "ebook": ["guide", "complete", "ultimate", "comprehensive", "handbook"],
            "course": ["masterclass", "training", "bootcamp", "academy", "workshop"],
            "template": ["template", "checklist", "worksheet", "planner", "framework"],
            "tool": ["calculator", "generator", "analyzer", "tracker", "dashboard"]
        }
        
        for product_type, indicators in product_mappings.items():
            if any(indicator in text for indicator in indicators):
                products.append({
                    "type": product_type,
                    "estimated_price": self._estimate_product_price(product_type, difficulty),
                    "development_time": self._estimate_development_time(product_type),
                    "market_demand": "high" if any(indicator in text for indicator in indicators[:2]) else "medium"
                })
        
        return products[:2]  # Return top 2 products

    def _identify_service_types(self, title: str, keywords: List[str], 
                              target_audience: str) -> List[Dict[str, Any]]:
        """Identify suitable service offerings"""
        
        services = []
        text = (title + " " + " ".join(keywords)).lower()
        
        service_mappings = {
            "consulting": ["strategy", "consulting", "advice", "planning", "optimization"],
            "coaching": ["coaching", "mentoring", "training", "guidance", "support"],
            "done_for_you": ["implementation", "setup", "management", "service", "solution"]
        }
        
        for service_type, indicators in service_mappings.items():
            if any(indicator in text for indicator in indicators):
                services.append({
                    "type": service_type,
                    "estimated_price": self._estimate_service_price(service_type, target_audience),
                    "delivery_method": "remote" if service_type != "done_for_you" else "hybrid",
                    "scalability": "high" if service_type == "consulting" else "medium"
                })
        
        return services

    def _identify_lead_magnet_opportunities(self, title: str, keywords: List[str], 
                                          content_format: str) -> List[Dict[str, Any]]:
        """Identify lead magnet opportunities"""
        
        magnets = []
        text = (title + " " + " ".join(keywords)).lower()
        
        magnet_types = {
            "checklist": ["checklist", "steps", "process", "guide"],
            "template": ["template", "framework", "worksheet", "planner"],
            "ebook": ["ebook", "guide", "handbook", "manual"],
            "calculator": ["calculator", "tool", "estimator", "planner"],
            "swipe_file": ["examples", "templates", "samples", "scripts"]
        }
        
        for magnet_type, indicators in magnet_types.items():
            if any(indicator in text for indicator in indicators):
                magnets.append({
                    "type": magnet_type,
                    "estimated_conversion_rate": 0.05 if magnet_type == "calculator" else 0.08,
                    "value_proposition": self._create_magnet_value_proposition(magnet_type, title),
                    "follow_up_sequence": self._create_follow_up_sequence(magnet_type)
                })
        
        return magnets[:2]  # Return top 2 magnets

    def _estimate_revenue_potential(self, idea: Dict[str, Any], 
                                  affiliate_analysis: Dict[str, Any],
                                  product_analysis: Dict[str, Any],
                                  service_analysis: Dict[str, Any],
                                  lead_analysis: Dict[str, Any]) -> int:
        """Estimate total annual revenue potential"""
        
        affiliate_revenue = affiliate_analysis.get("estimated_annual_revenue", 0)
        product_revenue = product_analysis.get("estimated_annual_revenue", 0)
        service_revenue = service_analysis.get("estimated_annual_revenue", 0)
        lead_revenue = lead_analysis.get("estimated_annual_revenue", 0)
        
        # Apply diversification factor (not all revenue streams will be maximized)
        diversification_factor = 0.7
        
        total_revenue = (affiliate_revenue + product_revenue + service_revenue + lead_revenue) * diversification_factor
        
        return int(total_revenue)

    def _determine_monetization_priority(self, overall_score: float, revenue_potential: int) -> str:
        """Determine monetization priority based on score and revenue"""
        
        if int(overall_score) >= 80 and int(revenue_potential) >= 5000:
            return "High Priority - Immediate Implementation"
        elif int(overall_score) >= 60 and int(revenue_potential) >= 2000:
            return "Medium Priority - Next 30 Days"
        elif int(overall_score) >= 40 and int(revenue_potential) >= 1000:
            return "Low Priority - Next 90 Days"
        else:
            return "Research Phase - Validate Market"

    def _generate_monetization_strategy(self, idea: Dict[str, Any], 
                                      affiliate_analysis: Dict[str, Any],
                                      product_analysis: Dict[str, Any],
                                      service_analysis: Dict[str, Any],
                                      lead_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive monetization strategy"""
        
        strategy = {
            "immediate_actions": [],
            "30_day_plan": [],
            "90_day_plan": [],
            "long_term_strategy": []
        }
        
        # Immediate actions (within 7 days)
        if affiliate_analysis["score"] >= 60:
            strategy["immediate_actions"].append("Research and join relevant affiliate programs")
            strategy["immediate_actions"].append("Update content with affiliate links")
        
        if lead_analysis["score"] >= 50:
            strategy["immediate_actions"].append("Create lead magnet based on content")
            strategy["immediate_actions"].append("Set up email capture system")
        
        # 30-day plan
        if product_analysis["score"] >= 60:
            strategy["30_day_plan"].append("Develop digital product outline")
            strategy["30_day_plan"].append("Create product landing page")
        
        if service_analysis["score"] >= 70:
            strategy["30_day_plan"].append("Create service packages")
            strategy["30_day_plan"].append("Set up consultation booking system")
        
        # 90-day plan
        strategy["90_day_plan"].extend([
            "Launch first digital product",
            "Implement advanced affiliate strategies",
            "Develop premium service offerings",
            "Create sales funnels for each revenue stream"
        ])
        
        # Long-term strategy
        strategy["long_term_strategy"].extend([
            "Build product ecosystem around topic",
            "Develop recurring revenue streams",
            "Create high-ticket service offerings",
            "Build authority and premium pricing"
        ])
        
        return strategy

    # Helper methods for estimates and recommendations
    def _estimate_product_price(self, product_type: str, difficulty: str) -> int:
        """Estimate appropriate price for digital products"""
        base_prices = {
            "ebook": 19,
            "course": 99,
            "template": 39,
            "tool": 79
        }
        
        difficulty_multipliers = {
            "beginner": 0.8,
            "intermediate": 1.0,
            "advanced": 1.5
        }
        
        base = base_prices.get(product_type, 49)
        multiplier = difficulty_multipliers.get(difficulty, 1.0)
        
        return int(base * multiplier)

    def _estimate_development_time(self, product_type: str) -> str:
        """Estimate development time for digital products"""
        development_times = {
            "ebook": "2-4 weeks",
            "course": "4-8 weeks",
            "template": "1-2 weeks",
            "tool": "6-12 weeks"
        }
        return development_times.get(product_type, "4-6 weeks")

    def _assess_product_complexity(self, product_types: List[Dict[str, Any]]) -> str:
        """Assess complexity of digital products"""
        if not product_types:
            return "Low"
        
        complexity_scores = {
            "ebook": 1,
            "template": 1,
            "course": 2,
            "tool": 3
        }
        
        max_complexity = max([complexity_scores.get(pt["type"], 2) for pt in product_types])
        
        if max_complexity <= 1:
            return "Low"
        elif max_complexity == 2:
            return "Medium"
        else:
            return "High"

    def _validate_product_market(self, product_types: List[Dict[str, Any]], keywords: List[str]) -> str:
        """Validate market demand for digital products"""
        market_keywords = ["guide", "course", "template", "tool", "software", "system"]
        keyword_text = " ".join(keywords).lower()
        
        keyword_matches = sum(1 for kw in market_keywords if kw in keyword_text)
        
        if keyword_matches >= 3:
            return "High market validation"
        elif keyword_matches >= 1:
            return "Medium market validation"
        else:
            return "Requires market research"

    def _assess_audience_service_fit(self, target_audience: str, service_types: List[Dict[str, Any]]) -> str:
        """Assess how well services fit the target audience"""
        if not service_types:
            return "Low fit - Consider different service offerings"
        
        audience_service_mapping = {
            "professional": ["consulting", "coaching"],
            "entrepreneur": ["consulting", "coaching", "done_for_you"],
            "small_business": ["done_for_you", "coaching"],
            "enterprise": ["consulting", "done_for_you"]
        }
        
        recommended_services = audience_service_mapping.get(target_audience, ["consulting"])
        service_types_list = [st["type"] for st in service_types]
        
        matches = sum(1 for st in service_types_list if st in recommended_services)
        
        if matches >= 2:
            return "High fit - Strong alignment with audience needs"
        elif matches >= 1:
            return "Medium fit - Good alignment with some optimization needed"
        else:
            return "Low fit - Consider audience-specific service offerings"

    def _assess_service_scalability(self, service_types: List[Dict[str, Any]]) -> str:
        """Assess scalability of service offerings"""
        if not service_types:
            return "Limited scalability"
        
        scalability_scores = {
            "consulting": "High",
            "coaching": "Medium",
            "done_for_you": "Low"
        }
        
        service_types_list = [st["type"] for st in service_types]
        
        if "consulting" in service_types_list:
            return "High scalability - Can leverage group programs and digital products"
        elif "coaching" in service_types_list:
            return "Medium scalability - Can create courses and group programs"
        else:
            return "Low scalability - Consider productizing services"

    def _assess_email_sequence_potential(self, title: str, keywords: List[str]) -> str:
        """Assess email sequence potential based on content topic"""
        sequence_keywords = ["guide", "strategy", "tips", "best", "complete", "ultimate"]
        title_lower = title.lower()
        keyword_text = " ".join(keywords).lower()
        
        combined_text = title_lower + " " + keyword_text
        
        matches = sum(1 for kw in sequence_keywords if kw in combined_text)
        
        if matches >= 3:
            return "High potential - Strong educational content opportunity"
        elif matches >= 1:
            return "Medium potential - Good educational value"
        else:
            return "Low potential - Consider content angle optimization"

    def _generate_lead_nurturing_strategy(self, lead_magnets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate lead nurturing strategy based on lead magnets"""
        if not lead_magnets:
            return {
                "strategy_type": "Direct sales",
                "email_count": 3,
                "duration_days": 7,
                "key_messages": ["Problem identification", "Solution presentation", "Product offer"]
            }
        
        magnet_types = [lm["type"] for lm in lead_magnets]
        
        if "calculator" in magnet_types or "tool" in magnet_types:
            return {
                "strategy_type": "Value demonstration",
                "email_count": 5,
                "duration_days": 14,
                "key_messages": [
                    "Tool usage guide",
                    "Advanced strategies",
                    "Case study examples",
                    "Premium tool upsell",
                    "Consultation offer"
                ]
            }
        elif "template" in magnet_types or "checklist" in magnet_types:
            return {
                "strategy_type": "Implementation support",
                "email_count": 4,
                "duration_days": 10,
                "key_messages": [
                    "Template customization",
                    "Best practices",
                    "Common mistakes",
                    "Premium templates offer"
                ]
            }
        else:
            return {
                "strategy_type": "Educational series",
                "email_count": 5,
                "duration_days": 14,
                "key_messages": [
                    "Welcome and overview",
                    "Problem deep-dive",
                    "Solution framework",
                    "Case study",
                    "Product recommendation"
                ]
            }

    def _estimate_service_price(self, service_type: str, target_audience: str) -> int:
        """Estimate appropriate price for services"""
        base_prices = {
            "consulting": {"professional": 200, "entrepreneur": 150, "small_business": 100},
            "coaching": {"professional": 500, "entrepreneur": 300, "small_business": 200},
            "done_for_you": {"professional": 2000, "entrepreneur": 1500, "small_business": 1000}
        }
        
        service_pricing = base_prices.get(service_type, base_prices["consulting"])
        return service_pricing.get(target_audience, 150)

    def _get_recommended_programs(self, category: str) -> List[str]:
        """Get recommended affiliate programs for category"""
        programs = {
            "saas": ["PartnerStack", "Impact", "Direct vendor programs"],
            "ecommerce": ["Amazon Associates", "ShareASale", "CJ Affiliate"],
            "digital_products": ["ClickBank", "JVZoo", "Gumroad"],
            "online_courses": ["Udemy Affiliate", "Teachable Affiliate", "Thinkific"],
            "software_tools": ["AppSumo", "StackSocial", "Vendor direct programs"],
            "web_hosting": ["Bluehost", "SiteGround", "WP Engine"],
            "marketing_tools": ["HubSpot", "SEMrush", "Ahrefs", "ConvertKit"]
        }
        
        return programs.get(category, ["Research vendor programs"])

    def _suggest_content_integration(self, title: str, category: str) -> str:
        """Suggest how to integrate affiliate links naturally"""
        suggestions = {
            "saas": "Create comparison tables and in-depth reviews",
            "ecommerce": "Product roundups and buyer's guides",
            "digital_products": "How-to guides with tool recommendations",
            "software_tools": "Tutorial content with software walkthroughs"
        }
        
        return suggestions.get(category, "Natural product mentions within educational content")

    def _create_magnet_value_proposition(self, magnet_type: str, title: str) -> str:
        """Create compelling value proposition for lead magnet"""
        propositions = {
            "checklist": f"Download the complete {title} checklist to ensure you don't miss any crucial steps",
            "template": f"Get the exact {title} template I use to save hours of work",
            "ebook": f"Free guide: The complete {title} handbook with actionable strategies",
            "calculator": f"Use this {title} calculator to get instant personalized results"
        }
        
        return propositions.get(magnet_type, f"Exclusive {title} resource to accelerate your results")

    def _create_follow_up_sequence(self, magnet_type: str) -> List[str]:
        """Create email follow-up sequence for lead magnet"""
        sequences = {
            "checklist": [
                "Implementation guide for checklist",
                "Common mistakes to avoid",
                "Advanced tips and tricks",
                "Product/service recommendations"
            ],
            "template": [
                "Template customization guide",
                "Best practices for usage",
                "Premium template upsell",
                "Done-for-you service offer"
            ]
        }
        
        return sequences.get(magnet_type, [
            "Welcome and implementation guide",
            "Advanced strategies",
            "Product recommendations",
            "Service consultation offer"
        ])


# Usage example and integration
async def enhance_blog_ideas_with_monetization(blog_ideas: List[Dict[str, Any]], 
                                             context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convenience function to enhance blog ideas with monetization analysis"""
    
    enhancer = MonetizationEnhancer()
    return await enhancer.enhance_ideas_with_monetization(blog_ideas, context)


if __name__ == "__main__":
    import asyncio
    
    async def test_monetization_enhancement():
        """Test the monetization enhancement"""
        
        # Sample blog ideas for testing
        sample_ideas = [
            {
                "title": "Complete Guide to AI-Powered Marketing Automation Tools 2025",
                "description": "Learn how to implement AI marketing automation to scale your business",
                "primary_keywords": ["ai marketing automation", "marketing tools", "business automation"],
                "secondary_keywords": ["ai marketing software", "automation tools", "marketing platforms"],
                "content_format": "how_to_guide",
                "difficulty_level": "intermediate",
                "performance_estimates": {
                    "estimated_monthly_traffic": 1200
                }
            },
            {
                "title": "Best Email Marketing Software Compared: ConvertKit vs Mailchimp vs ActiveCampaign",
                "description": "Detailed comparison of top email marketing platforms with pricing and features",
                "primary_keywords": ["email marketing software", "email marketing comparison", "best email tools"],
                "secondary_keywords": ["convertkit review", "mailchimp vs activecampaign", "email platform pricing"],
                "content_format": "comparison",
                "difficulty_level": "beginner",
                "performance_estimates": {
                    "estimated_monthly_traffic": 2500
                }
            }
        ]
        
        context = {
            "research_context": {
                "target_audience": "professional",
                "topic": "digital marketing"
            }
        }
        
        enhanced_ideas = await enhance_blog_ideas_with_monetization(sample_ideas, context)
        
        print("🎯 Monetization Analysis Results:")
        print("=" * 50)
        
        for i, idea in enumerate(enhanced_ideas, 1):
            analysis = idea.get("monetization_analysis", {})
            print(f"{i}. {idea['title']}")
            print(f"   💰 Monetization Score: {analysis.get('monetization_score', 0)}/100")
            print(f"   💵 Est. Annual Revenue: ${analysis.get('estimated_annual_revenue', 0):,}")
            print(f"   🎯 Priority: {analysis.get('monetization_priority', 'Unknown')}")
            print(f"   🔗 Affiliate Categories: {', '.join(analysis.get('affiliate_opportunities', {}).get('relevant_categories', []))}")
            print()
    
    asyncio.run(test_monetization_enhancement())