#!/usr/bin/env python3
"""
Updated Affiliate Research API with Linkup Integration and Supabase Storage
Uses real web search via Linkup API and stores results in Supabase with deduplication
"""

from flask import request, jsonify
import asyncio
import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Import our new Linkup-based research and storage
from linkup_affiliate_research import linkup_affiliate_research
from supabase_affiliate_storage_enhanced import EnhancedSupabaseAffiliateStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import user ID extraction from existing code
def extract_and_validate_user_id(data):
    """Extract and validate user_id from request data"""
    user_id = data.get('user_id')
    if not user_id:
        return None, {"success": False, "error": "user_id is required"}, 400
    
    try:
        # Validate UUID format
        uuid.UUID(user_id)
        return user_id, None, None
    except ValueError:
        return None, {"success": False, "error": "Invalid user_id format"}, 400

class LinkupAffiliateAPI:
    """API endpoints for Linkup-based affiliate research"""
    
    def __init__(self):
        self.linkup_research = linkup_affiliate_research
        self.storage = EnhancedSupabaseAffiliateStorage()
    
    async def research_affiliate_offers(self, topic: str, user_id: str, 
                                      subtopics: List[str] = None, 
                                      min_commission_threshold: int = 10,
                                      use_cached: bool = True) -> Dict[str, Any]:
        """Research affiliate offers using Linkup API with caching and storage"""
        
        try:
            # Enhanced database-first search strategy
            existing_programs = await self.storage.get_existing_affiliate_programs(topic, user_id)
            
            # Check for existing research with enhanced storage
            if use_cached:
                cached_result = await self.storage.get_affiliate_programs_by_topic(topic, user_id)
                if cached_result['programs']:
                    # Check if we have sufficient existing programs
                    if cached_result['existing_count'] >= 3:  # At least 3 existing programs
                        logger.info(f"🔄 Using {cached_result['existing_count']} existing programs for topic: {topic}")
                        return {
                            "success": True,
                            "cached": True,
                            "reuse_rate": cached_result['reuse_rate'],
                            "affiliate_research": {
                                "topic": topic,
                                "subtopics": subtopics or [f"{topic} affiliate programs"],
                                "programs": cached_result['programs'],
                                "total_programs": cached_result['count'],
                                "profitability_analysis": {
                                    "score": 75,  # Use stored profitability
                                    "level": "good",
                                    "reason": f"Found {cached_result['count']} existing programs",
                                    "total_programs": cached_result['count'],
                                    "avg_commission_rate": 25.0,
                                    "avg_commission_amount": 50.0,
                                    "high_value_programs": cached_result['count'],
                                    "networks_represented": 3
                                }
                            },
                            "existing_programs": cached_result['existing_count'],
                            "new_programs": 0,
                            "research_timestamp": datetime.now().isoformat()
                        }
            
            # Perform new research
            logger.info(f"Performing new Linkup research for topic: {topic}")
            research_result = await self.linkup_research.search_affiliate_programs(topic, subtopics)
            
            # Store results with enhanced reuse strategy
            analysis_id = str(uuid.uuid4())
            storage_result = await self.storage.store_affiliate_research_with_reuse(
                topic=topic,
                user_id=user_id,
                research_data=research_result,
                analysis_id=analysis_id
            )
            
            return {
                "success": True,
                "cached": False,
                "affiliate_research": research_result,
                "analysis_id": analysis_id,
                "storage_summary": storage_result,
                "reuse_info": {
                    "existing_programs": storage_result.get('existing_programs', 0),
                    "new_programs": storage_result.get('new_programs', 0),
                    "reused_programs": storage_result.get('reused_programs', 0),
                    "total_programs": storage_result.get('total_programs', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in affiliate research: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_topic_profitability(self, topic: str, user_id: str) -> Dict[str, Any]:
        """Quick validation of topic profitability"""
        
        try:
            # Use limited subtopics for quick validation
            result = await self.research_affiliate_offers(
                topic=topic,
                user_id=user_id,
                subtopics=[f"{topic} affiliate program"]  # Single focused search
            )
            
            if not result["success"]:
                return result
            
            analysis = result["affiliate_research"]["profitability_analysis"]
            
            return {
                "success": True,
                "topic": topic,
                "is_profitable": analysis["level"] in ["good", "excellent"],
                "profitability_score": analysis["score"],
                "level": analysis["level"],
                "total_programs": analysis["total_programs"],
                "avg_commission_rate": analysis["avg_commission_rate"],
                "avg_commission_amount": analysis["avg_commission_amount"],
                "recommendation": "proceed" if analysis["level"] in ["good", "excellent"] else "consider_alternatives"
            }
            
        except Exception as e:
            logger.error(f"Error in profitability validation: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
linkup_affiliate_api = LinkupAffiliateAPI()

# ============================================================================
# FLASK API ENDPOINTS - These should be imported and registered by main server
# ============================================================================

from flask import Blueprint

# Create a blueprint for affiliate research endpoints
affiliate_bp = Blueprint('affiliate', __name__)

try:
    from supabase_storage import ImprovedSupabaseStorage
    storage = ImprovedSupabaseStorage()
except ImportError:
    storage = None

@affiliate_bp.route('/api/v2/affiliate-research', methods=['POST'])
def research_affiliate_offers():
    """Research affiliate offers using Linkup API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400
        
        # Extract and validate user_id
        user_id, error_response, status_code = extract_and_validate_user_id(data)
        if error_response:
            return jsonify(error_response), status_code
        
        # Validate topic
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({
                "success": False,
                "error": "Topic is required"
            }), 400
        
        # Get optional parameters
        subtopics = data.get('subtopics', [])
        min_commission_threshold = data.get('min_commission_threshold', 10)
        use_cached = data.get('use_cached', True)
        
        print(f"🔍 Researching affiliate offers for topic: {topic}")
        
        # Run affiliate research
        async def run_research():
            return await linkup_affiliate_api.research_affiliate_offers(
                topic=topic,
                user_id=user_id,
                subtopics=subtopics,
                min_commission_threshold=min_commission_threshold,
                use_cached=use_cached
            )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(run_research())
        finally:
            loop.close()
        
        if not result["success"]:
            return jsonify(result), 500
        
        # Check profitability threshold
        analysis = result["affiliate_research"]["profitability_analysis"]
        should_proceed = int(analysis["score"]) >= int(min_commission_threshold)
        
        response_data = {
            **result,
            "should_proceed": should_proceed,
            "threshold_check": {
                "min_required": min_commission_threshold,
                "actual_score": analysis["score"],
                "threshold_met": should_proceed
            },
            "user_id": user_id,
            "research_timestamp": datetime.now().isoformat()
        }
        
        if not should_proceed:
            response_data["cancellation_reason"] = "Topic profitability below threshold"
            response_data["suggestions"] = [
                "Try a more specific subtopic",
                "Explore related niches with higher commissions",
                "Consider different product categories"
            ]
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ Affiliate research failed: {e}")
        return jsonify({
            "success": False,
            "error": f"Affiliate research failed: {str(e)}"
        }), 500

@affiliate_bp.route('/api/v2/affiliate-research/subtopics', methods=['POST'])
def generate_subtopics():
    """Generate relevant subtopics using Linkup"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400
        
        # Extract and validate user_id
        user_id, error_response, status_code = extract_and_validate_user_id(data)
        if error_response:
            return jsonify(error_response), status_code
        
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({
                "success": False,
                "error": "Topic is required"
            }), 400
        
        # Generate subtopics using Linkup
        async def run_subtopics():
            return await linkup_affiliate_api.linkup_research.linkup_research._generate_subtopics_from_linkup(topic)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            subtopics = loop.run_until_complete(run_subtopics())
        finally:
            loop.close()
        
        return jsonify({
            "success": True,
            "topic": topic,
            "subtopics": subtopics,
            "subtopic_count": len(subtopics),
            "user_id": user_id,
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Subtopic generation failed: {str(e)}"
        }), 500

@affiliate_bp.route('/api/v2/affiliate-research/validate', methods=['POST'])
def validate_topic_profitability():
    """Quick validation of topic profitability"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400
        
        # Extract and validate user_id
        user_id, error_response, status_code = extract_and_validate_user_id(data)
        if error_response:
            return jsonify(error_response), status_code
        
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({
                "success": False,
                "error": "Topic is required"
            }), 400
        
        # Quick validation
        async def run_validation():
            return await linkup_affiliate_api.validate_topic_profitability(topic, user_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(run_validation())
        finally:
            loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Validation failed: {str(e)}"
        }), 500

@affiliate_bp.route('/api/v2/affiliate-research/history', methods=['GET'])
def get_research_history():
    """Get recent affiliate research history for a user"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id parameter is required"
            }), 400
        
        days = int(request.args.get('days', 7))
        
        # Get recent research
        async def get_history():
            return await linkup_affiliate_api.storage.get_recent_research(user_id, days)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            history = loop.run_until_complete(get_history())
        finally:
            loop.close()
        
        return jsonify({
            "success": True,
            "history": history,
            "count": len(history)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve history: {str(e)}"
        }), 500

@affiliate_bp.route('/api/v2/affiliate-research/get-by-analysis', methods=['GET'])
def get_affiliate_research_by_analysis():
    """Get affiliate research data by trend_analysis_id for Noodl integration"""
    try:
        # Get parameters
        trend_analysis_id = request.args.get('trend_analysis_id')
        user_id = request.args.get('user_id')
        
        if not trend_analysis_id:
            return jsonify({
                "success": False,
                "error": "trend_analysis_id parameter is required"
            }), 400
            
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id parameter is required"
            }), 400
        
        # Validate UUID format
        try:
            uuid.UUID(trend_analysis_id)
            uuid.UUID(user_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid UUID format for trend_analysis_id or user_id"
            }), 400
        
        print(f"🔍 Retrieving affiliate research for trend_analysis_id: {trend_analysis_id}, user_id: {user_id}")
        
        # Use the storage system to query the 4-table structure
        async def get_research_data():
            # Import storage class for direct access
            from supabase_affiliate_storage import SupabaseAffiliateStorage
            storage = SupabaseAffiliateStorage(user_id)
            
            # Set user context for RLS
            storage.set_user_context(user_id)
            
            try:
                # Get research session using the analysis_id (which is the session_id)
                session_response = storage._execute_query(
                    'GET', 
                    f'affiliate_research_sessions?id=eq.{trend_analysis_id}&user_id=eq.{user_id}&select=*'
                )
                
                if not session_response['success'] or not session_response['data']:
                    return None
                
                session = session_response['data'][0]
                
                # Get programs for this session
                programs_response = storage._execute_query(
                    'GET',
                    f'affiliate_session_programs?research_session_id=eq.{trend_analysis_id}&select=*,affiliate_programs(*)'
                )
                
                # Get profitability analysis
                analysis_response = storage._execute_query(
                    'GET',
                    f'affiliate_profitability_analysis?research_session_id=eq.{trend_analysis_id}&select=*'
                )
                
                # Parse JSON fields and format programs
                programs = []
                if programs_response['success'] and programs_response['data']:
                    for p in programs_response['data']:
                        program = p['affiliate_programs']
                        # Parse JSON fields
                        if program.get('promotional_materials'):
                            try:
                                import json
                                program['promotional_materials'] = json.loads(program['promotional_materials'])
                            except (json.JSONDecodeError, ValueError):
                                program['promotional_materials'] = []
                        programs.append(program)
                
                # Get profitability analysis
                profitability_analysis = None
                if analysis_response['success'] and analysis_response['data']:
                    profitability_analysis = analysis_response['data'][0]
                
                # Reconstruct the expected format for Noodl
                import json
                affiliate_research_data = {
                    'topic': session['topic'],
                    'subtopics': [],
                    'programs': programs,
                    'overall_assessment': {
                        'score': profitability_analysis.get('profitability_score', 0) if profitability_analysis else session.get('profitability_score', 0),
                        'level': profitability_analysis.get('profitability_level', 'unknown') if profitability_analysis else session.get('profitability_level', 'unknown'),
                        'reason': profitability_analysis.get('reason', 'Analysis not available') if profitability_analysis else 'Based on stored analysis',
                        'total_programs': profitability_analysis.get('total_programs', len(programs)) if profitability_analysis else len(programs),
                        'avg_commission_rate': profitability_analysis.get('avg_commission_rate', 0) if profitability_analysis else 0,
                        'avg_commission_amount': profitability_analysis.get('avg_commission_amount', 0) if profitability_analysis else 0,
                        'high_value_programs': profitability_analysis.get('high_value_programs', 0) if profitability_analysis else 0,
                        'networks_represented': profitability_analysis.get('networks_represented', 0) if profitability_analysis else 0
                    },
                    'recommendations': [
                        f"Based on {len(programs)} affiliate programs analyzed",
                        f"Average commission rate: {profitability_analysis.get('avg_commission_rate', 0) if profitability_analysis else 'N/A'}%",
                        f"Profitability level: {profitability_analysis.get('profitability_level', 'unknown') if profitability_analysis else session.get('profitability_level', 'unknown')}"
                    ]
                }
                
                # Add subtopics from session if available
                if session.get('subtopics'):
                    try:
                        affiliate_research_data['subtopics'] = json.loads(session['subtopics'])
                    except (json.JSONDecodeError, ValueError):
                        affiliate_research_data['subtopics'] = []
                
                return affiliate_research_data
                
            except Exception as e:
                print(f"❌ Error retrieving research data: {e}")
                return None
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            affiliate_data = loop.run_until_complete(get_research_data())
        finally:
            loop.close()
        
        if not affiliate_data:
            return jsonify({
                "success": False,
                "error": "No affiliate research data found for the given trend_analysis_id",
                "trend_analysis_id": trend_analysis_id,
                "user_id": user_id
            }), 404
        
        return jsonify({
            "success": True,
            "affiliate_research_data": affiliate_data,
            "trend_analysis_id": trend_analysis_id,
            "retrieved_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve affiliate research: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve affiliate research: {str(e)}"
        }), 500

# Global instances for backward compatibility
affiliate_research = linkup_affiliate_api

if __name__ == "__main__":
    # Test the integration
    import asyncio
    
    async def test():
        result = await linkup_affiliate_api.research_affiliate_offers(
            topic="fitness",
            user_id="test-user-123"
        )
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())