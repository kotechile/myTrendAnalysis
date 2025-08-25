#!/usr/bin/env python3
"""
Enhanced Content Opportunities Generator - Topic-Specific and Relevant
Fixes the generic content opportunity issue in trend research
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional

class EnhancedContentOpportunitiesGenerator:
    """Enhanced generator that ensures topic-specific content opportunities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_topic_specific_opportunities_prompt(
        self, 
        topic: str, 
        trending_topics: List[Dict], 
        focus_area: str = "general",
        target_audience: str = "professional"
    ) -> str:
        """Create a highly specific prompt that forces topic relevance"""
        
        # Extract trending topic names for context
        trending_names = [t.get("trend", t.get("trend_name", "")) for t in trending_topics[:3]]
        trending_context = ", ".join([name for name in trending_names if name])
        
        # Create topic-specific content formats
        topic_formats = self._get_topic_specific_formats(topic)
        
        prompt = f"""
You are a content strategist specializing in {topic}. Create EXACTLY 6 content opportunities specifically for "{topic}" that are:

1. DIRECTLY related to {topic} (not generic marketing content)
2. Based on these trending subtopics: {trending_context}
3. Targeted at {target_audience} in the {focus_area} space
4. Actionable and specific to {topic}

STRICT REQUIREMENT: Every opportunity MUST contain the word "{topic}" or closely related terms.

Return as JSON array with this EXACT format:
[
  {{
    "opportunity_title": "Specific {topic} content title",
    "content_format": "how_to_guide",
    "difficulty_score": 45,
    "engagement_potential": "High",
    "keywords": ["keyword1 {topic}", "keyword2 {topic}"],
    "topic_relevance_score": 95,
    "why_relevant": "Explanation of direct connection to {topic}"
  }}
]

Content formats to choose from: {topic_formats}

EXAMPLES for {topic}:
- "Complete {topic} Buyer's Guide for {target_audience}"
- "Top 10 {topic} Mistakes to Avoid in 2025"
- "{topic} ROI Calculator and Implementation Framework"
- "How to Choose the Right {topic} Solution for Your Business"

Focus on PRACTICAL, SPECIFIC {topic} content that solves real problems.
Return ONLY valid JSON, no other text.
"""
        return prompt
    
    def _get_topic_specific_formats(self, topic: str) -> List[str]:
        """Get content formats specific to the topic domain"""
        
        # Topic-specific format mapping
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ["security", "safety", "protection"]):
            return ["buyer_guide", "comparison", "checklist", "case_study", "how_to_guide", "assessment_tool"]
        elif any(word in topic_lower for word in ["marketing", "advertising", "sales"]):
            return ["strategy_guide", "template", "case_study", "toolkit", "campaign_analysis", "roi_calculator"]
        elif any(word in topic_lower for word in ["technology", "software", "ai", "automation"]):
            return ["implementation_guide", "comparison", "tutorial", "best_practices", "integration_guide", "troubleshooting"]
        elif any(word in topic_lower for word in ["health", "fitness", "wellness"]):
            return ["plan", "guide", "tracker", "assessment", "routine", "nutrition_guide"]
        elif any(word in topic_lower for word in ["finance", "investment", "money"]):
            return ["calculator", "guide", "strategy", "analysis", "planner", "comparison"]
        else:
            # Generic but still better than current
            return ["how_to_guide", "buyer_guide", "comparison", "checklist", "case_study", "best_practices"]
    
    async def generate_topic_specific_opportunities(
        self,
        topic: str,
        trending_topics: List[Dict],
        llm_client,
        llm_config: Dict[str, Any],
        focus_area: str = "general",
        target_audience: str = "professional"
    ) -> List[Dict[str, Any]]:
        """Generate content opportunities that are guaranteed to be topic-specific"""
        
        self.logger.info(f"🎯 Generating topic-specific opportunities for: {topic}")
        
        try:
            # Create highly specific prompt
            prompt = self.create_topic_specific_opportunities_prompt(
                topic, trending_topics, focus_area, target_audience
            )
            
            # Call LLM with retry
            response = await asyncio.wait_for(
                self._call_llm_with_retry(llm_client, prompt, llm_config),
                timeout=30
            )
            
            # Parse and validate response
            opportunities = self._parse_and_validate_opportunities(response, topic)
            
            # If we got valid topic-specific opportunities, enhance them
            if opportunities and self._validate_topic_relevance(opportunities, topic):
                enhanced_opportunities = self._enhance_opportunities_with_intelligence(
                    opportunities, topic, trending_topics
                )
                self.logger.info(f"✅ Generated {len(enhanced_opportunities)} topic-specific opportunities")
                return enhanced_opportunities
            else:
                self.logger.warning("⚠️ LLM response not topic-specific enough, using smart fallback")
                return self._create_smart_topic_fallback(topic, trending_topics, target_audience)
                
        except Exception as e:
            self.logger.error(f"❌ Topic-specific generation failed: {e}")
            return self._create_smart_topic_fallback(topic, trending_topics, target_audience)
    
    def _parse_and_validate_opportunities(self, response: str, topic: str) -> List[Dict[str, Any]]:
        """Parse LLM response and validate topic relevance"""
        
        try:
            # Extract JSON from response
            json_data = self._extract_json_from_response(response)
            
            if isinstance(json_data, list):
                opportunities_list = json_data
            elif isinstance(json_data, dict) and 'opportunities' in json_data:
                opportunities_list = json_data['opportunities']
            else:
                raise ValueError("Invalid JSON structure")
            
            # Validate each opportunity for topic relevance
            validated_opportunities = []
            topic_lower = topic.lower()
            
            for opp in opportunities_list:
                if isinstance(opp, dict):
                    title = opp.get("opportunity_title", "").lower()
                    keywords = str(opp.get("keywords", [])).lower()
                    
                    # Check if opportunity is actually about the topic
                    if (topic_lower in title or 
                        any(word in title for word in topic_lower.split()) or
                        topic_lower in keywords):
                        validated_opportunities.append(opp)
                    else:
                        self.logger.warning(f"⚠️ Filtered out non-relevant opportunity: {opp.get('opportunity_title', 'Unknown')}")
            
            return validated_opportunities
            
        except Exception as e:
            self.logger.error(f"❌ Failed to parse opportunities: {e}")
            return []
    
    def _validate_topic_relevance(self, opportunities: List[Dict], topic: str) -> bool:
        """Validate that opportunities are actually relevant to the topic"""
        
        if not opportunities:
            return False
        
        topic_words = set(topic.lower().split())
        relevant_count = 0
        
        for opp in opportunities:
            title = opp.get("opportunity_title", "").lower()
            keywords = str(opp.get("keywords", [])).lower()
            
            # Check for topic word overlap
            title_words = set(title.split())
            keyword_words = set(keywords.split())
            
            overlap = topic_words.intersection(title_words.union(keyword_words))
            if overlap:
                relevant_count += 1
        
        # At least 50% of opportunities should be relevant
        relevance_ratio = relevant_count / len(opportunities)
        
        self.logger.info(f"📊 Topic relevance ratio: {relevance_ratio:.2f} ({relevant_count}/{len(opportunities)})")
        return relevance_ratio >= 0.5
    
    def _enhance_opportunities_with_intelligence(
        self,
        opportunities: List[Dict],
        topic: str,
        trending_topics: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Enhance opportunities with strategic intelligence"""
        
        enhanced_opportunities = []
        
        for i, opp in enumerate(opportunities):
            # Get topic-specific difficulty and monetization
            difficulty = self._calculate_topic_specific_difficulty(opp, topic)
            monetization = self._assess_topic_monetization(opp, topic)
            distribution = self._suggest_topic_distribution(topic)
            
            enhanced_opp = {
                "opportunity": opp.get("opportunity_title", f"{topic} Content Opportunity #{i+1}"),
                "format": opp.get("content_format", "how_to_guide"),
                "difficulty": difficulty,
                "engagement_potential": opp.get("engagement_potential", "medium"),
                "time_investment": self._estimate_time_investment(difficulty),
                "keywords": opp.get("keywords", [f"{topic} guide"]),
                "monetization": monetization,
                "distribution": distribution,
                "topic_relevance_score": opp.get("topic_relevance_score", 95),
                "why_relevant": opp.get("why_relevant", f"Directly addresses {topic} needs"),
                "strategic_intelligence": {
                    "strategic_rationale": f"High-value {topic} content opportunity",
                    "competitive_advantage": f"Specialized {topic} expertise positioning",
                    "authority_building_value": f"Establishes {topic} thought leadership",
                    "lead_generation_potential": self._assess_lead_potential(topic),
                    "traffic_potential": "Medium to High",
                    "conversion_optimization": f"{topic}-specific lead capture approach"
                }
            }
            enhanced_opportunities.append(enhanced_opp)
        
        return enhanced_opportunities
    
    def _create_smart_topic_fallback(
        self, 
        topic: str, 
        trending_topics: List[Dict], 
        target_audience: str
    ) -> List[Dict[str, Any]]:
        """Create intelligent topic-specific fallback opportunities"""
        
        self.logger.info(f"🔧 Creating smart fallback opportunities for: {topic}")
        
        # Topic-specific opportunity templates
        topic_lower = topic.lower()
        
        # Define topic-specific templates
        if any(word in topic_lower for word in ["security", "safety", "protection"]):
            templates = self._get_security_templates(topic)
        elif any(word in topic_lower for word in ["marketing", "advertising", "sales"]):
            templates = self._get_marketing_templates(topic)
        elif any(word in topic_lower for word in ["health", "fitness", "wellness"]):
            templates = self._get_health_templates(topic)
        elif any(word in topic_lower for word in ["technology", "software", "ai"]):
            templates = self._get_technology_templates(topic)
        elif any(word in topic_lower for word in ["finance", "investment", "money"]):
            templates = self._get_finance_templates(topic)
        else:
            templates = self._get_generic_but_specific_templates(topic)
        
        # Build opportunities from templates
        opportunities = []
        for i, template in enumerate(templates[:6]):  # Limit to 6
            opportunity = {
                "opportunity": template["title"].format(topic=topic, audience=target_audience),
                "format": template["format"],
                "difficulty": template["difficulty"],
                "engagement_potential": template["engagement"],
                "time_investment": template["time"],
                "keywords": template["keywords"],
                "monetization": template["monetization"].format(topic=topic),
                "distribution": template["distribution"],
                "topic_relevance_score": 100,  # Our templates are guaranteed relevant
                "why_relevant": f"Specifically designed for {topic} market needs",
                "strategic_intelligence": {
                    "strategic_rationale": template["rationale"].format(topic=topic),
                    "competitive_advantage": f"Specialized {topic} content",
                    "authority_building_value": f"Builds {topic} expertise",
                    "lead_generation_potential": "High",
                    "traffic_potential": "Medium to High",
                    "conversion_optimization": f"{topic}-focused lead capture"
                }
            }
            opportunities.append(opportunity)
        
        return opportunities
    
    def _get_security_templates(self, topic: str) -> List[Dict]:
        """Security-specific content templates"""
        return [
            {
                "title": "Complete {topic} Buyer's Guide for {audience}",
                "format": "buyer_guide",
                "difficulty": 50,
                "engagement": "high",
                "time": "2-3 weeks",
                "keywords": [f"{topic} guide", f"best {topic}", f"{topic} comparison"],
                "monetization": "High potential for {topic} affiliate partnerships",
                "distribution": ["Blog", "LinkedIn", "Security Forums"],
                "rationale": "Buyers guides are highly searched in {topic}"
            },
            {
                "title": "Top 10 {topic} Mistakes That Could Cost You Everything",
                "format": "listicle",
                "difficulty": 35,
                "engagement": "very_high",
                "time": "1-2 weeks",
                "keywords": [f"{topic} mistakes", f"{topic} fails", f"avoid {topic} problems"],
                "monetization": "Strong lead magnet for {topic} consultations",
                "distribution": ["Social Media", "Blog", "Email"],
                "rationale": "Mistake-focused content drives high engagement in {topic}"
            },
            {
                "title": "{topic} ROI Calculator: Prove Your Investment Value",
                "format": "interactive_tool",
                "difficulty": 70,
                "engagement": "very_high",
                "time": "3-4 weeks",
                "keywords": [f"{topic} ROI", f"{topic} calculator", f"{topic} investment"],
                "monetization": "Excellent {topic} consultation lead generator",
                "distribution": ["Website", "LinkedIn", "Industry Publications"],
                "rationale": "ROI tools are highly valuable in {topic} decisions"
            },
            {
                "title": "{topic} Audit Checklist: 50-Point Assessment",
                "format": "checklist",
                "difficulty": 40,
                "engagement": "high",
                "time": "1-2 weeks",
                "keywords": [f"{topic} checklist", f"{topic} audit", f"{topic} assessment"],
                "monetization": "Lead magnet for {topic} services",
                "distribution": ["Email", "Blog", "PDF Download"],
                "rationale": "Checklists are practical tools for {topic} implementation"
            }
        ]
    
    def _get_marketing_templates(self, topic: str) -> List[Dict]:
        """Marketing-specific content templates"""
        return [
            {
                "title": "{topic} Strategy Template: Complete Campaign Framework",
                "format": "template",
                "difficulty": 45,
                "engagement": "high",
                "time": "2-3 weeks",
                "keywords": [f"{topic} strategy", f"{topic} template", f"{topic} framework"],
                "monetization": "Gateway to {topic} consulting services",
                "distribution": ["Blog", "LinkedIn", "Marketing Communities"],
                "rationale": "Templates provide immediate value in {topic}"
            },
            {
                "title": "Case Study: How We Increased {topic} ROI by 300%",
                "format": "case_study",
                "difficulty": 55,
                "engagement": "very_high",
                "time": "2-3 weeks",
                "keywords": [f"{topic} case study", f"{topic} results", f"{topic} ROI"],
                "monetization": "Showcases {topic} expertise for client acquisition",
                "distribution": ["Website", "LinkedIn", "Industry Publications"],
                "rationale": "Case studies build credibility in {topic}"
            }
        ]
    
    def _get_technology_templates(self, topic: str) -> List[Dict]:
        """Technology-specific content templates"""
        return [
            {
                "title": "{topic} Implementation Guide: Step-by-Step Setup",
                "format": "implementation_guide",
                "difficulty": 60,
                "engagement": "high",
                "time": "3-4 weeks",
                "keywords": [f"{topic} implementation", f"{topic} setup", f"how to implement {topic}"],
                "monetization": "Leads to {topic} implementation services",
                "distribution": ["Technical Blogs", "LinkedIn", "GitHub"],
                "rationale": "Implementation guides address key {topic} adoption barriers"
            },
            {
                "title": "{topic} vs Alternatives: Complete Comparison 2025",
                "format": "comparison",
                "difficulty": 50,
                "engagement": "high",
                "time": "2-3 weeks",
                "keywords": [f"{topic} comparison", f"{topic} vs", f"best {topic}"],
                "monetization": "Affiliate opportunities for {topic} tools",
                "distribution": ["Blog", "YouTube", "Tech Forums"],
                "rationale": "Comparisons help with {topic} decision-making"
            }
        ]
    
    def _get_generic_but_specific_templates(self, topic: str) -> List[Dict]:
        """Generic templates that are still topic-specific"""
        return [
            {
                "title": "Complete {topic} Guide for Beginners",
                "format": "how_to_guide",
                "difficulty": 40,
                "engagement": "high",
                "time": "2-3 weeks",
                "keywords": [f"{topic} guide", f"beginner {topic}", f"how to {topic}"],
                "monetization": "Gateway to advanced {topic} content and services",
                "distribution": ["Blog", "YouTube", "Social Media"],
                "rationale": "Comprehensive guides establish {topic} expertise"
            },
            {
                "title": "{topic} Best Practices: 2025 Professional Standards",
                "format": "best_practices",
                "difficulty": 55,
                "engagement": "medium",
                "time": "2-3 weeks",
                "keywords": [f"{topic} best practices", f"{topic} standards", f"professional {topic}"],
                "monetization": "Positions as {topic} thought leader",
                "distribution": ["LinkedIn", "Industry Publications", "Blog"],
                "rationale": "Best practices content builds {topic} authority"
            },
            {
                "title": "{topic} Trends and Predictions for 2025",
                "format": "trend_analysis",
                "difficulty": 50,
                "engagement": "medium",
                "time": "2-3 weeks",
                "keywords": [f"{topic} trends", f"{topic} 2025", f"future of {topic}"],
                "monetization": "Establishes forward-thinking {topic} expertise",
                "distribution": ["Blog", "LinkedIn", "Industry Events"],
                "rationale": "Trend analysis showcases {topic} market knowledge"
            }
        ]
    
    # Helper methods
    def _calculate_topic_specific_difficulty(self, opp: Dict, topic: str) -> int:
        """Calculate difficulty based on topic and content format"""
        base_difficulty = opp.get("difficulty_score", 50)
        
        # Adjust based on content format
        format_adjustments = {
            "interactive_tool": +20,
            "calculator": +20,
            "assessment_tool": +15,
            "implementation_guide": +15,
            "case_study": +10,
            "comparison": +5,
            "how_to_guide": 0,
            "listicle": -5,
            "checklist": -10
        }
        
        content_format = opp.get("content_format", "how_to_guide")
        adjustment = format_adjustments.get(content_format, 0)
        
        return max(20, min(90, base_difficulty + adjustment))
    
    def _assess_topic_monetization(self, opp: Dict, topic: str) -> str:
        """Assess monetization potential for topic-specific content"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ["security", "finance", "technology", "health"]):
            return f"High monetization potential through {topic} services, affiliate partnerships, and premium content"
        elif any(word in topic_lower for word in ["marketing", "business", "consulting"]):
            return f"Excellent lead generation for {topic} consulting and service offerings"
        else:
            return f"Medium to high potential for {topic}-related products and services"
    
    def _suggest_topic_distribution(self, topic: str) -> List[str]:
        """Suggest distribution channels based on topic"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ["security", "technology"]):
            return ["LinkedIn", "Technical Blogs", "Industry Forums", "YouTube"]
        elif any(word in topic_lower for word in ["marketing", "business"]):
            return ["LinkedIn", "Marketing Blogs", "Social Media", "Email Newsletter"]
        elif any(word in topic_lower for word in ["health", "fitness"]):
            return ["Health Blogs", "Social Media", "YouTube", "Podcast"]
        else:
            return ["Blog", "LinkedIn", "Social Media", "Email Newsletter"]
    
    def _estimate_time_investment(self, difficulty: int) -> str:
        """Estimate time investment based on difficulty"""
        if difficulty >= 70:
            return "4-6 weeks"
        elif difficulty >= 55:
            return "3-4 weeks"
        elif difficulty >= 40:
            return "2-3 weeks"
        else:
            return "1-2 weeks"
    
    def _assess_lead_potential(self, topic: str) -> str:
        """Assess lead generation potential for topic"""
        topic_lower = topic.lower()
        
        high_value_topics = ["security", "finance", "technology", "consulting", "legal", "healthcare"]
        if any(word in topic_lower for word in high_value_topics):
            return "Very High"
        else:
            return "High"
    
    async def _call_llm_with_retry(self, llm_client, prompt: str, llm_config: Dict[str, Any], max_retries: int = 2) -> str:
        """Call LLM with retry logic"""
        provider = llm_config.get('provider', 'openai').lower()
        
        for attempt in range(max_retries + 1):
            try:
                if provider == 'openai':
                    response = await llm_client.chat.completions.create(
                        model=llm_config.get('model', 'gpt-4o-mini'),
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=2000,
                        timeout=30
                    )
                    return response.choices[0].message.content
                elif provider == 'anthropic':
                    response = await llm_client.messages.create(
                        model=llm_config.get('model', 'claude-3-sonnet-20240229'),
                        max_tokens=2000,
                        messages=[{"role": "user", "content": prompt}],
                        timeout=30
                    )
                    return response.content[0].text
                else:
                    raise ValueError(f"Unsupported provider: {provider}")
            except Exception as e:
                if attempt == max_retries:
                    raise
                await asyncio.sleep(2 ** attempt)
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        # Try to parse entire response as JSON
        try:
            return json.loads(response)
        except:
            pass
        
        # Look for JSON blocks in markdown
        try:
            json_pattern = r'```json\s*(.*?)\s*```'
            json_match = re.search(json_pattern, response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except:
            pass
        
        # Look for arrays/objects
        try:
            json_pattern = r'(\[.*?\]|\{.*?\})'
            json_matches = re.findall(json_pattern, response, re.DOTALL)
            for match in json_matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, (list, dict)) and len(str(parsed)) > 50:
                        return parsed
                except:
                    continue
        except:
            pass
        
        raise ValueError("No valid JSON found in response")


# INTEGRATION WITH YOUR EXISTING SYSTEM
def integrate_enhanced_opportunities_generator():
    """
    Integration instructions for your existing system:
    
    1. Replace your existing _get_content_opportunities_fast method in fixed_trend_research.py
    2. Add the enhanced generator to your EnhancedTrendResearchIntegration class
    3. Update the content opportunities generation logic
    """
    
    integration_code = '''
# Add this to your EnhancedTrendResearchIntegration class:

def __init__(self, config: Dict[str, Any]):
    self.config = config
    self.logger = logging.getLogger(__name__)
    # ADD THIS LINE:
    self.opportunities_generator = EnhancedContentOpportunitiesGenerator()

async def _get_content_opportunities_fast(
    self,
    topic: str,
    trending_topics_data: List[Dict],
    llm_client,
    llm_config: Dict[str, Any],
    focus_area: str = "general",
    target_audience: str = "professional"
) -> List[Dict[str, Any]]:
    """REPLACE YOUR EXISTING METHOD WITH THIS"""
    
    self.logger.info(f"🎯 Generating topic-specific content opportunities for: {topic}")
    
    # Use the enhanced generator
    opportunities = await self.opportunities_generator.generate_topic_specific_opportunities(
        topic=topic,
        trending_topics=trending_topics_data,
        llm_client=llm_client,
        llm_config=llm_config,
        focus_area=focus_area,
        target_audience=target_audience
    )
    
    self.logger.info(f"✅ Generated {len(opportunities)} topic-specific opportunities")
    return opportunities
    '''
    
    return integration_code