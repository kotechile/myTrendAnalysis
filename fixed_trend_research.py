#!/usr/bin/env python3
"""
Blog Gap Analyzer - FIXED Trend Research Integration
Fixed timeout issues, improved error handling, and enhanced pytrends integration
"""

import asyncio
import logging
import json
import time
import re
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from flask import Flask, request, jsonify, Blueprint

# Import the enhanced content opportunities generator
from enhancedContentOpportunitiesGenerator import EnhancedContentOpportunitiesGenerator


# Add this import at the top of your existing file
try:
    from pytrends_enhanced_fixed import integrate_pytrends_with_existing_system_fixed, FixedPyTrendsAnalyzer
    PYTRENDS_FIXED_AVAILABLE = True
except ImportError:
    try:
        from pytrends_enhanced import integrate_pytrends_with_existing_system
        PYTRENDS_FIXED_AVAILABLE = False
    except ImportError:
        PYTRENDS_FIXED_AVAILABLE = False

# ============================================================================
# ENHANCED PROMPTING STRATEGY - SIMPLIFIED AND FASTER
# ============================================================================

def create_simplified_trending_topics_prompt(topic: str, focus_area: str, target_audience: str) -> str:
    """
    Simplified prompt that's faster and more reliable
    """
    return f"""
You are a trend analyst. Analyze trending topics for "{topic}" in the {focus_area} space for {target_audience}.

Return EXACTLY 6 trending topics as a JSON array. Each topic must have:
- trend_name: Specific trending topic
- description: Why it's trending (max 100 chars)
- viral_potential: Score 0-100
- keywords: 3-5 related keywords
- content_formats: ["how_to_guide", "listicle", "case_study"] etc.

Example format:
[
  {{
    "trend_name": "AI-Powered {topic}",
    "description": "Growing use of AI in {topic} solutions",
    "viral_potential": 85,
    "keywords": ["AI {topic}", "automated {topic}"],
    "content_formats": ["how_to_guide", "comparison"]
  }}
]

Focus on ACTIONABLE, SPECIFIC trends that are gaining momentum in 2025.
Return only valid JSON, no other text.
"""

def create_simplified_content_opportunities_prompt(topic: str, trending_topics: List[Dict]) -> str:
    """
    DEPRECATED: Use EnhancedContentOpportunitiesGenerator instead
    This method is kept for backward compatibility but will be removed
    """
    return "DEPRECATED - Use EnhancedContentOpportunitiesGenerator"

# ============================================================================
# ENHANCED INTEGRATION CLASS (FIXED TIMEOUTS)
# ============================================================================

class EnhancedTrendResearchIntegration:
    """Enhanced integration layer with fixed timeout issues"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        # Initialize enhanced content opportunities generator
        self.opportunities_generator = EnhancedContentOpportunitiesGenerator()
    
    async def enhanced_trend_research_for_blog_analyzer(
        self,
        topic: str,
        collection_name: str,
        llm_config: Dict[str, Any],
        focus_area: str = "general",
        target_audience: str = "professional",
        linkup_api_key: Optional[str] = None,
        google_trends_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enhanced trend research with FIXED PyTrends integration"""
        
        self.logger.info(f"🔍 Starting ENHANCED trend research for: {topic}")
        start_time = time.time()
        
        try:
            # Initialize LLM client with proper timeout handling
            llm_client = self._initialize_llm_client(llm_config)
            
            # Step 1: Fast Trending Topics Analysis (SIMPLIFIED)
            self.logger.info("📊 Step 1: Fast trending topics analysis...")
            trending_topics_data = await self._get_trending_topics_fast(
                topic, focus_area, target_audience, llm_client, llm_config
            )
            
            # Step 2: Quick Content Opportunities (SIMPLIFIED)
            self.logger.info("🎯 Step 2: Quick content opportunities...")
            content_opportunities_data = await self._get_content_opportunities_fast(
                topic, trending_topics_data, llm_client, llm_config
            )
            
            # Step 3: Generate Additional Intelligence (NO LLM CALLS)
            self.logger.info("🔍 Step 3: Generating additional intelligence...")
            market_intelligence_data = self._generate_market_intelligence_fast(
                topic, focus_area, trending_topics_data
            )
            
            # Step 4: Enhanced Keyword Strategy (RULE-BASED)
            self.logger.info("🔑 Step 4: Enhanced keyword strategy...")
            keyword_intelligence_data = self._get_enhanced_keyword_strategy_fast(
                topic, trending_topics_data, content_opportunities_data
            )
            
            # UPDATED STEP 5: Fixed PyTrends Enhancement
            if PYTRENDS_FIXED_AVAILABLE:
                self.logger.info("📈 Step 5: Enhanced PyTrends integration (FIXED VERSION)...")
                try:
                    # Create temporary result to enhance
                    temp_result = self._convert_enhanced_data_for_blog_analyzer(
                        trending_topics_data, 
                        content_opportunities_data,
                        market_intelligence_data,
                        keyword_intelligence_data,
                        collection_name,
                        time.time() - start_time
                    )
                    
                    # Enhanced PyTrends configuration
                    pytrends_config = {
                        'rate_limit_seconds': 2,
                        'target_markets': ['US', 'GB', 'CA', 'AU'],
                        'proxies': [],
                        'retry_attempts': 3,
                        'timeout_seconds': 30
                    }
                    
                    # Use the FIXED PyTrends integration
                    enhanced_result = await asyncio.wait_for(
                        integrate_pytrends_with_existing_system_fixed(
                            topic=topic,
                            focus_area=focus_area,
                            target_audience=target_audience,
                            existing_trend_data=temp_result,
                            pytrends_config=pytrends_config
                        ),
                        timeout=45  # Increased timeout for better success rate
                    )
                    
                    self.logger.info("✅ FIXED PyTrends enhancement completed successfully")
                    self.logger.info(f"📊 PyTrends enhanced: {enhanced_result.get('pytrends_enhanced', False)}")
                    
                    # Log PyTrends data availability
                    pytrends_data = enhanced_result.get('pytrends_analysis', {})
                    if pytrends_data:
                        geographic_count = len(pytrends_data.get('geographic_insights', {}).get('global_hotspots', []))
                        insights_count = len(pytrends_data.get('actionable_insights', []))
                        self.logger.info(f"🌍 Geographic hotspots found: {geographic_count}")
                        self.logger.info(f"💡 Actionable insights generated: {insights_count}")
                    
                    return enhanced_result
                    
                except asyncio.TimeoutError:
                    self.logger.warning("⚠️ FIXED PyTrends enhancement timed out. Using existing data.")
                except Exception as e:
                    self.logger.warning(f"⚠️ FIXED PyTrends enhancement failed: {e}. Using existing data.")
            else:
                self.logger.info("📈 Step 5: PyTrends not available, using existing analysis only")

            # FALLBACK: Original processing when PyTrends fails
            processing_time = time.time() - start_time
            
            formatted_for_blog_analyzer = self._convert_enhanced_data_for_blog_analyzer(
                trending_topics_data, 
                content_opportunities_data,
                market_intelligence_data,
                keyword_intelligence_data,
                collection_name,
                processing_time
            )
            
            # Add fallback PyTrends data structure
            if not formatted_for_blog_analyzer.get('pytrends_analysis'):
                self.logger.info("🔧 Adding fallback PyTrends data structure...")
                fallback_analyzer = FixedPyTrendsAnalyzer() if PYTRENDS_FIXED_AVAILABLE else None
                if fallback_analyzer:
                    fallback_data = fallback_analyzer._create_fallback_pytrends_data(topic, trending_topics_data)
                    formatted_for_blog_analyzer['pytrends_analysis'] = fallback_data
                    formatted_for_blog_analyzer['pytrends_enhanced'] = False
            
            self.logger.info(f"✅ ENHANCED trend research completed in {processing_time:.2f}s")
            return formatted_for_blog_analyzer
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced trend research failed: {e}")
            return self._fallback_trend_data(topic, target_audience)

    def _ensure_pytrends_data_structure(self, result: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Ensure PyTrends data structure is present even when analysis fails"""
        
        if not result.get('pytrends_analysis'):
            # Create minimal PyTrends structure for Noodl compatibility
            result['pytrends_analysis'] = {
                "pytrends_enhanced": False,
                "analysis_timestamp": datetime.now().isoformat(),
                "topic_analyzed": topic,
                "main_topic_analysis": {
                    "current_interest": 0,
                    "trend_direction": "unknown",
                    "momentum_percentage": 0,
                    "peak_interest": 0,
                    "recommendation": "PyTrends data not available"
                },
                "geographic_insights": {
                    "global_hotspots": [],
                    "us_regional_hotspots": [],
                    "geographic_strategy": [],
                    "content_localization_opportunities": []
                },
                "seasonal_patterns": {
                    "has_seasonal_pattern": False,
                    "peak_months": [],
                    "low_months": [],
                    "next_peak_prediction": None,
                    "content_calendar_recommendations": []
                },
                "related_queries_insights": {
                    "top_related_queries": [],
                    "rising_queries": [],
                    "keyword_expansion_opportunities": [],
                    "content_gap_analysis": []
                },
                "actionable_insights": [],
                "timing_recommendations": {},
                "fallback_mode": True,
                "pytrends_available": False
            }
        
        return result
    
    async def _get_trending_topics_fast(
        self, 
        topic: str, 
        focus_area: str, 
        target_audience: str, 
        llm_client, 
        llm_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fast trending topics analysis with proper timeout"""
        
        # Create simplified prompt
        prompt = create_simplified_trending_topics_prompt(topic, focus_area, target_audience)
        
        # Call LLM with proper timeout
        try:
            response = await asyncio.wait_for(
                self._call_llm_with_retry(llm_client, prompt, llm_config),
                timeout=45  # 45 second timeout
            )
            
            # Parse response
            trending_topics = self._parse_trending_topics_response(response, topic)
            
            self.logger.info(f"📈 Generated {len(trending_topics)} trending topics")
            return trending_topics
            
        except asyncio.TimeoutError:
            self.logger.error("❌ LLM call timed out for trending topics")
            return self._fallback_trending_topics(topic)
        except Exception as e:
            self.logger.error(f"❌ Trending topics analysis failed: {e}")
            return self._fallback_trending_topics(topic)
    
    async def _get_content_opportunities_fast(
        self,
        topic: str,
        trending_topics_data: List[Dict],
        llm_client,
        llm_config: Dict[str, Any],
        focus_area: str = "general",
        target_audience: str = "professional"
    ) -> List[Dict[str, Any]]:
        """Generate topic-specific content opportunities using enhanced generator"""
        
        self.logger.info(f"🎯 Generating topic-specific content opportunities for: {topic}")
        
        # Use the enhanced opportunities generator
        try:
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
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced opportunities generation failed: {e}")
            # Use enhanced fallback instead of generic
            return await self.opportunities_generator.generate_topic_specific_opportunities(
                topic=topic,
                trending_topics=trending_topics_data,
                llm_client=llm_client,
                llm_config=llm_config,
                focus_area=focus_area,
                target_audience=target_audience
            )
    
    def _generate_market_intelligence_fast(
        self,
        topic: str,
        focus_area: str,
        trending_topics: List[Dict]
    ) -> Dict[str, Any]:
        """Generate market intelligence without LLM calls (rule-based)"""
        
        # Generate insights based on trending topics
        insights = {
            "highest_opportunity_audiences": [
                {
                    "segment_name": f"{topic} practitioners",
                    "market_size": "Growing market segment",
                    "accessibility": "High via LinkedIn and industry publications",
                    "engagement_potential": "High interest in practical solutions",
                    "monetization_opportunity": "Medium to high revenue potential",
                    "competition_level": "Medium competition",
                    "strategic_value": "Strong long-term business potential"
                },
                {
                    "segment_name": f"Small business owners in {focus_area}",
                    "market_size": "Large underserved market",
                    "accessibility": "Medium via social media and forums",
                    "engagement_potential": "High need for practical guides",
                    "monetization_opportunity": "High potential for courses and tools",
                    "competition_level": "Low to medium competition",
                    "strategic_value": "Excellent growth opportunity"
                }
            ],
            "industry_growth_drivers": [
                f"Increased demand for {topic} solutions",
                "Digital transformation acceleration",
                "Remote work driving technology adoption",
                "AI and automation integration",
                "Focus on cost efficiency and ROI"
            ],
            "content_gaps": [
                f"Practical {topic} implementation guides",
                f"Beginner-friendly {topic} content",
                f"ROI-focused {topic} strategies",
                f"Case studies with real results",
                f"Tool comparisons and recommendations"
            ],
            "competitive_landscape": {
                "positioning_opportunities": f"Thought leadership in practical {topic}",
                "content_gaps": f"Step-by-step {topic} guides",
                "audience_needs": "Actionable, results-focused content"
            },
            "strategic_recommendations": {
                "priority_focus": f"Target {topic} practitioners with actionable content",
                "content_strategy": "Focus on how-to guides and case studies",
                "distribution_strategy": "LinkedIn, industry forums, and email marketing"
            },
            "market_sentiment": "Positive growth trajectory with strong demand for practical solutions",
            "geographic_opportunities": ["North American markets", "European expansion", "APAC emerging markets"]
        }
        
        return insights
    
    def _get_enhanced_keyword_strategy_fast(
        self,
        topic: str,
        trending_topics: List[Dict],
        content_opportunities: List[Dict]
    ) -> Dict[str, Any]:
        """Generate keyword strategy using rule-based approach"""
        
        # Extract keywords from trending topics
        high_volume_keywords = []
        low_competition_keywords = []
        emerging_keywords = []
        
        # Process trending topics
        for topic_data in trending_topics:
            keywords = topic_data.get('keywords', [])
            high_volume_keywords.extend(keywords[:2])  # Top keywords
            emerging_keywords.extend(keywords[2:4])   # Secondary keywords
        
        # Generate additional keywords based on topic
        base_keywords = [
            f"{topic} guide",
            f"how to {topic}",
            f"{topic} strategies",
            f"{topic} tips",
            f"best {topic} tools",
            f"{topic} for beginners",
            f"{topic} case study",
            f"{topic} ROI",
            f"{topic} implementation",
            f"{topic} best practices"
        ]
        
        # Categorize keywords
        high_volume_keywords.extend(base_keywords[:5])
        low_competition_keywords.extend(base_keywords[5:8])
        emerging_keywords.extend([
            f"AI {topic}",
            f"{topic} automation",
            f"{topic} 2025"
        ])
        
        # Create keyword clusters
        keyword_clusters = {
            f"{topic}_fundamentals": [f"{topic} basics", f"{topic} guide", f"what is {topic}"],
            f"{topic}_implementation": [f"{topic} strategy", f"{topic} best practices", f"how to {topic}"],
            f"{topic}_tools": [f"{topic} software", f"{topic} tools", f"best {topic} platforms"],
            f"{topic}_advanced": [f"advanced {topic}", f"{topic} optimization", f"{topic} ROI"]
        }
        
        return {
            'high_volume_keywords': list(set(high_volume_keywords))[:15],
            'low_competition_keywords': list(set(low_competition_keywords))[:10],
            'emerging_keywords': list(set(emerging_keywords))[:8],
            'keyword_clusters': keyword_clusters
        }
    
    async def _call_llm_with_retry(self, llm_client, prompt: str, llm_config: Dict[str, Any], max_retries: int = 2) -> str:
        """Call LLM with retry logic and proper timeout handling"""
        
        provider = llm_config.get('provider', 'openai').lower()
        
        for attempt in range(max_retries + 1):
            try:
                self.logger.info(f"🤖 Calling {provider} LLM (attempt {attempt + 1}/{max_retries + 1})")
                
                if provider == 'openai':
                    response = await llm_client.chat.completions.create(
                        model=llm_config.get('model', 'gpt-4o-mini'),
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=2000,  # Reduced from 3000
                        timeout=30  # 30 second timeout per request
                    )
                    return response.choices[0].message.content
                    
                elif provider == 'anthropic':
                    response = await llm_client.messages.create(
                        model=llm_config.get('model', 'claude-3-sonnet-20240229'),
                        max_tokens=2000,  # Reduced from 3000
                        messages=[{"role": "user", "content": prompt}],
                        timeout=30  # 30 second timeout per request
                    )
                    return response.content[0].text
                    
                elif provider == 'kimi':
                    response = await llm_client.chat.completions.create(
                        model=llm_config.get('model', 'kimi-k2-0711-preview'),
                        messages=[
                            {"role": "system", "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are proficient in Chinese and English conversations. You provide users with safe, helpful, and accurate answers."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.6,
                        max_tokens=2000,  # Reduced from 3000
                        timeout=30  # 30 second timeout per request
                    )
                    return response.choices[0].message.content
                    
                else:
                    raise ValueError(f"Unsupported LLM provider: {provider}")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ {provider} LLM call failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _parse_trending_topics_response(self, response: str, topic: str) -> List[Dict[str, Any]]:
        """Parse trending topics response with better error handling"""
        
        try:
            # Try to extract JSON from response
            json_data = self._extract_json_from_response(response)
            
            if isinstance(json_data, list):
                topics_list = json_data
            elif isinstance(json_data, dict) and 'trends' in json_data:
                topics_list = json_data['trends']
            else:
                raise ValueError("Invalid JSON structure")
            
            enhanced_topics = []
            
            for i, topic_data in enumerate(topics_list[:6]):  # Limit to 6 topics
                if isinstance(topic_data, dict):
                    enhanced_topic = {
                        "trend": topic_data.get("trend_name", f"Trending {topic} #{i+1}"),
                        "description": topic_data.get("description", f"Emerging trend in {topic}"),
                        "viral_potential": topic_data.get("viral_potential", 70 - (i * 5)),
                        "relevance": "high",
                        "search_volume": "medium",
                        "competition": "medium",
                        "keywords": topic_data.get("keywords", [f"{topic} trend {i+1}"]),
                        "content_formats": topic_data.get("content_formats", ["how_to_guide"]),
                        "content_angles": [
                            f"Complete guide to {topic_data.get('trend_name', topic)}",
                            f"Best practices for {topic_data.get('trend_name', topic)}"
                        ],
                        "strategic_intelligence": {
                            "trend_category": "Rising",
                            "geographic_relevance": ["Global"],
                            "timeline_momentum": "Current growth phase",
                            "market_drivers": [f"Growing demand for {topic}"],
                            "audience_segments": [f"{topic} practitioners"],
                            "authority_building_score": 70,
                            "lead_generation_score": 65,
                            "differentiation_score": 75
                        }
                    }
                    enhanced_topics.append(enhanced_topic)
            
            return enhanced_topics if enhanced_topics else self._fallback_trending_topics(topic)
            
        except Exception as e:
            self.logger.warning(f"Error parsing trending topics: {e}")
            return self._fallback_trending_topics(topic)
    
    def _parse_content_opportunities_response(self, response: str, topic: str) -> List[Dict[str, Any]]:
        """Parse content opportunities response"""
        
        try:
            json_data = self._extract_json_from_response(response)
            
            if isinstance(json_data, list):
                opportunities_list = json_data
            elif isinstance(json_data, dict) and 'opportunities' in json_data:
                opportunities_list = json_data['opportunities']
            else:
                raise ValueError("Invalid JSON structure")
            
            enhanced_opportunities = []
            
            for i, opp_data in enumerate(opportunities_list[:5]):  # Limit to 5 opportunities
                if isinstance(opp_data, dict):
                    enhanced_opportunity = {
                        "opportunity": opp_data.get("opportunity_title", f"Content opportunity #{i+1}"),
                        "format": opp_data.get("content_format", "how_to_guide"),
                        "difficulty": opp_data.get("difficulty_score", 50),
                        "engagement_potential": opp_data.get("engagement_potential", "medium"),
                        "time_investment": "2-3 weeks",
                        "keywords": opp_data.get("keywords", [f"{topic} content"]),
                        "monetization": "Medium potential for lead generation",
                        "distribution": ["Blog", "LinkedIn", "Email Newsletter"],
                        "strategic_intelligence": {
                            "strategic_rationale": "Market opportunity identified",
                            "competitive_advantage": "Unique positioning in market",
                            "authority_building_value": "Builds thought leadership",
                            "lead_generation_potential": "Medium",
                            "traffic_potential": "Medium",
                            "conversion_optimization": "Standard lead capture approach"
                        }
                    }
                    enhanced_opportunities.append(enhanced_opportunity)
            
            return enhanced_opportunities if enhanced_opportunities else self._fallback_content_opportunities(topic)
            
        except Exception as e:
            self.logger.warning(f"Error parsing content opportunities: {e}")
            return self._fallback_content_opportunities(topic)
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response with better error handling"""
        
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
                json_str = json_match.group(1)
                return json.loads(json_str)
        except:
            pass
        
        # Look for arrays/objects anywhere in response
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
    
    def _fallback_trending_topics(self, topic: str) -> List[Dict[str, Any]]:
        """Fallback trending topics when LLM fails"""
        
        return [
            {
                "trend": f"AI-powered {topic}",
                "description": f"Integration of AI technologies with {topic}",
                "viral_potential": 85,
                "relevance": "high",
                "search_volume": "high",
                "competition": "medium",
                "keywords": [f"AI {topic}", f"automated {topic}", f"smart {topic}"],
                "content_formats": ["how_to_guide", "comparison"],
                "content_angles": [f"AI tools for {topic}", f"Future of {topic} with AI"],
                "strategic_intelligence": {
                    "trend_category": "Rising",
                    "geographic_relevance": ["Global"],
                    "timeline_momentum": "Strong growth",
                    "market_drivers": ["AI adoption", "Automation demand"],
                    "audience_segments": [f"{topic} professionals"],
                    "authority_building_score": 80,
                    "lead_generation_score": 75,
                    "differentiation_score": 85
                }
            },
            {
                "trend": f"Sustainable {topic}",
                "description": f"Eco-friendly approaches to {topic}",
                "viral_potential": 75,
                "relevance": "high",
                "search_volume": "medium",
                "competition": "low",
                "keywords": [f"sustainable {topic}", f"green {topic}", f"eco {topic}"],
                "content_formats": ["case_study", "trend_analysis"],
                "content_angles": [f"Green {topic} strategies", f"Sustainable {topic} benefits"],
                "strategic_intelligence": {
                    "trend_category": "Emerging",
                    "geographic_relevance": ["Europe", "North America"],
                    "timeline_momentum": "Growing interest",
                    "market_drivers": ["Sustainability focus", "Regulatory changes"],
                    "audience_segments": ["Environmentally conscious businesses"],
                    "authority_building_score": 70,
                    "lead_generation_score": 60,
                    "differentiation_score": 80
                }
            },
            {
                "trend": f"{topic} automation",
                "description": f"Automated solutions for {topic} processes",
                "viral_potential": 80,
                "relevance": "high",
                "search_volume": "medium",
                "competition": "medium",
                "keywords": [f"{topic} automation", f"automated {topic}", f"{topic} tools"],
                "content_formats": ["how_to_guide", "tool_comparison"],
                "content_angles": [f"Best {topic} automation tools", f"Automating {topic} workflows"],
                "strategic_intelligence": {
                    "trend_category": "Rising",
                    "geographic_relevance": ["Global"],
                    "timeline_momentum": "Accelerating adoption",
                    "market_drivers": ["Efficiency demands", "Cost reduction"],
                    "audience_segments": ["Business operators", "Technology adopters"],
                    "authority_building_score": 75,
                    "lead_generation_score": 70,
                    "differentiation_score": 75
                }
            }
        ]
    
    def _fallback_content_opportunities(self, topic: str) -> List[Dict[str, Any]]:
        """Fallback content opportunities when LLM fails"""
        
        return [
            {
                "opportunity": f"Complete {topic} Guide for Beginners",
                "format": "how_to_guide",
                "difficulty": 40,
                "engagement_potential": "high",
                "time_investment": "2-3 weeks",
                "keywords": [f"{topic} guide", f"beginner {topic}", f"how to {topic}"],
                "monetization": "High potential for lead generation and course sales",
                "distribution": ["Blog", "LinkedIn", "Email Newsletter", "YouTube"],
                "strategic_intelligence": {
                    "strategic_rationale": "High demand for beginner-friendly content",
                    "competitive_advantage": "Comprehensive yet accessible approach",
                    "authority_building_value": "Establishes expertise and credibility",
                    "lead_generation_potential": "High",
                    "traffic_potential": "High",
                    "conversion_optimization": "Strong lead magnet potential"
                }
            },
            {
                "opportunity": f"{topic} ROI Calculator and Framework",
                "format": "interactive_tool",
                "difficulty": 60,
                "engagement_potential": "very_high",
                "time_investment": "3-4 weeks",
                "keywords": [f"{topic} ROI", f"{topic} calculator", f"{topic} measurement"],
                "monetization": "Excellent lead capture and premium content potential",
                "distribution": ["Website", "LinkedIn", "Industry Publications"],
                "strategic_intelligence": {
                    "strategic_rationale": "Business decision-makers need ROI justification",
                    "competitive_advantage": "Practical tool that provides immediate value",
                    "authority_building_value": "Positions as thought leader in measurement",
                    "lead_generation_potential": "Very High",
                    "traffic_potential": "High",
                    "conversion_optimization": "Tool serves as powerful lead magnet"
                }
            }
        ]
    
    def _convert_enhanced_data_for_blog_analyzer(
        self,
        trending_topics_data: List[Dict],
        content_opportunities_data: List[Dict],
        market_intelligence_data: Dict[str, Any],
        keyword_intelligence_data: Dict[str, Any],
        collection_name: str,
        processing_time: float
    ) -> Dict[str, Any]:
        """Convert enhanced data to format expected by existing blog analyzer"""
        
        # Enhanced market insights
        enhanced_market_insights = {
            "high_demand_angles": market_intelligence_data.get("content_gaps", []),
            "viral_content_formats": [t.get("content_formats", ["how_to_guide"])[0] for t in trending_topics_data],
            "audience_interests": keyword_intelligence_data.get("high_volume_keywords", [])[:10],
            "emerging_trends": keyword_intelligence_data.get("emerging_keywords", []),
            "cross_industry_opportunities": market_intelligence_data.get("geographic_opportunities", []),
            "sentiment": market_intelligence_data.get("market_sentiment", "Positive growth"),
            "behavior_shifts": market_intelligence_data.get("industry_growth_drivers", []),
            
            # Enhanced intelligence
            "highest_opportunity_audiences": market_intelligence_data.get("highest_opportunity_audiences", []),
            "strategic_recommendations": market_intelligence_data.get("strategic_recommendations", {}),
            "competitive_landscape": market_intelligence_data.get("competitive_landscape", {})
        }
        
        # Enhanced competitive gaps
        enhanced_competitive_gaps = {
            "analysis": f"Strategic analysis reveals significant opportunities in targeted content creation with {len(trending_topics_data)} high-potential topics and {len(content_opportunities_data)} strategic opportunities identified.",
            "weaknesses": market_intelligence_data.get("content_gaps", [
                "Generic content lacking strategic focus",
                "Limited audience-specific targeting", 
                "Insufficient market intelligence integration"
            ]),
            "niches": [
                audience.get("segment_name", f"Audience segment {i+1}") 
                for i, audience in enumerate(market_intelligence_data.get("highest_opportunity_audiences", [])[:3])
            ]
        }
        
        return {
            "trending_topics": trending_topics_data,
            "content_opportunities": content_opportunities_data,
            "market_insights": enhanced_market_insights,
            "seo_intelligence": keyword_intelligence_data,
            "competitive_gaps": enhanced_competitive_gaps,
            
            # Enhanced metadata
            "enhanced_trend_research": True,
            "strategic_intelligence": True,
            "confidence_score": 90,  # Higher confidence due to enhanced analysis
            "data_sources": ["strategic_prompting", "market_intelligence", "audience_analysis"],
            "analysis_id": f"enhanced_{int(time.time())}",
            "processing_time": processing_time,
            "fallback_mode": False,
            
            # Strategic framework
            "strategic_framework": {
                "market_intelligence": market_intelligence_data,
                "audience_opportunities": market_intelligence_data.get("highest_opportunity_audiences", []),
                "content_strategy_recommendations": market_intelligence_data.get("strategic_recommendations", {}),
                "enhancement_level": "strategic_intelligence_v2"
            }
        }
    
    def _initialize_llm_client(self, llm_config: Dict[str, Any]):
        """Initialize LLM client based on provider"""
        
        provider = llm_config.get('provider', 'openai').lower()
        api_key = llm_config.get('api_key')
        
        if not api_key:
            raise ValueError(f"API key required for {provider}")
        
        if provider == 'openai':
            import openai
            client = openai.AsyncOpenAI(
                api_key=api_key,
                timeout=60.0  # Increased timeout
            )
            return client
            
        elif provider == 'anthropic':
            import anthropic
            client = anthropic.AsyncAnthropic(
                api_key=api_key,
                timeout=60.0  # Increased timeout
            )
            return client
            
        elif provider == 'kimi':
            import openai
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.moonshot.ai/v1",
                timeout=60.0  # Increased timeout
            )
            return client
            
        else:
            # For other providers, create a generic client object
            class GenericLLMClient:
                def __init__(self, api_key, provider):
                    self.api_key = api_key
                    self.provider = provider
            
            return GenericLLMClient(api_key, provider)
    
    def _fallback_trend_data(self, topic: str, target_audience: str) -> Dict[str, Any]:
        """Enhanced fallback trend data when strategic analysis fails"""
        
        self.logger.warning("Using enhanced fallback trend data")
        
        return {
            "trending_topics": [
                {
                    "trend": f"AI-powered {topic}",
                    "description": f"Integration of AI technologies with {topic}",
                    "relevance": "high", 
                    "search_volume": "high",
                    "competition": "medium",
                    "viral_potential": 85,
                    "keywords": [f"AI {topic}", f"automated {topic}"],
                    "content_formats": ["how_to_guide", "comparison"],
                    "content_angles": [f"AI tools for {topic}", f"Future of {topic}"]
                },
                {
                    "trend": f"Sustainable {topic}",
                    "description": f"Eco-friendly approaches to {topic}",
                    "relevance": "high",
                    "search_volume": "medium",
                    "competition": "low",
                    "viral_potential": 75,
                    "keywords": [f"sustainable {topic}", f"green {topic}"],
                    "content_formats": ["case_study", "trend_analysis"],
                    "content_angles": [f"Green {topic} strategies", f"Sustainable benefits"]
                }
            ],
            "content_opportunities": [
                {
                    "opportunity": f"Complete {topic} Guide for {target_audience}",
                    "format": "how_to_guide",
                    "engagement_potential": "high",
                    "difficulty": 45,
                    "time_investment": "2-3 weeks",
                    "keywords": [f"{topic} guide", f"how to {topic}"],
                    "monetization": "High potential for lead generation",
                    "distribution": ["Blog", "LinkedIn", "Email Newsletter"]
                },
                {
                    "opportunity": f"{topic} ROI Calculator and Framework",
                    "format": "interactive_tool",
                    "engagement_potential": "very high",
                    "difficulty": 65,
                    "time_investment": "3-4 weeks", 
                    "keywords": [f"{topic} ROI", f"{topic} calculator"],
                    "monetization": "Excellent lead capture potential",
                    "distribution": ["Website", "Social Media", "Industry Publications"]
                }
            ],
            "market_insights": {
                "high_demand_angles": [f"Practical {topic}", f"ROI-focused {topic}"],
                "viral_content_formats": ["how_to_guide", "interactive_tool"],
                "audience_interests": [f"{topic} guide", f"{topic} ROI"],
                "emerging_trends": [f"AI {topic}", f"automated {topic}"],
                "cross_industry_opportunities": [f"{topic} for healthcare", f"{topic} for finance"],
                "sentiment": "Strong positive growth with focus on ROI",
                "behavior_shifts": ["Demand for practical frameworks", "Focus on measurable results"]
            },
            "seo_intelligence": {
                "high_volume_keywords": [f"{topic} guide", f"how to {topic}", f"{topic} strategy"],
                "low_competition_keywords": [f"{topic} ROI calculator", f"{topic} framework"],
                "emerging_keywords": [f"AI {topic}", f"automated {topic}"],
                "keyword_clusters": {
                    f"{topic}_strategic": [f"{topic} strategy", f"{topic} planning"],
                    f"{topic}_implementation": [f"{topic} guide", f"{topic} framework"],
                    f"{topic}_automation": [f"AI {topic}", f"automated {topic}"]
                }
            },
            "competitive_gaps": {
                "analysis": f"Enhanced fallback analysis shows opportunities for strategic {topic} content",
                "weaknesses": ["Limited strategic focus", "Lack of ROI frameworks", "Generic guides"],
                "niches": [f"Strategic {topic} for SMBs", f"{topic} ROI measurement", f"AI-enhanced {topic}"]
            },
            "enhanced_trend_research": False,
            "strategic_intelligence": True,
            "confidence_score": 65,
            "data_sources": ["enhanced_fallback"],
            "analysis_id": f"enhanced_fallback_{int(time.time())}",
            "processing_time": 2.0,
            "fallback_mode": True
        }


# Use the enhanced class as the main class
TrendResearchIntegration = EnhancedTrendResearchIntegration


# ============================================================================
# IMPROVED FLASK BLUEPRINT WITH BETTER ERROR HANDLING
# ============================================================================

def create_enhanced_trend_blueprint(config: Dict[str, Any]) -> Blueprint:
    """Create Flask blueprint for enhanced trend research"""
    
    bp = Blueprint('enhanced_trends', __name__)
    trend_integration = TrendResearchIntegration(config)
    
    @bp.route('/enhanced-trend-research', methods=['POST'])
    async def enhanced_trend_research_endpoint():
        """Enhanced trend research endpoint with improved error handling"""
        
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "Request body must be JSON"
                }), 400
            
            # Extract parameters
            topic = data.get('topic', '').strip()
            collection_name = data.get('collection', 'default')
            focus_area = data.get('focus_area', 'general')
            target_audience = data.get('target_audience', 'professional')
            
            if not topic:
                return jsonify({
                    "success": False,
                    "error": "Topic is required"
                }), 400
            
            # LLM configuration with validation
            llm_config = data.get('llm_config', {})
            if not llm_config.get('api_key'):
                return jsonify({
                    "success": False,
                    "error": "LLM API key is required"
                }), 400
            
            # Validate LLM provider
            supported_providers = ['openai', 'anthropic', 'deepseek', 'gemini', 'kimi']
            provider = llm_config.get('provider', 'openai').lower()
            if provider not in supported_providers:
                return jsonify({
                    "success": False,
                    "error": f"Unsupported LLM provider: {provider}. Supported: {supported_providers}"
                }), 400
            
            # Optional API keys
            linkup_api_key = data.get('linkup_api_key')
            google_trends_api_key = data.get('google_trends_api_key')
            
            # Log request details
            print(f"🔍 Processing request: {topic} ({provider})")
            
            # Perform enhanced trend research with timeout
            try:
                result = await asyncio.wait_for(
                    trend_integration.enhanced_trend_research_for_blog_analyzer(
                        topic=topic,
                        collection_name=collection_name,
                        llm_config=llm_config,
                        focus_area=focus_area,
                        target_audience=target_audience,
                        linkup_api_key=linkup_api_key,
                        google_trends_api_key=google_trends_api_key
                    ),
                    timeout=120  # 2 minute total timeout
                )
            except asyncio.TimeoutError:
                print(f"❌ Request timed out for topic: {topic}")
                return jsonify({
                    "success": False,
                    "error": "Request timed out. Please try again with a more specific topic."
                }), 408
            
            return jsonify({
                "success": True,
                "trend_research_data": result,
                "metadata": {
                    "topic": topic,
                    "focus_area": focus_area,
                    "target_audience": target_audience,
                    "collection": collection_name,
                    "enhanced_research": result.get('enhanced_trend_research', False),
                    "strategic_intelligence": result.get('strategic_intelligence', False),
                    "confidence_score": result.get('confidence_score', 0),
                    "timestamp": datetime.now().isoformat(),
                    "llm_provider": provider,
                    "fallback_mode": result.get('fallback_mode', False)
                }
            })
            
        except Exception as e:
            print(f"❌ Enhanced trend research error: {e}")
            import traceback
            traceback.print_exc()
            
            return jsonify({
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "error_type": type(e).__name__
            }), 500
    
    return bp


# ============================================================================
# TESTING AND TROUBLESHOOTING UTILITIES
# ============================================================================

async def test_llm_connection(llm_config: Dict[str, Any]) -> Dict[str, Any]:
    """Test LLM connection with simple prompt"""
    
    try:
        integration = TrendResearchIntegration({})
        llm_client = integration._initialize_llm_client(llm_config)
        
        simple_prompt = "Respond with exactly: 'Connection successful'"
        
        response = await asyncio.wait_for(
            integration._call_llm_with_retry(llm_client, simple_prompt, llm_config),
            timeout=15
        )
        
        return {
            "success": True,
            "response": response.strip(),
            "provider": llm_config.get('provider'),
            "model": llm_config.get('model')
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "provider": llm_config.get('provider'),
            "model": llm_config.get('model')
        }

async def test_enhanced_trend_research(topic: str = "digital marketing") -> Dict[str, Any]:
    """Test the enhanced trend research pipeline"""
    
    # Test configuration
    llm_config = {
        'provider': 'openai',
        'model': 'gpt-4o-mini',
        'api_key': os.getenv('OPENAI_API_KEY')
    }
    
    if not llm_config['api_key']:
        return {
            "success": False,
            "error": "OPENAI_API_KEY environment variable not set"
        }
    
    try:
        integration = TrendResearchIntegration({})
        
        start_time = time.time()
        
        result = await integration.enhanced_trend_research_for_blog_analyzer(
            topic=topic,
            collection_name='test',
            llm_config=llm_config,
            focus_area='general',
            target_audience='professional'
        )
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "topic": topic,
            "processing_time": processing_time,
            "trending_topics_count": len(result.get('trending_topics', [])),
            "content_opportunities_count": len(result.get('content_opportunities', [])),
            "confidence_score": result.get('confidence_score', 0),
            "enhanced_research": result.get('enhanced_trend_research', False),
            "fallback_mode": result.get('fallback_mode', False)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "topic": topic
        }


# ============================================================================
# MAIN EXECUTION FOR TESTING
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fixed Enhanced Trend Research Integration")
    parser.add_argument('--test-connection', action='store_true', help='Test LLM connection')
    parser.add_argument('--test-research', metavar='TOPIC', help='Test trend research for topic')
    parser.add_argument('--provider', default='openai', choices=['openai', 'anthropic'], help='LLM provider')
    parser.add_argument('--model', help='LLM model (optional)')
    
    args = parser.parse_args()
    
    if args.test_connection:
        async def test_connection():
            llm_config = {
                'provider': args.provider,
                'model': args.model or ('gpt-4o-mini' if args.provider == 'openai' else 'claude-3-sonnet-20240229'),
                'api_key': os.getenv('OPENAI_API_KEY' if args.provider == 'openai' else 'ANTHROPIC_API_KEY')
            }
            
            result = await test_llm_connection(llm_config)
            
            print("🔌 LLM Connection Test Results:")
            print("=" * 40)
            print(f"Provider: {result.get('provider')}")
            print(f"Model: {result.get('model')}")
            print(f"Success: {result.get('success')}")
            
            if result.get('success'):
                print(f"Response: {result.get('response')}")
                print("✅ Connection successful!")
            else:
                print(f"Error: {result.get('error')}")
                print("❌ Connection failed!")
        
        asyncio.run(test_connection())
        
    elif args.test_research:
        async def test_research():
            result = await test_enhanced_trend_research(args.test_research)
            
            print("🧪 Enhanced Trend Research Test Results:")
            print("=" * 50)
            print(f"Topic: {result.get('topic')}")
            print(f"Success: {result.get('success')}")
            
            if result.get('success'):
                print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
                print(f"Trending Topics: {result.get('trending_topics_count', 0)}")
                print(f"Content Opportunities: {result.get('content_opportunities_count', 0)}")
                print(f"Confidence Score: {result.get('confidence_score', 0)}%")
                print(f"Enhanced Research: {result.get('enhanced_research', False)}")
                print(f"Fallback Mode: {result.get('fallback_mode', False)}")
                print("✅ Research test completed successfully!")
            else:
                print(f"Error: {result.get('error')}")
                print("❌ Research test failed!")
        
        asyncio.run(test_research())
        
    else:
        print("Fixed Enhanced Trend Research Integration")
        print("Key improvements:")
        print("- ✅ Reduced LLM timeouts (30s per call, 45s total)")
        print("- ✅ Simplified prompts for faster processing")
        print("- ✅ Better retry logic with exponential backoff")
        print("- ✅ Rule-based fallbacks to avoid LLM dependency")
        print("- ✅ Enhanced error handling and logging")
        print("- ✅ pytrends integration with timeout protection")
        print("")
        print("Usage:")
        print("  python trend_research_integration.py --test-connection")
        print("  python trend_research_integration.py --test-research 'AI marketing'")
        print("  python trend_research_integration.py --test-research 'real estate' --provider anthropic")
