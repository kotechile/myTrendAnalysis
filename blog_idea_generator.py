#!/usr/bin/env python3
"""
Core Blog Idea Generation Engine - Phase 2
Transforms Phase 1 market intelligence into actionable blog post ideas
"""

import asyncio
import logging
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
import uuid
import aiohttp
from collections import Counter

try:
    from linkup import LinkupClient
    LINKUP_AVAILABLE = True
except ImportError:
    try:
        # Try alternative import for linkup-sdk package
        from linkup import LinkupClient
        LINKUP_AVAILABLE = True
    except ImportError:
        LINKUP_AVAILABLE = False


# Add these imports at the top of your blog_idea_generator.py file:

# Import Phase 1 components
from working_supabase_integration import RLSSupabaseStorage

#!/usr/bin/env python3
"""
FIXED: Blog Idea Generation Engine - Phase 2
Fixed missing scoring calculation before saving to Supabase
"""



# Import Phase 1 components
from working_supabase_integration import RLSSupabaseStorage

#!/usr/bin/env python3
"""
LinkupResearcher Class - Add this to blog_idea_generator.py
Enhanced content research using Linkup API for blog idea generation
"""


# ============================================================================
# STEP 1: Update the method signature in blog_idea_generator.py
# ============================================================================

# Find this method in your BlogIdeaGenerationEngine class and update it:

async def generate_comprehensive_blog_ideas(
    self,
    analysis_id: str,
    user_id: str,
    llm_config: Dict[str, Any],
    generation_config: Dict[str, Any] = None,
    linkup_api_key: Optional[str] = None  # ADD THIS PARAMETER
) -> Dict[str, Any]:
    """
    ENHANCED: Main method to generate comprehensive blog ideas with optional Linkup research
    """
    
    self.logger.info(f"🚀 Starting blog idea generation for analysis: {analysis_id}")
    if linkup_api_key:
        self.logger.info("📡 Linkup research enabled")
    
    start_time = time.time()
    
    try:
        # Step 1: Load Phase 1 strategic context (existing)
        self.logger.info("📊 Loading Phase 1 strategic context...")
        context = await self._load_phase1_strategic_context(analysis_id, user_id)
        
        # Step 2: ENHANCED - Optional Linkup Research
        if linkup_api_key:
            self.logger.info("🔍 Conducting Linkup research...")
            context = await self._enhance_context_with_linkup_research(
                context, linkup_api_key, llm_config
            )
        
        # Step 3: Initialize LLM client (existing)
        llm_client = self._initialize_llm_client(llm_config)
        
        # Step 4: Generate ideas from trending topics (existing code)
        self.logger.info("💡 Generating ideas from trending topics...")
        trending_ideas = await self._generate_from_trending_topics(context, llm_client, llm_config)
        
        # Step 5: Generate ideas from content opportunities (existing code)
        self.logger.info("🎯 Generating ideas from content opportunities...")
        opportunity_ideas = await self._generate_from_opportunities(context, llm_client, llm_config)
        
        # Step 6: Generate ideas from PyTrends insights (existing code)
        self.logger.info("📈 Generating ideas from PyTrends insights...")
        pytrends_ideas = await self._generate_from_pytrends_data(context, llm_client, llm_config)
        
        # Step 7: Generate ideas from keyword clusters (existing code)
        self.logger.info("🔑 Generating ideas from keyword clusters...")
        keyword_ideas = await self._generate_from_keyword_clusters(context, llm_client, llm_config)
        
        # Step 8: Combine and deduplicate ideas (existing code)
        all_ideas = trending_ideas + opportunity_ideas + pytrends_ideas + keyword_ideas
        unique_ideas = self._deduplicate_ideas(all_ideas)

        # Step 9: Calculate all scores before optimization (existing code)
        self.logger.info("🔢 Calculating idea scores...")
        scored_ideas = self._calculate_all_idea_scores(unique_ideas, context)

        # Step 10: Optimize ideas for SEO and engagement (existing code)
        self.logger.info("⚡ Optimizing ideas for SEO and engagement...")
        optimized_ideas = await self._optimize_ideas_for_seo_and_engagement(scored_ideas, context)
        
        # Step 11: Final scoring and ranking (existing code)
        self.logger.info("📊 Final scoring and ranking...")
        final_scored_ideas = self._score_and_rank_ideas(optimized_ideas)
        
        # Step 12: Select top ideas based on target range (existing code)
        final_ideas = self._select_optimal_idea_set(final_scored_ideas, generation_config)
        
        # Step 13: Generate content calendar recommendations (existing code)
        self.logger.info("📅 Generating content calendar...")
        content_calendar = self._generate_content_calendar(final_ideas, context)
        
        # Step 14: Calculate success metrics and insights (existing code)
        strategic_insights = self._generate_strategic_insights(final_ideas, context)
        success_predictions = self._calculate_success_predictions(final_ideas, context)
        
        processing_time = time.time() - start_time
        
        result = {
            "blog_ideas": final_ideas,
            "content_calendar": content_calendar,
            "strategic_insights": strategic_insights,
            "success_predictions": success_predictions,
            "generation_metadata": {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "total_ideas_generated": len(final_ideas),
                "average_quality_score": sum(idea["overall_quality_score"] for idea in final_ideas) / len(final_ideas),
                "processing_time_seconds": round(processing_time, 2),
                "generation_timestamp": datetime.now().isoformat(),
                "llm_provider": llm_config.get("provider"),
                "phase1_context_loaded": bool(context),
                "ideas_by_source": {
                    "trending_topics": len(trending_ideas),
                    "content_opportunities": len(opportunity_ideas), 
                    "pytrends_insights": len(pytrends_ideas),
                    "keyword_clusters": len(keyword_ideas)
                }
            }
        }
        
        # NEW: Add Linkup research results if available
        if linkup_api_key and context.get('linkup_research'):
            result['linkup_insights'] = context['linkup_research']
            result['generation_metadata']['linkup_research_conducted'] = True
            result['generation_metadata']['linkup_searches_analyzed'] = context['linkup_research'].get('search_results_analyzed', 0)
        else:
            result['generation_metadata']['linkup_research_conducted'] = False
        
        self.logger.info(f"✅ Blog idea generation completed: {len(final_ideas)} ideas in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        self.logger.error(f"❌ Blog idea generation failed: {e}")
        raise


# ============================================================================
# STEP 2: Add the Linkup enhancement method to BlogIdeaGenerationEngine class
# ============================================================================

async def _enhance_context_with_linkup_research(
    self,
    context: Dict[str, Any], 
    linkup_api_key: str,
    llm_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Enhance context with Linkup research"""
    
    try:
        # Import the LinkupResearcher class (make sure it's in the same file)
        # If you haven't added it yet, you need to add the entire LinkupResearcher class to blog_idea_generator.py
        
        # Initialize Linkup researcher with configuration
        linkup_config = {
            'max_searches': 8,
            'results_per_search': 10,
            'search_timeout': 30,
            'rate_limit_delay': 1.5
        }
        
        linkup_researcher = LinkupResearcher(linkup_api_key, linkup_config)
        
        # Get selected data for research
        selected_topics = context.get('selected_trending_topics', [])
        selected_opportunities = context.get('selected_opportunities', [])
        
        if not selected_topics and not selected_opportunities:
            self.logger.warning("⚠️ No selected topics/opportunities for Linkup research")
            return context
        
        # Conduct research with timeout
        self.logger.info(f"🔍 Starting Linkup research: {len(selected_topics)} topics, {len(selected_opportunities)} opportunities")
        
        linkup_research = await asyncio.wait_for(
            linkup_researcher.research_content_gaps(selected_topics, selected_opportunities),
            timeout=90  # 1.5 minute timeout for all Linkup research
        )
        
        # Enhance context with research
        context['linkup_research'] = linkup_research
        context['research_enhanced'] = True
        
        # Log research results
        gaps_found = linkup_research.get('total_gaps_identified', 0)
        searches_conducted = linkup_research.get('search_results_analyzed', 0)
        confidence_score = linkup_research.get('research_confidence_score', 0)
        
        self.logger.info(f"✅ Linkup research completed:")
        self.logger.info(f"   📊 {searches_conducted} searches analyzed")
        self.logger.info(f"   🔍 {gaps_found} content gaps identified")
        self.logger.info(f"   🎯 {confidence_score}% research confidence")
        
        return context
        
    except asyncio.TimeoutError:
        self.logger.warning("⚠️ Linkup research timed out, continuing without enhancement")
        return context
    except Exception as e:
        self.logger.warning(f"⚠️ Linkup research failed: {e}, continuing without enhancement")
        return context


# ============================================================================
# STEP 3: Add imports at the top of blog_idea_generator.py
# ============================================================================


#!/usr/bin/env python3
"""
FIXED: Linkup Integration using Official Linkup Client
This replaces the manual HTTP approach with the official Linkup Python SDK
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from linkup import LinkupClient
    LINKUP_AVAILABLE = True
except ImportError:
    LINKUP_AVAILABLE = False

class LinkupResearcher:
    """
    Fixed Linkup researcher using the official Linkup client
    """
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        self.api_key = api_key
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration with sensible defaults
        self.max_searches = self.config.get('max_searches', 8)
        self.rate_limit_delay = self.config.get('rate_limit_delay', 2.0)
        
        # Initialize Linkup client
        if LINKUP_AVAILABLE:
            try:
                self.client = LinkupClient(api_key=self.api_key)
                self.logger.info("✅ Linkup client initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Linkup client: {e}")
                self.client = None
        else:
            self.client = None
            self.logger.warning("⚠️ Linkup client not available. Install with: pip install linkup")
        
        self.logger.info(f"🔍 LinkupResearcher initialized with max {self.max_searches} searches")
    
    async def research_content_gaps(
        self, 
        selected_topics: List[Dict[str, Any]], 
        selected_opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Main research method using official Linkup client
        """
        
        self.logger.info(f"🔍 Starting Linkup research: {len(selected_topics)} topics, {len(selected_opportunities)} opportunities")
        
        if not LINKUP_AVAILABLE or not self.client:
            self.logger.warning("⚠️ Linkup client not available, using fallback insights")
            return self._create_fallback_research_result(selected_topics, selected_opportunities)
        
        try:
            # Step 1: Generate strategic search queries with proper prompts
            research_queries = self._generate_strategic_research_queries(selected_topics, selected_opportunities)
            
            if not research_queries:
                self.logger.warning("⚠️ No research queries generated")
                return self._create_fallback_research_result(selected_topics, selected_opportunities)
            
            # Step 2: Execute searches using official client
            search_results = await self._execute_linkup_searches(research_queries)
            
            # Step 3: Analyze results comprehensively
            analysis = self._analyze_search_results_comprehensive(search_results)
            
            # Step 4: Generate actionable insights
            insights = self._generate_research_insights(analysis, selected_topics, selected_opportunities)
            
            self.logger.info(f"✅ Linkup research completed: {len(search_results)} searches, {insights['total_gaps_identified']} gaps found")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"❌ Linkup research failed: {e}")
            return self._create_fallback_research_result(selected_topics, selected_opportunities)
    
    def _generate_strategic_research_queries(
        self, 
        selected_topics: List[Dict[str, Any]], 
        selected_opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate strategic research queries following Linkup best practices"""
        
        queries = []
        
        # Generate topic-based queries with proper prompting
        for topic in selected_topics[:3]:  # Limit to prevent API overuse
            topic_title = topic.get('title', topic.get('trend', ''))
            if not topic_title:
                continue
            
            # Extract keywords safely
            keywords = topic.get('keywords', [])
            if isinstance(keywords, str):
                try:
                    keywords = json.loads(keywords)
                except:
                    keywords = [keywords] if keywords else []
            
            # Create strategic queries following Linkup best practices
            queries.extend([
                {
                    'query': self._create_comprehensive_analysis_prompt(topic_title, "content strategy"),
                    'type': 'topic_comprehensive',
                    'source_topic': topic_title,
                    'intent': 'comprehensive_content_analysis'
                },
                {
                    'query': self._create_competitive_gap_prompt(topic_title),
                    'type': 'competitive_analysis',
                    'source_topic': topic_title,
                    'intent': 'identify_content_gaps'
                }
            ])
        
        # Generate opportunity-based queries
        for opp in selected_opportunities[:2]:  # Limit opportunities
            opp_title = opp.get('title', opp.get('opportunity', ''))
            if not opp_title:
                continue
            
            queries.append({
                'query': self._create_market_opportunity_prompt(opp_title),
                'type': 'opportunity_validation',
                'source_opportunity': opp_title,
                'intent': 'validate_market_opportunity'
            })
        
        # Limit total queries
        limited_queries = queries[:self.max_searches]
        
        self.logger.info(f"📝 Generated {len(limited_queries)} strategic research queries")
        
        return limited_queries
    
    def _create_comprehensive_analysis_prompt(self, topic: str, focus_area: str) -> str:
        """Create comprehensive analysis prompt following Linkup best practices"""
        
        return f"""You are an expert content strategist and market researcher. 

🎯 **Goal**: Analyze the current content landscape for "{topic}" to identify content gaps and opportunities.

📍 **Scope**: Search for and analyze:
- Recent blog posts, articles, and guides about {topic}
- Popular content formats and approaches
- Leading websites and publications covering {topic}
- Social media discussions and trending content

🧠 **Criteria**: Focus on identifying:
- Content types that are popular but underserved
- Audience questions that aren't being answered adequately
- Gaps in beginner vs advanced content
- Opportunities for unique angles or approaches
- Content format opportunities (guides, lists, comparisons, etc.)

📦 **Format**: Provide a structured analysis highlighting:
1. Most common content types currently available
2. Identified content gaps or underserved areas
3. Audience needs not being met
4. Opportunities for differentiation"""
    
    def _create_competitive_gap_prompt(self, topic: str) -> str:
        """Create competitive gap analysis prompt"""
        
        return f"""You are a competitive intelligence analyst specializing in content marketing.

🎯 **Goal**: Identify content gaps and weaknesses in how "{topic}" is currently covered online.

📍 **Scope**: Analyze top-ranking content for "{topic}" including:
- Top 10 search results for main "{topic}" keywords
- Popular blog posts and articles
- Leading industry publications
- Educational and how-to content

🧠 **Criteria**: Look for:
- Areas where existing content is shallow or incomplete
- Audience questions left unanswered
- Outdated information or approaches
- Missing content formats (tutorials, case studies, tools)
- Opportunities for more practical or actionable content

📦 **Format**: Return findings as:
1. Common weaknesses in existing content
2. Specific gaps where quality content is missing
3. Audience pain points not being addressed
4. Opportunities for superior content creation"""
    
    def _create_market_opportunity_prompt(self, opportunity: str) -> str:
        """Create market opportunity validation prompt"""
        
        return f"""You are a market research analyst evaluating content opportunities.

🎯 **Goal**: Validate the market opportunity for creating content about "{opportunity}".

📍 **Scope**: Research and analyze:
- Current content covering "{opportunity}"
- Search volume and interest indicators
- Competitor content quality and depth
- Audience engagement with existing content

🧠 **Criteria**: Evaluate:
- Market demand vs content supply
- Quality of existing content
- Audience satisfaction with current resources
- Potential for content differentiation
- Business/commercial potential

📦 **Format**: Provide assessment including:
1. Market demand level (high/medium/low)
2. Current content quality assessment
3. Identified opportunities for improvement
4. Recommended content approach for maximum impact"""
    
    async def _execute_linkup_searches(self, research_queries: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
        """Execute searches using official Linkup client"""
        
        search_results = {}
        successful_searches = 0
        
        for i, query_data in enumerate(research_queries):
            query = query_data['query']
            
            try:
                self.logger.info(f"🔍 Executing Linkup search {i+1}/{len(research_queries)}")
                
                # Use official Linkup client with proper parameters
                response = await asyncio.to_thread(
                    self.client.search,
                    query=query,
                    depth="deep",  # Use deep search for better quality
                    output_type="sourcedAnswer"  # Get sourced answers
                )
                
                # Process the response
                processed_results = self._process_linkup_response(response, query_data)
                
                search_results[query] = {
                    'results': processed_results,
                    'metadata': query_data,
                    'search_timestamp': datetime.now().isoformat(),
                    'results_count': len(processed_results),
                    'search_successful': True,
                    'raw_response': response  # Store raw response for debugging
                }
                
                successful_searches += 1
                self.logger.info(f"✅ Search completed: {len(processed_results)} insights extracted")
                
                # Rate limiting between searches
                if i < len(research_queries) - 1:
                    await asyncio.sleep(self.rate_limit_delay)
                
            except Exception as e:
                self.logger.warning(f"❌ Search failed for query: {e}")
                search_results[query] = {
                    'results': [],
                    'metadata': query_data,
                    'error': str(e),
                    'search_timestamp': datetime.now().isoformat(),
                    'results_count': 0,
                    'search_successful': False
                }
        
        self.logger.info(f"📊 Linkup searches completed: {successful_searches}/{len(research_queries)} successful")
        
        return search_results
    
    def _process_linkup_response(self, response: Any, query_metadata: Dict[str, str]) -> List[Dict[str, Any]]:
        """Process Linkup client response into structured data"""
        
        processed_results = []
        
        try:
            # Handle different response types from Linkup client
            if hasattr(response, 'answer') and hasattr(response, 'sources'):
                # SourcedAnswer response type
                main_insight = {
                    'type': 'main_analysis',
                    'content': response.answer,
                    'sources': [],
                    'confidence': 'high',
                    'query_type': query_metadata.get('type', 'unknown')
                }
                
                # Process sources
                if hasattr(response, 'sources') and response.sources:
                    for source in response.sources[:5]:  # Limit sources
                        if hasattr(source, 'name') and hasattr(source, 'url'):
                            main_insight['sources'].append({
                                'title': getattr(source, 'name', 'Unknown Source'),
                                'url': getattr(source, 'url', ''),
                                'snippet': getattr(source, 'snippet', '')[:200]
                            })
                
                processed_results.append(main_insight)
                
            elif isinstance(response, dict):
                # Dictionary response
                if 'answer' in response:
                    processed_results.append({
                        'type': 'analysis',
                        'content': response['answer'],
                        'sources': response.get('sources', [])[:5],
                        'confidence': 'medium',
                        'query_type': query_metadata.get('type', 'unknown')
                    })
                    
            elif isinstance(response, str):
                # String response
                processed_results.append({
                    'type': 'text_analysis',
                    'content': response,
                    'sources': [],
                    'confidence': 'medium',
                    'query_type': query_metadata.get('type', 'unknown')
                })
            
            # Extract insights from content
            for result in processed_results:
                result['insights'] = self._extract_insights_from_content(result['content'])
            
        except Exception as e:
            self.logger.error(f"Error processing Linkup response: {e}")
            # Return basic fallback result
            processed_results.append({
                'type': 'error',
                'content': f"Error processing response: {str(e)}",
                'sources': [],
                'confidence': 'low',
                'query_type': query_metadata.get('type', 'unknown'),
                'insights': []
            })
        
        return processed_results
    
    def _extract_insights_from_content(self, content: str) -> List[str]:
        """Extract actionable insights from content"""
        
        insights = []
        
        if not content:
            return insights
        
        content_lower = content.lower()
        
        # Look for gap indicators
        gap_indicators = [
            "gap", "missing", "lacking", "insufficient", "limited", 
            "opportunity", "underserved", "not covered", "absent"
        ]
        
        sentences = content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(indicator in sentence.lower() for indicator in gap_indicators):
                insights.append(sentence)
        
        # Look for opportunity indicators
        opportunity_indicators = [
            "opportunity", "potential", "could create", "should focus", 
            "recommend", "suggest", "consider"
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(indicator in sentence.lower() for indicator in opportunity_indicators):
                if sentence not in insights:  # Avoid duplicates
                    insights.append(sentence)
        
        return insights[:5]  # Limit to top 5 insights
    
    def _analyze_search_results_comprehensive(self, search_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive analysis of Linkup search results"""
        
        analysis = {
            'content_gap_analysis': {},
            'competitive_analysis': {},
            'market_opportunities': {},
            'search_summary': {
                'total_searches': len(search_results),
                'successful_searches': len([r for r in search_results.values() if r.get('search_successful', False)]),
                'total_insights_found': 0
            }
        }
        
        all_insights = []
        content_gaps = []
        market_opportunities = []
        
        # Process each search result
        for query, search_data in search_results.items():
            if not search_data.get('search_successful', False):
                continue
            
            results = search_data.get('results', [])
            query_type = search_data.get('metadata', {}).get('type', 'unknown')
            
            for result in results:
                insights = result.get('insights', [])
                all_insights.extend(insights)
                
                # Categorize insights by query type
                if query_type == 'competitive_analysis':
                    content_gaps.extend(insights)
                elif query_type == 'opportunity_validation':
                    market_opportunities.extend(insights)
        
        analysis['search_summary']['total_insights_found'] = len(all_insights)
        
        # Content gap analysis
        analysis['content_gap_analysis'] = {
            'gaps_identified': content_gaps[:10],  # Top 10 gaps
            'total_gaps': len(content_gaps),
            'gap_categories': self._categorize_gaps(content_gaps)
        }
        
        # Market opportunities
        analysis['market_opportunities'] = {
            'opportunities_found': market_opportunities[:8],  # Top 8 opportunities
            'total_opportunities': len(market_opportunities),
            'opportunity_score': min(85, len(market_opportunities) * 10)  # Simple scoring
        }
        
        return analysis
    
    def _categorize_gaps(self, gaps: List[str]) -> Dict[str, int]:
        """Categorize content gaps by type"""
        
        categories = {
            'tutorial_gaps': 0,
            'beginner_content_gaps': 0,
            'advanced_content_gaps': 0,
            'practical_application_gaps': 0,
            'tool_comparison_gaps': 0,
            'case_study_gaps': 0
        }
        
        for gap in gaps:
            gap_lower = gap.lower()
            
            if any(word in gap_lower for word in ['tutorial', 'how-to', 'step-by-step']):
                categories['tutorial_gaps'] += 1
            elif any(word in gap_lower for word in ['beginner', 'basic', 'introduction']):
                categories['beginner_content_gaps'] += 1
            elif any(word in gap_lower for word in ['advanced', 'expert', 'deep']):
                categories['advanced_content_gaps'] += 1
            elif any(word in gap_lower for word in ['practical', 'implementation', 'application']):
                categories['practical_application_gaps'] += 1
            elif any(word in gap_lower for word in ['comparison', 'vs', 'versus', 'tools']):
                categories['tool_comparison_gaps'] += 1
            elif any(word in gap_lower for word in ['case study', 'example', 'real-world']):
                categories['case_study_gaps'] += 1
        
        return categories
    
    def _generate_research_insights(
        self, 
        analysis: Dict[str, Any], 
        selected_topics: List[Dict[str, Any]], 
        selected_opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive research insights"""
        
        content_gaps = analysis.get('content_gap_analysis', {})
        market_opportunities = analysis.get('market_opportunities', {})
        search_summary = analysis.get('search_summary', {})
        
        # Generate content opportunities based on research
        content_opportunities = []
        
        # Add gap-based opportunities
        for gap in content_gaps.get('gaps_identified', [])[:5]:
            content_opportunities.append({
                'title': self._gap_to_content_opportunity(gap),
                'opportunity_type': 'content_gap',
                'description': gap,
                'priority': 'high',
                'opportunity_score': 80,
                'source': 'linkup_research',
                'recommended_format': self._suggest_format_from_gap(gap)
            })
        
        # Add market opportunities
        for opp in market_opportunities.get('opportunities_found', [])[:3]:
            content_opportunities.append({
                'title': self._opportunity_to_content_title(opp),
                'opportunity_type': 'market_opportunity',
                'description': opp,
                'priority': 'medium',
                'opportunity_score': 70,
                'source': 'linkup_market_research',
                'recommended_format': 'how_to_guide'
            })
        
        return {
            'content_gaps_found': content_gaps.get('gaps_identified', []),
            'market_opportunities_identified': market_opportunities.get('opportunities_found', []),
            'content_opportunities': content_opportunities,
            'total_gaps_identified': len(content_opportunities),
            'total_opportunities_found': len(content_opportunities),
            'research_confidence_score': self._calculate_confidence_score(search_summary),
            'search_results_analyzed': search_summary.get('total_insights_found', 0),
            'research_timestamp': datetime.now().isoformat(),
            'linkup_enhanced': True,
            'analysis_depth': 'comprehensive' if search_summary.get('successful_searches', 0) >= 3 else 'basic'
        }
    
    def _gap_to_content_opportunity(self, gap: str) -> str:
        """Convert a content gap into a content opportunity title"""
        
        gap_lower = gap.lower()
        
        if 'tutorial' in gap_lower or 'how-to' in gap_lower:
            return f"Comprehensive Tutorial Series: {gap[:50]}..."
        elif 'beginner' in gap_lower:
            return f"Beginner's Guide: {gap[:50]}..."
        elif 'advanced' in gap_lower:
            return f"Advanced Strategies: {gap[:50]}..."
        elif 'comparison' in gap_lower:
            return f"Ultimate Comparison Guide: {gap[:50]}..."
        else:
            return f"Content Opportunity: {gap[:50]}..."
    
    def _opportunity_to_content_title(self, opportunity: str) -> str:
        """Convert market opportunity into content title"""
        return f"Market Opportunity: {opportunity[:50]}..."
    
    def _suggest_format_from_gap(self, gap: str) -> str:
        """Suggest content format based on gap description"""
        
        gap_lower = gap.lower()
        
        if 'tutorial' in gap_lower or 'how-to' in gap_lower:
            return 'tutorial'
        elif 'comparison' in gap_lower or 'vs' in gap_lower:
            return 'comparison'
        elif 'case study' in gap_lower or 'example' in gap_lower:
            return 'case_study'
        elif 'guide' in gap_lower:
            return 'how_to_guide'
        elif 'list' in gap_lower or 'best' in gap_lower:
            return 'listicle'
        else:
            return 'how_to_guide'
    
    def _calculate_confidence_score(self, search_summary: Dict[str, Any]) -> int:
        """Calculate research confidence score"""
        
        total_searches = search_summary.get('total_searches', 0)
        successful_searches = search_summary.get('successful_searches', 0)
        total_insights = search_summary.get('total_insights_found', 0)
        
        if total_searches == 0:
            return 0
        
        success_rate = successful_searches / total_searches
        insight_factor = min(total_insights / 10, 1.0)  # Cap at 10 insights
        
        confidence = int((success_rate * 0.7 + insight_factor * 0.3) * 100)
        
        return max(25, min(95, confidence))  # Clamp between 25-95
    
    def _create_fallback_research_result(
        self, 
        selected_topics: List[Dict[str, Any]], 
        selected_opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create fallback research result when Linkup is unavailable"""
        
        # Generate strategic insights based on selected topics and opportunities
        content_opportunities = []
        
        # Generate opportunities from topics
        for topic in selected_topics[:3]:
            topic_title = topic.get('title', topic.get('trend', ''))
            viral_potential = topic.get('viral_potential', 50)
            
            content_opportunities.append({
                'title': f"Comprehensive Guide to {topic_title}",
                'opportunity_type': 'topic_analysis',
                'description': f"Create in-depth content about {topic_title} based on trend analysis",
                'priority': 'high' if viral_potential >= 80 else 'medium',
                'opportunity_score': viral_potential,
                'source': 'trend_analysis',
                'recommended_format': 'how_to_guide'
            })
        
        # Generate opportunities from selected opportunities
        for opp in selected_opportunities[:2]:
            opp_title = opp.get('title', opp.get('opportunity', ''))
            difficulty = opp.get('difficulty', 50)
            
            content_opportunities.append({
                'title': f"Market Opportunity: {opp_title}",
                'opportunity_type': 'market_opportunity',
                'description': f"Validated content opportunity: {opp_title}",
                'priority': 'high' if difficulty <= 40 else 'medium',
                'opportunity_score': 100 - difficulty,
                'source': 'opportunity_analysis',
                'recommended_format': opp.get('format', 'how_to_guide')
            })
        
        return {
            'content_gaps_found': [
                "Limited comprehensive guides in the selected topic areas",
                "Opportunity for beginner-friendly content",
                "Gap in practical implementation guides"
            ],
            'market_opportunities_identified': [
                "Strong demand for selected trending topics",
                "Underserved audience needs in content opportunities"
            ],
            'content_opportunities': content_opportunities,
            'total_gaps_identified': len(content_opportunities),
            'total_opportunities_found': len(content_opportunities),
            'research_confidence_score': 65,  # Moderate confidence for fallback
            'search_results_analyzed': 0,
            'research_timestamp': datetime.now().isoformat(),
            'linkup_enhanced': False,
            'analysis_depth': 'fallback',
            'status': 'fallback_analysis',
            'message': 'Linkup unavailable - using trend-based analysis'
        }


# Replace the LinkupResearcher class in your blog_idea_generator.py
# Update the import and class usage:

class BlogIdeaGenerationEngine:
    # ... existing code ...
    
    async def _enhance_context_with_linkup_research(
        self,
        context: Dict[str, Any], 
        linkup_api_key: str,
        llm_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhanced context with Linkup research using official client"""
        
        try:
            # Use the fixed Linkup researcher
            linkup_config = {
                'max_searches': 6,  # Reduced for cost control
                'rate_limit_delay': 2.0
            }
            
            # REPLACE the old LinkupResearcher with the new LinkupResearcher
            linkup_researcher = LinkupResearcher(linkup_api_key, linkup_config)
            
            # Get selected data for research
            selected_topics = context.get('selected_trending_topics', [])
            selected_opportunities = context.get('selected_opportunities', [])
            
            if not selected_topics and not selected_opportunities:
                self.logger.warning("⚠️ No selected topics/opportunities for Linkup research")
                return context
            
            # Conduct research with timeout
            self.logger.info(f"🔍 Starting fixed Linkup research: {len(selected_topics)} topics, {len(selected_opportunities)} opportunities")
            
            linkup_research = await asyncio.wait_for(
                linkup_researcher.research_content_gaps(selected_topics, selected_opportunities),
                timeout=120  # 2 minute timeout
            )
            
            # Enhance context with research
            context['linkup_research'] = linkup_research
            context['research_enhanced'] = True
            
            # Log research results
            gaps_found = linkup_research.get('total_gaps_identified', 0)
            searches_conducted = linkup_research.get('search_results_analyzed', 0)
            confidence_score = linkup_research.get('research_confidence_score', 0)
            
            self.logger.info(f"✅ Fixed Linkup research completed:")
            self.logger.info(f"   📊 {searches_conducted} insights analyzed")
            self.logger.info(f"   🔍 {gaps_found} content opportunities identified")
            self.logger.info(f"   🎯 {confidence_score}% research confidence")
            
            return context
            
        except asyncio.TimeoutError:
            self.logger.warning("⚠️ Linkup research timed out, continuing without enhancement")
            return context
        except Exception as e:
            self.logger.warning(f"⚠️ Linkup research failed: {e}, continuing without enhancement")
            return context

class BlogIdeaGenerationEngine:
    # ... existing code ...
    
    async def _enhance_context_with_linkup_research(
        self,
        context: Dict[str, Any], 
        linkup_api_key: str,
        llm_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhanced context with Linkup research using official client"""
        
        try:
            # Use the fixed Linkup researcher
            linkup_config = {
                'max_searches': 6,  # Reduced for cost control
                'rate_limit_delay': 2.0
            }
            
            # REPLACE the old LinkupResearcher with LinkupResearcher
            linkup_researcher = LinkupResearcher(linkup_api_key, linkup_config)
            
            # Get selected data for research
            selected_topics = context.get('selected_trending_topics', [])
            selected_opportunities = context.get('selected_opportunities', [])
            
            if not selected_topics and not selected_opportunities:
                self.logger.warning("⚠️ No selected topics/opportunities for Linkup research")
                return context
            
            # Conduct research with timeout
            self.logger.info(f"🔍 Starting fixed Linkup research: {len(selected_topics)} topics, {len(selected_opportunities)} opportunities")
            
            linkup_research = await asyncio.wait_for(
                linkup_researcher.research_content_gaps(selected_topics, selected_opportunities),
                timeout=120  # 2 minute timeout
            )
            
            # Enhance context with research
            context['linkup_research'] = linkup_research
            context['research_enhanced'] = True
            
            # Log research results
            gaps_found = linkup_research.get('total_gaps_identified', 0)
            searches_conducted = linkup_research.get('search_results_analyzed', 0)
            confidence_score = linkup_research.get('research_confidence_score', 0)
            
            self.logger.info(f"✅ Fixed Linkup research completed:")
            self.logger.info(f"   📊 {searches_conducted} insights analyzed")
            self.logger.info(f"   🔍 {gaps_found} content opportunities identified")
            self.logger.info(f"   🎯 {confidence_score}% research confidence")
            
            return context
            
        except asyncio.TimeoutError:
            self.logger.warning("⚠️ Linkup research timed out, continuing without enhancement")
            return context
        except Exception as e:
            self.logger.warning(f"⚠️ Linkup research failed: {e}, continuing without enhancement")
            return context

# ============================================================================
# HELPER FUNCTIONS TO ADD TO BLOG_IDEA_GENERATOR.PY
# ============================================================================

def _extract_keywords_from_context(context: Dict[str, Any]) -> List[str]:
    """
    Helper function to extract keywords from Phase 1 context
    Add this as a method to your BlogIdeaGenerationEngine class
    """
    
    keywords = []
    
    # Extract from selected topics
    selected_topics = context.get('selected_trending_topics', [])
    for topic in selected_topics:
        topic_keywords = topic.get('keywords', [])
        if isinstance(topic_keywords, str):
            try:
                topic_keywords = json.loads(topic_keywords)
            except:
                topic_keywords = [topic_keywords] if topic_keywords else []
        keywords.extend(topic_keywords or [])
    
    # Extract from selected opportunities
    selected_opportunities = context.get('selected_opportunities', [])
    for opp in selected_opportunities:
        # Safely parse additional_data
        additional_data = opp.get('additional_data', {})
        if isinstance(additional_data, str):
            try:
                additional_data = json.loads(additional_data)
            except:
                additional_data = {}
        
        opp_keywords = additional_data.get('keywords', [])
        if isinstance(opp_keywords, str):
            try:
                opp_keywords = json.loads(opp_keywords)
            except:
                opp_keywords = [opp_keywords] if opp_keywords else []
        keywords.extend(opp_keywords or [])
    
    # Extract from keyword intelligence
    keyword_intelligence = context.get('keyword_intelligence', {})
    high_volume = keyword_intelligence.get('high_volume_keywords', [])
    if isinstance(high_volume, str):
        try:
            high_volume = json.loads(high_volume)
        except:
            high_volume = []
    keywords.extend(high_volume or [])
    
    # Remove duplicates and return
    return list(set(keywords))[:15]  # Limit to top 15 keywords


# ============================================================================
# MONETIZATION ENHANCEMENT INTEGRATION
# ============================================================================

# Import the monetization enhancer
from monetization_enhancer import enhance_blog_ideas_with_monetization

class MonetizedBlogIdeaGenerationEngine(BlogIdeaGenerationEngine):
    """Enhanced blog idea generation with monetization analysis"""
    
    async def generate_monetized_blog_ideas(
        self,
        analysis_id: str,
        user_id: str,
        llm_config: Dict[str, Any],
        generation_config: Dict[str, Any] = None,
        linkup_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate blog ideas with comprehensive monetization analysis"""
        
        self.logger.info("🚀 Starting monetized blog idea generation...")
        
        try:
            # Step 1: Generate regular blog ideas using existing engine
            self.logger.info("💡 Generating blog ideas...")
            blog_result = await self.generate_comprehensive_blog_ideas(
                analysis_id=analysis_id,
                user_id=user_id,
                llm_config=llm_config,
                generation_config=generation_config,
                linkup_api_key=linkup_api_key
            )
            
            # Step 2: Load context for monetization analysis
            context = await self._load_phase1_strategic_context(analysis_id, user_id)
            
            # Step 3: Add monetization analysis to each blog idea
            self.logger.info("💰 Adding monetization analysis...")
            monetized_ideas = await enhance_blog_ideas_with_monetization(
                blog_result['blog_ideas'],
                context
            )
            
            # Step 4: Sort by monetization score (highest revenue potential first)
            monetized_ideas = sorted(
                monetized_ideas,
                key=lambda x: x.get('monetization_score', 0),
                reverse=True
            )
            
            # Step 5: Update result with monetized ideas
            blog_result['blog_ideas'] = monetized_ideas
            blog_result['monetization_summary'] = self._generate_monetization_summary(monetized_ideas)
            
            # Step 6: Add monetization insights to strategic insights
            if 'strategic_insights' in blog_result:
                blog_result['strategic_insights']['monetization_analysis'] = self._generate_monetization_insights(monetized_ideas)
            
            self.logger.info(f"✅ Monetized blog idea generation completed: {len(monetized_ideas)} ideas analyzed")
            return blog_result
            
        except Exception as e:
            self.logger.error(f"❌ Monetized blog idea generation failed: {e}")
            raise
    
    def _generate_monetization_summary(self, monetized_ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for monetization analysis"""
        
        if not monetized_ideas:
            return {}
        
        # Calculate revenue ranges
        total_revenue = sum(idea.get('revenue_potential', 0) for idea in monetized_ideas)
        high_revenue_ideas = [idea for idea in monetized_ideas if idea.get('revenue_potential', 0) >= 5000]
        medium_revenue_ideas = [idea for idea in monetized_ideas if 1000 <= idea.get('revenue_potential', 0) < 5000]
        low_revenue_ideas = [idea for idea in monetized_ideas if idea.get('revenue_potential', 0) < 1000]
        
        # Monetization score distribution
        score_distribution = {
            "high": len([idea for idea in monetized_ideas if idea.get('monetization_score', 0) >= 80]),
            "medium": len([idea for idea in monetized_ideas if 60 <= idea.get('monetization_score', 0) < 80]),
            "low": len([idea for idea in monetized_ideas if idea.get('monetization_score', 0) < 60])
        }
        
        # Revenue stream analysis
        revenue_streams = {
            "affiliate": sum(
                idea.get('monetization_analysis', {}).get('affiliate_opportunities', {}).get('estimated_annual_revenue', 0)
                for idea in monetized_ideas
            ),
            "digital_products": sum(
                idea.get('monetization_analysis', {}).get('digital_product_opportunities', {}).get('estimated_annual_revenue', 0)
                for idea in monetized_ideas
            ),
            "services": sum(
                idea.get('monetization_analysis', {}).get('service_opportunities', {}).get('estimated_annual_revenue', 0)
                for idea in monetized_ideas
            ),
            "lead_generation": sum(
                idea.get('monetization_analysis', {}).get('lead_generation_opportunities', {}).get('estimated_annual_revenue', 0)
                for idea in monetized_ideas
            )
        }
        
        return {
            "total_estimated_annual_revenue": total_revenue,
            "revenue_distribution": revenue_streams,
            "high_value_ideas": len(high_revenue_ideas),
            "medium_value_ideas": len(medium_revenue_ideas),
            "low_value_ideas": len(low_revenue_ideas),
            "monetization_score_distribution": score_distribution,
            "average_monetization_score": sum(idea.get('monetization_score', 0) for idea in monetized_ideas) / len(monetized_ideas),
            "top_monetization_opportunities": [
                {
                    "title": idea.get('title', ''),
                    "revenue_potential": idea.get('revenue_potential', 0),
                    "monetization_score": idea.get('monetization_score', 0),
                    "priority": idea.get('monetization_priority', ''),
                    "top_revenue_stream": max(
                        idea.get('monetization_analysis', {}).get('affiliate_opportunities', {}).get('estimated_annual_revenue', 0),
                        idea.get('monetization_analysis', {}).get('digital_product_opportunities', {}).get('estimated_annual_revenue', 0),
                        idea.get('monetization_analysis', {}).get('service_opportunities', {}).get('estimated_annual_revenue', 0),
                        idea.get('monetization_analysis', {}).get('lead_generation_opportunities', {}).get('estimated_annual_revenue', 0)
                    )
                }
                for idea in monetized_ideas[:5]
            ]
        }
    
    def _generate_monetization_insights(self, monetized_ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate strategic monetization insights"""
        
        if not monetized_ideas:
            return {}
        
        # Analyze top monetization strategies
        strategies = []
        for idea in monetized_ideas[:10]:  # Top 10 ideas
            analysis = idea.get('monetization_analysis', {})
            strategy = analysis.get('monetization_strategy', {})
            
            strategies.append({
                "blog_title": idea.get('title', ''),
                "estimated_revenue": idea.get('revenue_potential', 0),
                "monetization_priority": idea.get('monetization_priority', ''),
                "immediate_actions": strategy.get('immediate_actions', []),
                "thirty_day_plan": strategy.get('30_day_plan', []),
                "ninety_day_plan": strategy.get('90_day_plan', []),
                "long_term_strategy": strategy.get('long_term_strategy', [])
            })
        
        # Identify best monetization approaches
        affiliate_ideas = [idea for idea in monetized_ideas 
                          if idea.get('monetization_analysis', {}).get('affiliate_opportunities', {}).get('score', 0) >= 70]
        
        product_ideas = [idea for idea in monetized_ideas 
                        if idea.get('monetization_analysis', {}).get('digital_product_opportunities', {}).get('score', 0) >= 70]
        
        service_ideas = [idea for idea in monetized_ideas 
                        if idea.get('monetization_analysis', {}).get('service_opportunities', {}).get('score', 0) >= 70]
        
        return {
            "monetization_strategy_overview": {
                "best_affiliate_opportunities": len(affiliate_ideas),
                "best_product_opportunities": len(product_ideas),
                "best_service_opportunities": len(service_ideas),
                "total_revenue_streams": 4,
                "diversification_score": "high" if len([i for i in monetized_ideas if i.get('monetization_score', 0) >= 70]) >= 5 else "medium"
            },
            "revenue_optimization_recommendations": [
                "Focus on high-scoring affiliate opportunities for immediate revenue",
                "Develop digital products for scalable income streams",
                "Create service packages for high-ticket revenue",
                "Build email lists for lead generation and nurturing",
                "Implement multiple monetization streams per blog post"
            ],
            "implementation_timeline": {
                "week_1": ["Set up affiliate programs", "Create lead magnets"],
                "week_2_4": ["Launch first digital products", "Optimize affiliate links"],
                "month_2_3": ["Develop service offerings", "Build sales funnels"],
                "ongoing": ["Monitor revenue performance", "Scale successful strategies"]
            },
            "top_monetization_strategies": strategies
        }

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
Example usage of LinkupResearcher within blog_idea_generator.py:

async def _enhance_context_with_linkup_research(
    self,
    context: Dict[str, Any], 
    linkup_api_key: str,
    llm_config: Dict[str, Any]
) -> Dict[str, Any]:
    '''Enhance context with Linkup research'''
    
    try:
        # Initialize Linkup researcher
        linkup_config = {
            'max_searches': 8,
            'results_per_search': 10,
            'search_timeout': 30,
            'rate_limit_delay': 1.5
        }
        
        linkup_researcher = LinkupResearcher(linkup_api_key, linkup_config)
        
        # Get selected data for research
        selected_topics = context.get('selected_trending_topics', [])
        selected_opportunities = context.get('selected_opportunities', [])
        
        if not selected_topics and not selected_opportunities:
            self.logger.warning("⚠️ No selected topics/opportunities for Linkup research")
            return context
        
        # Conduct research with timeout
        linkup_research = await asyncio.wait_for(
            linkup_researcher.research_content_gaps(selected_topics, selected_opportunities),
            timeout=90  # 1.5 minute timeout for all Linkup research
        )
        
        # Enhance context with research
        context['linkup_research'] = linkup_research
        context['research_enhanced'] = True
        
        # Log research results
        gaps_found = linkup_research.get('total_gaps_identified', 0)
        searches_conducted = linkup_research.get('search_results_analyzed', 0)
        confidence_score = linkup_research.get('research_confidence_score', 0)
        
        self.logger.info(f"✅ Linkup research completed:")
        self.logger.info(f"   📊 {searches_conducted} searches analyzed")
        self.logger.info(f"   🔍 {gaps_found} content gaps identified")
        self.logger.info(f"   🎯 {confidence_score}% research confidence")
        
        return context
        
    except asyncio.TimeoutError:
        self.logger.warning("⚠️ Linkup research timed out, continuing without enhancement")
        return context
    except Exception as e:
        self.logger.warning(f"⚠️ Linkup research failed: {e}, continuing without enhancement")
        return context
"""






class BlogIdeaGenerationEngine:

    def __init__(self, config: Dict[str, Any] = None):
            self.config = config or {}
            self.logger = logging.getLogger(__name__)
            
            # Generation parameters
            self.TARGET_IDEAS_MIN = 20
            self.TARGET_IDEAS_MAX = 50
            self.IDEAS_PER_TRENDING_TOPIC = 3
            self.IDEAS_PER_OPPORTUNITY = 2
            self.BONUS_IDEAS_FROM_PYTRENDS = 5
            
            # Content format distribution
            self.CONTENT_FORMATS = {
                "how_to_guide": {
                    "weight": 25,
                    "description": "Step-by-step instructional content",
                    "typical_length": "2000-3500 words",
                    "engagement_factor": 0.85
                },
                "listicle": {
                    "weight": 20,
                    "description": "List-based content with actionable items",
                    "typical_length": "1500-2500 words", 
                    "engagement_factor": 0.90
                },
                "case_study": {
                    "weight": 15,
                    "description": "Real-world example with analysis",
                    "typical_length": "2500-4000 words",
                    "engagement_factor": 0.80
                },
                "comparison": {
                    "weight": 15,
                    "description": "Comparing tools, strategies, or approaches",
                    "typical_length": "2000-3000 words",
                    "engagement_factor": 0.85
                },
                "trend_analysis": {
                    "weight": 10,
                    "description": "Analysis of current trends and predictions",
                    "typical_length": "1800-2800 words",
                    "engagement_factor": 0.75
                },
                "beginner_guide": {
                    "weight": 10,
                    "description": "Comprehensive introduction for newcomers",
                    "typical_length": "3000-5000 words",
                    "engagement_factor": 0.80
                },
                "tool_review": {
                    "weight": 5,
                    "description": "In-depth review of tools or software",
                    "typical_length": "1500-2500 words",
                    "engagement_factor": 0.75
                }
            }
            
            # Quality scoring weights
            self.SCORING_WEIGHTS = {
                "viral_potential": 0.25,
                "seo_optimization": 0.25,
                "audience_alignment": 0.20,
                "content_feasibility": 0.15,
                "business_impact": 0.15
            }




    """FIXED: Core engine for generating comprehensive blog post ideas from Phase 1 data"""
    async def _load_phase1_strategic_context(self, analysis_id: str, user_id: str) -> Dict[str, Any]:
        """Load comprehensive Phase 1 context for idea generation"""
        
        try:
            from working_supabase_integration import RLSSupabaseStorage
            supabase_storage = RLSSupabaseStorage()
            
            # Get enhanced Phase 2 data
            async def get_phase1_data():
                return await supabase_storage.get_selected_data_for_phase2(analysis_id, user_id)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                phase1_data = loop.run_until_complete(get_phase1_data())
            finally:
                loop.close()
            
            # Extract PyTrends data from analysis metadata
            analysis_info = phase1_data.get("analysis_info", {})
            metadata = analysis_info.get("metadata", {})
            pytrends_data = metadata.get("pytrends_analysis", {})
            
            # Build comprehensive context
            context = {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "research_context": phase1_data.get("research_context", {}),
                "selected_trending_topics": phase1_data.get("selected_trending_topics", []),
                "selected_opportunities": phase1_data.get("selected_opportunities", []),
                "keyword_intelligence": phase1_data.get("keyword_intelligence", {}),
                "pytrends_insights": pytrends_data,
                "phase2_enhancements": phase1_data.get("phase2_enhancements", {}),
                "blog_idea_generation_config": phase1_data.get("blog_idea_generation_config", {}),
                "strategic_intelligence_summary": phase1_data.get("strategic_intelligence_summary", {})
            }
            
            self.logger.info(f"📊 Loaded context: {len(context['selected_trending_topics'])} topics, {len(context['selected_opportunities'])} opportunities")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to load Phase 1 context: {e}")
            raise

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
                timeout=60.0
            )
            return client
            
        elif provider == 'anthropic':
            import anthropic
            client = anthropic.AsyncAnthropic(
                api_key=api_key,
                timeout=60.0
            )
            return client
            
        elif provider == 'kimi':
            import openai
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.moonshot.ai/v1",
                timeout=60.0
            )
            return client
            
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def _generate_from_trending_topics(
        self,
        context: Dict[str, Any],
        llm_client,
        llm_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate blog ideas from selected trending topics"""
        
        trending_topics = context.get("selected_trending_topics", [])
        if not trending_topics:
            self.logger.warning("No trending topics found in context")
            return []
        
        ideas = []
        
        for topic in trending_topics[:5]:  # Limit to top 5 topics
            try:
                # Create prompt for this specific topic
                prompt = self._create_trending_topic_prompt(topic, context)
                
                # Generate ideas with LLM
                response = await self._call_llm_with_retry(llm_client, prompt, llm_config)
                
                # Parse and validate response
                topic_ideas = self._parse_blog_ideas_response(response, topic, "trending_topic")
                
                # Add topic context to each idea
                for idea in topic_ideas:
                    idea.update({
                        "source_type": "trending_topic",
                        "source_topic_id": topic.get("id"),
                        "source_viral_potential": topic.get("viral_potential", 70),
                        "generation_source": f"Trending Topic: {topic.get('title', '')}"
                    })
                
                ideas.extend(topic_ideas)
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.warning(f"Failed to generate ideas for topic {topic.get('title', 'unknown')}: {e}")
        
        self.logger.info(f"Generated {len(ideas)} ideas from trending topics")
        return ideas

    async def _generate_from_opportunities(
        self,
        context: Dict[str, Any],
        llm_client,
        llm_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate blog ideas from selected content opportunities"""
        
        opportunities = context.get("selected_opportunities", [])
        if not opportunities:
            self.logger.warning("No content opportunities found in context")
            return []
        
        ideas = []
        
        for opportunity in opportunities[:3]:  # Limit to top 3 opportunities
            try:
                # Create prompt for this specific opportunity
                prompt = self._create_opportunity_prompt(opportunity, context)
                
                # Generate ideas with LLM
                response = await self._call_llm_with_retry(llm_client, prompt, llm_config)
                
                # Parse and validate response
                opp_ideas = self._parse_blog_ideas_response(response, opportunity, "content_opportunity")
                
                # Add opportunity context to each idea
                for idea in opp_ideas:
                    idea.update({
                        "source_type": "content_opportunity",
                        "source_opportunity_id": opportunity.get("id"),
                        "source_difficulty": opportunity.get("difficulty", 50),
                        "generation_source": f"Content Opportunity: {opportunity.get('title', '')}"
                    })
                
                ideas.extend(opp_ideas)
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.warning(f"Failed to generate ideas for opportunity {opportunity.get('title', 'unknown')}: {e}")
        
        self.logger.info(f"Generated {len(ideas)} ideas from content opportunities")
        return ideas

    async def _generate_from_pytrends_data(
        self,
        context: Dict[str, Any],
        llm_client,
        llm_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate blog ideas from PyTrends insights - ENHANCED with sub-topics"""
        
        # Get PyTrends data from context
        pytrends_data = context.get("pytrends_insights", {})
        if not pytrends_data:
            self.logger.info("No PyTrends data available")
            return []
        
        ideas = []
        
        # Generate ideas from geographic insights
        geographic_insights = pytrends_data.get("geographic_insights", {})
        global_hotspots = geographic_insights.get("global_hotspots", [])
        
        if global_hotspots:
            try:
                prompt = self._create_geographic_insights_prompt(global_hotspots, context)
                response = await self._call_llm_with_retry(llm_client, prompt, llm_config)
                geo_ideas = self._parse_blog_ideas_response(response, {"title": "Geographic Insights"}, "geographic_insights")
                
                for idea in geo_ideas:
                    idea.update({
                        "source_type": "geographic_insights",
                        "generation_source": "PyTrends Geographic Analysis"
                    })
                
                ideas.extend(geo_ideas)
                
            except Exception as e:
                self.logger.warning(f"Failed to generate geographic insights ideas: {e}")
        
        # Generate ideas from rising queries (sub-topics)
        related_queries = pytrends_data.get("related_queries_insights", {})
        rising_queries = related_queries.get("rising_queries", [])
        top_queries = related_queries.get("top_related_queries", [])
        
        if rising_queries or top_queries:
            try:
                # Generate ideas from both rising and top queries as sub-topics
                subtopic_data = {
                    "rising_subtopics": rising_queries,
                    "top_subtopics": top_queries
                }
                prompt = self._create_subtopics_prompt(subtopic_data, context)
                response = await self._call_llm_with_retry(llm_client, prompt, llm_config)
                subtopic_ideas = self._parse_blog_ideas_response(response, {"title": "Sub-Topics"}, "subtopics")
                
                for idea in subtopic_ideas:
                    idea.update({
                        "source_type": "subtopics",
                        "generation_source": "PyTrends Sub-Topic Analysis"
                    })
                
                ideas.extend(subtopic_ideas)
                
            except Exception as e:
                self.logger.warning(f"Failed to generate sub-topics ideas: {e}")
        
        # Generate ideas from subtopic analysis if available
        subtopic_analysis = pytrends_data.get("subtopic_analysis", {})
        subtopic_results = subtopic_analysis.get("subtopic_results", [])
        
        if subtopic_results:
            try:
                prompt = self._create_subtopic_analysis_prompt(subtopic_results, context)
                response = await self._call_llm_with_retry(llm_client, prompt, llm_config)
                analysis_ideas = self._parse_blog_ideas_response(response, {"title": "Sub-Topic Analysis"}, "subtopic_analysis")
                
                for idea in analysis_ideas:
                    idea.update({
                        "source_type": "subtopic_analysis",
                        "generation_source": "PyTrends Sub-Topic Performance Analysis"
                    })
                
                ideas.extend(analysis_ideas)
                
            except Exception as e:
                self.logger.warning(f"Failed to generate sub-topic analysis ideas: {e}")
        
        # Legacy rising queries for backward compatibility
        if rising_queries and not subtopic_results:
            try:
                prompt = self._create_rising_queries_prompt(rising_queries, context)
                response = await self._call_llm_with_retry(llm_client, prompt, llm_config)
                rising_ideas = self._parse_blog_ideas_response(response, {"title": "Rising Queries"}, "rising_queries")
                
                for idea in rising_ideas:
                    idea.update({
                        "source_type": "rising_queries",
                        "generation_source": "PyTrends Rising Queries"
                    })
                
                ideas.extend(rising_ideas)
                
            except Exception as e:
                self.logger.warning(f"Failed to generate rising queries ideas: {e}")
        
        self.logger.info(f"Generated {len(ideas)} ideas from PyTrends data (including sub-topics)")
        return ideas

    async def _generate_from_keyword_clusters(
        self,
        context: Dict[str, Any],
        llm_client,
        llm_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate blog ideas from keyword intelligence - FIXED VERSION"""
        
        keyword_intelligence = context.get("keyword_intelligence", {})
        if not keyword_intelligence:
            self.logger.info("No keyword intelligence available")
            return []
        
        ideas = []
        
        # FIXED: Safe access to additional_data (might be string or dict)
        additional_data = keyword_intelligence.get("additional_data", {})
        
        # Handle case where additional_data is a JSON string
        if isinstance(additional_data, str):
            try:
                additional_data = json.loads(additional_data)
            except (json.JSONDecodeError, ValueError):
                self.logger.warning("Failed to parse additional_data as JSON, using empty dict")
                additional_data = {}
        
        # Now safely access keyword_clusters
        keyword_clusters = additional_data.get("keyword_clusters", {}) if isinstance(additional_data, dict) else {}
        
        if keyword_clusters:
            try:
                prompt = self._create_keyword_clusters_prompt(keyword_clusters, context)
                response = await self._call_llm_with_retry(llm_client, prompt, llm_config)
                keyword_ideas = self._parse_blog_ideas_response(response, {"title": "Keyword Clusters"}, "keyword_clusters")
                
                for idea in keyword_ideas:
                    idea.update({
                        "source_type": "keyword_clusters",
                        "generation_source": "Keyword Intelligence Analysis"
                    })
                
                ideas.extend(keyword_ideas)
                
            except Exception as e:
                self.logger.warning(f"Failed to generate keyword cluster ideas: {e}")
        else:
            self.logger.info("No keyword clusters found in additional_data")
        
        self.logger.info(f"Generated {len(ideas)} ideas from keyword clusters")
        return ideas


    def _create_trending_topic_prompt(self, topic: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Create prompt for generating ideas from a trending topic - IMPROVED"""
        
        topic_title = topic.get("title", "")
        additional_data = self._safe_parse_json_field(topic, "additional_data", {})
        topic_description = additional_data.get("description", "")
        keywords = topic.get("keywords", [])
        viral_potential = topic.get("viral_potential", 70)
        
        research_context = context.get("research_context", {})
        target_audience = research_context.get("target_audience", "professional")
        main_topic = research_context.get("topic", "")
    
        return f"""
        Generate {self.IDEAS_PER_TRENDING_TOPIC} high-quality blog ideas based on this trending topic.

        Topic: {topic_title}
        Description: {topic_description}
        Main Subject: {main_topic}
        Target Audience: {target_audience}
        Viral Potential: {viral_potential}%
        Keywords: {', '.join(keywords[:5]) if isinstance(keywords, list) else str(keywords)}

        IMPORTANT: Return ONLY a valid JSON array with no additional text, comments, or markdown formatting.

        Each blog idea must include these exact fields:
        - title: string (compelling and SEO-friendly)
        - description: string (2-3 sentences)
        - content_format: string (how_to_guide, listicle, case_study, comparison, trend_analysis, or tutorial)
        - difficulty_level: string (beginner, intermediate, or advanced)
        - primary_keywords: array of strings (3-5 keywords that are highly relevant to the title and description. Do not include generic keywords.)
        - secondary_keywords: array of strings (5-8 keywords that are highly relevant to the title and description. Do not include generic keywords.)
        - outline: array of strings (5-8 sections)
        - key_points: array of strings (3-5 points)
        - business_value: string (how this helps audience)
        - call_to_action: string (what readers should do)
        - estimated_word_count: number (1500-4000)
        - estimated_reading_time: number (5-20 minutes)

        Example format:
        [
        {{
            "title": "Complete Guide to {main_topic} for {target_audience}",
            "description": "A comprehensive guide that helps {target_audience} understand and implement {main_topic} strategies.",
            "content_format": "how_to_guide",
            "difficulty_level": "intermediate",
            "primary_keywords": ["{main_topic}", "{main_topic} implementation", "{main_topic} framework"],
            "secondary_keywords": ["{main_topic} methodology", "{main_topic} case study", "{main_topic} step-by-step"],
            "outline": ["Introduction", "Getting Started", "Key Strategies", "Implementation", "Best Practices", "Common Mistakes", "Conclusion"],
            "key_points": ["Practical implementation steps", "Real-world examples", "Actionable takeaways"],
            "business_value": "Helps {target_audience} implement effective {main_topic} strategies to achieve better results",
            "call_to_action": "Start implementing these {main_topic} strategies in your business today",
            "estimated_word_count": 2500,
            "estimated_reading_time": 12
        }}
        ]

        Return only the JSON array, no other text.
        """

    def _create_opportunity_prompt(self, opportunity: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Create prompt for generating ideas from a content opportunity - IMPROVED"""
        
        opp_title = opportunity.get("title", "")
        opp_format = opportunity.get("format", "how_to_guide")
        difficulty = opportunity.get("difficulty", 50)
        engagement_potential = opportunity.get("engagement_potential", "medium")
        
        additional_data = self._safe_parse_json_field(opportunity, "additional_data", {})
        time_investment = additional_data.get("time_investment", "2-3 weeks")
        keywords = additional_data.get("keywords", [])
        
        research_context = context.get("research_context", {})
        target_audience = research_context.get("target_audience", "professional")
        main_topic = research_context.get("topic", "")
        
        return f"""
    Generate {self.IDEAS_PER_OPPORTUNITY} high-quality blog ideas based on this content opportunity.

    Opportunity: {opp_title}
    Format: {opp_format}
    Main Subject: {main_topic}
    Target Audience: {target_audience}
    Difficulty Score: {difficulty}/100
    Engagement Potential: {engagement_potential}
    Keywords: {', '.join(keywords[:5]) if isinstance(keywords, list) else str(keywords)}

    IMPORTANT: Return ONLY a valid JSON array with no additional text, comments, or markdown formatting.

    Each blog idea must include these exact fields:
    - title: string (compelling and SEO-friendly)
    - description: string (2-3 sentences)
    - content_format: string (how_to_guide, listicle, case_study, comparison, trend_analysis, or tutorial)
    - difficulty_level: string (beginner, intermediate, or advanced)
    - primary_keywords: array of strings (3-5 keywords that are highly relevant to the title and description. Do not include generic keywords.)
    - secondary_keywords: array of strings (5-8 keywords that are highly relevant to the title and description. Do not include generic keywords.)
    - outline: array of strings (5-8 sections)
    - key_points: array of strings (3-5 points)
    - business_value: string (how this helps audience)
    - call_to_action: string (what readers should do)
    - estimated_word_count: number (1500-4000)
    - estimated_reading_time: number (5-20 minutes)

    Use the same exact format as specified in the trending topics prompt with all required fields.

    Return only the JSON array, no other text.
    """

    def _create_geographic_insights_prompt(self, hotspots: List[Dict], context: Dict[str, Any]) -> str:
        """Create prompt for geographic insights ideas"""
        
        top_countries = [h.get("country", "") for h in hotspots[:3]]
        research_context = context.get("research_context", {})
        main_topic = research_context.get("topic", "")
        
        return f"""
    Generate {self.BONUS_IDEAS_FROM_PYTRENDS} blog ideas based on geographic trends analysis:

    Top Markets: {', '.join(top_countries)}
    Main Topic: {main_topic}

    Create blog ideas that leverage geographic insights and market differences. Focus on:
    - Regional market analysis
    - Geographic-specific strategies
    - International comparisons
    - Market entry strategies

    Return as valid JSON array of detailed blog ideas.
    """

    def _create_rising_queries_prompt(self, rising_queries: List[Dict], context: Dict[str, Any]) -> str:
        """Create prompt for rising queries ideas"""
        
        top_queries = [q.get("query", "") for q in rising_queries[:5]]
        research_context = context.get("research_context", {})
        main_topic = research_context.get("topic", "")
        
        return f"""
    Generate {self.BONUS_IDEAS_FROM_PYTRENDS} blog ideas based on rising search queries:

    Rising Queries: {', '.join(top_queries)}
    Main Topic: {main_topic}

    Create blog ideas that capture emerging search trends. Focus on:
    - Addressing new questions and concerns
    - Covering emerging subtopics
    - Providing timely insights
    - Answering trending questions

    Return as valid JSON array of detailed blog ideas.
    """

    def _create_subtopics_prompt(self, subtopic_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Create prompt for sub-topics ideas"""
        
        rising_subtopics = subtopic_data.get("rising_subtopics", [])
        top_subtopics = subtopic_data.get("top_subtopics", [])
        
        rising_queries = [q.get("query", "") for q in rising_subtopics[:5]]
        top_queries = [q.get("query", "") for q in top_subtopics[:5]]
        
        research_context = context.get("research_context", {})
        main_topic = research_context.get("topic", "")
        
        return f"""
    Generate {self.BONUS_IDEAS_FROM_PYTRENDS * 2} blog ideas based on PyTrends sub-topic analysis:

    Main Topic: {main_topic}
    
    Top Sub-Topics: {', '.join(top_queries)}
    Rising Sub-Topics: {', '.join(rising_queries)}

    Create comprehensive blog ideas targeting these sub-topics. Focus on:
    - Specific aspects and angles of the main topic
    - Addressing specific user questions and pain points
    - Creating content for different search intents
    - Building topical authority through sub-topic coverage
    - Leveraging trending queries for immediate traffic

    Each blog idea should target a specific sub-topic while relating back to the main topic.

    Return as valid JSON array of detailed blog ideas.
    """

    def _create_subtopic_analysis_prompt(self, subtopic_results: List[Dict], context: Dict[str, Any]) -> str:
        """Create prompt for sub-topic performance analysis ideas"""
        
        top_performing = [s.get("subtopic", "") for s in subtopic_results[:5]]
        
        research_context = context.get("research_context", {})
        main_topic = research_context.get("topic", "")
        
        return f"""
    Generate {self.BONUS_IDEAS_FROM_PYTRENDS} blog ideas based on sub-topic performance analysis:

    Main Topic: {main_topic}
    High-Performing Sub-Topics: {', '.join(top_performing)}

    Create strategic blog ideas that leverage high-performing sub-topics. Focus on:
    - Targeting sub-topics with proven search interest
    - Creating comprehensive guides for each sub-topic
    - Building content clusters around successful sub-topics
    - Addressing specific user needs within each sub-topic
    - Creating competitive content that outperforms existing results

    Return as valid JSON array of detailed blog ideas.
    """

    def _create_keyword_clusters_prompt(self, clusters: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Create prompt for keyword cluster ideas"""
        
        cluster_names = list(clusters.keys())[:3]
        research_context = context.get("research_context", {})
        main_topic = research_context.get("topic", "")
        
        return f"""
    Generate {self.BONUS_IDEAS_FROM_PYTRENDS} blog ideas based on keyword clusters:

    Keyword Clusters: {', '.join(cluster_names)}
    Main Topic: {main_topic}

    Create comprehensive blog ideas that target specific keyword clusters. Focus on:
    - Cluster-specific content strategies
    - Semantic keyword optimization
    - Topic authority building
    - Comprehensive coverage

    Return as valid JSON array of detailed blog ideas.
    """

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
                        max_tokens=3000,
                        timeout=60
                    )
                    return response.choices[0].message.content
                    
                elif provider == 'anthropic':
                    response = await llm_client.messages.create(
                        model=llm_config.get('model', 'claude-3-sonnet-20240229'),
                        max_tokens=3000,
                        messages=[{"role": "user", "content": prompt}],
                        timeout=60
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
                        max_tokens=3000,
                        timeout=60
                    )
                    return response.choices[0].message.content
                    
                else:
                    raise ValueError(f"Unsupported LLM provider: {provider}")
                    
            except Exception as e:
                self.logger.warning(f"LLM call failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries:
                    raise
                await asyncio.sleep(2 ** attempt)

    def _parse_blog_ideas_response(self, response: str, source: Dict[str, Any], source_type: str) -> List[Dict[str, Any]]:
        """Parse LLM response into blog ideas - IMPROVED VERSION"""
        
        try:
            self.logger.info(f"Parsing LLM response for {source_type}")
            
            # Clean the response first
            cleaned_response = response.strip()
            
            # Try multiple JSON extraction methods
            json_data = None
            
            # Method 1: Try direct JSON parsing
            try:
                json_data = json.loads(cleaned_response)
            except:
                pass
            
            # Method 2: Look for JSON array in markdown code blocks
            if json_data is None:
                json_pattern = r'```json\s*(.*?)\s*```'
                json_match = re.search(json_pattern, cleaned_response, re.DOTALL | re.IGNORECASE)
                if json_match:
                    try:
                        json_str = json_match.group(1).strip()
                        json_data = json.loads(json_str)
                    except:
                        pass
            
            # Method 3: Look for array anywhere in response
            if json_data is None:
                json_pattern = r'\[[\s\S]*\]'
                json_match = re.search(json_pattern, cleaned_response)
                if json_match:
                    try:
                        json_str = json_match.group(0)
                        # Try to fix common JSON issues
                        json_str = self._fix_common_json_issues(json_str)
                        json_data = json.loads(json_str)
                    except Exception as e:
                        self.logger.warning(f"JSON parsing attempt failed: {e}")
                        self.logger.debug(f"Problematic JSON: {json_str[:500]}...")
            
            # Method 4: Try to extract objects and build array
            if json_data is None:
                objects = re.findall(r'\{[^{}]*\}', cleaned_response)
                if objects:
                    try:
                        fixed_objects = []
                        for obj_str in objects:
                            fixed_obj = self._fix_common_json_issues(obj_str)
                            try:
                                parsed_obj = json.loads(fixed_obj)
                                fixed_objects.append(parsed_obj)
                            except:
                                continue
                        if fixed_objects:
                            json_data = fixed_objects
                    except:
                        pass
            
            # If we got valid JSON data, validate and enhance it
            if json_data and isinstance(json_data, list):
                return self._validate_and_enhance_ideas(json_data, source, source_type)
            
            # If all parsing failed, create fallback ideas
            self.logger.warning(f"All JSON parsing methods failed for {source_type}, using fallback")
            self.logger.debug(f"Original response: {cleaned_response[:200]}...")
            return self._create_fallback_ideas(source, source_type)
            
        except Exception as e:
            self.logger.error(f"Failed to parse blog ideas response: {e}")
            return self._create_fallback_ideas(source, source_type)
    def _fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues"""
        
        # Remove any trailing commas before closing brackets/braces
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix missing quotes around keys
        json_str = re.sub(r'(\w+):', r'"\1":', json_str)
        
        # Fix single quotes to double quotes
        json_str = json_str.replace("'", '"')
        
        # Fix escaped quotes issues
        json_str = json_str.replace('\\"', '"')
        
        # Remove any control characters
        json_str = re.sub(r'[\x00-\x1f\x7f]', '', json_str)
        
        return json_str
    def _validate_and_enhance_ideas(self, ideas_data: List[Dict], source: Dict[str, Any], source_type: str) -> List[Dict[str, Any]]:
        """Validate and enhance parsed ideas"""
        
        enhanced_ideas = []
        
        for idea in ideas_data:
            if not isinstance(idea, dict) or not idea.get("title"):
                continue
            
            # Ensure required fields have default values
            enhanced_idea = {
                "title": idea.get("title", "Untitled Blog Idea"),
                "description": idea.get("description", "Description not provided"),
                "content_format": idea.get("content_format", "how_to_guide"),
                "difficulty_level": idea.get("difficulty_level", "intermediate"),
                "primary_keywords": idea.get("primary_keywords", []),
                "secondary_keywords": idea.get("secondary_keywords", []),
                "outline": idea.get("outline", []),
                "key_points": idea.get("key_points", []),
                "business_value": idea.get("business_value", "Provides value to target audience"),
                "call_to_action": idea.get("call_to_action", "Learn more about this topic"),
                "estimated_word_count": idea.get("estimated_word_count", 2500),
                "estimated_reading_time": idea.get("estimated_reading_time", 12),
                "featured_snippet_opportunity": True,
                "engagement_hooks": idea.get("engagement_hooks", []),
                "visual_elements": idea.get("visual_elements", []),
                "notes": "",
                "selected": False,
                "priority_level": "medium"
            }
            
            enhanced_ideas.append(enhanced_idea)
        
        return enhanced_ideas

    def _create_fallback_ideas(self, source: Dict[str, Any], source_type: str, count: int = 2) -> List[Dict[str, Any]]:
        """Create fallback ideas when LLM parsing fails"""
        
        source_title = source.get("title", "Unknown Source")
        
        fallback_ideas = []
        
        for i in range(count):
            idea = {
                "title": f"Blog Idea from {source_title} #{i+1}",
                "description": f"A comprehensive guide based on {source_title}",
                "content_format": "how_to_guide",
                "difficulty_level": "intermediate",
                "primary_keywords": [source_title.lower()],
                "secondary_keywords": [f"{source_title.lower()} guide", f"{source_title.lower()} tips"],
                "outline": [
                    "Introduction",
                    "Understanding the Basics",
                    "Key Strategies",
                    "Implementation Steps",
                    "Best Practices",
                    "Common Mistakes to Avoid",
                    "Conclusion and Next Steps"
                ],
                "key_points": [
                    "Practical implementation strategies",
                    "Real-world examples and case studies",
                    "Actionable takeaways for immediate use"
                ],
                "business_value": "Helps audience understand and implement effective strategies",
                "call_to_action": "Start implementing these strategies in your own work",
                "estimated_word_count": 2500,
                "estimated_reading_time": 12,
                "featured_snippet_opportunity": True,
                "engagement_hooks": [
                    "Have you ever wondered about...",
                    "The surprising truth about...",
                    "What most people get wrong about..."
                ],
                "visual_elements": [
                    "Infographic showing key statistics",
                    "Step-by-step process diagram",
                    "Before/after comparison charts"
                ],
                "notes": f"Generated from {source_type} fallback",
                "selected": False,
                "priority_level": "medium"
            }
            
            fallback_ideas.append(idea)
        
        return fallback_ideas

    def _deduplicate_ideas(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate ideas based on title similarity"""
        
        unique_ideas = []
        seen_titles = set()
        
        for idea in ideas:
            title = idea.get("title", "").lower().strip()
            
            # Simple deduplication based on title
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_ideas.append(idea)
        
        self.logger.info(f"Deduplicated {len(ideas)} ideas down to {len(unique_ideas)} unique ideas")
        return unique_ideas

    async def _optimize_ideas_for_seo_and_engagement(self, ideas: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Optimize ideas for SEO and engagement"""
        
        optimized_ideas = []
        
        for idea in ideas:
            optimized_idea = self._optimize_idea_for_seo_and_engagement(idea)
            optimized_idea = self._enhance_idea_with_performance_estimates(optimized_idea)
            optimized_ideas.append(optimized_idea)
        
        return optimized_ideas

    def _optimize_idea_for_seo_and_engagement(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize individual blog idea for SEO and engagement"""
        
        try:
            optimized_idea = idea.copy()
            
            # Safe access to idea fields
            title = str(idea.get('title', ''))
            description = str(idea.get('description', ''))
            
            # Safe parsing of keywords (handle both string and list)
            primary_keywords = idea.get('primary_keywords', [])
            if isinstance(primary_keywords, str):
                try:
                    primary_keywords = json.loads(primary_keywords)
                except:
                    primary_keywords = [primary_keywords] if primary_keywords else []
            
            # Title optimization
            if title and len(title) < 50:
                if '2025' not in title:
                    optimized_idea['title'] = f"{title} (2025 Guide)"
            
            # SEO optimization
            seo_score = int(idea.get('seo_optimization_score', 0))
            if primary_keywords and len(primary_keywords) > 0:
                seo_score = min(100, seo_score + 10)
                
                # Check if primary keyword is in title
                primary_kw = str(primary_keywords[0]).lower() if primary_keywords else ''
                if primary_kw and primary_kw in title.lower():
                    seo_score = min(100, seo_score + 5)
            
            optimized_idea['seo_optimization_score'] = seo_score
            
            # Engagement optimization
            engagement_score = int(idea.get('viral_potential_score', 0))
            
            # Boost for trending keywords
            trending_indicators = ['2025', 'latest', 'new', 'trending', 'best', 'ultimate', 'complete']
            if title and any(indicator in title.lower() for indicator in trending_indicators):
                engagement_score = min(100, engagement_score + 5)
            
            optimized_idea['viral_potential_score'] = engagement_score
            
            # Featured snippet optimization
            if title and any(title.lower().startswith(q) for q in ['what is', 'how to', 'why']):
                optimized_idea['featured_snippet_opportunity'] = True
            
            return optimized_idea
            
        except Exception as e:
            self.logger.warning(f"Failed to optimize idea {idea.get('title', 'Unknown')}: {e}")
            return idea

    def _enhance_idea_with_performance_estimates(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Add performance estimates to blog idea"""
        
        try:
            enhanced_idea = idea.copy()
            
            # Safe access to scores
            viral_score = idea.get('viral_potential_score', 0)
            seo_score = idea.get('seo_optimization_score', 0)
            business_score = idea.get('business_impact_score', 0)
            difficulty = idea.get('difficulty_level', 'intermediate')
            
            # Estimate traffic based on SEO score
            if seo_score >= 80:
                estimated_traffic = 1000 + (viral_score * 10)
            elif seo_score >= 60:
                estimated_traffic = 500 + (viral_score * 5)
            else:
                estimated_traffic = 200 + (viral_score * 2)
            
            # Estimate social shares based on viral potential
            estimated_shares = max(5, viral_score // 2)
            
            # Estimate time to rank based on competition and SEO
            difficulty_multiplier = {'beginner': 1.0, 'intermediate': 1.2, 'advanced': 1.5, 'expert': 2.0}
            base_weeks = 8
            time_to_rank = int(base_weeks * difficulty_multiplier.get(difficulty, 1.2) * (100 - seo_score) / 100 + 4)
            
            # Estimate backlink potential based on quality
            overall_quality = idea.get('overall_quality_score', 0)
            backlink_potential = max(1, overall_quality // 20)
            
            performance_estimates = {
                "viral_potential_score": viral_score,
                "traffic_potential_score": min(100, int(estimated_traffic / 20)),
                "conversion_potential_score": business_score,
                "estimated_time_to_rank_weeks": max(4, time_to_rank),
                "estimated_monthly_traffic": int(estimated_traffic),
                "estimated_social_shares": int(estimated_shares),
                "estimated_backlink_potential": int(backlink_potential)
            }
            
            enhanced_idea['performance_estimates'] = performance_estimates
            
            return enhanced_idea
            
        except Exception as e:
            self.logger.warning(f"Failed to enhance idea with performance estimates: {e}")
            return idea

    def _score_and_rank_ideas(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score and rank blog ideas by overall quality"""
        
        try:
            scored_ideas = []
            
            for idea in ideas:
                try:
                    # Safe access to all score fields with defaults
                    viral_score = float(idea.get('viral_potential_score', 0))
                    seo_score = float(idea.get('seo_optimization_score', 0))
                    audience_score = float(idea.get('audience_alignment_score', 0))
                    feasibility_score = float(idea.get('content_feasibility_score', 0))
                    business_score = float(idea.get('business_impact_score', 0))
                    
                    # Calculate weighted overall score
                    overall_score = (
                        viral_score * 0.25 +
                        seo_score * 0.25 +
                        audience_score * 0.20 +
                        feasibility_score * 0.15 +
                        business_score * 0.15
                    )
                    
                    idea['overall_quality_score'] = int(overall_score)
                    scored_ideas.append(idea)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to score idea {idea.get('title', 'Unknown')}: {e}")
                    # Add with default score
                    idea['overall_quality_score'] = 50
                    scored_ideas.append(idea)
            
            # Sort by overall quality score (highest first)
            ranked_ideas = sorted(scored_ideas, key=lambda x: x.get('overall_quality_score', 0), reverse=True)
            
            self.logger.info(f"📊 Scored and ranked {len(ranked_ideas)} ideas")
            
            return ranked_ideas
            
        except Exception as e:
            self.logger.error(f"Failed to score and rank ideas: {e}")
            # Return original ideas with default scores
            for idea in ideas:
                if 'overall_quality_score' not in idea:
                    idea['overall_quality_score'] = 50
            return ideas

    def _select_optimal_idea_set(self, ideas: List[Dict[str, Any]], generation_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Select optimal set of ideas based on configuration"""
        
        target_count = min(self.TARGET_IDEAS_MAX, max(self.TARGET_IDEAS_MIN, len(ideas)))
        
        if generation_config:
            min_ideas = generation_config.get("min_ideas", self.TARGET_IDEAS_MIN)
            max_ideas = generation_config.get("max_ideas", self.TARGET_IDEAS_MAX)
            target_count = min(max_ideas, max(min_ideas, len(ideas)))
        
        # Ideas are already sorted by overall_quality_score, so just take the top ones
        selected_ideas = ideas[:target_count]
        
        self.logger.info(f"Selected {len(selected_ideas)} ideas from {len(ideas)} total ideas")
        return selected_ideas

    def _generate_content_calendar(self, ideas: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content calendar recommendations"""
        
        # Analyze ideas for calendar planning
        high_priority_ideas = [i for i in ideas if i.get("overall_quality_score", 0) >= 80]
        quick_wins = [i for i in ideas if i.get("difficulty_level") == "beginner" and i.get("overall_quality_score", 0) >= 70]
        
        # Calculate publishing frequency
        total_ideas = len(ideas)
        if total_ideas <= 10:
            frequency = "1-2 posts per week"
            timeline = "6-8 weeks"
        elif total_ideas <= 20:
            frequency = "2-3 posts per week"
            timeline = "8-12 weeks"
        else:
            frequency = "3-4 posts per week"
            timeline = "12-16 weeks"
        
        return {
            "publishing_strategy": {
                "recommended_frequency": frequency,
                "estimated_timeline": timeline,
                "total_ideas_in_calendar": total_ideas
            },
            "priority_scheduling": {
                "immediate_priority_ideas": [i.get("title") for i in high_priority_ideas[:3]],
                "quick_win_ideas": [i.get("title") for i in quick_wins[:3]],
                "long_term_ideas": [i.get("title") for i in ideas[10:] if len(ideas) > 10]
            },
            "seasonal_optimization": {
                "q1_focus": "Educational and foundational content",
                "q2_focus": "Implementation and case studies",
                "q3_focus": "Advanced strategies and optimization",
                "q4_focus": "Year-end reviews and planning"
            },
            "content_series_opportunities": [
                f"Complete {context.get('research_context', {}).get('topic', 'Topic')} Guide Series",
                "Tool Reviews and Comparisons Series",
                "Case Study Deep-Dive Series"
            ],
            "format_distribution": {
                format_name: len([i for i in ideas if i.get("content_format") == format_name])
                for format_name in self.CONTENT_FORMATS.keys()
            },
            "estimated_resource_requirements": {
                "total_estimated_hours": sum(self._estimate_creation_time(idea) for idea in ideas),
                "average_hours_per_post": sum(self._estimate_creation_time(idea) for idea in ideas) / len(ideas) if ideas else 0,
                "recommended_team_size": "1-2 content creators" if total_ideas <= 15 else "2-3 content creators"
            }
        }

    def _estimate_creation_time(self, idea: Dict[str, Any]) -> int:
        """Estimate content creation time in hours"""
        
        word_count = idea.get("estimated_word_count", 2500)
        difficulty = idea.get("difficulty_level", "intermediate")
        
        # Base time: 500 words per hour for writing
        base_hours = word_count / 500
        
        # Difficulty multipliers
        multipliers = {
            "beginner": 1.0,
            "intermediate": 1.3,
            "advanced": 1.6,
            "expert": 2.0
        }
        
        # Add research, editing, and optimization time
        total_hours = (base_hours * multipliers.get(difficulty, 1.3)) + 3
        
        return int(total_hours)

    def _generate_strategic_insights(self, ideas: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic insights from the ideas"""
        
        total_ideas = len(ideas)
        avg_quality = sum(i.get("overall_quality_score", 0) for i in ideas) / total_ideas if total_ideas > 0 else 0
        
        # Quality distribution
        quality_tiers = {
            "excellent": len([i for i in ideas if i.get("overall_quality_score", 0) >= 85]),
            "high": len([i for i in ideas if 75 <= i.get("overall_quality_score", 0) < 85]),
            "good": len([i for i in ideas if 65 <= i.get("overall_quality_score", 0) < 75]),
            "needs_work": len([i for i in ideas if i.get("overall_quality_score", 0) < 65])
        }
        
        # Format analysis
        format_distribution = {}
        for idea in ideas:
            fmt = idea.get("content_format", "unknown")
            format_distribution[fmt] = format_distribution.get(fmt, 0) + 1
        
        return {
            "overall_quality_assessment": {
                "average_quality_score": round(avg_quality, 1),
                "quality_tier_distribution": quality_tiers,
                "recommendations": self._generate_quality_recommendations(quality_tiers, avg_quality)
            },
            "content_strategy_insights": {
                "format_distribution": format_distribution,
                "recommended_mix": "Balanced approach with emphasis on how-to guides and listicles",
                "content_pillars": list(set([
                    kw for idea in ideas 
                    for kw in (idea.get("primary_keywords", []) or [])[:2]
                ]))[:5]
            },
            "implementation_recommendations": [
                "Start with highest-scoring ideas for immediate impact",
                "Focus on beginner-level content for quick wins",
                "Develop content series around top keywords",
                "Create comprehensive guides for authority building",
                "Optimize for featured snippets and SEO"
            ],
            "business_impact_analysis": {
                "high_business_impact_count": len([i for i in ideas if i.get("business_impact_score", 0) >= 80]),
                "lead_generation_potential": "High" if avg_quality >= 75 else "Medium",
                "authority_building_score": round(avg_quality * 0.9, 1),
                "competitive_advantage": "Strong content foundation with diverse formats"
            }
        }

    def _generate_quality_recommendations(self, quality_tiers: Dict[str, int], avg_quality: float) -> List[str]:
        """Generate quality-based recommendations"""
        
        recommendations = []
        
        if avg_quality >= 80:
            recommendations.append("Excellent quality foundation - proceed with confidence")
        elif avg_quality >= 70:
            recommendations.append("Good quality base - minor optimizations recommended")
        else:
            recommendations.append("Consider regenerating or optimizing lower-scoring ideas")
        
        if quality_tiers["excellent"] >= 5:
            recommendations.append("Strong set of high-impact ideas for immediate implementation")
        
        if quality_tiers["needs_work"] > quality_tiers["excellent"]:
            recommendations.append("Focus on improving lower-quality ideas before implementation")
        
        return recommendations

    def _calculate_success_predictions(self, ideas: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate success predictions for the idea set"""
        
        total_ideas = len(ideas)
        high_quality_count = len([i for i in ideas if i.get("overall_quality_score", 0) >= 80])
        viral_potential_count = len([i for i in ideas if i.get("viral_potential_score", 0) >= 80])
        seo_optimized_count = len([i for i in ideas if i.get("seo_optimization_score", 0) >= 80])
        
        # Success probability calculation
        quality_factor = high_quality_count / total_ideas if total_ideas > 0 else 0
        viral_factor = viral_potential_count / total_ideas if total_ideas > 0 else 0
        seo_factor = seo_optimized_count / total_ideas if total_ideas > 0 else 0
        
        overall_success_probability = (quality_factor * 0.4 + viral_factor * 0.3 + seo_factor * 0.3) * 100
        
        return {
            "overall_success_probability": round(overall_success_probability, 1),
            "traffic_growth_prediction": {
                "expected_increase": f"{round(seo_factor * 100)}% increase in organic traffic",
                "timeline": "3-6 months for full impact",
                "high_impact_ideas": high_quality_count
            },
            "engagement_predictions": {
                "viral_potential_ideas": viral_potential_count,
                "expected_social_shares": round(viral_factor * total_ideas * 50),
                "engagement_rate_estimate": f"{round(viral_factor * 8, 1)}%"
            },
            "business_impact_forecast": {
                "lead_generation_potential": "High" if quality_factor >= 0.6 else "Medium",
                "authority_building_timeline": "6-12 months",
                "roi_expectation": "3:1 within 12 months" if overall_success_probability >= 70 else "2:1 within 18 months"
            },
            "risk_assessment": {
                "implementation_risk_level": "Low" if quality_factor >= 0.7 else "Medium",
                "content_quality_risk": "Low" if high_quality_count >= 10 else "Medium",
                "market_fit_confidence": round((quality_factor + viral_factor) * 50, 1),
                "recommended_monitoring": [
                    "Track organic traffic growth monthly",
                    "Monitor social engagement rates", 
                    "Measure lead generation conversion",
                    "Assess brand authority metrics"
                ]
            },
            "optimization_opportunities": [
                "Focus on SEO optimization for lower-scoring ideas",
                "Develop content series from high-performing topics",
                "Create pillar content around top keywords",
                "Implement structured data for featured snippets"
            ] if overall_success_probability < 80 else [
                "Maintain current quality standards",
                "Scale content production gradually",
                "Develop advanced content formats",
                "Build thought leadership positioning"
            ]
        }

    def _safe_parse_json_field(self, data, field_name, default=None):
        """Safely parse JSON field that might be string or already parsed - IMPROVED"""
        if not data:
            return default if default is not None else {}
        
        field_value = data.get(field_name) if isinstance(data, dict) else None
        
        if field_value is None:
            return default if default is not None else {}
        
        # Already parsed
        if isinstance(field_value, (dict, list)):
            return field_value
        
        # Try to parse string as JSON
        if isinstance(field_value, str):
            try:
                parsed = json.loads(field_value)
                return parsed
            except (json.JSONDecodeError, ValueError, TypeError):
                self.logger.warning(f"Failed to parse JSON field '{field_name}': {field_value[:100]}...")
                return default if default is not None else {}
        
        # For any other type, return default
        self.logger.warning(f"Unexpected type for field '{field_name}': {type(field_value)}")
        return default if default is not None else {}

    def _calculate_topic_priority(self, viral_potential: int) -> str:
        """Calculate topic priority level"""
        if viral_potential >= 80:
            return "High"
        elif viral_potential >= 60:
            return "Medium"
        else:
            return "Low"
    
    

    async def generate_comprehensive_blog_ideas(
        self,
        analysis_id: str,
        user_id: str,
        llm_config: Dict[str, Any],
        generation_config: Dict[str, Any] = None,
        linkup_api_key: Optional[str] = None  # ADD THIS LINE
    ) -> Dict[str, Any]:
        """
        ENHANCED: Main method to generate comprehensive blog ideas with optional Linkup research
        """
        
        self.logger.info(f"🚀 Starting blog idea generation for analysis: {analysis_id}")
        if linkup_api_key:  # ADD THIS LINE
            self.logger.info("📡 Linkup research enabled")  # ADD THIS LINE
        
        start_time = time.time()
        
        try:
            # Step 1: Load Phase 1 strategic context
            self.logger.info("📊 Loading Phase 1 strategic context...")
            context = await self._load_phase1_strategic_context(analysis_id, user_id)
            
            # ADD THESE LINES AFTER STEP 1:
            # Step 2: ENHANCED - Optional Linkup Research
            if linkup_api_key:
                self.logger.info("🔍 Conducting Linkup research...")
                try:
                    context = await self._enhance_context_with_linkup_research(
                        context, linkup_api_key, llm_config
                    )
                except Exception as e:
                    self.logger.warning(f"⚠️ Linkup research failed: {e}, continuing without enhancement")
            
            # Step 2: Initialize LLM client (CHANGE TO STEP 3)
            llm_client = self._initialize_llm_client(llm_config)
            
            # Step 3: Generate ideas from multiple sources (CHANGE TO STEP 4)
            self.logger.info("💡 Generating ideas from trending topics...")
            trending_ideas = await self._generate_from_trending_topics(context, llm_client, llm_config)
            
            self.logger.info("🎯 Generating ideas from content opportunities...")
            opportunity_ideas = await self._generate_from_opportunities(context, llm_client, llm_config)
            
            self.logger.info("📈 Generating ideas from PyTrends insights...")
            pytrends_ideas = await self._generate_from_pytrends_data(context, llm_client, llm_config)
            
            self.logger.info("🔑 Generating ideas from keyword clusters...")
            keyword_ideas = await self._generate_from_keyword_clusters(context, llm_client, llm_config)
            
            # Step 4: Combine and deduplicate ideas (CHANGE TO STEP 5)
            all_ideas = trending_ideas + opportunity_ideas + pytrends_ideas + keyword_ideas
            unique_ideas = self._deduplicate_ideas(all_ideas)

            # CRITICAL FIX: Calculate all scores before optimization (CHANGE TO STEP 6)
            self.logger.info("🔢 Calculating idea scores...")
            scored_ideas = self._calculate_all_idea_scores(unique_ideas, context)

            # Step 5: Optimize ideas for SEO and engagement (CHANGE TO STEP 7)
            self.logger.info("⚡ Optimizing ideas for SEO and engagement...")
            optimized_ideas = await self._optimize_ideas_for_seo_and_engagement(scored_ideas, context)
            
            # Step 6: Final scoring and ranking (CHANGE TO STEP 8)
            self.logger.info("📊 Final scoring and ranking...")
            final_scored_ideas = self._score_and_rank_ideas(optimized_ideas)
            
            # Step 7: Select top ideas based on target range (CHANGE TO STEP 9)
            final_ideas = self._select_optimal_idea_set(final_scored_ideas, generation_config)
            
            # Step 8: Generate content calendar recommendations (CHANGE TO STEP 10)
            self.logger.info("📅 Generating content calendar...")
            content_calendar = self._generate_content_calendar(final_ideas, context)
            
            # Step 9: Calculate success metrics and insights (CHANGE TO STEP 11)
            strategic_insights = self._generate_strategic_insights(final_ideas, context)
            success_predictions = self._calculate_success_predictions(final_ideas, context)
            
            processing_time = time.time() - start_time
            
            result = {
                "blog_ideas": final_ideas,
                "content_calendar": content_calendar,
                "strategic_insights": strategic_insights,
                "success_predictions": success_predictions,
                "generation_metadata": {
                    "analysis_id": analysis_id,
                    "user_id": user_id,
                    "total_ideas_generated": len(final_ideas),
                    "average_quality_score": sum(idea["overall_quality_score"] for idea in final_ideas) / len(final_ideas),
                    "processing_time_seconds": round(processing_time, 2),
                    "generation_timestamp": datetime.now().isoformat(),
                    "llm_provider": llm_config.get("provider"),
                    "phase1_context_loaded": bool(context),
                    "ideas_by_source": {
                        "trending_topics": len(trending_ideas),
                        "content_opportunities": len(opportunity_ideas), 
                        "pytrends_insights": len(pytrends_ideas),
                        "keyword_clusters": len(keyword_ideas)
                    }
                }
            }

            if linkup_api_key and context.get('linkup_research'):
                result['linkup_insights'] = context['linkup_research']
                result['generation_metadata']['linkup_research_conducted'] = True
                result['generation_metadata']['linkup_searches_analyzed'] = context['linkup_research'].get('search_results_analyzed', 0)
            else:
                result['generation_metadata']['linkup_research_conducted'] = False
            
            self.logger.info(f"✅ Blog idea generation completed: {len(final_ideas)} ideas in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Blog idea generation failed: {e}")
            raise
            

    def _calculate_all_idea_scores(self, ideas: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        CRITICAL FIX: Calculate ALL scoring metrics for each idea before saving
        """
        
        self.logger.info(f"🔢 Calculating scores for {len(ideas)} ideas...")
        
        scored_ideas = []
        
        for idea in ideas:
            try:
                # Calculate all individual scores
                viral_score = self._calculate_viral_potential_score(idea, context)
                seo_score = self._calculate_seo_optimization_score(idea, context)
                audience_score = self._calculate_audience_alignment_score(idea, context)
                feasibility_score = self._calculate_content_feasibility_score(idea, context)
                business_score = self._calculate_business_impact_score(idea, context)
                
                # Calculate overall quality score
                overall_score = (
                    viral_score * self.SCORING_WEIGHTS["viral_potential"] +
                    seo_score * self.SCORING_WEIGHTS["seo_optimization"] +
                    audience_score * self.SCORING_WEIGHTS["audience_alignment"] +
                    feasibility_score * self.SCORING_WEIGHTS["content_feasibility"] +
                    business_score * self.SCORING_WEIGHTS["business_impact"]
                )
                
                # Add all scores to the idea
                idea.update({
                    "viral_potential_score": int(viral_score),
                    "seo_optimization_score": int(seo_score),
                    "audience_alignment_score": int(audience_score),
                    "content_feasibility_score": int(feasibility_score),
                    "business_impact_score": int(business_score),
                    "overall_quality_score": int(overall_score)
                })
                
                scored_ideas.append(idea)
                
            except Exception as e:
                self.logger.warning(f"Failed to score idea {idea.get('title', 'Unknown')}: {e}")
                # Add default scores if calculation fails
                idea.update({
                    "viral_potential_score": 50,
                    "seo_optimization_score": 50,
                    "audience_alignment_score": 50,
                    "content_feasibility_score": 50,
                    "business_impact_score": 50,
                    "overall_quality_score": 50
                })
                scored_ideas.append(idea)
        
        self.logger.info(f"✅ Calculated scores for {len(scored_ideas)} ideas")
        return scored_ideas

    def _calculate_viral_potential_score(self, idea: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate viral potential score (0-100)"""
        
        score = 50  # Base score
        
        # Source viral potential
        source_viral = idea.get("source_viral_potential", 50)
        score += (source_viral - 50) * 0.3
        
        # Content format viral factor
        content_format = idea.get("content_format", "how_to_guide")
        format_data = self.CONTENT_FORMATS.get(content_format, {})
        engagement_factor = format_data.get("engagement_factor", 0.80)
        score += (engagement_factor - 0.80) * 50
        
        # Trending topic bonus
        if idea.get("source_type") == "trending_topic":
            score += 15
        
        # PyTrends data bonus
        if idea.get("source_type") in ["geographic_insights", "rising_queries"]:
            score += 10
        
        # Title engagement factors
        title = idea.get("title", "").lower()
        if any(word in title for word in ["ultimate", "complete", "secret", "mistake", "hack"]):
            score += 8
        
        if any(word in title for word in ["how to", "guide", "step by step"]):
            score += 5
        
        return max(0, min(100, score))

    def _calculate_seo_optimization_score(self, idea: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate SEO optimization score (0-100)"""
        
        score = 40  # Base score
        
        # Keyword optimization
        primary_keywords = idea.get("primary_keywords", [])
        secondary_keywords = idea.get("secondary_keywords", [])
        
        if len(primary_keywords) >= 2:
            score += 15
        if len(secondary_keywords) >= 5:
            score += 10
        
        # Title optimization
        title = idea.get("title", "")
        if 50 <= len(title) <= 70:
            score += 10
        
        # Featured snippet opportunity
        if idea.get("featured_snippet_opportunity", False):
            score += 15
        
        # Content length optimization
        word_count = idea.get("estimated_word_count", 0)
        if 2000 <= word_count <= 4000:
            score += 10
        elif word_count >= 1500:
            score += 5
        
        return max(0, min(100, score))

    def _calculate_audience_alignment_score(self, idea: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate audience alignment score (0-100)"""
        
        score = 50  # Base score
        
        target_audience = context.get("research_context", {}).get("target_audience", "professional")
        difficulty_level = idea.get("difficulty_level", "intermediate")
        
        # Audience-difficulty alignment
        alignment_map = {
            "professional": {"intermediate": 15, "advanced": 10, "beginner": 5},
            "entrepreneur": {"beginner": 15, "intermediate": 10, "advanced": 5},
            "small_business": {"beginner": 15, "intermediate": 8, "advanced": 3},
            "student": {"beginner": 15, "intermediate": 12, "advanced": 8}
        }
        
        alignment_bonus = alignment_map.get(target_audience, {}).get(difficulty_level, 0)
        score += alignment_bonus
        
        # Content format alignment
        content_format = idea.get("content_format", "")
        if target_audience == "professional" and content_format in ["case_study", "trend_analysis"]:
            score += 10
        elif target_audience in ["entrepreneur", "small_business"] and content_format in ["how_to_guide", "beginner_guide"]:
            score += 10
        
        return max(0, min(100, score))

    def _calculate_content_feasibility_score(self, idea: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate content feasibility score (0-100)"""
        
        score = 60  # Base score
        
        # Word count feasibility
        word_count = idea.get("estimated_word_count", 2500)
        if word_count <= 2000:
            score += 15  # Easier to produce
        elif word_count <= 3000:
            score += 10
        elif word_count <= 4000:
            score += 5
        else:
            score -= 5  # Harder to produce
        
        # Difficulty level impact
        difficulty = idea.get("difficulty_level", "intermediate")
        difficulty_scores = {"beginner": 15, "intermediate": 10, "advanced": 5}
        score += difficulty_scores.get(difficulty, 10)
        
        # Outline completeness
        outline = idea.get("outline", [])
        if len(outline) >= 5:
            score += 10
        elif len(outline) >= 3:
            score += 5
        
        return max(0, min(100, score))

    def _calculate_business_impact_score(self, idea: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate business impact score (0-100)"""
        
        score = 50  # Base score
        
        # Business value assessment
        business_value = idea.get("business_value", "").lower()
        if any(word in business_value for word in ["lead generation", "conversion", "sales"]):
            score += 15
        
        if any(word in business_value for word in ["authority", "thought leadership", "brand"]):
            score += 10
        
        # Call to action strength
        cta = idea.get("call_to_action", "")
        if cta and len(cta) > 20:
            score += 10
        
        # Content format business impact
        content_format = idea.get("content_format", "")
        business_impact_map = {
            "case_study": 15,
            "how_to_guide": 12,
            "comparison": 12,
            "tool_review": 10,
            "beginner_guide": 8,
            "listicle": 8,
            "trend_analysis": 6
        }
        score += business_impact_map.get(content_format, 5)
        
        return max(0, min(100, score))

    # [Include all other methods from the original file - they remain the same]
    # For brevity, I'm including just the key methods that needed fixes

    async def _load_phase1_strategic_context(self, analysis_id: str, user_id: str) -> Dict[str, Any]:
        """Load comprehensive Phase 1 context for idea generation"""
        
        try:
            supabase_storage = RLSSupabaseStorage()
            
            # Get enhanced Phase 2 data (your existing method)
            phase1_data = await supabase_storage.get_selected_data_for_phase2(analysis_id, user_id)
            
            # Extract PyTrends data from analysis metadata
            analysis_info = phase1_data.get("analysis_info", {})
            metadata = analysis_info.get("metadata", {})
            pytrends_data = metadata.get("pytrends_analysis", {})
            
            # Build comprehensive context
            context = {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "research_context": phase1_data.get("research_context", {}),
                "selected_trending_topics": phase1_data.get("selected_trending_topics", []),
                "selected_opportunities": phase1_data.get("selected_opportunities", []),
                "keyword_intelligence": phase1_data.get("keyword_intelligence", {}),
                "pytrends_insights": pytrends_data,
                "phase2_enhancements": phase1_data.get("phase2_enhancements", {}),
                "blog_idea_generation_config": phase1_data.get("blog_idea_generation_config", {}),
                "strategic_intelligence_summary": phase1_data.get("strategic_intelligence_summary", {})
            }
            
            self.logger.info(f"📊 Loaded context: {len(context['selected_trending_topics'])} topics, {len(context['selected_opportunities'])} opportunities")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to load Phase 1 context: {e}")
            raise

    def _score_and_rank_ideas(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score and rank blog ideas by overall quality - FIXED VERSION"""
        
        try:
            scored_ideas = []
            
            for idea in ideas:
                try:
                    # FIXED: Safe access to all score fields with defaults
                    viral_score = float(idea.get('viral_potential_score', 0))
                    seo_score = float(idea.get('seo_optimization_score', 0))
                    audience_score = float(idea.get('audience_alignment_score', 0))
                    feasibility_score = float(idea.get('content_feasibility_score', 0))
                    business_score = float(idea.get('business_impact_score', 0))
                    
                    # Calculate weighted overall score
                    overall_score = (
                        viral_score * 0.25 +
                        seo_score * 0.25 +
                        audience_score * 0.20 +
                        feasibility_score * 0.15 +
                        business_score * 0.15
                    )
                    
                    idea['overall_quality_score'] = int(overall_score)
                    scored_ideas.append(idea)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to score idea {idea.get('title', 'Unknown')}: {e}")
                    # Add with default score
                    idea['overall_quality_score'] = 50
                    scored_ideas.append(idea)
            
            # Sort by overall quality score (highest first)
            ranked_ideas = sorted(scored_ideas, key=lambda x: x.get('overall_quality_score', 0), reverse=True)
            
            self.logger.info(f"📊 Scored and ranked {len(ranked_ideas)} ideas")
            
            return ranked_ideas
            
        except Exception as e:
            self.logger.error(f"Failed to score and rank ideas: {e}")
            # Return original ideas with default scores
            for idea in ideas:
                if 'overall_quality_score' not in idea:
                    idea['overall_quality_score'] = 50
            return ideas

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
                timeout=60.0
            )
            return client
            
        elif provider == 'anthropic':
            import anthropic
            client = anthropic.AsyncAnthropic(
                api_key=api_key,
                timeout=60.0
            )
            return client
            
        elif provider == 'kimi':
            import openai
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.moonshot.ai/v1",
                timeout=60.0
            )
            return client
            
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    # Additional methods would go here - keeping the same logic from original
    # Just the scoring calculation was the main issue that needed fixing

#################
    def _safe_parse_json_field(self, data, field_name, default=None):
        """Safely parse JSON field that might be string or already parsed"""
        if not data:
            return default if default is not None else {}
        
        field_value = data.get(field_name) if isinstance(data, dict) else None
        
        if field_value is None:
            return default if default is not None else {}
        
        if isinstance(field_value, dict) or isinstance(field_value, list):
            return field_value  # Already parsed
        
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except (json.JSONDecodeError, ValueError):
                self.logger.warning(f"Failed to parse JSON field '{field_name}': {field_value}")
                return default if default is not None else {}
        
        return default if default is not None else {}

    def _optimize_idea_for_seo_and_engagement(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize individual blog idea for SEO and engagement"""
        
        try:
            optimized_idea = idea.copy()
            
            # Safe access to idea fields
            title = str(idea.get('title', ''))
            description = str(idea.get('description', ''))
            
            # Safe parsing of keywords (handle both string and list)
            primary_keywords = idea.get('primary_keywords', [])
            if isinstance(primary_keywords, str):
                try:
                    import json
                    primary_keywords = json.loads(primary_keywords)
                except:
                    primary_keywords = [primary_keywords] if primary_keywords else []
            
            # Title optimization
            if title and len(title) < 50:
                if '2025' not in title:
                    optimized_idea['title'] = f"{title} (2025 Guide)"
            
            # SEO optimization
            seo_score = int(idea.get('seo_optimization_score', 0))
            if primary_keywords and len(primary_keywords) > 0:
                seo_score = min(100, seo_score + 10)
                
                # Check if primary keyword is in title
                primary_kw = str(primary_keywords[0]).lower() if primary_keywords else ''
                if primary_kw and primary_kw in title.lower():
                    seo_score = min(100, seo_score + 5)
            
            optimized_idea['seo_optimization_score'] = seo_score
            
            # Engagement optimization
            engagement_score = int(idea.get('viral_potential_score', 0))
            
            # Boost for trending keywords
            trending_indicators = ['2025', 'latest', 'new', 'trending', 'best', 'ultimate', 'complete']
            if title and any(indicator in title.lower() for indicator in trending_indicators):
                engagement_score = min(100, engagement_score + 5)
            
            optimized_idea['viral_potential_score'] = engagement_score
            
            # Featured snippet optimization
            if title and any(title.lower().startswith(q) for q in ['what is', 'how to', 'why']):
                optimized_idea['featured_snippet_opportunity'] = True
            
            return optimized_idea
            
        except Exception as e:
            self.logger.warning(f"Failed to optimize idea {idea.get('title', 'Unknown')}: {e}")
            return idea  # Return original idea if optimization fails

    def _enhance_idea_with_performance_estimates(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Add performance estimates to blog idea - FIXED VERSION"""
        
        try:
            enhanced_idea = idea.copy()
            
            # FIXED: Safe access to scores
            viral_score = idea.get('viral_potential_score', 0)
            seo_score = idea.get('seo_optimization_score', 0)
            business_score = idea.get('business_impact_score', 0)
            difficulty = idea.get('difficulty_level', 'intermediate')
            
            # Estimate traffic based on SEO score
            if seo_score >= 80:
                estimated_traffic = 1000 + (viral_score * 10)
            elif seo_score >= 60:
                estimated_traffic = 500 + (viral_score * 5)
            else:
                estimated_traffic = 200 + (viral_score * 2)
            
            # Estimate social shares based on viral potential
            estimated_shares = max(5, viral_score // 2)
            
            # Estimate time to rank based on competition and SEO
            difficulty_multiplier = {'beginner': 1.0, 'intermediate': 1.2, 'advanced': 1.5, 'expert': 2.0}
            base_weeks = 8
            time_to_rank = int(base_weeks * difficulty_multiplier.get(difficulty, 1.2) * (100 - seo_score) / 100 + 4)
            
            # Estimate backlink potential based on quality
            overall_quality = idea.get('overall_quality_score', 0)
            backlink_potential = max(1, overall_quality // 20)
            
            performance_estimates = {
                "viral_potential_score": viral_score,
                "traffic_potential_score": min(100, int(estimated_traffic / 20)),
                "conversion_potential_score": business_score,
                "estimated_time_to_rank_weeks": max(4, time_to_rank),
                "estimated_monthly_traffic": int(estimated_traffic),
                "estimated_social_shares": int(estimated_shares),
                "estimated_backlink_potential": int(backlink_potential)
            }
            
            enhanced_idea['performance_estimates'] = performance_estimates
            
            return enhanced_idea
            
        except Exception as e:
            self.logger.warning(f"Failed to enhance idea with performance estimates: {e}")
            return idea

    def _score_and_rank_ideas(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score and rank blog ideas by overall quality - FIXED VERSION"""
        
        try:
            scored_ideas = []
            
            for idea in ideas:
                try:
                    # FIXED: Safe access to all score fields
                    viral_score = float(idea.get('viral_potential_score', 0))
                    seo_score = float(idea.get('seo_optimization_score', 0))
                    audience_score = float(idea.get('audience_alignment_score', 0))
                    feasibility_score = float(idea.get('content_feasibility_score', 0))
                    business_score = float(idea.get('business_impact_score', 0))
                    
                    # Calculate weighted overall score
                    overall_score = (
                        viral_score * 0.25 +
                        seo_score * 0.25 +
                        audience_score * 0.20 +
                        feasibility_score * 0.15 +
                        business_score * 0.15
                    )
                    
                    idea['overall_quality_score'] = int(overall_score)
                    scored_ideas.append(idea)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to score idea {idea.get('title', 'Unknown')}: {e}")
                    # Add with default score
                    idea['overall_quality_score'] = 50
                    scored_ideas.append(idea)
            
            # Sort by overall quality score (highest first)
            ranked_ideas = sorted(scored_ideas, key=lambda x: x.get('overall_quality_score', 0), reverse=True)
            
            self.logger.info(f"📊 Scored and ranked {len(ranked_ideas)} ideas")
            
            return ranked_ideas
            
        except Exception as e:
            self.logger.error(f"Failed to score and rank ideas: {e}")
            # Return original ideas with default scores
            for idea in ideas:
                if 'overall_quality_score' not in idea:
                    idea['overall_quality_score'] = 50
            return ideas
        ##############

    def _calculate_all_idea_scores(self, ideas: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        CRITICAL FIX: Calculate ALL scoring metrics for each idea before saving
        ADD THIS METHOD TO YOUR BlogIdeaGenerationEngine CLASS
        """
        
        self.logger.info(f"🔢 Calculating scores for {len(ideas)} ideas...")
        
        scored_ideas = []
        
        for idea in ideas:
            try:
                # Calculate all individual scores
                viral_score = self._calculate_viral_potential_score(idea, context)
                seo_score = self._calculate_seo_optimization_score(idea, context)
                audience_score = self._calculate_audience_alignment_score(idea, context)
                feasibility_score = self._calculate_content_feasibility_score(idea, context)
                business_score = self._calculate_business_impact_score(idea, context)
                
                # Calculate overall quality score
                overall_score = (
                    viral_score * self.SCORING_WEIGHTS["viral_potential"] +
                    seo_score * self.SCORING_WEIGHTS["seo_optimization"] +
                    audience_score * self.SCORING_WEIGHTS["audience_alignment"] +
                    feasibility_score * self.SCORING_WEIGHTS["content_feasibility"] +
                    business_score * self.SCORING_WEIGHTS["business_impact"]
                )
                
                # Add all scores to the idea
                idea.update({
                    "viral_potential_score": int(viral_score),
                    "seo_optimization_score": int(seo_score),
                    "audience_alignment_score": int(audience_score),
                    "content_feasibility_score": int(feasibility_score),
                    "business_impact_score": int(business_score),
                    "overall_quality_score": int(overall_score)
                })
                
                # Log the scores for verification
                self.logger.debug(f"Scored '{idea.get('title', 'Unknown')}': "
                                f"Overall={int(overall_score)}, "
                                f"Viral={int(viral_score)}, "
                                f"SEO={int(seo_score)}, "
                                f"Audience={int(audience_score)}, "
                                f"Feasibility={int(feasibility_score)}, "
                                f"Business={int(business_score)}")
                
                scored_ideas.append(idea)
                
            except Exception as e:
                self.logger.warning(f"Failed to score idea {idea.get('title', 'Unknown')}: {e}")
                # Add default scores if calculation fails
                idea.update({
                    "viral_potential_score": 50,
                    "seo_optimization_score": 50,
                    "audience_alignment_score": 50,
                    "content_feasibility_score": 50,
                    "business_impact_score": 50,
                    "overall_quality_score": 50
                })
                scored_ideas.append(idea)
        
        self.logger.info(f"✅ Calculated scores for {len(scored_ideas)} ideas")
        return scored_ideas


    #########################
    def _calculate_topic_priority(self, viral_potential: int) -> str:
        """Calculate topic priority level"""
        if viral_potential >= 80:
            return "High"
        elif viral_potential >= 60:
            return "Medium"
        else:
            return "Low"
    
    async def _enhance_context_with_linkup_research(
        self,
        context: Dict[str, Any], 
        linkup_api_key: str,
        llm_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance context with Linkup research"""
        
        try:
            # Initialize Linkup researcher
            linkup_config = {
                'max_searches': 8,
                'results_per_search': 10,
                'search_timeout': 30,
                'rate_limit_delay': 1.5
            }
            
            linkup_researcher = LinkupResearcher(linkup_api_key, linkup_config)
            
            # Get selected data for research
            selected_topics = context.get('selected_trending_topics', [])
            selected_opportunities = context.get('selected_opportunities', [])
            
            if not selected_topics and not selected_opportunities:
                self.logger.warning("⚠️ No selected topics/opportunities for Linkup research")
                return context
            
            # Conduct research with timeout
            self.logger.info(f"🔍 Starting Linkup research: {len(selected_topics)} topics, {len(selected_opportunities)} opportunities")
            
            linkup_research = await asyncio.wait_for(
                linkup_researcher.research_content_gaps(selected_topics, selected_opportunities),
                timeout=90  # 1.5 minute timeout
            )
            
            # Enhance context with research
            context['linkup_research'] = linkup_research
            context['research_enhanced'] = True
            
            # Log results
            gaps_found = linkup_research.get('total_gaps_identified', 0)
            searches_conducted = linkup_research.get('search_results_analyzed', 0)
            confidence_score = linkup_research.get('research_confidence_score', 0)
            
            self.logger.info(f"✅ Linkup research completed:")
            self.logger.info(f"   📊 {searches_conducted} searches analyzed")
            self.logger.info(f"   🔍 {gaps_found} content gaps identified") 
            self.logger.info(f"   🎯 {confidence_score}% research confidence")
            
            return context
            
        except asyncio.TimeoutError:
            self.logger.warning("⚠️ Linkup research timed out, continuing without enhancement")
            return context
        except Exception as e:
            self.logger.warning(f"⚠️ Linkup research failed: {e}, continuing without enhancement")
            return context


# Usage example and testing
if __name__ == "__main__":
    import argparse
    import os
    
    async def test_blog_idea_generation():
        """Test the blog idea generation engine"""
        
        # Test configuration
        llm_config = {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'api_key': os.getenv('OPENAI_API_KEY')
        }
        
        if not llm_config['api_key']:
            print("❌ OPENAI_API_KEY environment variable not set")
            return
        
        # Initialize engine
        engine = BlogIdeaGenerationEngine()
        
        # Test with sample analysis ID (replace with real ID)
        test_analysis_id = "your-test-analysis-id"
        test_user_id = "your-test-user-id"
        
        try:
            print("🚀 Testing blog idea generation...")
            
            result = await engine.generate_comprehensive_blog_ideas(
                analysis_id=test_analysis_id,
                user_id=test_user_id,
                llm_config=llm_config
            )
            
            print("✅ Generation completed successfully!")
            print(f"📊 Generated {len(result['blog_ideas'])} blog ideas")
            print(f"⭐ Average quality score: {result['generation_metadata']['average_quality_score']}")
            print(f"⏱️ Processing time: {result['generation_metadata']['processing_time_seconds']}s")
            
            # Print sample ideas
            print("\n🎯 Top 3 Blog Ideas:")
            for i, idea in enumerate(result['blog_ideas'][:3], 1):
                print(f"{i}. {idea['title']} (Score: {idea['overall_quality_score']})")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    # Command line interface
    parser = argparse.ArgumentParser(description="Blog Idea Generation Engine")
    parser.add_argument('--test', action='store_true', help='Run test generation')
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_blog_idea_generation())
    else:
        print("Blog Idea Generation Engine - Phase 2")
        print("Key features:")
        print("- ✅ Multi-source idea generation (trending topics, opportunities, PyTrends, keywords)")
        print("- ✅ Comprehensive SEO and engagement optimization")
        print("- ✅ Multi-factor quality scoring and ranking")
        print("- ✅ Content calendar generation")
        print("- ✅ Strategic insights and success predictions")
        print("- ✅ Diverse content format support")
        print("- ✅ 20-50 high-quality ideas per analysis")
        print("")
        print("Usage: python blog_idea_generator.py --test")