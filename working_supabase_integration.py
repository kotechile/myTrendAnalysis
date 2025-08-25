#!/usr/bin/env python3
"""
RLS-Compatible Supabase Integration - Updated for user_id support
Bypasses Supabase 2.16.0 http_client issue while supporting Row Level Security
"""

import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add this method to your working_supabase_integration.py class:

async def get_trend_analysis_for_phase2(self, trend_analysis_id: str, user_id: str) -> Dict[str, Any]:
    """Retrieve trend analysis data for Phase 2 with PyTrends data"""
    
    self.set_user_context(user_id)
    
    try:
        # Get main analysis (filtered by user_id)
        result = self._execute_query('GET', f'trend_analyses?id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
        
        if not result['success']:
            raise Exception(f"Failed to get trend analysis: {result.get('error')}")
        
        if not result['data']:
            raise Exception(f"Trend analysis {trend_analysis_id} not found or access denied")
        
        analysis = result['data'][0]
        
        # Get other data with user filtering
        trending_topics = []
        content_opportunities = []
        keyword_intelligence = {}
        
        try:
            topics_result = self._execute_query('GET', f'trending_topics?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
            if topics_result['success']:
                trending_topics = topics_result['data']
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get trending topics: {e}")
        
        try:
            opps_result = self._execute_query('GET', f'content_opportunities?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
            if opps_result['success']:
                content_opportunities = opps_result['data']
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get content opportunities: {e}")
        
        try:
            keywords_result = self._execute_query('GET', f'keyword_intelligence?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
            if keywords_result['success'] and keywords_result['data']:
                keyword_intelligence = keywords_result['data'][0]
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get keyword intelligence: {e}")
        
        # CRITICAL FIX: Extract PyTrends data from metadata
        metadata = analysis.get('metadata', {})
        pytrends_data = metadata.get('pytrends_analysis', {})
        
        # Log PyTrends data availability
        if pytrends_data:
            self.logger.info(f"✅ PyTrends data found in metadata for analysis {trend_analysis_id}")
            self.logger.info(f"📊 Geographic hotspots: {len(pytrends_data.get('geographic_insights', {}).get('global_hotspots', []))}")
            self.logger.info(f"💡 Actionable insights: {len(pytrends_data.get('actionable_insights', []))}")
        else:
            self.logger.warning(f"⚠️ No PyTrends data found for analysis {trend_analysis_id}")
        
        return {
            "trend_analysis_id": trend_analysis_id,
            "analysis_info": analysis,
            "trending_topics": trending_topics,
            "content_opportunities": content_opportunities,
            "keyword_intelligence": keyword_intelligence,
            # FIXED: Include PyTrends data from metadata
            "pytrends_analysis": pytrends_data,
            "pytrends_enhanced": pytrends_data.get('pytrends_enhanced', False),
            "pytrends_available": bool(pytrends_data)
        }
        
    except Exception as e:
        self.logger.error(f"Error retrieving trend analysis: {e}")
        raise


# Add this method to ensure PyTrends data is properly stored
async def save_trend_analysis_results(
    self, 
    trend_result: Dict[str, Any],
    user_id: str,
    topic: str = "",
    target_audience: str = "",
    focus_area: str = ""
) -> str:
    """Save complete trend analysis results with PyTrends data"""
    
    if not user_id:
        raise ValueError("user_id is required for RLS")
    
    # Set user context
    self.set_user_context(user_id)
    
    try:
        self.logger.info(f"💾 Saving trend analysis results for user {user_id}, topic: {topic}")
        
        # Extract PyTrends data for metadata storage
        pytrends_data = trend_result.get('pytrends_analysis', {})
        
        # Enhanced metadata with PyTrends data
        enhanced_metadata = {
            'confidence_score': trend_result.get('confidence_score', 85),
            'enhanced_research': trend_result.get('enhanced_trend_research', False),
            'strategic_intelligence': trend_result.get('strategic_intelligence', False),
            'data_sources': trend_result.get('data_sources', []),
            'processing_time': trend_result.get('processing_time', 0),
            'trending_topics_count': len(trend_result.get('trending_topics', [])),
            'opportunities_count': len(trend_result.get('content_opportunities', [])),
            # CRITICAL: Store PyTrends data in metadata
            'pytrends_analysis': pytrends_data,
            'pytrends_enhanced': pytrends_data.get('pytrends_enhanced', False),
            'pytrends_timestamp': pytrends_data.get('analysis_timestamp'),
            'geographic_hotspots_count': len(pytrends_data.get('geographic_insights', {}).get('global_hotspots', [])),
            'actionable_insights_count': len(pytrends_data.get('actionable_insights', []))
        }
        
        # Step 1: Create main trend analysis record with enhanced metadata
        trend_analysis_id = await self._create_trend_analysis_record_rls(
            user_id=user_id,
            topic=topic,
            target_audience=target_audience,
            focus_area=focus_area,
            metadata=enhanced_metadata
        )
        
        # Log PyTrends data storage
        if pytrends_data:
            self.logger.info(f"✅ PyTrends data stored in metadata for analysis {trend_analysis_id}")
        else:
            self.logger.warning(f"⚠️ No PyTrends data to store for analysis {trend_analysis_id}")
        
        # Steps 2-4: Save other data (existing code)
        if trend_result.get('trending_topics'):
            try:
                await self._save_trending_topics_rls(
                    trend_analysis_id, 
                    trend_result['trending_topics'],
                    user_id
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to save trending topics: {e}")
        
        if trend_result.get('content_opportunities'):
            try:
                await self._save_content_opportunities_rls(
                    trend_analysis_id,
                    trend_result['content_opportunities'],
                    user_id
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to save content opportunities: {e}")
        
        if trend_result.get('seo_intelligence'):
            try:
                await self._save_keyword_intelligence_rls(
                    trend_analysis_id,
                    trend_result['seo_intelligence'],
                    user_id
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to save keyword intelligence: {e}")

        self.logger.info(f"✅ Trend analysis saved with ID: {trend_analysis_id} for user: {user_id}")
        return trend_analysis_id
        
    except Exception as e:
        self.logger.error(f"❌ Failed to save trend analysis: {e}")
        raise

class RLSSupabaseStorage:
    """Supabase storage with Row Level Security support that bypasses 2.16.0 issues"""
    
    def __init__(self, user_id: Optional[str] = None):
        print("*****RLSSupabaseStorage - RLS Compatible with HTTP Workaround******")
        
        # Get credentials
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if not self.SUPABASE_URL or not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.logger = logging.getLogger(__name__)
        self.current_user_id = user_id
        
        # Setup HTTP session (bypasses Supabase client issues)
        import requests
        self.session = requests.Session()
        self.session.headers.update({
            'apikey': self.SUPABASE_KEY,
            'Authorization': f'Bearer {self.SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        })
        
        # Base URL for REST API
        self.rest_url = f"{self.SUPABASE_URL}/rest/v1"
        
        self.logger.info("✅ RLS Supabase client initialized (HTTP-based workaround)")
        
        # Test connection
        try:
            response = self.session.get(f"{self.rest_url}/trend_analyses?limit=1")
            if response.status_code in [200, 206]:
                self.logger.info("✅ Supabase connection test successful")
            else:
                self.logger.warning(f"⚠️ Connection test returned {response.status_code}")
        except Exception as e:
            self.logger.warning(f"⚠️ Connection test failed: {e}")

    def set_user_context(self, user_id: str):
        """Set user context for RLS operations"""
        if not user_id:
            raise ValueError("user_id cannot be None or empty")
        
        # Validate UUID format
        try:
            uuid.UUID(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id format: {user_id}. Must be a valid UUID.")
        
        self.current_user_id = user_id
        self.logger.debug(f"Set user context to: {user_id}")

    def _validate_user_context(self):
        """Ensure user context is set for RLS operations"""
        if not self.current_user_id:
            raise ValueError("User context not set. Call set_user_context(user_id) first.")

    def _execute_query(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Execute HTTP query to Supabase REST API with user context"""
        
        url = f"{self.rest_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check response
            if response.status_code in [200, 201, 204, 206]:
                try:
                    return {
                        'success': True,
                        'data': response.json() if response.content else [],
                        'status_code': response.status_code
                    }
                except:
                    return {
                        'success': True,
                        'data': [],
                        'status_code': response.status_code
                    }
            else:
                self.logger.error(f"HTTP Error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'status_code': response.status_code
                }
                
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'status_code': 0
            }

    async def save_trend_analysis_results(
        self, 
        trend_result: Dict[str, Any],
        user_id: str,  # Now required for RLS
        topic: str = "",
        target_audience: str = "",
        focus_area: str = ""
    ) -> str:
        """Save complete trend analysis results with RLS"""
        
        if not user_id:
            raise ValueError("user_id is required for RLS")
        
        # Set user context
        self.set_user_context(user_id)
        
        try:
            self.logger.info(f"💾 Saving trend analysis results for user {user_id}, topic: {topic}")
            
            # Step 1: Create main trend analysis record
            trend_analysis_id = await self._create_trend_analysis_record_rls(
                user_id=user_id,
                topic=topic,
                target_audience=target_audience,
                focus_area=focus_area,
                metadata=trend_result.get('metadata', {})
            )
            
            # Step 2: Save trending topics
            if trend_result.get('trending_topics'):
                try:
                    await self._save_trending_topics_rls(
                        trend_analysis_id, 
                        trend_result['trending_topics'],
                        user_id
                    )
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to save trending topics: {e}")
            
            # Step 3: Save content opportunities
            if trend_result.get('content_opportunities'):
                try:
                    await self._save_content_opportunities_rls(
                        trend_analysis_id,
                        trend_result['content_opportunities'],
                        user_id
                    )
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to save content opportunities: {e}")
            
            # Step 4: Save keyword intelligence
            if trend_result.get('seo_intelligence'):
                try:
                    await self._save_keyword_intelligence_rls(
                        trend_analysis_id,
                        trend_result['seo_intelligence'],
                        user_id
                    )
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to save keyword intelligence: {e}")

            self.logger.info(f"✅ Trend analysis saved with ID: {trend_analysis_id} for user: {user_id}")
            return trend_analysis_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save trend analysis: {e}")
            raise

    async def _create_trend_analysis_record_rls(
        self,
        user_id: str,
        topic: str,
        target_audience: str,
        focus_area: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Create main trend analysis record with RLS"""
        
        try:
            trend_analysis_data = {
                "user_id": user_id,  # Include user_id for RLS
                "topic": topic,
                "target_audience": target_audience,
                "focus_area": focus_area,
                "status": "completed",
                "metadata": metadata,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.debug(f"Creating trend analysis with data: {trend_analysis_data}")
            
            # Execute insert using HTTP
            result = self._execute_query('POST', 'trend_analyses', trend_analysis_data)
            
            if result['success'] and result['data'] and len(result['data']) > 0:
                record_id = result['data'][0]["id"]
                self.logger.info(f"✅ Created trend analysis record with ID: {record_id}")
                return record_id
            else:
                raise Exception(f"Failed to create trend analysis record: {result.get('error', 'No data returned')}")
            
        except Exception as e:
            self.logger.error(f"Error creating trend analysis record: {e}")
            raise




    async def _save_trending_topics_rls(
        self,
        trend_analysis_id: str,
        trending_topics: List[Dict[str, Any]],
        user_id: str
    ) -> None:
        """Save trending topics with RLS"""
        
        try:
            topics_to_insert = []
            
            for i, topic_data in enumerate(trending_topics):
                topic_record = {
                    "user_id": user_id,  # Include user_id for RLS
                    "trend_analysis_id": trend_analysis_id,
                    "title": topic_data.get("trend", topic_data.get("topic", f"Trending Topic {i+1}")),
                    "viral_potential": topic_data.get("viral_potential", 0),
                    "keywords": topic_data.get("keywords", []),
                    "search_volume": topic_data.get("search_volume", "unknown"),
                    "competition": topic_data.get("competition", "unknown"),
                    "selected": False,
                    "additional_data": {
                        "description": topic_data.get("description", ""),
                        "relevance": topic_data.get("relevance", ""),
                        "content_formats": topic_data.get("content_formats", []),
                        "content_angles": topic_data.get("content_angles", []),
                        "trend_strength": topic_data.get("trend_strength", ""),
                        "audience_alignment_score": topic_data.get("audience_alignment_score", 0),
                        "content_gap_score": topic_data.get("content_gap_score", 0),
                        "traffic_potential": topic_data.get("traffic_potential", ""),
                        "geographic_relevance": topic_data.get("geographic_relevance", []),
                        "seasonal_factors": topic_data.get("seasonal_factors", "")
                    },
                    "created_at": datetime.utcnow().isoformat()
                }
                topics_to_insert.append(topic_record)
            
            if topics_to_insert:
                result = self._execute_query('POST', 'trending_topics', topics_to_insert)
                
                if result['success']:
                    self.logger.info(f"✅ Saved {len(topics_to_insert)} trending topics for user {user_id}")
                else:
                    raise Exception(f"Failed to save trending topics: {result.get('error')}")
            
        except Exception as e:
            self.logger.error(f"Error saving trending topics: {e}")
            raise

    async def _save_content_opportunities_rls(
        self,
        trend_analysis_id: str,
        content_opportunities: List[Dict[str, Any]],
        user_id: str
    ) -> None:
        """Save content opportunities with RLS"""
        
        try:
            opportunities_to_insert = []
            
            for i, opp_data in enumerate(content_opportunities):
                opportunity_record = {
                    "user_id": user_id,  # Include user_id for RLS
                    "trend_analysis_id": trend_analysis_id,
                    "title": opp_data.get("opportunity", opp_data.get("title", f"Content Opportunity {i+1}")),
                    "format": opp_data.get("format", "unknown"),
                    "difficulty": opp_data.get("difficulty", 50),
                    "engagement_potential": opp_data.get("engagement_potential", "medium"),
                    "selected": False,
                    "additional_data": {
                        "time_investment": opp_data.get("time_investment", ""),
                        "keywords": opp_data.get("keywords", []),
                        "monetization": opp_data.get("monetization", ""),
                        "distribution": opp_data.get("distribution", []),
                        "competitive_advantage": opp_data.get("competitive_advantage", ""),
                        "target_keywords": opp_data.get("target_keywords", [])
                    },
                    "created_at": datetime.utcnow().isoformat()
                }
                opportunities_to_insert.append(opportunity_record)
            
            if opportunities_to_insert:
                result = self._execute_query('POST', 'content_opportunities', opportunities_to_insert)
                
                if result['success']:
                    self.logger.info(f"✅ Saved {len(opportunities_to_insert)} content opportunities for user {user_id}")
                else:
                    raise Exception(f"Failed to save content opportunities: {result.get('error')}")
            
        except Exception as e:
            self.logger.error(f"Error saving content opportunities: {e}")
            raise

    async def _save_keyword_intelligence_rls(
        self,
        trend_analysis_id: str,
        seo_intelligence: Dict[str, Any],
        user_id: str
    ) -> None:
        """Save keyword intelligence with RLS"""
        
        try:
            keyword_record = {
                "user_id": user_id,  # Include user_id for RLS
                "trend_analysis_id": trend_analysis_id,
                "high_volume_keywords": seo_intelligence.get("high_volume_keywords", []),
                "low_competition_keywords": seo_intelligence.get("low_competition_keywords", []),
                "emerging_keywords": seo_intelligence.get("emerging_keywords", []),
                "additional_data": {
                    "keyword_clusters": seo_intelligence.get("keyword_clusters", {}),
                    "semantic_clusters": seo_intelligence.get("semantic_keyword_clusters", {}),
                    "keyword_difficulty_scores": seo_intelligence.get("keyword_difficulty_scores", {}),
                    "search_volumes": seo_intelligence.get("search_volumes", {}),
                    "trend_data": seo_intelligence.get("trend_data", {})
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self._execute_query('POST', 'keyword_intelligence', keyword_record)
            
            if result['success']:
                self.logger.info(f"✅ Saved keyword intelligence data for user {user_id}")
            else:
                raise Exception(f"Failed to save keyword intelligence: {result.get('error')}")
            
        except Exception as e:
            self.logger.error(f"Error saving keyword intelligence: {e}")
            raise

    async def get_trend_analysis_for_phase2(self, trend_analysis_id: str, user_id: str) -> Dict[str, Any]:
        """Retrieve trend analysis data for Phase 2 with PyTrends data"""
        
        self.set_user_context(user_id)
        
        try:
            # Get main analysis (filtered by user_id)
            result = self._execute_query('GET', f'trend_analyses?id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
            
            if not result['success']:
                raise Exception(f"Failed to get trend analysis: {result.get('error')}")
            
            if not result['data']:
                raise Exception(f"Trend analysis {trend_analysis_id} not found or access denied")
            
            analysis = result['data'][0]
            
            # Get other data with user filtering
            trending_topics = []
            content_opportunities = []
            keyword_intelligence = {}
            
            try:
                topics_result = self._execute_query('GET', f'trending_topics?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
                if topics_result['success']:
                    trending_topics = topics_result['data']
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get trending topics: {e}")
            
            try:
                opps_result = self._execute_query('GET', f'content_opportunities?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
                if opps_result['success']:
                    content_opportunities = opps_result['data']
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get content opportunities: {e}")
            
            try:
                keywords_result = self._execute_query('GET', f'keyword_intelligence?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
                if keywords_result['success'] and keywords_result['data']:
                    keyword_intelligence = keywords_result['data'][0]
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get keyword intelligence: {e}")
            
            # CRITICAL FIX: Extract PyTrends data from metadata
            metadata = analysis.get('metadata', {})
            pytrends_data = metadata.get('pytrends_analysis', {})
            
            # Log PyTrends data availability
            if pytrends_data:
                self.logger.info(f"✅ PyTrends data found in metadata for analysis {trend_analysis_id}")
                self.logger.info(f"📊 Geographic hotspots: {len(pytrends_data.get('geographic_insights', {}).get('global_hotspots', []))}")
                self.logger.info(f"💡 Actionable insights: {len(pytrends_data.get('actionable_insights', []))}")
            else:
                self.logger.warning(f"⚠️ No PyTrends data found for analysis {trend_analysis_id}")
            
            return {
                "trend_analysis_id": trend_analysis_id,
                "analysis_info": analysis,
                "trending_topics": trending_topics,
                "content_opportunities": content_opportunities,
                "keyword_intelligence": keyword_intelligence,
                # FIXED: Include PyTrends data from metadata
                "pytrends_analysis": pytrends_data,
                "pytrends_enhanced": pytrends_data.get('pytrends_enhanced', False),
                "pytrends_available": bool(pytrends_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving trend analysis: {e}")
            raise

    def get_all_trend_analyses(self, limit: int = 20, user_id: str = None) -> List[Dict[str, Any]]:
        """Get trend analyses filtered by user"""
        try:
            # Filter by user_id for RLS
            filter_query = f"user_id=eq.{user_id}&" if user_id else ""
            endpoint = f"trend_analyses?{filter_query}select=*&order=created_at.desc&limit={limit}"
            
            result = self._execute_query('GET', endpoint)
            
            if result['success']:
                return result['data']
            else:
                self.logger.error(f"Failed to get trend analyses: {result.get('error')}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting trend analyses: {e}")
            return []

    async def get_selected_data_for_phase2(self, trend_analysis_id: str, user_id: str) -> Dict[str, Any]:
        """Get selected data for Phase 2 with enhanced strategic context"""
        
        try:
            self.set_user_context(user_id)
            
            # Get main analysis info
            analysis_result = self._execute_query('GET', f'trend_analyses?id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
            
            if not analysis_result['success'] or not analysis_result['data']:
                raise Exception(f"Trend analysis {trend_analysis_id} not found or access denied")
            
            analysis_info = analysis_result['data'][0]
            
            # Get selected trending topics
            selected_topics_result = self._execute_query('GET', f'trending_topics?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&selected=eq.true&select=*')
            selected_topics = selected_topics_result['data'] if selected_topics_result['success'] else []
            
            # Get selected content opportunities  
            selected_opps_result = self._execute_query('GET', f'content_opportunities?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&selected=eq.true&select=*')
            selected_opportunities = selected_opps_result['data'] if selected_opps_result['success'] else []
            
            # Get keyword intelligence
            keywords_result = self._execute_query('GET', f'keyword_intelligence?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
            keyword_intelligence = keywords_result['data'][0] if keywords_result['success'] and keywords_result['data'] else {}
            
            # Get ALL topics and opportunities for strategic analysis
            all_topics_result = self._execute_query('GET', f'trending_topics?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
            all_topics = all_topics_result['data'] if all_topics_result['success'] else []
            
            all_opps_result = self._execute_query('GET', f'content_opportunities?trend_analysis_id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*')
            all_opportunities = all_opps_result['data'] if all_opps_result['success'] else []
            
            # ================================================================
            # ENHANCED PHASE 2 CONTEXT GENERATION
            # ================================================================
            
            # 1. Content Strategy Context
            content_strategy_context = self._generate_content_strategy_context(
                selected_topics, selected_opportunities, all_topics, all_opportunities, analysis_info
            )
            
            # 2. Audience Intelligence
            audience_intelligence = self._generate_audience_intelligence(
                analysis_info, selected_topics, selected_opportunities
            )
            
            # 3. SEO Enhancement Strategy
            seo_enhancement_strategy = self._generate_seo_enhancement_strategy(
                keyword_intelligence, selected_topics, selected_opportunities
            )
            
            # 4. Content Calendar Context
            content_calendar_context = self._generate_content_calendar_context(
                selected_topics, selected_opportunities, analysis_info
            )
            
            # 5. Blog Idea Generation Parameters
            generation_parameters = self._calculate_blog_idea_generation_parameters(
                selected_topics, selected_opportunities, analysis_info
            )
            
            # 6. Competitive Positioning Strategy
            competitive_positioning = self._generate_competitive_positioning_strategy(
                selected_topics, selected_opportunities, all_topics, all_opportunities
            )
            
            # 7. Success Metrics and Benchmarks
            success_metrics = self._define_success_metrics(
                selected_topics, selected_opportunities, analysis_info
            )
            
            # ================================================================
            # COMPILE COMPREHENSIVE PHASE 2 DATA
            # ================================================================
            
            return {
                # Original data structure (for backward compatibility)
                "research_context": {
                    "analysis_id": trend_analysis_id,
                    "topic": analysis_info.get('topic'),
                    "target_audience": analysis_info.get('target_audience'),
                    "focus_area": analysis_info.get('focus_area'),
                    "user_id": user_id,
                    "confidence_score": analysis_info.get('metadata', {}).get('confidence_score', 85),
                    "analysis_timestamp": analysis_info.get('created_at')
                },
                "selected_trending_topics": selected_topics,
                "selected_opportunities": selected_opportunities,
                "keyword_intelligence": keyword_intelligence,
                "selection_counts": {
                    "trending_topics": len(selected_topics),
                    "content_opportunities": len(selected_opportunities),
                    "total_selections": len(selected_topics) + len(selected_opportunities)
                },
                
                # ENHANCED PHASE 2 CONTEXT
                "phase2_enhancements": {
                    "content_strategy_context": content_strategy_context,
                    "audience_intelligence": audience_intelligence,
                    "seo_enhancement_strategy": seo_enhancement_strategy,
                    "content_calendar_context": content_calendar_context,
                    "blog_idea_generation_parameters": generation_parameters,
                    "competitive_positioning": competitive_positioning,
                    "success_metrics": success_metrics
                },
                
                # Blog Idea Generation Configuration
                "blog_idea_generation_config": {
                    "total_ideas_target": generation_parameters["total_ideas_to_generate"],
                    "ideas_per_selected_topic": generation_parameters["ideas_per_topic"],
                    "ideas_per_selected_opportunity": generation_parameters["ideas_per_opportunity"],
                    "content_format_distribution": generation_parameters["content_format_distribution"],
                    "difficulty_targeting": generation_parameters["difficulty_targeting"],
                    "viral_optimization_enabled": True,
                    "seo_optimization_enabled": True,
                    "audience_personalization_enabled": True
                },
                
                # Quality Assurance Parameters
                "quality_assurance": {
                    "minimum_idea_quality_score": 75,
                    "uniqueness_threshold": 0.8,
                    "keyword_optimization_required": True,
                    "audience_alignment_check": True,
                    "viral_potential_weighting": 0.3,
                    "seo_potential_weighting": 0.3,
                    "practicality_weighting": 0.4
                },
                
                # Strategic Intelligence Summary
                "strategic_intelligence_summary": {
                    "high_potential_count": len([t for t in selected_topics if t.get('viral_potential', 0) >= 80]),
                    "quick_win_count": len([o for o in selected_opportunities if o.get('difficulty', 100) <= 40]),
                    "content_pillar_opportunities": content_strategy_context["content_pillar_opportunities"],
                    "competitive_advantages": competitive_positioning["unique_positioning_angles"],
                    "primary_content_themes": content_strategy_context["primary_content_themes"],
                    "recommended_publishing_frequency": content_calendar_context["recommended_publishing_frequency"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced Phase 2 data: {e}")
            raise

    def _generate_content_strategy_context(self, selected_topics: List[Dict], selected_opportunities: List[Dict], 
                                        all_topics: List[Dict], all_opportunities: List[Dict], analysis_info: Dict) -> Dict[str, Any]:
        """Generate comprehensive content strategy context"""
        
        total_viral_score = sum(topic.get('viral_potential', 0) for topic in selected_topics)
        avg_viral_score = total_viral_score / len(selected_topics) if selected_topics else 0
        
        high_viral_count = len([t for t in selected_topics if t.get('viral_potential', 0) >= 80])
        quick_win_count = len([o for o in selected_opportunities if o.get('difficulty', 100) <= 40])
        
        # Content format analysis
        selected_formats = []
        for opp in selected_opportunities:
            if opp.get('format'):
                selected_formats.append(opp['format'])
        
        format_distribution = {}
        for fmt in selected_formats:
            format_distribution[fmt] = format_distribution.get(fmt, 0) + 1
        
        # Content themes extraction
        content_themes = set()
        for topic in selected_topics:
            keywords = topic.get('keywords', [])
            for keyword in keywords[:2]:  # Top 2 keywords per topic
                content_themes.add(keyword.lower())
        
        return {
            "content_mix_strategy": {
                "trending_focus_percentage": 60 if high_viral_count >= 2 else 40,
                "evergreen_percentage": 40 if high_viral_count >= 2 else 60,
                "viral_content_priority": "high" if avg_viral_score >= 75 else "medium",
                "quick_win_emphasis": "high" if quick_win_count >= 3 else "medium"
            },
            "content_format_distribution": {
                "how_to_guides": 35,
                "listicles": 25, 
                "case_studies": 20,
                "comparisons": 10,
                "trend_analyses": 10
            },
            "content_pillar_opportunities": list(content_themes)[:5],
            "primary_content_themes": [
                f"{analysis_info.get('topic', '')} fundamentals",
                f"Advanced {analysis_info.get('topic', '')} strategies", 
                f"{analysis_info.get('topic', '')} tools and resources",
                f"Industry-specific {analysis_info.get('topic', '')} applications"
            ],
            "viral_optimization_strategy": {
                "high_viral_topics_count": high_viral_count,
                "viral_content_triggers": [
                    "How to achieve [specific result] in [timeframe]",
                    "[Number] secrets that [audience] don't know about [topic]",
                    "Why [conventional wisdom] is wrong about [topic]",
                    "The ultimate guide to [specific aspect of topic]"
                ],
                "trending_timing_strategy": "Publish high-viral content within 48-72 hours for maximum impact"
            }
        }

    def _generate_audience_intelligence(self, analysis_info: Dict, selected_topics: List[Dict], 
                                    selected_opportunities: List[Dict]) -> Dict[str, Any]:
        """Generate enhanced audience intelligence"""
        
        target_audience = analysis_info.get('target_audience', 'professional')
        topic = analysis_info.get('topic', '')
        
        # Audience-specific pain points
        pain_points_map = {
            "professional": [
                f"Limited time to research and implement {topic} strategies",
                f"Need ROI justification for {topic} investments",
                f"Staying updated with latest {topic} trends",
                f"Scaling {topic} solutions across teams",
                f"Measuring and proving {topic} success"
            ],
            "entrepreneur": [
                f"Budget constraints for {topic} tools and services",
                f"Wearing multiple hats with limited {topic} expertise",
                f"Finding reliable and actionable {topic} advice",
                f"Prioritizing {topic} growth initiatives",
                f"Building {topic} systems that scale"
            ],
            "small_business": [
                f"Competing with larger companies in {topic}",
                f"Limited resources and budget for {topic}",
                f"Need for immediate {topic} results",
                f"Simplifying complex {topic} strategies",
                f"Local market {topic} considerations"
            ],
            "student": [
                f"Understanding {topic} fundamentals",
                f"Practical {topic} application examples",
                f"Career preparation in {topic}",
                f"Free and low-cost {topic} resources",
                f"Building {topic} portfolio projects"
            ]
        }
        
        # Content preferences by audience
        content_preferences_map = {
            "professional": {
                "preferred_length": "1500-2500 words",
                "content_style": "data-driven with actionable insights",
                "preferred_formats": ["how-to guides", "case studies", "industry reports"],
                "engagement_drivers": ["ROI data", "implementation timelines", "best practices"]
            },
            "entrepreneur": {
                "preferred_length": "1000-2000 words", 
                "content_style": "practical and results-focused",
                "preferred_formats": ["step-by-step guides", "tool reviews", "success stories"],
                "engagement_drivers": ["cost-effective solutions", "quick wins", "growth strategies"]
            },
            "small_business": {
                "preferred_length": "800-1500 words",
                "content_style": "simple and actionable",
                "preferred_formats": ["beginner guides", "checklists", "templates"],
                "engagement_drivers": ["budget-friendly options", "easy implementation", "local relevance"]
            },
            "student": {
                "preferred_length": "1200-2000 words",
                "content_style": "educational and comprehensive",
                "preferred_formats": ["tutorials", "explained examples", "resource lists"],
                "engagement_drivers": ["learning objectives", "practical exercises", "career relevance"]
            }
        }
        
        audience_prefs = content_preferences_map.get(target_audience, content_preferences_map["professional"])
        
        return {
            "primary_audience": {
                "segment": target_audience,
                "pain_points": pain_points_map.get(target_audience, pain_points_map["professional"]),
                "content_preferences": audience_prefs,
                "decision_making_factors": [
                    "Credibility and expertise demonstration",
                    "Practical applicability",
                    "Time investment required",
                    "Expected outcomes and ROI"
                ]
            },
            "content_personalization": {
                "tone_and_style": "professional but accessible" if target_audience == "professional" else "conversational and supportive",
                "technical_depth": "advanced" if target_audience == "professional" else "intermediate",
                "example_types": f"industry-specific {topic} examples" if target_audience == "professional" else f"practical {topic} applications",
                "call_to_action_style": "data-driven recommendations" if target_audience == "professional" else "actionable next steps"
            },
            "engagement_optimization": {
                "optimal_publishing_times": "Tuesday-Thursday, 10-11 AM" if target_audience == "professional" else "Weekends and evenings",
                "platform_preferences": ["LinkedIn", "industry publications"] if target_audience == "professional" else ["social media", "email newsletters"],
                "content_distribution_strategy": f"Focus on {target_audience}-specific channels and communities"
            }
        }

    def _generate_content_calendar_context(self, selected_topics: List[Dict], selected_opportunities: List[Dict], 
                                        analysis_info: Dict) -> Dict[str, Any]:
        """Generate content calendar strategic context"""
        
        total_selections = len(selected_topics) + len(selected_opportunities)
        high_viral_count = len([t for t in selected_topics if t.get('viral_potential', 0) >= 80])
        
        # Calculate publishing frequency
        if total_selections <= 5:
            frequency = "1-2 posts per week"
            timeline = "2-3 months to complete"
        elif total_selections <= 10:
            frequency = "2-3 posts per week" 
            timeline = "3-4 months to complete"
        else:
            frequency = "3-4 posts per week"
            timeline = "4-6 months to complete"
        
        return {
            "recommended_publishing_frequency": frequency,
            "content_production_timeline": timeline,
            "priority_scheduling": {
                "immediate_priority": [topic.get('title', '') for topic in selected_topics if topic.get('viral_potential', 0) >= 85],
                "high_priority": [topic.get('title', '') for topic in selected_topics if 70 <= topic.get('viral_potential', 0) < 85],
                "standard_priority": [opp.get('title', '') for opp in selected_opportunities if opp.get('difficulty', 100) <= 40]
            },
            "content_series_opportunities": [
                f"Complete {analysis_info.get('topic', '')} Guide Series",
                f"{analysis_info.get('topic', '')} Tools and Resources Series",
                f"{analysis_info.get('topic', '')} Case Study Series"
            ],
            "seasonal_considerations": {
                "q1_focus": "Planning and strategy content",
                "q2_focus": "Implementation and how-to content",
                "q3_focus": "Optimization and advanced strategies",
                "q4_focus": "Year-end reviews and future trends"
            },
            "content_distribution_schedule": {
                "trending_content": "Publish within 48-72 hours of creation for maximum viral potential",
                "evergreen_content": "Schedule during peak audience engagement times",
                "pillar_content": "Monthly comprehensive guides to establish authority"
            }
        }

    def _calculate_blog_idea_generation_parameters(self, selected_topics: List[Dict], selected_opportunities: List[Dict], 
                                                analysis_info: Dict) -> Dict[str, Any]:
        """Calculate optimal parameters for blog idea generation - FIXED VERSION"""
        
        total_selections = len(selected_topics) + len(selected_opportunities)
        topic_count = len(selected_topics)
        opp_count = len(selected_opportunities)
        
        # Calculate idea generation targets
        ideas_per_topic = 3
        ideas_per_opportunity = 2
        base_ideas = (topic_count * ideas_per_topic) + (opp_count * ideas_per_opportunity)
        bonus_ideas = min(max(total_selections // 2, 3), 8)  # 3-8 bonus ideas
        
        total_target = base_ideas + bonus_ideas
        
        # Content format distribution based on selections
        format_weights = {
            "how_to_guide": 30,
            "listicle": 25,
            "case_study": 20,
            "comparison": 15,
            "trend_analysis": 10
        }
        
        # Adjust based on selected opportunities - FIXED JSON parsing
        for opp in selected_opportunities:
            opp_format = opp.get('format', '')
            if opp_format in format_weights:
                format_weights[opp_format] += 5
        
        # Normalize to 100%
        total_weight = sum(format_weights.values())
        format_distribution = {k: round((v/total_weight) * 100) for k, v in format_weights.items()}
        
        return {
            "total_ideas_to_generate": min(max(total_target, 10), 50),  # 10-50 range
            "ideas_per_topic": ideas_per_topic,
            "ideas_per_opportunity": ideas_per_opportunity,
            "bonus_wildcard_ideas": bonus_ideas,
            "content_format_distribution": format_distribution,
            "difficulty_targeting": {
                "beginner_content": 40,
                "intermediate_content": 40, 
                "advanced_content": 20
            },
            "viral_optimization_weighting": {
                "trending_topic_weight": 0.6,
                "evergreen_weight": 0.4,
                "viral_potential_threshold": 70,
                "quick_win_bonus_multiplier": 1.2
            }
        }
    def _generate_competitive_positioning_strategy(self, selected_topics: List[Dict], selected_opportunities: List[Dict],
                                                all_topics: List[Dict], all_opportunities: List[Dict]) -> Dict[str, Any]:
        """Generate competitive positioning strategy"""
        
        # Extract unique positioning opportunities
        high_viral_topics = [t.get('title', '') for t in selected_topics if t.get('viral_potential', 0) >= 80]
        easy_opportunities = [o.get('title', '') for o in selected_opportunities if o.get('difficulty', 100) <= 40]
        
        return {
            "unique_positioning_angles": [
                "Data-driven approach with real metrics and case studies",
                "Beginner-friendly content with step-by-step implementation", 
                "Industry-specific applications and use cases",
                "Budget-conscious solutions for resource-constrained teams",
                "Advanced tactics for experienced practitioners",
                "Tool-focused content with hands-on tutorials"
            ],
            "content_differentiation_strategy": {
                "depth_advantage": "Create more comprehensive content than competitors",
                "practical_focus": "Emphasize actionable takeaways and implementation guides",
                "visual_enhancement": "Include more diagrams, screenshots, and visual aids",
                "case_study_integration": "Use real-world examples and success stories"
            },
            "market_gap_opportunities": [
                f"Comprehensive beginner guides in {topic}" for topic in high_viral_topics[:2]
            ] + [
                f"Advanced implementation strategies for {opp}" for opp in easy_opportunities[:2]
            ],
            "competitive_advantages": {
                "content_quality": "Higher research depth and accuracy",
                "audience_focus": "Better audience segmentation and personalization",
                "update_frequency": "More timely updates and trend integration",
                "practical_value": "Greater emphasis on actionable insights"
            }
        }

    def _define_success_metrics(self, selected_topics: List[Dict], selected_opportunities: List[Dict], 
                            analysis_info: Dict) -> Dict[str, Any]:
        """Define success metrics and benchmarks for blog content"""
        
        high_viral_count = len([t for t in selected_topics if t.get('viral_potential', 0) >= 80])
        avg_viral_score = sum(t.get('viral_potential', 0) for t in selected_topics) / len(selected_topics) if selected_topics else 0
        
        return {
            "content_performance_targets": {
                "average_viral_score_target": max(70, avg_viral_score),
                "engagement_rate_target": "5-8% for high-viral content, 3-5% for evergreen",
                "organic_traffic_target": "25-50% increase within 3 months",
                "conversion_rate_target": "2-4% for lead generation content"
            },
            "seo_performance_benchmarks": {
                "keyword_ranking_target": "Top 10 for primary keywords within 6 months",
                "featured_snippet_target": "Capture 2-3 featured snippets per content pillar",
                "backlink_target": "5-10 quality backlinks per pillar post",
                "domain_authority_impact": "Gradual improvement through topical authority"
            },
            "business_impact_metrics": {
                "lead_generation_target": f"15-25 qualified leads per month from {analysis_info.get('topic', '')} content",
                "brand_awareness_target": "Increase in branded search volume",
                "thought_leadership_target": "Recognition as authority in selected topic areas",
                "roi_expectation": "3:1 return on content creation investment within 12 months"
            },
            "content_quality_benchmarks": {
                "minimum_word_count": "1500+ words for pillar content, 800+ for supporting content",
                "readability_target": "Flesch-Kincaid Grade Level 8-10",
                "user_engagement_target": "Average time on page 3+ minutes",
                "social_sharing_target": "20+ shares per high-quality post"
            }
        }

    async def update_opportunity_selection(self, opportunity_id: str, selected: bool, user_id: str = None):
        """Update opportunity selection status with RLS"""
        try:
            if user_id:
                self.set_user_context(user_id)
            
            update_data = {
                "selected": selected,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update with user filtering if provided
            filter_query = f"id=eq.{opportunity_id}"
            if user_id:
                filter_query += f"&user_id=eq.{user_id}"
            
            endpoint = f"content_opportunities?{filter_query}"
            result = self._execute_query('PATCH', endpoint, update_data)
            
            if result['success']:
                self.logger.info(f"✅ Updated opportunity {opportunity_id} selection to {selected}")
            else:
                raise Exception(f"Failed to update opportunity selection: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error updating opportunity selection: {e}")
            raise
########################################

    def _safe_parse_json(self, data, default=None):
        """Safely parse JSON data, handling both strings and already-parsed objects"""
        if data is None:
            return default if default is not None else {}
        
        if isinstance(data, dict):
            return data  # Already parsed
        
        if isinstance(data, str):
            try:
                return json.loads(data)
            except (json.JSONDecodeError, ValueError):
                self.logger.warning(f"Failed to parse JSON: {data}")
                return default if default is not None else {}
        
        # For any other type, return default
        return default if default is not None else {}

    def _generate_seo_enhancement_strategy(self, keyword_intelligence: Dict, selected_topics: List[Dict], 
                                        selected_opportunities: List[Dict]) -> Dict[str, Any]:
        """Generate SEO enhancement strategy for blog ideas - FIXED VERSION"""
        
        # Extract keywords from selected items
        selected_keywords = set()
        
        # Process selected topics with safe JSON parsing
        for topic in selected_topics:
            keywords = topic.get('keywords', [])
            if isinstance(keywords, str):
                try:
                    keywords = json.loads(keywords)
                except (json.JSONDecodeError, ValueError):
                    keywords = []
            selected_keywords.update(keywords or [])
        
        # Process selected opportunities with safe JSON parsing - FIX HERE
        for opp in selected_opportunities:
            # FIXED: Safely parse additional_data
            additional_data = self._safe_parse_json(opp.get('additional_data', {}), {})
            keywords = additional_data.get('keywords', [])
            
            # Ensure keywords is a list
            if isinstance(keywords, str):
                try:
                    keywords = json.loads(keywords)
                except (json.JSONDecodeError, ValueError):
                    keywords = []
            
            selected_keywords.update(keywords or [])
        
        # Get keyword intelligence data with safe parsing
        high_volume = keyword_intelligence.get('high_volume_keywords', [])
        low_competition = keyword_intelligence.get('low_competition_keywords', [])
        emerging = keyword_intelligence.get('emerging_keywords', [])
        
        # Ensure keyword intelligence data is properly formatted
        if isinstance(high_volume, str):
            high_volume = self._safe_parse_json(high_volume, [])
        if isinstance(low_competition, str):
            low_competition = self._safe_parse_json(low_competition, [])
        if isinstance(emerging, str):
            emerging = self._safe_parse_json(emerging, [])
        
        return {
            "primary_keyword_targets": list(selected_keywords)[:10],
            "seo_optimization_strategy": {
                "primary_keywords": high_volume[:5],
                "long_tail_opportunities": [f"{kw} for beginners" for kw in list(selected_keywords)[:3]] + 
                                        [f"best {kw} tools" for kw in list(selected_keywords)[:3]],
                "low_competition_targets": low_competition[:8],
                "emerging_keyword_opportunities": emerging[:5]
            },
            "content_seo_guidelines": {
                "title_optimization": [
                    "Include primary keyword in first 60 characters",
                    "Use power words: Ultimate, Complete, Essential, Proven",
                    "Include year (2025) for recency",
                    "Add audience qualifier when relevant"
                ],
                "header_structure": [
                    "H1: Primary keyword + compelling benefit",
                    "H2: Subtopics with related keywords", 
                    "H3: Specific points with long-tail keywords"
                ],
                "keyword_density_target": "1-2% for primary keyword, natural distribution for related keywords",
                "internal_linking_opportunities": "Link to related blog posts within same content pillar"
            },
            "featured_snippet_opportunities": [
                f"What is {kw}?" for kw in list(selected_keywords)[:3]
            ] + [
                f"How to {kw}?" for kw in list(selected_keywords)[:3]
            ],
            "semantic_seo_strategy": {
                "topic_clusters": self._safe_parse_json(keyword_intelligence.get('additional_data', {}), {}).get('keyword_clusters', {}),
                "entity_optimization": f"Establish topical authority in {list(selected_keywords)[0] if selected_keywords else 'main topic'}",
                "content_depth_recommendation": "Create comprehensive pillar pages with supporting cluster content"
            }
        }

    def _generate_content_strategy_context(self, selected_topics: List[Dict], selected_opportunities: List[Dict], 
                                        all_topics: List[Dict], all_opportunities: List[Dict], analysis_info: Dict) -> Dict[str, Any]:
        """Generate comprehensive content strategy context - FIXED VERSION"""
        
        total_viral_score = sum(topic.get('viral_potential', 0) for topic in selected_topics)
        avg_viral_score = total_viral_score / len(selected_topics) if selected_topics else 0
        
        high_viral_count = len([t for t in selected_topics if t.get('viral_potential', 0) >= 80])
        quick_win_count = len([o for o in selected_opportunities if o.get('difficulty', 100) <= 40 and o.get('engagement_potential') == 'High'])
        
        # Content format analysis with safe JSON parsing
        selected_formats = []
        for opp in selected_opportunities:
            if opp.get('format'):
                selected_formats.append(opp['format'])
        
        format_distribution = {}
        for fmt in selected_formats:
            format_distribution[fmt] = format_distribution.get(fmt, 0) + 1
        
        # Content themes extraction with safe JSON parsing
        content_themes = set()
        for topic in selected_topics:
            keywords = topic.get('keywords', [])
            # Handle both string and list formats
            if isinstance(keywords, str):
                try:
                    keywords = json.loads(keywords)
                except (json.JSONDecodeError, ValueError):
                    keywords = []
            
            for keyword in (keywords or [])[:2]:  # Top 2 keywords per topic
                content_themes.add(keyword.lower())
        
        return {
            "content_mix_strategy": {
                "trending_focus_percentage": 60 if high_viral_count >= 2 else 40,
                "evergreen_percentage": 40 if high_viral_count >= 2 else 60,
                "viral_content_priority": "high" if avg_viral_score >= 75 else "medium",
                "quick_win_emphasis": "high" if quick_win_count >= 3 else "medium"
            },
            "content_format_distribution": {
                "how_to_guides": 35,
                "listicles": 25, 
                "case_studies": 20,
                "comparisons": 10,
                "trend_analyses": 10
            },
            "content_pillar_opportunities": list(content_themes)[:5],
            "primary_content_themes": [
                f"{analysis_info.get('topic', '')} fundamentals",
                f"Advanced {analysis_info.get('topic', '')} strategies", 
                f"{analysis_info.get('topic', '')} tools and resources",
                f"Industry-specific {analysis_info.get('topic', '')} applications"
            ],
            "viral_optimization_strategy": {
                "high_viral_topics_count": high_viral_count,
                "viral_content_triggers": [
                    "How to achieve [specific result] in [timeframe]",
                    "[Number] secrets that [audience] don't know about [topic]",
                    "Why [conventional wisdom] is wrong about [topic]",
                    "The ultimate guide to [specific aspect of topic]"
                ],
                "trending_timing_strategy": "Publish high-viral content within 48-72 hours for maximum impact"
            }
        }

    def _generate_audience_intelligence(self, analysis_info: Dict, selected_topics: List[Dict], 
                                    selected_opportunities: List[Dict]) -> Dict[str, Any]:
        """Generate enhanced audience intelligence - FIXED VERSION"""
        
        target_audience = analysis_info.get('target_audience', 'professional')
        topic = analysis_info.get('topic', '')
        
        # Audience-specific pain points
        pain_points_map = {
            "professional": [
                f"Limited time to research and implement {topic} strategies",
                f"Need ROI justification for {topic} investments",
                f"Staying updated with latest {topic} trends",
                f"Scaling {topic} solutions across teams",
                f"Measuring and proving {topic} success"
            ],
            "entrepreneur": [
                f"Budget constraints for {topic} tools and services",
                f"Wearing multiple hats with limited {topic} expertise",
                f"Finding reliable and actionable {topic} advice",
                f"Prioritizing {topic} growth initiatives",
                f"Building {topic} systems that scale"
            ],
            "small_business": [
                f"Competing with larger companies in {topic}",
                f"Limited resources and budget for {topic}",
                f"Need for immediate {topic} results",
                f"Simplifying complex {topic} strategies",
                f"Local market {topic} considerations"
            ],
            "student": [
                f"Understanding {topic} fundamentals",
                f"Practical {topic} application examples",
                f"Career preparation in {topic}",
                f"Free and low-cost {topic} resources",
                f"Building {topic} portfolio projects"
            ]
        }
        
        # Content preferences by audience
        content_preferences_map = {
            "professional": {
                "preferred_length": "1500-2500 words",
                "content_style": "data-driven with actionable insights",
                "preferred_formats": ["how-to guides", "case studies", "industry reports"],
                "engagement_drivers": ["ROI data", "implementation timelines", "best practices"]
            },
            "entrepreneur": {
                "preferred_length": "1000-2000 words", 
                "content_style": "practical and results-focused",
                "preferred_formats": ["step-by-step guides", "tool reviews", "success stories"],
                "engagement_drivers": ["cost-effective solutions", "quick wins", "growth strategies"]
            },
            "small_business": {
                "preferred_length": "800-1500 words",
                "content_style": "simple and actionable",
                "preferred_formats": ["beginner guides", "checklists", "templates"],
                "engagement_drivers": ["budget-friendly options", "easy implementation", "local relevance"]
            },
            "student": {
                "preferred_length": "1200-2000 words",
                "content_style": "educational and comprehensive",
                "preferred_formats": ["tutorials", "explained examples", "resource lists"],
                "engagement_drivers": ["learning objectives", "practical exercises", "career relevance"]
            }
        }
        
        audience_prefs = content_preferences_map.get(target_audience, content_preferences_map["professional"])
        
        return {
            "primary_audience": {
                "segment": target_audience,
                "pain_points": pain_points_map.get(target_audience, pain_points_map["professional"]),
                "content_preferences": audience_prefs,
                "decision_making_factors": [
                    "Credibility and expertise demonstration",
                    "Practical applicability",
                    "Time investment required",
                    "Expected outcomes and ROI"
                ]
            },
            "content_personalization": {
                "tone_and_style": "professional but accessible" if target_audience == "professional" else "conversational and supportive",
                "technical_depth": "advanced" if target_audience == "professional" else "intermediate",
                "example_types": f"industry-specific {topic} examples" if target_audience == "professional" else f"practical {topic} applications",
                "call_to_action_style": "data-driven recommendations" if target_audience == "professional" else "actionable next steps"
            },
            "engagement_optimization": {
                "optimal_publishing_times": "Tuesday-Thursday, 10-11 AM" if target_audience == "professional" else "Weekends and evenings",
                "platform_preferences": ["LinkedIn", "industry publications"] if target_audience == "professional" else ["social media", "email newsletters"],
                "content_distribution_strategy": f"Focus on {target_audience}-specific channels and communities"
            }
        }

# For backwards compatibility, alias the RLS class
WorkingSupabaseStorage = RLSSupabaseStorage
Phase1SupabaseStorage = RLSSupabaseStorage


# ============================================================================
# UTILITY FUNCTIONS - RLS VERSIONS
# ============================================================================

async def save_trend_research_to_supabase(
    trend_result: Dict[str, Any],
    topic: str,
    user_id: str,  # Now required
    target_audience: str = "professional",
    focus_area: str = "general"
) -> str:
    """
    Utility function to save trend research results to Supabase - RLS VERSION
    """
    
    try:
        storage = RLSSupabaseStorage()
        
        trend_analysis_id = await storage.save_trend_analysis_results(
            trend_result=trend_result,
            user_id=user_id,
            topic=topic,
            target_audience=target_audience,
            focus_area=focus_area
        )
        
        return trend_analysis_id
        
    except Exception as e:
        logging.getLogger(__name__).error(f"❌ Failed to save trend research: {e}")
        raise



# Test function
def test_rls_connection(user_id: str = None):
    """Test the RLS Supabase connection"""
    try:
        storage = RLSSupabaseStorage()
        
        if user_id:
            # Test with specific user
            try:
                uuid.UUID(user_id)
                analyses = storage.get_all_trend_analyses(limit=3, user_id=user_id)
                print(f"✅ RLS connection successful! Found {len(analyses)} analyses for user {user_id}")
            except ValueError:
                print(f"❌ Invalid user_id format: {user_id}")
                return False
        else:
            # Test basic connection
            analyses = storage.get_all_trend_analyses(limit=3)
            print(f"✅ RLS connection successful! Found {len(analyses)} total analyses")
        
        return True
    except Exception as e:
        print(f"❌ RLS connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not installed. Make sure environment variables are set manually.")
    
    # Test the RLS connection
    print("🧪 Testing RLS Supabase Connection...")
    print("=" * 50)
    test_rls_connection()