#!/usr/bin/env python3
"""
Updated noodl_server.py with RLS support and user_id handling
Compatible with Noodl authentication approach
"""
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import os
import sys
import logging
import uuid
from datetime import datetime, timedelta
from blog_idea_generator import BlogIdeaGenerationEngine
from phase2_supabase_storage import Phase2SupabaseStorage
# Import the RLS-compatible Supabase integration
from working_supabase_integration import RLSSupabaseStorage as ImprovedSupabaseStorage
from manual_keyword_integration import ManualKeywordResearchIntegration, KeywordData
import pandas as pd
import io
import json

# Load environment variables at startup
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
CORS(app)

# Register affiliate research blueprint
from affiliate_research_api_updated import affiliate_bp
app.register_blueprint(affiliate_bp)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_and_validate_user_id(data):
    """Helper function to extract and validate user_id from request data"""
    user_id = data.get('user_id') if data else None
    
    if not user_id:
        return None, {"success": False, "error": "user_id is required"}, 400
    
    # Validate UUID format
    try:
        uuid.UUID(user_id)
        return user_id, None, None
    except ValueError:
        return None, {"success": False, "error": "Invalid user_id format. Must be a valid UUID."}, 400

def _calculate_topic_opportunity_score(topic):
    """Calculate opportunity score for a topic"""
    viral_weight = topic["viral_potential"] * 0.4
    volume_weight = {"High": 30, "Medium": 20, "Low": 10}.get(topic["search_volume"], 20) * 0.3
    competition_weight = {"Low": 30, "Medium": 20, "High": 10}.get(topic["competition"], 20) * 0.3
    return round(viral_weight + volume_weight + competition_weight)

def _get_topic_priority_level(viral_potential):
    """Get priority level based on viral potential"""
    if viral_potential >= 80:
        return "High"
    elif viral_potential >= 60:
        return "Medium"
    else:
        return "Low"

def _get_difficulty_level(score):
    """Get difficulty level from score"""
    if score >= 80:
        return 'Expert'
    elif score >= 60:
        return 'Advanced'
    elif score >= 40:
        return 'Intermediate'
    else:
        return 'Beginner'

def _get_difficulty_color(score):
    """Get color for difficulty level"""
    if score >= 80:
        return '#ff4444'  # Expert - red
    elif score >= 60:
        return '#ff8800'  # Advanced - orange
    elif score >= 40:
        return '#ffaa00'  # Intermediate - yellow
    else:
        return '#44aa44'  # Beginner - green

def _is_recent_analysis(created_at):
    """Check if analysis is recent (within 7 days)"""
    if not created_at:
        return False
    
    try:
        from datetime import datetime, timedelta
        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return datetime.now().replace(tzinfo=created_date.tzinfo) - created_date <= timedelta(days=7)
    except:
        return False

# ============================================================================
# MAIN TREND RESEARCH ENDPOINT
# ============================================================================

@app.route('/api/v2/enhanced-trend-research', methods=['POST'])
async def enhanced_trend_research():
    try:
        print("📡 Received request from Noodl")
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400
        
        print(f"🎯 Topic: {data.get('topic', 'N/A')}")
        print(f"🤖 LLM Provider: {data.get('llm_config', {}).get('provider', 'N/A')}")
        
        # EXTRACT AND VALIDATE USER_ID
        user_id, error_response, status_code = extract_and_validate_user_id(data)
        if error_response:
            return jsonify(error_response), status_code
        
        print(f"👤 User ID: {user_id}")
        
        # Validate required fields
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({
                "success": False,
                "error": "Topic is required"
            }), 400
        
        llm_config = data.get('llm_config', {})
        if not llm_config.get('api_key'):
            return jsonify({
                "success": False,
                "error": "LLM API key is required in llm_config"
            }), 400
        
        # Validate LLM provider
        supported_providers = ['openai', 'anthropic', 'deepseek', 'gemini', 'kimi']
        provider = llm_config.get('provider', 'openai').lower()
        if provider not in supported_providers:
            return jsonify({
                "success": False,
                "error": f"Unsupported LLM provider: {provider}. Supported: {supported_providers}"
            }), 400
        
        # Import trend research integration and affiliate research
        try:
            from fixed_trend_research import TrendResearchIntegration
        except ImportError as e:
            try:
                # Fallback to original
                from trend_research_integration import TrendResearchIntegration
                print("⚠️ Using original trend_research_integration.py (not the fixed version)")
            except ImportError as e2:
                return jsonify({
                    "success": False,
                    "error": f"Import failed: {e2}. Make sure trend_research_integration.py is in the same directory."
                }), 500
        
        # Import Linkup-based affiliate research
        try:
            from affiliate_research_api_updated import linkup_affiliate_api as affiliate_research
            affiliate_research_available = True
            print("✅ Linkup affiliate research module loaded")
        except ImportError as e:
            print("⚠️ Affiliate research module not available, proceeding without profitability check")
            affiliate_research_available = False
        
        # Setup configuration
        config = {
            'linkup_api_key': data.get('linkup_api_key'),
            'google_trends_api_key': data.get('google_trends_api_key')
        }
        
        # Create integration instance
        integration = TrendResearchIntegration(config)
        
        # Initialize RLS Supabase storage
        supabase_storage = ImprovedSupabaseStorage()
        
        print("🔍 Starting enhanced trend research analysis...")
        
        # PHASE 0: AFFILIATE OFFER RESEARCH (NEW FIRST STEP)
        print("💰 PHASE 0: Researching affiliate offers for profitability...")
        
        affiliate_result = None
        should_proceed = True
        cancellation_reason = None
        
        if affiliate_research_available:
            try:
                async def run_affiliate_research():
                    return await affiliate_research.research_affiliate_offers(
                        topic=topic,
                        user_id=user_id,
                        min_commission_threshold=data.get('min_affiliate_score', 30)
                    )
                
                affiliate_result = await asyncio.wait_for(
                    run_affiliate_research(),
                    timeout=30  # 30 second timeout for affiliate research
                )
                
                # Check if affiliate research was successful
                if not affiliate_result.get('success', False):
                    print(f"⚠️ Affiliate research failed: {affiliate_result.get('error', 'Unknown error')}, proceeding with trend analysis")
                    affiliate_result = None
                    should_proceed = True  # Allow to proceed even if affiliate research fails
                else:
                    # Store affiliate research results in Supabase
                    print("💾 Storing affiliate research results...")
                    try:
                        # Import the storage module
                        from supabase_affiliate_storage import affiliate_storage
                        
                        # Store the complete affiliate research
                        storage_result = await affiliate_storage.store_affiliate_research(
                            topic=topic,
                            user_id=user_id,
                            research_data=affiliate_result['affiliate_research']
                        )
                        print(f"✅ Affiliate research stored successfully: {storage_result}")
                        
                        # Update affiliate_result with storage info
                        affiliate_result['storage_id'] = storage_result
                        
                    except Exception as e:
                        print(f"⚠️ Failed to store affiliate research: {e}")
                        # Don't fail the whole process if storage fails
                    
                    # Access profitability analysis safely
                    profitability = affiliate_result.get('affiliate_research', {}).get('profitability_analysis', {})
                    score = profitability.get('score', 0)
                    level = profitability.get('level', 'unknown')
                    
                    should_proceed = int(score) >= int(data.get('min_affiliate_score', 30))
                    
                    if not should_proceed:
                        warning_message = f"⚠️ Topic profitability score {score} below threshold {data.get('min_affiliate_score', 30)}"
                        print(f"🔄 {warning_message} - Continuing with caution")
                        
                        # Continue with analysis but provide warnings and suggestions
                        affiliate_result['profitability_analysis']['warning'] = warning_message
                        affiliate_result['profitability_analysis']['suggestions'] = [
                            "Try more specific subtopics (e.g., 'smart home security cameras' instead of 'home security')",
                            "Explore related high-commission niches (e.g., 'home automation systems', 'security software')",
                            "Consider seasonal trends - holiday security sales spike in Q4",
                            "Focus on high-ticket items like complete security systems vs individual sensors",
                            "Research B2B opportunities - commercial security systems have higher commissions",
                            "Look for subscription-based security services with recurring commissions",
                            "Expand to related categories: insurance, home improvement, smart home hubs",
                            "Check for high-commission software/tools used in security industry"
                        ]
                        
                        # Always proceed but flag as low profitability
                        should_proceed = True
                        affiliate_result['profitability_analysis']['force_continue'] = True
                    else:
                        print(f"✅ Topic approved - profitability score: {score}")
                        
            except asyncio.TimeoutError:
                print("⚠️ Affiliate research timed out, proceeding with trend analysis")
            except Exception as e:
                print(f"⚠️ Affiliate research failed: {e}, proceeding with trend analysis")
        else:
            print("⚠️ Affiliate research unavailable, proceeding directly to trend analysis")
        
        # Run the analysis with timeout handling
 
## &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

        async def run_analysis():
            try:
                # Perform trend research with total timeout
                result = await asyncio.wait_for(
                    integration.enhanced_trend_research_for_blog_analyzer(
                        topic=topic,
                        collection_name=data.get('collection', 'default'),
                        llm_config=llm_config,
                        focus_area=data.get('focus_area', 'general'),
                        target_audience=data.get('target_audience', 'professional'),
                        linkup_api_key=data.get('linkup_api_key'),
                        google_trends_api_key=data.get('google_trends_api_key')
                    ),
                    timeout=150  # 2.5 minute total timeout
                )
                
                # Enhanced: Save results to Supabase WITH USER_ID
                print(f"💾 Saving enhanced results to Supabase for user: {user_id}")
                trend_analysis_id = await supabase_storage.save_trend_analysis_results(
                    trend_result=result,
                    user_id=user_id,
                    topic=topic,
                    target_audience=data.get('target_audience', 'professional'),
                    focus_area=data.get('focus_area', 'general')
                )
                
                # CRITICAL FIX: Save PyTrends data to analysis metadata
                if result.get('pytrends_analysis'):
                    print("🔧 Saving PyTrends data to analysis metadata...")
                    try:
                        # Update the analysis record with PyTrends data
                        pytrends_metadata = {
                            "pytrends_analysis": result['pytrends_analysis'],
                            "pytrends_enhanced": result.get('pytrends_enhanced', False),
                            "pytrends_timestamp": datetime.now().isoformat(),
                            "confidence_score": result.get('confidence_score', 85)
                        }
                        
                        # Update the trend analysis with PyTrends metadata
                        update_result = supabase_storage._execute_query(
                            'PATCH',
                            f'trend_analyses?id=eq.{trend_analysis_id}&user_id=eq.{user_id}',
                            {"metadata": pytrends_metadata, "updated_at": datetime.now().isoformat()}
                        )
                        
                        if update_result['success']:
                            print("✅ PyTrends data saved to Supabase metadata")
                        else:
                            print(f"⚠️ Failed to save PyTrends metadata: {update_result.get('error')}")
                            
                    except Exception as e:
                        print(f"⚠️ Error saving PyTrends metadata: {e}")
                
                # Add enhanced Supabase metadata to result
                result['trend_analysis_id'] = trend_analysis_id
                result['supabase_saved'] = True
                result['storage_timestamp'] = datetime.now().isoformat()
                result['enhanced_storage'] = True
                result['user_id'] = user_id
                result['pytrends_data_saved'] = bool(result.get('pytrends_analysis'))
                
                print(f"✅ Enhanced results saved to Supabase with ID: {trend_analysis_id}")
                print(f"📊 PyTrends data included: {bool(result.get('pytrends_analysis'))}")
                
                return result
                
            except asyncio.TimeoutError:
                print("❌ Analysis timed out after 2.5 minutes")
                raise Exception("Analysis timed out. Please try with a more specific topic or check your API keys.")
            except Exception as e:
                print(f"❌ Analysis failed: {e}")
                raise
        
        # Execute async analysis using existing event loop
        try:
            # Check if we're already in an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in a running loop, use async_to_sync pattern
                import nest_asyncio
                nest_asyncio.apply()
                result = loop.run_until_complete(run_analysis())
            else:
                # No loop running, use normal approach
                result = loop.run_until_complete(run_analysis())
        except RuntimeError:
            # No event loop in current context
            result = asyncio.run(run_analysis())
        
        print("✅ Enhanced analysis completed successfully")
        
        # Enhanced response with PyTrends quality metrics and affiliate research
        response_data = {
            "success": True,
            "trend_research_data": result,
            "affiliate_research_data": affiliate_result,
            "metadata": {
                "topic": topic,
                "focus_area": data.get('focus_area', 'general'),
                "target_audience": data.get('target_audience', 'professional'),
                "collection": data.get('collection', 'default'),
                "trend_analysis_id": result.get('trend_analysis_id'),
                "user_id": user_id,
                "supabase_saved": True,
                "enhanced_storage": True,
                "confidence_score": result.get('confidence_score', 0),
                "enhanced_research": result.get('enhanced_trend_research', False),
                "strategic_intelligence": result.get('strategic_intelligence', False),
                "pytrends_enhanced": result.get('pytrends_enhanced', False),
                "pytrends_data_available": bool(result.get('pytrends_analysis')),
                "affiliate_research_completed": affiliate_result is not None,
                "profitability_score": affiliate_result.get('affiliate_research', {}).get('profitability_analysis', {}).get('score', 0) if affiliate_result else None,
                "profitability_level": affiliate_result.get('affiliate_research', {}).get('profitability_analysis', {}).get('level', 'unknown') if affiliate_result else None,
                "profitability_warning": affiliate_result.get('affiliate_research', {}).get('profitability_analysis', {}).get('warning') if affiliate_result else None,
                "profitability_suggestions": affiliate_result.get('affiliate_research', {}).get('profitability_analysis', {}).get('suggestions') if affiliate_result else None,
                "force_continue": affiliate_result.get('affiliate_research', {}).get('profitability_analysis', {}).get('force_continue', False) if affiliate_result else False,
                "fallback_mode": result.get('fallback_mode', False),
                "processing_time": result.get('processing_time', 0),
                "timestamp": datetime.now().isoformat(),
                "llm_provider": provider,
                "api_version": "v2_enhanced_rls_pytrends_affiliate"
            },
            "quality_indicators": {
                "data_richness": len(result.get('trending_topics', [])) + len(result.get('content_opportunities', [])),
                "analysis_depth": "enhanced" if result.get('strategic_intelligence', False) else "standard",
                "market_intelligence": bool(result.get('market_insights', {}).get('highest_opportunity_audiences')),
                "pytrends_integration": result.get('pytrends_enhanced', False),
                "affiliate_integration": affiliate_result is not None,
                "geographic_insights": len(result.get('pytrends_analysis', {}).get('geographic_insights', {}).get('global_hotspots', [])),
                "actionable_insights": len(result.get('pytrends_analysis', {}).get('actionable_insights', [])),
                "ready_for_phase2": bool(result.get('trend_analysis_id')),
                "profitable_topic": affiliate_result.get('affiliate_research', {}).get('profitability_analysis', {}).get('level', 'unknown') in ['good', 'excellent'] if affiliate_result else None,
                "low_profitability_warning": bool(affiliate_result and affiliate_result.get('affiliate_research', {}).get('profitability_analysis', {}).get('warning')),
                "profitability_score": affiliate_result.get('affiliate_research', {}).get('profitability_analysis', {}).get('score', 0) if affiliate_result else None
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        
        error_response = {
            "success": False,
            "error": f"Analysis failed: {str(e)}",
            "error_type": type(e).__name__,
            "troubleshooting": {
                "common_causes": [
                    "Invalid or missing API key",
                    "Invalid or missing user_id",
                    "Network connectivity issues",
                    "LLM service unavailable",
                    "Topic too broad or complex"
                ],
                "suggested_actions": [
                    "Verify your API key is correct and active",
                    "Ensure user_id is a valid UUID from Noodl authentication",
                    "Try a more specific topic",
                    "Check your internet connection",
                    "Wait a moment and try again"
                ]
            }
        }
        
        # Determine appropriate HTTP status code
        if "timeout" in str(e).lower():
            return jsonify(error_response), 408  # Request Timeout
        elif "api key" in str(e).lower():
            return jsonify(error_response), 401  # Unauthorized
        elif "user_id" in str(e).lower() or "uuid" in str(e).lower():
            return jsonify(error_response), 400  # Bad Request
        elif "not found" in str(e).lower():
            return jsonify(error_response), 404  # Not Found
        else:
            return jsonify(error_response), 500  # Internal Server Error

# ============================================================================
# RLS-ENABLED ENDPOINTS FOR PHASE 2 INTEGRATION
# ============================================================================

@app.route('/api/v2/trend-analyses', methods=['GET'])
def get_trend_analyses():
    """Get list of saved trend analyses for authenticated user"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate user_id
        try:
            uuid.UUID(user_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id format. Must be a valid UUID."
            }), 400
        
        supabase_storage = ImprovedSupabaseStorage()
        
        # Get query parameters
        limit = int(request.args.get('limit', 20))
        
        # Get user's trend analyses only (RLS filtered)
        analyses = supabase_storage.get_all_trend_analyses(limit=limit, user_id=user_id)
        
        # Add enhanced metadata to each analysis
        enhanced_analyses = []
        for analysis in analyses:
            enhanced_analysis = analysis.copy()
            enhanced_analysis.update({
                "has_trending_topics": bool(analysis.get('metadata', {}).get('trending_topics_count', 0)),
                "has_opportunities": bool(analysis.get('metadata', {}).get('opportunities_count', 0)),
                "confidence_score": analysis.get('metadata', {}).get('confidence_score', 0),
                "created_date": analysis.get('created_at', '').split('T')[0] if analysis.get('created_at') else '',
                "is_recent": _is_recent_analysis(analysis.get('created_at', ''))
            })
            enhanced_analyses.append(enhanced_analysis)
        
        return jsonify({
            "success": True,
            "trend_analyses": enhanced_analyses,
            "count": len(enhanced_analyses),
            "user_id": user_id,
            "metadata": {
                "limit": limit,
                "user_filtered": True,
                "timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        print(f"❌ Error getting trend analyses: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get trend analyses: {str(e)}"
        }), 500


@app.route('/api/v2/trend-analysis/<analysis_id>', methods=['GET'])
def get_trend_analysis_details(analysis_id):
    """Get detailed trend analysis data for authenticated user"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id or analysis_id format. Must be valid UUIDs."
            }), 400
        
        supabase_storage = ImprovedSupabaseStorage()
        
        # Get complete trend analysis data (RLS will ensure user can only access their own)
        async def get_data():
            return await supabase_storage.get_trend_analysis_for_phase2(analysis_id, user_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            data = loop.run_until_complete(get_data())
        finally:
            loop.close()
        
        # Add enhanced metadata
        enhanced_metadata = {
            "has_pytrends_data": bool(data.get('pytrends_data')),
            "data_completeness": {
                "trending_topics": len(data.get('trending_topics', [])),
                "content_opportunities": len(data.get('content_opportunities', [])),
                "keyword_intelligence": bool(data.get('keyword_intelligence')),
                "market_insights": bool(data.get('market_insights')),
                "pytrends_insights": len(data.get('pytrends_data', {}))
            },
            "quality_score": data.get('analysis_info', {}).get('metadata', {}).get('confidence_score', 0),
            "user_id": user_id,
            "access_verified": True
        }
        
        return jsonify({
            "success": True,
            "trend_analysis": data,
            "enhanced_metadata": enhanced_metadata
        })
        
    except Exception as e:
        print(f"❌ Error getting trend analysis details: {e}")
        
        # Check if it's an access denied error
        if "not found or access denied" in str(e):
            return jsonify({
                "success": False,
                "error": "Trend analysis not found or access denied"
            }), 403
        
        return jsonify({
            "success": False,
            "error": f"Failed to get trend analysis: {str(e)}"
        }), 500

@app.route('/api/v2/trend-analysis/<analysis_id>/topics', methods=['GET'])
def get_trending_topics(analysis_id):
    """Get trending topics with enhanced filtering and sorting for authenticated user"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id or analysis_id format"
            }), 400
        
        supabase_storage = ImprovedSupabaseStorage()
        
        # Get query parameters
        selected_only = request.args.get('selected_only', 'false').lower() == 'true'
        sort_by = request.args.get('sort_by', 'viral_potential')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query with user filtering (RLS)
        filter_params = f"trend_analysis_id=eq.{analysis_id}&user_id=eq.{user_id}"
        
        if selected_only:
            filter_params += "&selected=eq.true"
        
        # Apply sorting
        ascending = sort_order.lower() == 'asc'
        order_param = f"&order={sort_by}.{'asc' if ascending else 'desc'}"
        
        endpoint = f"trending_topics?{filter_params}&select=*{order_param}"
        response = supabase_storage._execute_query('GET', endpoint)
        
        if not response['success']:
            raise Exception(f"Failed to get trending topics: {response.get('error')}")
        
        # Format topics for frontend consumption with enhanced data
        formatted_topics = []
        for topic in response['data']:
            additional_data = topic.get("additional_data", {})
            
            formatted_topic = {
                "id": topic["id"],
                "title": topic["title"],
                "viral_potential": topic["viral_potential"],
                "keywords": topic["keywords"],
                "search_volume": topic["search_volume"],
                "competition": topic["competition"],
                "selected": topic["selected"],
                "additional_data": additional_data,
                "created_at": topic["created_at"],
                "user_id": topic.get("user_id"),
                
                # Enhanced fields
                "opportunity_score": _calculate_topic_opportunity_score(topic),
                "is_high_potential": topic["viral_potential"] >= 80,
                "is_quick_win": topic["viral_potential"] >= 60 and topic["competition"] == "Low",
                "priority_level": _get_topic_priority_level(topic["viral_potential"])
            }
            formatted_topics.append(formatted_topic)
        
        return jsonify({
            "success": True,
            "trending_topics": formatted_topics,
            "count": len(formatted_topics),
            "user_id": user_id,
            "analysis_id": analysis_id,
            "filters_applied": {
                "selected_only": selected_only,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        })
        
    except Exception as e:
        print(f"❌ Error getting trending topics: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get trending topics: {str(e)}"
        }), 500

@app.route('/api/v2/trend-analysis/<analysis_id>/opportunities', methods=['GET'])
def get_content_opportunities(analysis_id):
    """Get content opportunities with enhanced filtering for authenticated user"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id or analysis_id format"
            }), 400
        
        supabase_storage = ImprovedSupabaseStorage()
        
        # Get query parameters
        selected_only = request.args.get('selected_only', 'false').lower() == 'true'
        format_filter = request.args.get('format')
        engagement_filter = request.args.get('engagement')
        
        # Build query with user filtering (RLS)
        filter_params = f"trend_analysis_id=eq.{analysis_id}&user_id=eq.{user_id}"
        
        if selected_only:
            filter_params += "&selected=eq.true"
        
        if format_filter:
            filter_params += f"&format=eq.{format_filter}"
            
        if engagement_filter:
            filter_params += f"&engagement_potential=eq.{engagement_filter}"
        
        endpoint = f"content_opportunities?{filter_params}&select=*&order=difficulty.asc"
        response = supabase_storage._execute_query('GET', endpoint)
        
        if not response['success']:
            raise Exception(f"Failed to get content opportunities: {response.get('error')}")
        
        # Format opportunities for frontend with enhanced data
        formatted_opportunities = []
        for opp in response['data']:
            additional_data = opp.get("additional_data", {})
            
            formatted_opp = {
                "id": opp["id"],
                "title": opp["title"],
                "format": opp["format"],
                "difficulty": opp["difficulty"],
                "engagement_potential": opp["engagement_potential"],
                "selected": opp["selected"],
                "additional_data": additional_data,
                "created_at": opp["created_at"],
                "user_id": opp.get("user_id"),
                
                # Enhanced fields
                "format_display": opp["format"].replace('_', ' ').title(),
                "difficulty_level": _get_difficulty_level(opp["difficulty"]),
                "difficulty_color": _get_difficulty_color(opp["difficulty"]),
                "time_investment": additional_data.get("time_investment", "2-3 weeks")
            }
            formatted_opportunities.append(formatted_opp)
        
        return jsonify({
            "success": True,
            "content_opportunities": formatted_opportunities,
            "count": len(formatted_opportunities),
            "user_id": user_id,
            "analysis_id": analysis_id,
            "filters_applied": {
                "selected_only": selected_only,
                "format_filter": format_filter,
                "engagement_filter": engagement_filter
            }
        })
        
    except Exception as e:
        print(f"❌ Error getting content opportunities: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get content opportunities: {str(e)}"
        }), 500

@app.route('/api/v2/topics/<topic_id>/select', methods=['PATCH'])
def toggle_topic_selection(topic_id):
    """Toggle trending topic selection for authenticated user"""
    try:
        data = request.get_json()
        
        # Extract and validate user_id
        user_id, error_response, status_code = extract_and_validate_user_id(data)
        if error_response:
            return jsonify(error_response), status_code
        
        selected = data.get('selected', True) if data else True
        
        # Validate topic_id
        try:
            uuid.UUID(topic_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid topic_id format"
            }), 400
        
        supabase_storage = ImprovedSupabaseStorage()
        
        # Update selection with user filtering (RLS ensures user can only update their own topics)
        update_data = {
            "selected": selected,
            "updated_at": datetime.now().isoformat()
        }
        
        endpoint = f"trending_topics?id=eq.{topic_id}&user_id=eq.{user_id}"
        response = supabase_storage._execute_query('PATCH', endpoint, update_data)
        
        if not response['success']:
            raise Exception(f"Failed to update topic selection: {response.get('error')}")
        
        if not response['data']:
            return jsonify({
                "success": False,
                "error": "Topic not found or access denied"
            }), 403
        
        return jsonify({
            "success": True,
            "topic_id": topic_id,
            "user_id": user_id,
            "selected": selected,
            "updated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error updating topic selection: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to update topic selection: {str(e)}"
        }), 500

@app.route('/api/v2/opportunities/<opportunity_id>/select', methods=['PATCH'])
def toggle_opportunity_selection(opportunity_id):
    """Toggle content opportunity selection for authenticated user"""
    try:
        data = request.get_json()
        
        # Extract and validate user_id
        user_id, error_response, status_code = extract_and_validate_user_id(data)
        if error_response:
            return jsonify(error_response), status_code
        
        selected = data.get('selected', True) if data else True
        
        # Validate opportunity_id
        try:
            uuid.UUID(opportunity_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid opportunity_id format"
            }), 400
        
        supabase_storage = ImprovedSupabaseStorage()
        
        # Update selection with user filtering (RLS)
        update_data = {
            "selected": selected,
            "updated_at": datetime.now().isoformat()
        }
        
        endpoint = f"content_opportunities?id=eq.{opportunity_id}&user_id=eq.{user_id}"
        response = supabase_storage._execute_query('PATCH', endpoint, update_data)
        
        if not response['success']:
            raise Exception(f"Failed to update opportunity selection: {response.get('error')}")
        
        if not response['data']:
            return jsonify({
                "success": False,
                "error": "Opportunity not found or access denied"
            }), 403
        
        return jsonify({
            "success": True,
            "opportunity_id": opportunity_id,
            "user_id": user_id,
            "selected": selected,
            "updated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error updating opportunity selection: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to update opportunity selection: {str(e)}"
        }), 500

# ============================================================================
# HEALTH AND STATUS ENDPOINTS
# ============================================================================

@app.route('/api/v2/health', methods=['GET'])
def enhanced_health_check():
    """Enhanced health check with system status"""
    try:
        # Test Supabase connection
        supabase_storage = ImprovedSupabaseStorage()
        test_query = supabase_storage._execute_query('GET', 'trend_analyses?limit=1')
        supabase_healthy = test_query['success']
        supabase_error = test_query.get('error') if not supabase_healthy else None
    except Exception as e:
        supabase_healthy = False
        supabase_error = str(e)
    
    # Check environment variables
    env_check = {
        "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
        "SUPABASE_KEY": bool(os.getenv("SUPABASE_KEY")),
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY"))
    }
    
    health_status = {
        "status": "healthy" if supabase_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "api_version": "v2_enhanced_rls",
        "components": {
            "supabase": {
                "status": "healthy" if supabase_healthy else "unhealthy",
                "error": supabase_error if not supabase_healthy else None
            },
            "environment": {
                "status": "healthy" if all(env_check.values()) else "degraded",
                "missing_vars": [k for k, v in env_check.items() if not v]
            }
        },
        "features": {
            "enhanced_trend_research": True,
            "pytrends_integration": True,
            "supabase_storage": supabase_healthy,
            "rls_support": True,
            "user_scoped_data": True,
            "phase2_ready": supabase_healthy
        }
    }
    
    status_code = 200 if supabase_healthy else 503
    return jsonify(health_status), status_code

@app.route('/')
def index():
    return jsonify({
        "service": "Enhanced Trend Research - Noodl Integration Server",
        "version": "2.2.0 RLS",
        "status": "operational",
        "features": [
            "RLS (Row Level Security) Support",
            "User-Scoped Data Access",
            "Fixed LLM Timeout Issues", 
            "Enhanced Supabase Integration", 
            "Pytrends Support",
            "Phase 2 Ready",
            "Advanced Error Handling"
        ],
        "authentication": {
            "method": "Noodl handles authentication, API expects user_id",
            "rls_enabled": True,
            "user_scoped_access": True
        },
        "endpoints": {
            "POST /api/v2/enhanced-trend-research": "Main trend research endpoint (RLS enabled)",
            "GET /api/v2/trend-analyses": "Get saved trend analyses for user",
            "GET /api/v2/trend-analysis/<id>": "Get specific trend analysis for user",
            "GET /api/v2/trend-analysis/<id>/topics": "Get trending topics for user",
            "GET /api/v2/trend-analysis/<id>/opportunities": "Get content opportunities for user",
            "PATCH /api/v2/topics/<id>/select": "Toggle topic selection for user",
            "PATCH /api/v2/opportunities/<id>/select": "Toggle opportunity selection for user",
            "GET /api/v2/health": "Enhanced health check"
        },
        "usage": {
            "authentication": "Include user_id in all requests (from Noodl authentication)",
            "example_request": {
                "url": "/api/v2/enhanced-trend-research",
                "method": "POST",
                "body": {
                    "topic": "AI marketing",
                    "user_id": "uuid-from-noodl-auth",
                    "llm_config": {
                        "provider": "openai",
                        "api_key": "your-key"
                    }
                }
            }
        }
    })

@app.route('/health')
def basic_health():
    return jsonify({
        "status": "healthy",
        "server": "enhanced_noodl_integration_rls",
        "timestamp": datetime.now().isoformat(),
        "rls_enabled": True
    })


# ============================================================================
# PHASE 2 ENDPOINTS - Add these to your existing noodl_server.py
# ============================================================================
@app.route('/api/v2/generate-blog-ideas/<analysis_id>', methods=['POST'])
async def generate_blog_ideas_endpoint(analysis_id):
    """
    CORRECTED: Phase 2 blog idea generation with optional Linkup integration
    """
    try:
        print(f"📡 Received blog idea generation request for analysis: {analysis_id}")
        
        # Get request data
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
        
        # Validate analysis_id
        try:
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid analysis_id format. Must be a valid UUID."
            }), 400
        
        # CORRECTED: Extract Linkup API key (OPTIONAL parameter)
        linkup_api_key = data.get('linkup_api_key')  # This should be optional
        print(f"🔍 Linkup API KEY: {linkup_api_key}")
        linkup_enabled = bool(linkup_api_key)
        
        if linkup_enabled:
            print(f"🔍 Linkup research enabled for analysis: {analysis_id}")
        
        # REMOVED: Don't require Linkup key - it should be optional
        # The original code incorrectly required the Linkup key
        
        # Validate LLM configuration (unchanged)
        llm_config = data.get('llm_config', {})
        if not llm_config.get('api_key'):
            return jsonify({
                "success": False,
                "error": "LLM API key is required in llm_config"
            }), 400
        
        # Validate LLM provider (unchanged)
        supported_providers = ['openai', 'anthropic', 'deepseek', 'gemini', 'kimi']
        provider = llm_config.get('provider', 'openai').lower()
        if provider not in supported_providers:
            return jsonify({
                "success": False,
                "error": f"Unsupported LLM provider: {provider}. Supported: {supported_providers}"
            }), 400
        
        print(f"🎯 Generating blog ideas for analysis: {analysis_id}")
        print(f"👤 User ID: {user_id}")
        print(f"🤖 LLM Provider: {provider}")
        print(f"🔗 Linkup Enabled: {linkup_enabled}")
        
        # Optional generation configuration
        generation_config = data.get('generation_config', {})
        
        # Initialize blog idea generation engine
        engine = BlogIdeaGenerationEngine()
        
        # Initialize Phase 2 storage
        phase2_storage = Phase2SupabaseStorage()
        
        print("🚀 Starting blog idea generation...")
        
        # Run the generation with timeout handling
        async def run_generation():
            try:
                # CORRECTED: Generate comprehensive blog ideas with optional Linkup
                result = await asyncio.wait_for(
                    engine.generate_comprehensive_blog_ideas(
                        analysis_id=analysis_id,
                        user_id=user_id,
                        llm_config=llm_config,
                        generation_config=generation_config,
                        linkup_api_key=linkup_api_key  # CORRECTED: Pass as optional parameter
                    ),
                    timeout=240  # INCREASED: 4 minute timeout to account for Linkup research
                )
                
                # Save results to Supabase
                print(f"💾 Saving blog generation results to Supabase...")
                generation_result_id = await phase2_storage.save_blog_generation_results(
                    analysis_id=analysis_id,
                    user_id=user_id,
                    generation_result=result,
                    llm_config=llm_config
                )
                
                # Add storage metadata to result
                result['storage_metadata'] = {
                    'generation_result_id': generation_result_id,
                    'supabase_saved': True,
                    'phase2_storage_timestamp': datetime.now().isoformat()
                }
                
                print(f"✅ Blog idea generation completed: {len(result.get('blog_ideas', []))} ideas generated")
                return result
                
            except asyncio.TimeoutError:
                print("❌ Blog idea generation timed out after 4 minutes")
                raise Exception("Blog idea generation timed out. Please try again or reduce the scope.")
            except Exception as e:
                print(f"❌ Blog idea generation failed: {e}")
                raise
        
        # Execute async generation with proper event loop handling
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Use nest_asyncio to handle running loop
                import nest_asyncio
                nest_asyncio.apply()
                result = loop.run_until_complete(run_generation())
            else:
                result = loop.run_until_complete(run_generation())
        except RuntimeError as e:
            if "event loop" in str(e).lower():
                # Fallback: create new loop if no loop exists
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(run_generation())
                finally:
                    loop.close()
            else:
                raise
        
        print("✅ Blog idea generation completed successfully")
        
        # ENHANCED: Add Linkup info to response metadata
        response_data = {
            "success": True,
            "blog_generation_data": result,
            "metadata": {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "total_blog_ideas": len(result.get('blog_ideas', [])),
                "average_quality_score": result.get('generation_metadata', {}).get('average_quality_score', 0),
                "processing_time_seconds": result.get('generation_metadata', {}).get('processing_time_seconds', 0),
                "llm_provider": provider,
                "generation_timestamp": datetime.now().isoformat(),
                "phase2_version": "v1.0",
                "storage_saved": bool(result.get('storage_metadata', {}).get('supabase_saved')),
                "calendar_generated": bool(result.get('content_calendar')),
                "insights_generated": bool(result.get('strategic_insights')),
                
                # NEW: Linkup research metadata
                "linkup_research_enabled": linkup_enabled,
                "linkup_research_included": bool(result.get('linkup_insights'))
            },
            "quality_metrics": {
                "excellent_ideas_count": len([i for i in result.get('blog_ideas', []) if i.get('overall_quality_score', 0) >= 80]),
                "high_quality_ideas_count": len([i for i in result.get('blog_ideas', []) if i.get('overall_quality_score', 0) >= 70]),
                "format_diversity": len(set(i.get('content_format', '') for i in result.get('blog_ideas', []))),
                "avg_viral_potential": sum(i.get('viral_potential_score', 0) for i in result.get('blog_ideas', [])) / len(result.get('blog_ideas', [])) if result.get('blog_ideas') else 0,
                "avg_seo_score": sum(i.get('seo_optimization_score', 0) for i in result.get('blog_ideas', [])) / len(result.get('blog_ideas', [])) if result.get('blog_ideas') else 0
            }
        }
        
        # ENHANCED: Add detailed Linkup insights to response if available
        if linkup_enabled and result.get('linkup_insights'):
            linkup_insights = result['linkup_insights']
            response_data["metadata"].update({
                "linkup_searches_conducted": linkup_insights.get('search_results_analyzed', 0),
                "content_gaps_found": linkup_insights.get('total_gaps_identified', 0),
                "research_confidence_score": linkup_insights.get('research_confidence_score', 0),
                "competitor_insights_available": bool(linkup_insights.get('competitor_insights', {}).get('top_competitors'))
            })
            
            # Add Linkup insights to response data
            response_data["linkup_research_summary"] = {
                "gaps_identified": linkup_insights.get('total_gaps_identified', 0),
                "opportunities_found": linkup_insights.get('total_opportunities_found', 0),
                "top_competitors": [comp.get('domain', '') for comp in linkup_insights.get('competitor_insights', {}).get('top_competitors', [])[:3]],
                "market_intelligence": linkup_insights.get('market_intelligence', {}),
                "research_confidence": linkup_insights.get('research_confidence_score', 0)
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Blog idea generation error: {e}")
        import traceback
        traceback.print_exc()
        
        error_response = {
            "success": False,
            "error": f"Blog idea generation failed: {str(e)}",
            "error_type": type(e).__name__,
            "troubleshooting": {
                "common_causes": [
                    "Invalid analysis ID or user access denied",
                    "Phase 1 analysis not completed or no selections made",
                    "Invalid or missing LLM API key",
                    "Linkup API key invalid or rate limited",
                    "Network connectivity issues"
                ],
                "suggested_actions": [
                    "Verify Phase 1 analysis completed successfully",
                    "Ensure trending topics and opportunities are selected",
                    "Check LLM API key is correct and active",
                    "Verify Linkup API key if using research enhancement",
                    "Try again with a different LLM provider"
                ]
            }
        }
        
        # Determine appropriate HTTP status code
        if "timeout" in str(e).lower():
            return jsonify(error_response), 408  # Request Timeout
        elif "api key" in str(e).lower():
            return jsonify(error_response), 401  # Unauthorized
        elif "access denied" in str(e).lower() or "not found" in str(e).lower():
            return jsonify(error_response), 403  # Forbidden
        elif "user_id" in str(e).lower() or "uuid" in str(e).lower():
            return jsonify(error_response), 400  # Bad Request
        else:
            return jsonify(error_response), 500  # Internal Server Error

@app.route('/api/v2/blog-ideas/<analysis_id>', methods=['GET'])
def get_blog_ideas_endpoint(analysis_id):
    """Get generated blog ideas with filtering and sorting"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id or analysis_id format. Must be valid UUIDs."
            }), 400
        
        # Extract filters from query parameters
        filters = {}
        
        # Content format filter
        if request.args.get('content_format'):
            filters['content_format'] = request.args.get('content_format')
        
        # Quality threshold filter
        if request.args.get('min_quality_score'):
            try:
                filters['min_quality_score'] = int(request.args.get('min_quality_score'))
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "min_quality_score must be an integer"
                }), 400
        
        # Selected only filter
        if request.args.get('selected_only', 'false').lower() == 'true':
            filters['selected_only'] = True
        
        # Priority level filter
        if request.args.get('priority_level'):
            filters['priority_level'] = request.args.get('priority_level')
        
        # Sorting options
        if request.args.get('sort_by'):
            filters['sort_by'] = request.args.get('sort_by')
        
        if request.args.get('sort_order'):
            filters['sort_order'] = request.args.get('sort_order')
        
        # Limit
        if request.args.get('limit'):
            try:
                filters['limit'] = int(request.args.get('limit'))
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "limit must be an integer"
                }), 400
        
        phase2_storage = Phase2SupabaseStorage()
        
        # Get blog ideas with filters
        async def get_ideas():
            return await phase2_storage.get_blog_ideas(analysis_id, user_id, filters)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            blog_ideas = loop.run_until_complete(get_ideas())
        finally:
            loop.close()
        
        # Enhanced formatting for frontend consumption
        formatted_ideas = []
        for idea in blog_ideas:
            formatted_idea = idea.copy()
            
            # Add computed fields for frontend
            formatted_idea.update({
                "quality_tier": _determine_quality_tier(idea.get("overall_quality_score", 0)),
                "difficulty_color": _get_difficulty_color_by_level(idea.get("difficulty_level", "intermediate")),
                "format_display": idea.get("content_format", "").replace('_', ' ').title(),
                "estimated_effort": _estimate_content_effort(idea.get("estimated_word_count", 2500), idea.get("difficulty_level", "intermediate")),
                "seo_strength": _assess_seo_strength(idea.get("seo_optimization_score", 0)),
                "viral_prediction": _assess_viral_prediction(idea.get("viral_potential_score", 0))
            })
            
            formatted_ideas.append(formatted_idea)
        
        return jsonify({
            "success": True,
            "blog_ideas": formatted_ideas,
            "count": len(formatted_ideas),
            "analysis_id": analysis_id,
            "user_id": user_id,
            "filters_applied": filters,
            "summary_stats": {
                "total_ideas": len(formatted_ideas),
                "selected_count": len([i for i in formatted_ideas if i.get("selected", False)]),
                "average_quality": round(sum(i.get("overall_quality_score", 0) for i in formatted_ideas) / len(formatted_ideas), 1) if formatted_ideas else 0,
                "format_breakdown": _calculate_format_breakdown(formatted_ideas),
                "quality_breakdown": _calculate_quality_breakdown(formatted_ideas)
            }
        })
        
    except Exception as e:
        print(f"❌ Error getting blog ideas: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get blog ideas: {str(e)}"
        }), 500


@app.route('/api/v2/blog-ideas/<idea_id>/select', methods=['PATCH'])
def toggle_blog_idea_selection_endpoint(idea_id):
    """Select/deselect blog ideas and update management fields"""
    try:
        data = request.get_json()
        
        # Extract and validate user_id
        user_id, error_response, status_code = extract_and_validate_user_id(data)
        if error_response:
            return jsonify(error_response), status_code
        
        # Validate idea_id
        try:
            uuid.UUID(idea_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid idea_id format. Must be a valid UUID."
            }), 400
        
        # Extract update fields
        selected = data.get('selected', True)
        priority_level = data.get('priority_level')
        scheduled_date = data.get('scheduled_publish_date')
        notes = data.get('notes')
        
        # Validate priority level if provided
        if priority_level and priority_level not in ['high', 'medium', 'low']:
            return jsonify({
                "success": False,
                "error": "priority_level must be 'high', 'medium', or 'low'"
            }), 400
        
        phase2_storage = Phase2SupabaseStorage()
        
        # Update blog idea selection
        async def update_selection():
            return await phase2_storage.update_blog_idea_selection(
                idea_id=idea_id,
                user_id=user_id,
                selected=selected,
                priority_level=priority_level,
                scheduled_date=scheduled_date,
                notes=notes
            )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(update_selection())
        finally:
            loop.close()
        
        if not success:
            return jsonify({
                "success": False,
                "error": "Blog idea not found or access denied"
            }), 403
        
        return jsonify({
            "success": True,
            "idea_id": idea_id,
            "user_id": user_id,
            "selected": selected,
            "priority_level": priority_level,
            "scheduled_date": scheduled_date,
            "updated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error updating blog idea selection: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to update blog idea selection: {str(e)}"
        }), 500


@app.route('/api/v2/blog-ideas/<idea_id>', methods=['GET'])
def get_blog_idea_details_endpoint(idea_id):
    """Get detailed information for a specific blog idea"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(idea_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id or idea_id format"
            }), 400
        
        phase2_storage = Phase2SupabaseStorage()
        
        # Get blog idea details
        async def get_idea():
            return await phase2_storage.get_blog_idea_by_id(idea_id, user_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            blog_idea = loop.run_until_complete(get_idea())
        finally:
            loop.close()
        
        if not blog_idea:
            return jsonify({
                "success": False,
                "error": "Blog idea not found or access denied"
            }), 404
        
        # Enhanced formatting with detailed analysis
        enhanced_idea = blog_idea.copy()
        enhanced_idea.update({
            "quality_tier": _determine_quality_tier(blog_idea.get("overall_quality_score", 0)),
            "detailed_analysis": {
                "seo_analysis": _generate_seo_analysis(blog_idea),
                "content_analysis": _generate_content_analysis(blog_idea),
                "business_analysis": _generate_business_analysis(blog_idea),
                "implementation_guide": _generate_implementation_guide(blog_idea)
            },
            "optimization_suggestions": _generate_optimization_suggestions(blog_idea)
        })
        
        return jsonify({
            "success": True,
            "blog_idea": enhanced_idea,
            "user_id": user_id
        })
        
    except Exception as e:
        print(f"❌ Error getting blog idea details: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get blog idea details: {str(e)}"
        }), 500


@app.route('/api/v2/content-calendar/<analysis_id>', methods=['GET'])
def get_content_calendar_endpoint(analysis_id):
    """Get content calendar with scheduling recommendations"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id or analysis_id format"
            }), 400
        
        phase2_storage = Phase2SupabaseStorage()
        
        # Get content calendar and blog ideas summary
        async def get_calendar_data():
            calendar = await phase2_storage.get_content_calendar(analysis_id, user_id)
            summary = await phase2_storage.get_blog_ideas_summary(analysis_id, user_id)
            return calendar, summary
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            content_calendar, ideas_summary = loop.run_until_complete(get_calendar_data())
        finally:
            loop.close()
        
        if not content_calendar:
            return jsonify({
                "success": False,
                "error": "Content calendar not found. Please generate blog ideas first."
            }), 404
        
        # Enhanced calendar with real-time data
        enhanced_calendar = content_calendar.copy()
        enhanced_calendar.update({
            "real_time_stats": ideas_summary,
            "implementation_timeline": _generate_implementation_timeline(content_calendar, ideas_summary),
            "resource_allocation": _calculate_resource_allocation(content_calendar, ideas_summary),
            "milestone_tracking": _generate_milestone_tracking(content_calendar)
        })
        
        return jsonify({
            "success": True,
            "content_calendar": enhanced_calendar,
            "analysis_id": analysis_id,
            "user_id": user_id,
            "calendar_metadata": {
                "generated_at": content_calendar.get("created_at"),
                "last_updated": content_calendar.get("updated_at"),
                "total_ideas_in_calendar": ideas_summary.get("total_ideas", 0),
                "selected_for_calendar": ideas_summary.get("selected_ideas", 0)
            }
        })
        
    except Exception as e:
        print(f"❌ Error getting content calendar: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get content calendar: {str(e)}"
        }), 500


@app.route('/api/v2/strategic-insights/<analysis_id>', methods=['GET'])
def get_strategic_insights_endpoint(analysis_id):
    """Get strategic insights and success predictions"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id or analysis_id format"
            }), 400
        
        phase2_storage = Phase2SupabaseStorage()
        
        # Get strategic insights
        async def get_insights():
            return await phase2_storage.get_strategic_insights(analysis_id, user_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            insights = loop.run_until_complete(get_insights())
        finally:
            loop.close()
        
        if not insights:
            return jsonify({
                "success": False,
                "error": "Strategic insights not found. Please generate blog ideas first."
            }), 404
        
        # Enhanced insights with actionable recommendations
        enhanced_insights = insights.copy()
        enhanced_insights.update({
            "actionable_recommendations": _generate_actionable_recommendations(insights),
            "risk_mitigation_strategies": _generate_risk_mitigation_strategies(insights),
            "success_optimization_tips": _generate_success_optimization_tips(insights),
            "competitive_positioning": _analyze_competitive_positioning(insights)
        })
        
        return jsonify({
            "success": True,
            "strategic_insights": enhanced_insights,
            "analysis_id": analysis_id,
            "user_id": user_id
        })
        
    except Exception as e:
        print(f"❌ Error getting strategic insights: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get strategic insights: {str(e)}"
        }), 500






@app.route('/api/v2/blog-ideas/bulk-update', methods=['PATCH'])
def bulk_update_blog_ideas_endpoint():
    """Bulk update multiple blog ideas"""
    try:
        data = request.get_json()
        
        # Extract and validate user_id
        user_id, error_response, status_code = extract_and_validate_user_id(data)
        if error_response:
            return jsonify(error_response), status_code
        
        # Get updates array
        updates = data.get('updates', [])
        if not updates or not isinstance(updates, list):
            return jsonify({
                "success": False,
                "error": "updates array is required"
            }), 400
        
        # Validate updates
        for update in updates:
            if not update.get('id'):
                return jsonify({
                    "success": False,
                    "error": "Each update must include an 'id' field"
                }), 400
            
            try:
                uuid.UUID(update['id'])
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": f"Invalid idea ID format: {update['id']}"
                }), 400
        
        phase2_storage = Phase2SupabaseStorage()
        
        # Perform bulk update
        async def bulk_update():
            return await phase2_storage.bulk_update_blog_ideas(updates, user_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            updated_count = loop.run_until_complete(bulk_update())
        finally:
            loop.close()
        
        return jsonify({
            "success": True,
            "updated_count": updated_count,
            "total_requested": len(updates),
            "user_id": user_id,
            "updated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error in bulk update: {e}")
        return jsonify({
            "success": False,
            "error": f"Bulk update failed: {str(e)}"
        }), 500


# ============================================================================
# HELPER FUNCTIONS FOR PHASE 2 ENDPOINTS
# ============================================================================

def _determine_quality_tier(quality_score: int) -> str:
    """Determine quality tier based on score"""
    if quality_score >= 85:
        return "Excellent"
    elif quality_score >= 75:
        return "High Quality"
    elif quality_score >= 65:
        return "Good"
    elif quality_score >= 55:
        return "Decent"
    else:
        return "Needs Work"


def _get_difficulty_color_by_level(difficulty_level: str) -> str:
    """Get color for difficulty level"""
    colors = {
        "beginner": "#44aa44",     # Green
        "intermediate": "#ffaa00", # Orange
        "advanced": "#ff8800",     # Dark Orange
        "expert": "#ff4444"        # Red
    }
    return colors.get(difficulty_level.lower(), "#999999")


def _estimate_content_effort(word_count: int, difficulty_level: str) -> str:
    """Estimate content creation effort"""
    base_hours = word_count / 500  # 500 words per hour base rate
    
    multipliers = {
        "beginner": 1.0,
        "intermediate": 1.2,
        "advanced": 1.5,
        "expert": 1.8
    }
    
    multiplier = multipliers.get(difficulty_level.lower(), 1.2)
    total_hours = base_hours * multiplier
    
    if total_hours <= 4:
        return "Low effort (< 4 hours)"
    elif total_hours <= 8:
        return "Medium effort (4-8 hours)"
    elif total_hours <= 16:
        return "High effort (8-16 hours)"
    else:
        return "Very high effort (16+ hours)"


def _assess_seo_strength(seo_score: int) -> str:
    """Assess SEO strength"""
    if seo_score >= 80:
        return "Excellent SEO potential"
    elif seo_score >= 70:
        return "Good SEO potential"
    elif seo_score >= 60:
        return "Moderate SEO potential"
    else:
        return "Needs SEO optimization"


def _assess_viral_prediction(viral_score: int) -> str:
    """Assess viral prediction"""
    if viral_score >= 80:
        return "High viral potential"
    elif viral_score >= 70:
        return "Good viral potential"
    elif viral_score >= 60:
        return "Moderate viral potential"
    else:
        return "Low viral potential"


def _calculate_format_breakdown(ideas: List[Dict]) -> Dict[str, int]:
    """Calculate format breakdown"""
    breakdown = {}
    for idea in ideas:
        fmt = idea.get("content_format", "unknown")
        breakdown[fmt] = breakdown.get(fmt, 0) + 1
    return breakdown


def _calculate_quality_breakdown(ideas: List[Dict]) -> Dict[str, int]:
    """Calculate quality tier breakdown"""
    breakdown = {
        "excellent": 0,
        "high_quality": 0,
        "good": 0,
        "decent": 0,
        "needs_work": 0
    }
    
    for idea in ideas:
        score = idea.get("overall_quality_score", 0)
        if score >= 85:
            breakdown["excellent"] += 1
        elif score >= 75:
            breakdown["high_quality"] += 1
        elif score >= 65:
            breakdown["good"] += 1
        elif score >= 55:
            breakdown["decent"] += 1
        else:
            breakdown["needs_work"] += 1
    
    return breakdown


def _generate_seo_analysis(blog_idea: Dict) -> Dict[str, Any]:
    """Generate detailed SEO analysis"""
    return {
        "keyword_optimization": {
            "primary_keywords_count": len(blog_idea.get("primary_keywords", [])),
            "secondary_keywords_count": len(blog_idea.get("secondary_keywords", [])),
            "featured_snippet_opportunity": blog_idea.get("featured_snippet_opportunity", False)
        },
        "content_optimization": {
            "title_length": len(blog_idea.get("title", "")),
            "title_seo_friendly": 50 <= len(blog_idea.get("title", "")) <= 70,
            "description_length": len(blog_idea.get("description", "")),
            "word_count_optimal": 1500 <= blog_idea.get("estimated_word_count", 0) <= 4000
        },
        "seo_score": blog_idea.get("seo_optimization_score", 0),
        "seo_recommendations": list(filter(None, [
            "Optimize title length to 50-70 characters" if not (50 <= len(blog_idea.get("title", "")) <= 70) else None,
            "Add more secondary keywords" if len(blog_idea.get("secondary_keywords", [])) < 5 else None,
            "Target featured snippet with FAQ section" if blog_idea.get("featured_snippet_opportunity") else None
        ]))
    }


def _generate_content_analysis(blog_idea: Dict) -> Dict[str, Any]:
    """Generate detailed content analysis"""
    return {
        "structure_analysis": {
            "outline_sections": len(blog_idea.get("outline", [])),
            "key_points_count": len(blog_idea.get("key_points", [])),
            "engagement_hooks_count": len(blog_idea.get("engagement_hooks", []))
        },
        "readability": {
            "estimated_reading_time": blog_idea.get("estimated_reading_time", 0),
            "difficulty_level": blog_idea.get("difficulty_level", "intermediate"),
            "format": blog_idea.get("content_format", "")
        },
        "engagement_potential": blog_idea.get("viral_potential_score", 0)
    }


def _generate_business_analysis(blog_idea: Dict) -> Dict[str, Any]:
    """Generate business impact analysis"""
    return {
        "business_metrics": {
            "business_impact_score": blog_idea.get("business_impact_score", 0),
            "conversion_potential": blog_idea.get("performance_estimates", {}).get("conversion_potential_score", 0),
            "lead_generation_potential": "high" if "lead generation" in blog_idea.get("business_value", "").lower() else "medium"
        },
        "roi_projection": {
            "estimated_traffic": blog_idea.get("performance_estimates", {}).get("estimated_monthly_traffic", 1000),
            "estimated_shares": blog_idea.get("performance_estimates", {}).get("estimated_social_shares", 25),
            "time_to_roi": blog_idea.get("performance_estimates", {}).get("estimated_time_to_rank_weeks", 12)
        },
        "call_to_action": blog_idea.get("call_to_action", ""),
        "business_value": blog_idea.get("business_value", "")
    }


def _generate_implementation_guide(blog_idea: Dict) -> Dict[str, Any]:
    """Generate implementation guide"""
    word_count = blog_idea.get("estimated_word_count", 2500)
    writing_hours = word_count / 500
    total_hours = writing_hours + 5  # Add research, editing, SEO time
    
    return {
        "content_creation_steps": [
            "Research and gather additional sources",
            "Create detailed outline from provided structure",
            "Write compelling introduction with hook",
            "Develop main content sections",
            "Add visual elements and examples",
            "Optimize for SEO keywords",
            "Write strong conclusion with CTA",
            "Review and edit for quality"
        ],
        "estimated_timeline": {
            "research_hours": 2,
            "writing_hours": round(writing_hours, 1),
            "editing_hours": 2,
            "seo_optimization_hours": 1,
            "total_estimated_hours": round(total_hours, 1)
        },
        "required_resources": [
            "Keyword research tool",
            "Image/graphic creation tool",
            "Content management system",
            "SEO optimization plugin"
        ],
        "success_metrics": [
            "Organic traffic growth",
            "Social media shares",
            "Time on page",
            "Conversion rate",
            "Backlink acquisition"
        ]
    }


def _generate_optimization_suggestions(blog_idea: Dict) -> List[str]:
    """Generate optimization suggestions"""
    suggestions = []
    
    # SEO optimization suggestions
    if blog_idea.get("seo_optimization_score", 0) < 75:
        suggestions.append("Enhance keyword optimization by including more related terms")
    
    if len(blog_idea.get("primary_keywords", [])) < 3:
        suggestions.append("Add more primary keywords to improve search visibility")
    
    # Content optimization suggestions
    if blog_idea.get("viral_potential_score", 0) < 70:
        suggestions.append("Add more engaging hooks and emotional triggers to increase viral potential")
    
    if len(blog_idea.get("outline", [])) < 5:
        suggestions.append("Expand outline to include more comprehensive sections")
    
    # Business optimization suggestions
    if not blog_idea.get("call_to_action"):
        suggestions.append("Add a strong call-to-action to improve conversion potential")
    
    if blog_idea.get("business_impact_score", 0) < 70:
        suggestions.append("Strengthen business value proposition and lead generation elements")
    
    return suggestions[:5]  # Limit to top 5 suggestions


def _generate_implementation_timeline(calendar: Dict, summary: Dict) -> Dict[str, Any]:
    """Generate implementation timeline"""
    total_ideas = summary.get("total_ideas", 0)
    selected_ideas = summary.get("selected_ideas", 0)
    
    publishing_freq = calendar.get("publishing_strategy", {}).get("recommended_frequency", "2-3 posts per week")
    
    # Extract frequency number
    freq_number = 2  # Default
    if "1-2" in publishing_freq:
        freq_number = 1.5
    elif "2-3" in publishing_freq:
        freq_number = 2.5
    elif "3-4" in publishing_freq:
        freq_number = 3.5
    
    weeks_to_complete = max(4, round(total_ideas / freq_number))
    
    return {
        "total_timeline_weeks": weeks_to_complete,
        "ideas_to_implement": selected_ideas if selected_ideas > 0 else total_ideas,
        "publishing_frequency": publishing_freq,
        "estimated_completion_date": (datetime.now() + timedelta(weeks=weeks_to_complete)).strftime("%Y-%m-%d"),
        "phase_breakdown": {
            "immediate_phase": "Weeks 1-2: High priority ideas",
            "growth_phase": f"Weeks 3-{min(8, weeks_to_complete)}: Regular publishing",
            "optimization_phase": f"Weeks {min(9, weeks_to_complete)}+: Optimize and scale"
        }
    }


def _calculate_resource_allocation(calendar: Dict, summary: Dict) -> Dict[str, Any]:
    """Calculate resource allocation recommendations"""
    total_ideas = summary.get("total_ideas", 0)
    avg_quality = summary.get("average_quality_score", 70)
    
    # Calculate estimated effort
    estimated_hours = calendar.get("estimated_resource_requirements", {}).get("total_estimated_hours", total_ideas * 6)
    
    return {
        "total_estimated_hours": estimated_hours,
        "weekly_time_commitment": round(estimated_hours / 16, 1),  # Spread over 16 weeks
        "team_recommendations": {
            "content_writer": "Primary resource - 60% of time",
            "seo_specialist": "Supporting resource - 20% of time", 
            "designer": "Supporting resource - 15% of time",
            "editor": "Review resource - 5% of time"
        },
        "budget_estimation": {
            "in_house_cost": f"${estimated_hours * 50:,.0f} (at $50/hour)",
            "freelance_cost": f"${estimated_hours * 75:,.0f} (at $75/hour)",
            "agency_cost": f"${total_ideas * 500:,.0f} (at $500/post)"
        },
        "quality_investment": "Higher quality ideas require less editing time" if avg_quality >= 75 else "Lower quality ideas need additional optimization"
    }


def _generate_milestone_tracking(calendar: Dict) -> List[Dict[str, Any]]:
    """Generate milestone tracking"""
    return [
        {
            "milestone": "Phase 1: Content Creation Setup",
            "timeline": "Week 1",
            "deliverables": ["Content templates", "SEO guidelines", "Publishing schedule"],
            "success_criteria": "All tools and processes in place"
        },
        {
            "milestone": "Phase 2: Initial Content Batch",
            "timeline": "Weeks 2-4",
            "deliverables": ["First 6-8 blog posts", "Social media promotion plan"],
            "success_criteria": "Consistent publishing rhythm established"
        },
        {
            "milestone": "Phase 3: Optimization & Scaling",
            "timeline": "Weeks 5-8",
            "deliverables": ["Performance analytics", "Content optimization", "Team scaling"],
            "success_criteria": "Measurable traffic and engagement growth"
        },
        {
            "milestone": "Phase 4: Results & Iteration",
            "timeline": "Weeks 9-12",
            "deliverables": ["ROI analysis", "Content strategy refinement", "Future planning"],
            "success_criteria": "Proven content system with positive ROI"
        }
    ]


def _generate_actionable_recommendations(insights: Dict) -> List[Dict[str, Any]]:
    """Generate actionable recommendations from insights"""
    recommendations = []
    
    strategic_insights = insights.get("strategic_insights", {})
    overall_quality = strategic_insights.get("overall_quality_assessment", {})
    
    # Quality-based recommendations
    avg_quality = overall_quality.get("average_quality_score", 0)
    if avg_quality >= 80:
        recommendations.append({
            "category": "Implementation",
            "priority": "High",
            "action": "Fast-track implementation with current high-quality ideas",
            "rationale": f"Average quality score of {avg_quality} indicates strong content foundation",
            "timeline": "Start immediately"
        })
    elif avg_quality >= 70:
        recommendations.append({
            "category": "Optimization", 
            "priority": "Medium",
            "action": "Optimize lower-scoring ideas before implementation",
            "rationale": "Good foundation but room for improvement",
            "timeline": "1-2 weeks optimization phase"
        })
    
    # Content strategy recommendations
    content_strategy = strategic_insights.get("content_strategy_insights", {})
    seo_level = content_strategy.get("seo_optimization_level", 0)
    
    if seo_level < 70:
        recommendations.append({
            "category": "SEO",
            "priority": "High", 
            "action": "Enhance SEO optimization across all content",
            "rationale": f"SEO optimization level of {seo_level} below optimal threshold",
            "timeline": "Before publishing"
        })
    
    return recommendations


def _generate_risk_mitigation_strategies(insights: Dict) -> List[Dict[str, Any]]:
    """Generate risk mitigation strategies"""
    strategies = []
    
    success_predictions = insights.get("success_predictions", {})
    risk_assessment = success_predictions.get("risk_assessment", {})
    
    # Implementation risk mitigation
    if risk_assessment.get("implementation_risk_level") == "Medium":
        strategies.append({
            "risk": "Implementation complexity",
            "mitigation": "Start with highest-scoring, easiest-to-implement ideas",
            "monitoring": "Track completion rates and time-to-publish metrics",
            "contingency": "Have backup simple content ideas ready"
        })
    
    # Quality risk mitigation
    low_risk_count = risk_assessment.get("low_risk_ideas_count", 0)
    if low_risk_count < 10:
        strategies.append({
            "risk": "Content quality variation",
            "mitigation": "Implement quality review process for all content",
            "monitoring": "Regular quality audits and reader feedback",
            "contingency": "Content editing and optimization protocols"
        })
    
    return strategies


def _generate_success_optimization_tips(insights: Dict) -> List[str]:
    """Generate success optimization tips"""
    tips = []
    
    strategic_insights = insights.get("strategic_insights", {})
    business_analysis = strategic_insights.get("business_impact_analysis", {})
    
    # Business impact optimization
    high_impact_count = business_analysis.get("high_business_impact_count", 0)
    if high_impact_count >= 5:
        tips.append("Prioritize your high business impact ideas for maximum ROI")
    
    tips.extend([
        "Create content clusters around your highest-scoring topics",
        "Develop a consistent publishing schedule for audience building",
        "Track and optimize based on actual performance data",
        "Repurpose top-performing content into multiple formats",
        "Build email capture into your highest-converting content"
    ])
    
    return tips[:5]


def _analyze_competitive_positioning(insights: Dict) -> Dict[str, Any]:
    """Analyze competitive positioning"""
    strategic_insights = insights.get("strategic_insights", {})
    content_strategy = strategic_insights.get("content_strategy_insights", {})
    
    return {
        "content_differentiation": {
            "format_diversity": len(content_strategy.get("dominant_formats", [])),
            "quality_advantage": content_strategy.get("audience_alignment_strength", 0) > 75,
            "unique_positioning": "Data-driven content strategy with comprehensive market research"
        },
        "competitive_advantages": [
            "Research-backed content topics with proven viral potential",
            "Multi-format content strategy for broader audience appeal", 
            "SEO-optimized approach for organic traffic growth",
            "Strategic timing based on seasonal trends"
        ],
        "market_opportunities": [
            "Early mover advantage on trending topics",
            "Content gaps in competitor strategies",
            "Audience segments with unmet content needs"
        ]
    }


# ============================================================================
# PHASE 2 STATUS AND HEALTH ENDPOINTS
# ============================================================================

@app.route('/api/v2/phase2/health', methods=['GET'])
def phase2_health_check():
    """Phase 2 specific health check"""
    try:
        # Test Phase 2 storage connection
        phase2_storage = Phase2SupabaseStorage()
        
        # Test basic queries
        test_results = {
            "blog_ideas_table": False,
            "content_calendar_table": False,
            "generation_results_table": False
        }
        
        try:
            result = phase2_storage._execute_query('GET', 'blog_ideas?limit=1')
            test_results["blog_ideas_table"] = result['success']
        except:
            pass
        
        try:
            result = phase2_storage._execute_query('GET', 'content_calendar?limit=1')
            test_results["content_calendar_table"] = result['success']
        except:
            pass
        
        try:
            result = phase2_storage._execute_query('GET', 'blog_generation_results?limit=1')
            test_results["generation_results_table"] = result['success']
        except:
            pass
        
        all_tables_healthy = all(test_results.values())
        
        return jsonify({
            "status": "healthy" if all_tables_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "phase2_version": "v1.0",
            "components": {
                "phase2_storage": {
                    "status": "healthy" if all_tables_healthy else "degraded",
                    "table_status": test_results
                },
                "blog_idea_generator": {
                    "status": "healthy",
                    "available": True
                },
                "llm_integration": {
                    "status": "ready",
                    "supported_providers": ["openai", "anthropic", "deepseek", "gemini", "kimi"]
                }
            },
            "features": {
                "blog_idea_generation": True,
                "content_calendar_creation": True,
                "strategic_insights": True,
                "quality_scoring": True,
                "seo_optimization": True,
                "bulk_operations": True
            }
        }), 200 if all_tables_healthy else 503
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "phase2_version": "v1.0"
        }), 503


@app.route('/api/v2/phase2/stats', methods=['GET'])
def phase2_system_stats():
    """Get Phase 2 system statistics"""
    try:
        # Get user_id from query (optional for system stats)
        user_id = request.args.get('user_id')
        
        phase2_storage = Phase2SupabaseStorage()
        
        # System-wide stats (if no user_id) or user-specific stats
        if user_id:
            try:
                uuid.UUID(user_id)
                stats_filter = f"user_id=eq.{user_id}&"
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Invalid user_id format"
                }), 400
        else:
            stats_filter = ""
        
        # Get basic counts
        ideas_result = phase2_storage._execute_query('GET', f'blog_ideas?{stats_filter}select=id&limit=1000')
        calendar_result = phase2_storage._execute_query('GET', f'content_calendar?{stats_filter}select=id')
        results_result = phase2_storage._execute_query('GET', f'blog_generation_results?{stats_filter}select=id')
        
        stats = {
            "total_blog_ideas": len(ideas_result.get('data', [])) if ideas_result['success'] else 0,
            "total_calendars": len(calendar_result.get('data', [])) if calendar_result['success'] else 0,
            "total_generation_sessions": len(results_result.get('data', [])) if results_result['success'] else 0,
            "user_scoped": bool(user_id),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "phase2_stats": stats
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get Phase 2 stats: {str(e)}"
        }), 500


# ============================================================================
# UPDATED INDEX ROUTE WITH PHASE 2 INFORMATION
# ============================================================================

# Replace your existing index route with this enhanced version
@app.route('/')
def enhanced_index_with_phase2():
    return jsonify({
        "service": "Enhanced Trend Research + Blog Idea Generation - Noodl Integration Server",
        "version": "2.3.0 RLS + Phase 2",
        "status": "operational",
        "features": [
            "Phase 1: Trend Research & Market Intelligence",
            "Phase 2: Blog Idea Generation & Content Strategy",
            "RLS (Row Level Security) Support",
            "User-Scoped Data Access",
            "Enhanced Supabase Integration",
            "PyTrends Support",
            "Advanced Error Handling",
            "Content Calendar Generation",
            "Strategic Insights & Success Predictions"
        ],
        "authentication": {
            "method": "Noodl handles authentication, API expects user_id",
            "rls_enabled": True,
            "user_scoped_access": True
        },
        "phase1_endpoints": {
            "POST /api/v2/enhanced-trend-research": "Main trend research endpoint",
            "GET /api/v2/trend-analyses": "Get saved trend analyses for user",
            "GET /api/v2/trend-analysis/<id>": "Get specific trend analysis",
            "PATCH /api/v2/topics/<id>/select": "Toggle topic selection",
            "PATCH /api/v2/opportunities/<id>/select": "Toggle opportunity selection"
        },
        "phase2_endpoints": {
            "POST /api/v2/generate-blog-ideas/<analysis_id>": "Generate blog ideas from Phase 1",
            "GET /api/v2/blog-ideas/<analysis_id>": "Get generated blog ideas",
            "GET /api/v2/blog-ideas/<idea_id>": "Get specific blog idea details",
            "PATCH /api/v2/blog-ideas/<idea_id>/select": "Select/manage blog ideas",
            "PATCH /api/v2/blog-ideas/bulk-update": "Bulk update blog ideas",
            "GET /api/v2/content-calendar/<analysis_id>": "Get content calendar",
            "GET /api/v2/strategic-insights/<analysis_id>": "Get strategic insights"
        },
        "health_endpoints": {
            "GET /api/v2/health": "Phase 1 health check",
            "GET /api/v2/phase2/health": "Phase 2 health check",
            "GET /api/v2/phase2/stats": "Phase 2 system statistics"
        },
        "complete_workflow": {
            "step1": "POST /api/v2/enhanced-trend-research (Phase 1)",
            "step2": "PATCH /api/v2/topics/{id}/select (User selections)",
            "step3": "POST /api/v2/generate-blog-ideas/{analysis_id} (Phase 2)",
            "step4": "GET /api/v2/blog-ideas/{analysis_id} (Manage ideas)",
            "step5": "GET /api/v2/content-calendar/{analysis_id} (Implementation)"
        },
        "usage_example": {
            "phase1_request": {
                "url": "/api/v2/enhanced-trend-research",
                "method": "POST",
                "body": {
                    "topic": "AI marketing",
                    "user_id": "uuid-from-noodl-auth",
                    "llm_config": {"provider": "openai", "api_key": "your-key"}
                }
            },
            "phase2_request": {
                "url": "/api/v2/generate-blog-ideas/{analysis_id}",
                "method": "POST", 
                "body": {
                    "user_id": "uuid-from-noodl-auth",
                    "llm_config": {"provider": "openai", "api_key": "your-key"},
                    "generation_config": {"min_ideas": 20, "max_ideas": 40}
                }
            }
        }
    })




# ============================================================================
# PHASE 3: KEYWORD RESEARCH ENDPOINTS
# Add these endpoints to your noodl_server.py file
# ============================================================================

@app.route('/api/v2/keyword-research/instructions/<tool_name>', methods=['GET'])
def get_keyword_import_instructions(tool_name: str):
    """Get instructions for importing keyword data from specific tools"""
    try:
        integration = ManualKeywordResearchIntegration()
        instructions = integration.get_import_instructions(tool_name)
        
        return jsonify({
            "success": True,
            "tool_name": tool_name,
            "instructions": instructions,
            "supported_tools": integration.supported_tools,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get instructions: {str(e)}"
        }), 500


@app.route('/api/v2/keyword-research/template/<tool_name>', methods=['GET'])
def get_keyword_csv_template_fixed(tool_name: str):
    """Download CSV template for manual keyword entry - WITH ERROR HANDLING"""
    try:
        print(f"🔧 Template request for tool: {tool_name}")
        
        # Check if manual_keyword_integration is imported
        try:
            from manual_keyword_integration import ManualKeywordResearchIntegration
            print("✅ Manual keyword integration imported successfully")
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return jsonify({
                "success": False,
                "error": f"Missing dependency: {str(e)}. Please ensure manual_keyword_integration.py is in the project directory."
            }), 500
        
        # Try to create integration instance
        try:
            integration = ManualKeywordResearchIntegration()
            print("✅ Integration instance created successfully")
        except Exception as e:
            print(f"❌ Integration creation error: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to create integration instance: {str(e)}"
            }), 500
        
        # Try to generate template
        try:
            template_content = integration.generate_csv_template(tool_name)
            print(f"✅ Template generated successfully, length: {len(template_content)}")
        except Exception as e:
            print(f"❌ Template generation error: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to generate template: {str(e)}"
            }), 500
        
        # Try to create file response
        try:
            # Create file-like object
            template_bytes = io.BytesIO(template_content.encode('utf-8'))
            print("✅ File object created successfully")
            
            return send_file(
                template_bytes,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{tool_name}_keyword_template.csv'
            )
            
        except Exception as e:
            print(f"❌ File creation error: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to create file: {str(e)}"
            }), 500
        
    except Exception as e:
        print(f"❌ Unexpected error in template endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": f"Template generation failed: {str(e)}",
            "debug_info": "Check server logs for detailed error information"
        }), 500

# ============================================================================
# 4. FALLBACK TEMPLATE ENDPOINT (IF INTEGRATION FILE IS MISSING)
# ============================================================================

@app.route('/api/v2/keyword-research/template-fallback/<tool_name>', methods=['GET'])
def get_keyword_csv_template_fallback(tool_name: str):
    """Fallback template endpoint with hardcoded templates"""
    try:
        print(f"🔧 Fallback template request for tool: {tool_name}")
        
        # Hardcoded templates
        templates = {
            'ahrefs': "Keyword,Volume,KD,CPC,Traffic potential\nemail marketing guide,1200,25,2.50,850\ncontent marketing strategy,890,30,3.20,650\nsocial media marketing,2500,45,1.80,1200",
            
            'semrush': "Keyword,Volume,KD%,CPC,Intent\nemail marketing tips,950,28,2.10,Informational\nmarketing automation tools,760,35,4.50,Commercial\nlead generation strategies,680,32,3.80,Informational",
            
            'moz': "Keyword,Monthly Volume,Difficulty,Organic CTR\nSEO best practices,1100,30,0.35\nkeyword research tools,850,40,0.28\nlocal SEO guide,720,25,0.42",
            
            'ubersuggest': "Keyword,Vol,SD,CPC\ndigital marketing,15000,45,2.80\ncontent creation,8500,38,1.95\nsocial media tips,12000,42,1.65",
            
            'kwfinder': "Keyword,Search Volume,Difficulty,CPC\nemail automation,3200,35,3.10\nmarketing strategy,5800,48,2.45\ncustomer retention,2100,29,2.90",
            
            'custom': "keyword,search_volume,difficulty,cpc,competition,intent,trend\nblog writing tips,1500,25,1.20,medium,informational,stable\ncontent calendar template,800,20,0.90,low,informational,rising\ncopywriting techniques,950,35,2.80,medium,informational,stable"
        }
        
        template_content = templates.get(tool_name.lower(), templates['custom'])
        
        # Create file response
        template_bytes = io.BytesIO(template_content.encode('utf-8'))
        
        return send_file(
            template_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{tool_name}_keyword_template.csv'
        )
        
    except Exception as e:
        print(f"❌ Fallback template error: {e}")
        return jsonify({
            "success": False,
            "error": f"Fallback template failed: {str(e)}"
        }), 500

# ============================================================================
# 5. DIAGNOSTIC ENDPOINT TO CHECK SYSTEM STATUS
# ============================================================================

@app.route('/api/v2/keyword-research/debug', methods=['GET'])
def debug_keyword_research():
    """Debug endpoint to check keyword research system status"""
    
    debug_info = {
        "timestamp": datetime.now().isoformat(),
        "system_checks": {},
        "import_status": {},
        "file_checks": {}
    }
    
    # Check imports
    try:
        from manual_keyword_integration import ManualKeywordResearchIntegration, KeywordData
        debug_info["import_status"]["manual_keyword_integration"] = "✅ SUCCESS"
        
        # Try to create instance
        try:
            integration = ManualKeywordResearchIntegration()
            debug_info["import_status"]["integration_instance"] = "✅ SUCCESS"
            
            # Try template generation
            try:
                template = integration.generate_csv_template('ahrefs')
                debug_info["import_status"]["template_generation"] = f"✅ SUCCESS (length: {len(template)})"
            except Exception as e:
                debug_info["import_status"]["template_generation"] = f"❌ ERROR: {str(e)}"
                
        except Exception as e:
            debug_info["import_status"]["integration_instance"] = f"❌ ERROR: {str(e)}"
            
    except ImportError as e:
        debug_info["import_status"]["manual_keyword_integration"] = f"❌ IMPORT ERROR: {str(e)}"
    
    # Check file existence
    import os
    files_to_check = [
        'manual_keyword_integration.py',
        'noodl_server.py',
        'blog_idea_generator.py',
        'phase2_supabase_storage.py'
    ]
    
    for file_name in files_to_check:
        exists = os.path.exists(file_name)
        debug_info["file_checks"][file_name] = "✅ EXISTS" if exists else "❌ MISSING"
    
    # Check required packages
    required_packages = ['pandas', 'flask', 'supabase']
    for package in required_packages:
        try:
            __import__(package)
            debug_info["system_checks"][f"{package}_package"] = "✅ INSTALLED"
        except ImportError:
            debug_info["system_checks"][f"{package}_package"] = "❌ MISSING"
    
    return jsonify(debug_info)

@app.route('/api/v2/keyword-research/upload', methods=['POST'])
def upload_keyword_research():
    """Upload and parse keyword research file"""
    try:
        # Get user_id
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400
        
        # Validate user_id
        try:
            uuid.UUID(user_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id format"
            }), 400
        
        # Get tool name
        tool_name = request.form.get('tool_name', 'custom')
        
        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file uploaded"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        # Read file content
        try:
            file_content = file.read().decode('utf-8-sig')  # Handle BOM
        except UnicodeDecodeError:
            try:
                file_content = file.read().decode('latin1')
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Failed to read file: {str(e)}"
                }), 400
        
        # Parse keywords
        integration = ManualKeywordResearchIntegration()
        keywords, errors = integration.parse_keyword_file(file_content, tool_name, file.filename)
        
        if not keywords and errors:
            return jsonify({
                "success": False,
                "error": "Failed to parse keywords",
                "parsing_errors": errors
            }), 400
        
        # Validate keyword data
        validation_result = integration.validate_imported_keywords(keywords)
        
        # Generate opportunities report
        opportunities_report = integration.generate_keyword_opportunities_report(keywords)
        
        # Store keywords temporarily (you might want to implement proper storage)
        keyword_session_id = str(uuid.uuid4())
        
        return jsonify({
            "success": True,
            "keyword_session_id": keyword_session_id,
            "upload_summary": {
                "total_keywords_imported": len(keywords),
                "source_tool": tool_name,
                "filename": file.filename,
                "upload_timestamp": datetime.now().isoformat(),
                "user_id": user_id
            },
            "validation_result": validation_result,
            "opportunities_report": opportunities_report,
            "parsing_errors": errors,
            "sample_keywords": [kw.to_dict() for kw in keywords[:5]],  # Show first 5 as sample
            "keyword_data": [kw.to_dict() for kw in keywords]  # Full keyword data for enhancement
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Keyword upload failed: {str(e)}"
        }), 500


# FIXED KEYWORD ENHANCEMENT ENDPOINT
# Replace the existing enhance-blog-ideas endpoint in noodl_server.py

@app.route('/api/v2/keyword-research/enhance-blog-ideas', methods=['POST'])
def enhance_blog_ideas_with_keywords_fixed():
    """Enhanced blog ideas with imported keyword research - FIXED VERSION"""
    try:
        data = request.get_json()
        
        # Extract and validate user_id
        user_id, error_response, status_code = extract_and_validate_user_id(data)
        if error_response:
            return jsonify(error_response), status_code
        
        # Get required parameters
        analysis_id = data.get('analysis_id')
        if not analysis_id:
            return jsonify({
                "success": False,
                "error": "analysis_id is required"
            }), 400
        
        # Validate analysis_id
        try:
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid analysis_id format"
            }), 400
        
        # Get keyword data
        keyword_data_raw = data.get('keyword_data')
        if not keyword_data_raw:
            return jsonify({
                "success": False,
                "error": "keyword_data is required"
            }), 400
        
        print(f"🔧 ENHANCEMENT DEBUG:")
        print(f"   User ID: {user_id}")
        print(f"   Analysis ID: {analysis_id}")
        print(f"   Keyword data count: {len(keyword_data_raw)}")
        
        # Parse keyword data
        keywords = []
        for kw_dict in keyword_data_raw:
            try:
                keyword = KeywordData(
                    keyword=kw_dict['keyword'],
                    search_volume=int(kw_dict.get('search_volume', 0)),
                    keyword_difficulty=float(kw_dict.get('keyword_difficulty', 0)),
                    cpc=float(kw_dict.get('cpc', 0)),
                    competition=kw_dict.get('competition', 'medium'),
                    search_intent=kw_dict.get('search_intent', 'informational'),
                    trend=kw_dict.get('trend', 'stable'),
                    related_keywords=kw_dict.get('related_keywords', []),
                    source_tool=kw_dict.get('source_tool', 'manual')
                )
                keywords.append(keyword)
            except Exception as e:
                logger.warning(f"Failed to parse keyword data: {e}")
        
        if not keywords:
            return jsonify({
                "success": False,
                "error": "No valid keyword data provided"
            }), 400
        
        print(f"✅ Parsed {len(keywords)} keywords successfully")
        
        # Get enhancement configuration
        enhancement_config = data.get('enhancement_config', {
            'max_primary_keywords': 5,
            'max_secondary_keywords': 10,
            'min_search_volume': 100,
            'max_difficulty': 50,
            'prefer_informational': True
        })
        
        # Get blog ideas from Phase 2 storage
        phase2_storage = Phase2SupabaseStorage()
        phase2_storage.set_user_context(user_id)
        
        try:
            # Use asyncio to run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                blog_ideas = loop.run_until_complete(phase2_storage.get_blog_ideas(analysis_id, user_id))
                print(f"✅ Retrieved {len(blog_ideas)} blog ideas")
            finally:
                loop.close()
                
        except Exception as e:
            print(f"❌ Failed to get blog ideas: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to get blog ideas: {str(e)}"
            }), 404
        
        if not blog_ideas:
            return jsonify({
                "success": False,
                "error": "No blog ideas found for this analysis"
            }), 404
        
        # Enhance blog ideas with keywords
        integration = ManualKeywordResearchIntegration()
        enhanced_ideas = integration.enhance_blog_ideas_with_keywords(
            blog_ideas, keywords, enhancement_config
        )
        
        print(f"🔧 Enhanced {len(enhanced_ideas)} ideas")
        
        # FIXED: Prepare updates with correct data structure
        updates = []
        for enhanced_idea in enhanced_ideas:
            if enhanced_idea.get('keyword_research_enhanced'):
                
                # Prepare enhanced keyword data properly
                enhanced_primary = enhanced_idea.get('enhanced_primary_keywords', [])
                enhanced_secondary = enhanced_idea.get('enhanced_secondary_keywords', [])
                keyword_research_data = enhanced_idea.get('keyword_research_data', {})
                
                print(f"🔧 Processing idea: {enhanced_idea.get('title', 'Unknown')[:50]}")
                print(f"   Enhanced primary keywords: {len(enhanced_primary)}")
                print(f"   Enhanced secondary keywords: {len(enhanced_secondary)}")
                print(f"   Total search volume: {keyword_research_data.get('total_search_volume', 0)}")
                
                update_data = {
                    'id': enhanced_idea['id'],
                    
                    # FIXED: Ensure JSON serialization for complex data
                    'enhanced_primary_keywords': json.dumps(enhanced_primary) if enhanced_primary else None,
                    'enhanced_secondary_keywords': json.dumps(enhanced_secondary) if enhanced_secondary else None,
                    'keyword_research_data': json.dumps(keyword_research_data) if keyword_research_data else None,
                    
                    # Updated scores
                    'seo_optimization_score': enhanced_idea.get('seo_optimization_score', 50),
                    'traffic_potential_score': enhanced_idea.get('traffic_potential_score', 50),
                    'competition_score': enhanced_idea.get('competition_score', 50),
                    
                    # Additional enhancement data
                    'keyword_suggestions': json.dumps(enhanced_idea.get('keyword_suggestions', {})),
                    'content_optimization_tips': json.dumps(enhanced_idea.get('content_optimization_tips', [])),
                    'keyword_research_enhanced': True,
                    'keyword_source_tools': json.dumps(enhanced_idea.get('keyword_source_tools', [])),
                    'enhancement_timestamp': enhanced_idea.get('enhancement_timestamp', datetime.now().isoformat())
                }
                
                # VALIDATION: Check that we have actual data
                has_data = (
                    enhanced_primary or 
                    enhanced_secondary or 
                    keyword_research_data.get('total_search_volume', 0) > 0
                )
                
                if has_data:
                    updates.append(update_data)
                    print(f"✅ Added update for idea: {enhanced_idea.get('title', 'Unknown')[:50]}")
                else:
                    print(f"⚠️ Skipping idea with no enhancement data: {enhanced_idea.get('title', 'Unknown')[:50]}")
        
        print(f"🔧 BULK UPDATE DEBUG:")
        print(f"   Total ideas processed: {len(enhanced_ideas)}")
        print(f"   Updates to send: {len(updates)}")
        
        if updates:
            print(f"   Sample update data:")
            sample = updates[0]
            print(f"      ID: {sample.get('id')}")
            print(f"      Enhanced flag: {sample.get('keyword_research_enhanced')}")
            print(f"      Primary keywords length: {len(json.loads(sample.get('enhanced_primary_keywords', '[]')))}")
            print(f"      Secondary keywords length: {len(json.loads(sample.get('enhanced_secondary_keywords', '[]')))}")
        
        # Bulk update blog ideas with enhanced data
        updated_count = 0
        if updates:
            # Use asyncio for the bulk update
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                print(f"📡 Sending bulk update to Supabase...")
                updated_count = loop.run_until_complete(phase2_storage.bulk_update_blog_ideas(updates, user_id))
                print(f"✅ Bulk update completed: {updated_count} ideas updated")
            except Exception as e:
                print(f"❌ Bulk update failed: {e}")
                raise
            finally:
                loop.close()
        
        # Generate enhancement summary
        enhanced_count = len([idea for idea in enhanced_ideas if idea.get('keyword_research_enhanced')])
        total_search_volume = sum(
            idea.get('keyword_research_data', {}).get('total_search_volume', 0) 
            for idea in enhanced_ideas
        )
        
        print(f"📊 ENHANCEMENT SUMMARY:")
        print(f"   Ideas enhanced: {enhanced_count}")
        print(f"   Database updates: {updated_count}")
        print(f"   Total search volume: {total_search_volume}")
        
        return jsonify({
            "success": True,
            "analysis_id": analysis_id,
            "user_id": user_id,
            "enhancement_summary": {
                "total_ideas_processed": len(blog_ideas),
                "ideas_enhanced": enhanced_count,
                "ideas_updated_in_db": updated_count,
                "keywords_used": len(keywords),
                "total_search_volume_added": total_search_volume,
                "enhancement_timestamp": datetime.now().isoformat()
            },
            "enhanced_ideas": enhanced_ideas,
            "keyword_usage_stats": {
                "avg_primary_keywords_per_idea": sum(
                    len(idea.get('enhanced_primary_keywords', [])) for idea in enhanced_ideas
                ) / len(enhanced_ideas) if enhanced_ideas else 0,
                "avg_secondary_keywords_per_idea": sum(
                    len(idea.get('enhanced_secondary_keywords', [])) for idea in enhanced_ideas
                ) / len(enhanced_ideas) if enhanced_ideas else 0,
                "total_keyword_opportunities": sum(
                    len(idea.get('keyword_suggestions', {}).get('content_keywords', [])) 
                    for idea in enhanced_ideas
                )
            },
            "debug_info": {
                "updates_prepared": len(updates),
                "updates_successful": updated_count,
                "sample_enhanced_idea_id": enhanced_ideas[0].get('id') if enhanced_ideas else None
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error enhancing blog ideas with keywords: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": f"Enhancement failed: {str(e)}",
            "debug_info": f"Check server logs for detailed error. Error type: {type(e).__name__}"
        }), 500


@app.route('/api/v2/keyword-research/health', methods=['GET'])
def keyword_research_health_check():
    """Health check for keyword research functionality"""
    try:
        # Test keyword research integration
        integration = ManualKeywordResearchIntegration()
        
        # Test template generation
        template_test = integration.generate_csv_template('custom')
        template_healthy = len(template_test) > 100
        
        # Test instruction generation
        instructions_test = integration.get_import_instructions('ahrefs')
        instructions_healthy = 'steps' in instructions_test
        
        return jsonify({
            "status": "healthy" if template_healthy and instructions_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "keyword_research_version": "v1.0",
            "components": {
                "template_generation": {
                    "status": "healthy" if template_healthy else "unhealthy",
                    "test_passed": template_healthy
                },
                "instruction_system": {
                    "status": "healthy" if instructions_healthy else "unhealthy",
                    "test_passed": instructions_healthy
                },
                "supported_tools": integration.supported_tools
            },
            "features": {
                "keyword_import": True,
                "data_validation": True,
                "blog_enhancement": True,
                "opportunities_analysis": True,
                "csv_export": True,
                "multi_tool_support": True
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 503


# ============================================================================
# ADDITIONAL KEYWORD RESEARCH ENDPOINTS (OPTIONAL)
# ============================================================================

@app.route('/api/v2/keyword-research/opportunities-report', methods=['POST'])
def generate_keyword_opportunities_report():
    """Generate detailed keyword opportunities report"""
    try:
        data = request.get_json()
        
        # Extract and validate user_id
        user_id, error_response, status_code = extract_and_validate_user_id(data)
        if error_response:
            return jsonify(error_response), status_code
        
        # Get keyword data
        keyword_data_raw = data.get('keyword_data', [])
        if not keyword_data_raw:
            return jsonify({
                "success": False,
                "error": "keyword_data is required"
            }), 400
        
        # Parse keyword data
        keywords = []
        for kw_dict in keyword_data_raw:
            try:
                keyword = KeywordData(
                    keyword=kw_dict['keyword'],
                    search_volume=int(kw_dict.get('search_volume', 0)),
                    keyword_difficulty=float(kw_dict.get('keyword_difficulty', 0)),
                    cpc=float(kw_dict.get('cpc', 0)),
                    competition=kw_dict.get('competition', 'medium'),
                    search_intent=kw_dict.get('search_intent', 'informational'),
                    trend=kw_dict.get('trend', 'stable'),
                    related_keywords=kw_dict.get('related_keywords', []),
                    source_tool=kw_dict.get('source_tool', 'manual')
                )
                keywords.append(keyword)
            except Exception as e:
                logger.warning(f"Failed to parse keyword: {e}")
        
        if not keywords:
            return jsonify({
                "success": False,
                "error": "No valid keywords provided"
            }), 400
        
        # Generate comprehensive report
        integration = ManualKeywordResearchIntegration()
        report = integration.generate_keyword_opportunities_report(keywords)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "report": report,
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "keywords_analyzed": len(keywords),
                "report_type": "comprehensive_opportunities"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Report generation failed: {str(e)}"
        }), 500


# CORRECTED EXPORT ENDPOINT - Replace your existing export endpoint with this version
# This version correctly reads the enhanced keyword data structure

# FINAL WORKING EXPORT ENDPOINT
# This version handles all possible data scenarios in your Supabase table
# KEYWORD RESEARCH STATUS FEEDBACK SYSTEM
# Add these endpoints to your noodl_server.py

@app.route('/api/v2/keyword-research/status/<analysis_id>', methods=['GET'])
def get_keyword_research_status(analysis_id):
    """Get comprehensive keyword research status for user feedback"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id or analysis_id format"
            }), 400
        
        # Get blog ideas to analyze status
        phase2_storage = Phase2SupabaseStorage()
        phase2_storage.set_user_context(user_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            blog_ideas = loop.run_until_complete(phase2_storage.get_blog_ideas(analysis_id, user_id))
        finally:
            loop.close()
        
        if not blog_ideas:
            return jsonify({
                "success": False,
                "error": "No blog ideas found for this analysis"
            }), 404
        
        # Analyze keyword research status
        status_analysis = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "total_ideas": len(blog_ideas),
            "status_timestamp": datetime.now().isoformat(),
            "overall_status": "",
            "progress_percentage": 0,
            "enhancement_statistics": {},
            "detailed_breakdown": {},
            "recommendations": [],
            "next_steps": []
        }
        
        # Count different enhancement statuses
        enhanced_count = 0
        basic_keywords_count = 0
        no_keywords_count = 0
        total_keywords = 0
        total_search_volume = 0
        
        for idea in blog_ideas:
            # Check for enhanced data
            enhanced_primary = idea.get('enhanced_primary_keywords')
            enhanced_secondary = idea.get('enhanced_secondary_keywords')
            keyword_research_data = idea.get('keyword_research_data')
            keyword_research_enhanced = idea.get('keyword_research_enhanced', False)
            
            # Parse enhanced data
            if isinstance(enhanced_primary, str) and enhanced_primary and enhanced_primary != 'null':
                try:
                    enhanced_primary = json.loads(enhanced_primary)
                except:
                    enhanced_primary = []
            elif not enhanced_primary:
                enhanced_primary = []
                
            if isinstance(enhanced_secondary, str) and enhanced_secondary and enhanced_secondary != 'null':
                try:
                    enhanced_secondary = json.loads(enhanced_secondary)
                except:
                    enhanced_secondary = []
            elif not enhanced_secondary:
                enhanced_secondary = []
                
            if isinstance(keyword_research_data, str) and keyword_research_data and keyword_research_data != 'null':
                try:
                    keyword_research_data = json.loads(keyword_research_data)
                except:
                    keyword_research_data = {}
            elif not keyword_research_data:
                keyword_research_data = {}
            
            # Check for basic data
            primary_keywords = idea.get('primary_keywords', [])
            secondary_keywords = idea.get('secondary_keywords', [])
            
            # Parse basic keywords if they're JSON strings
            if isinstance(primary_keywords, str) and primary_keywords and primary_keywords != 'null':
                try:
                    primary_keywords = json.loads(primary_keywords)
                except:
                    primary_keywords = primary_keywords.split(',') if primary_keywords else []
            elif not primary_keywords:
                primary_keywords = []
                
            if isinstance(secondary_keywords, str) and secondary_keywords and secondary_keywords != 'null':
                try:
                    secondary_keywords = json.loads(secondary_keywords)
                except:
                    secondary_keywords = secondary_keywords.split(',') if secondary_keywords else []
            elif not secondary_keywords:
                secondary_keywords = []
            
            # Determine status
            has_enhanced_data = (
                enhanced_primary or 
                enhanced_secondary or 
                keyword_research_data.get('total_search_volume', 0) > 0 or
                keyword_research_enhanced
            )
            
            has_basic_data = primary_keywords or secondary_keywords
            
            if has_enhanced_data:
                enhanced_count += 1
                total_keywords += len(enhanced_primary) + len(enhanced_secondary)
                total_search_volume += keyword_research_data.get('total_search_volume', 0)
            elif has_basic_data:
                basic_keywords_count += 1
                total_keywords += len(primary_keywords) + len(secondary_keywords)
            else:
                no_keywords_count += 1
        
        # Calculate progress and status
        progress_percentage = round((enhanced_count / len(blog_ideas)) * 100, 1)
        
        # Determine overall status
        if enhanced_count == len(blog_ideas):
            overall_status = "complete"
            status_message = "🎉 Keyword research completed!"
            status_color = "#22c55e"  # Green
        elif enhanced_count >= len(blog_ideas) * 0.8:
            overall_status = "mostly_complete"
            status_message = "🔥 Almost done with keyword research!"
            status_color = "#3b82f6"  # Blue
        elif enhanced_count >= len(blog_ideas) * 0.5:
            overall_status = "in_progress"
            status_message = "📊 Keyword research in progress..."
            status_color = "#f59e0b"  # Amber
        elif enhanced_count > 0:
            overall_status = "started"
            status_message = "🚀 Keyword research started!"
            status_color = "#6366f1"  # Indigo
        else:
            overall_status = "not_started"
            status_message = "📝 Ready for keyword research"
            status_color = "#6b7280"  # Gray
        
        # Fill in status analysis
        status_analysis.update({
            "overall_status": overall_status,
            "status_message": status_message,
            "status_color": status_color,
            "progress_percentage": progress_percentage,
            "enhancement_statistics": {
                "ideas_with_enhanced_keywords": enhanced_count,
                "ideas_with_basic_keywords_only": basic_keywords_count,
                "ideas_with_no_keywords": no_keywords_count,
                "total_keywords_researched": total_keywords,
                "total_search_volume": total_search_volume,
                "average_keywords_per_idea": round(total_keywords / len(blog_ideas), 1) if blog_ideas else 0,
                "enhancement_success_rate": f"{progress_percentage}%"
            },
            "detailed_breakdown": {
                "complete_research": {
                    "count": enhanced_count,
                    "percentage": round((enhanced_count / len(blog_ideas)) * 100, 1),
                    "description": "Ideas with complete keyword research data"
                },
                "basic_keywords": {
                    "count": basic_keywords_count,
                    "percentage": round((basic_keywords_count / len(blog_ideas)) * 100, 1),
                    "description": "Ideas with basic keywords (need research)"
                },
                "needs_keywords": {
                    "count": no_keywords_count,
                    "percentage": round((no_keywords_count / len(blog_ideas)) * 100, 1),
                    "description": "Ideas without any keywords"
                }
            }
        })
        
        # Generate recommendations based on status
        if overall_status == "complete":
            status_analysis["recommendations"] = [
                "✅ All blog ideas have enhanced keyword research!",
                "📊 Export your keyword analysis to CSV",
                "🚀 Start creating content based on highest-scoring ideas",
                "📈 Monitor keyword rankings after publishing"
            ]
            status_analysis["next_steps"] = [
                "Export keyword analysis",
                "Create content calendar",
                "Start with highest quality score ideas",
                "Set up keyword ranking tracking"
            ]
        elif overall_status in ["mostly_complete", "in_progress"]:
            remaining = len(blog_ideas) - enhanced_count
            status_analysis["recommendations"] = [
                f"🔄 {remaining} ideas still need keyword research",
                "📊 Export current progress to see what's complete",
                "🎯 Focus on highest-scoring ideas first",
                "⚡ Complete research for remaining ideas"
            ]
            status_analysis["next_steps"] = [
                f"Complete keyword research for {remaining} remaining ideas",
                "Export partial keyword analysis",
                "Prioritize based on quality scores",
                "Continue enhancement process"
            ]
        elif overall_status == "started":
            status_analysis["recommendations"] = [
                "🚀 Great start! Continue with keyword research process",
                "📈 Upload more keyword data to enhance remaining ideas",
                "🎯 Focus on your highest-scoring blog ideas first",
                "📊 Use tools like Ahrefs, SEMrush, or Moz for research"
            ]
            status_analysis["next_steps"] = [
                "Get keyword research template",
                "Export keywords from your SEO tool",
                "Upload and enhance remaining ideas",
                "Build complete keyword database"
            ]
        else:
            status_analysis["recommendations"] = [
                "📚 Start with keyword research instructions",
                "🔧 Download CSV template for your SEO tool",
                "📊 Export keywords for your blog topics",
                "⚡ Upload and enhance all blog ideas"
            ]
            status_analysis["next_steps"] = [
                "Get keyword research instructions",
                "Choose your keyword research tool",
                "Download appropriate CSV template",
                "Begin keyword research process"
            ]
        
        return jsonify({
            "success": True,
            "keyword_research_status": status_analysis
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get keyword research status: {str(e)}"
        }), 500


@app.route('/api/v2/keyword-research/progress/<analysis_id>', methods=['GET'])
def get_keyword_research_progress(analysis_id):
    """Get simple progress indicator for real-time updates"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id required"}), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({"error": "Invalid UUID format"}), 400
        
        # Quick query to get enhancement status
        phase2_storage = Phase2SupabaseStorage()
        phase2_storage.set_user_context(user_id)
        
        # Direct query for just the fields we need
        result = phase2_storage._execute_query(
            'GET', 
            f'blog_ideas?trend_analysis_id=eq.{analysis_id}&user_id=eq.{user_id}&select=id,keyword_research_enhanced'
        )
        
        if result['success']:
            ideas = result['data']
            total_ideas = len(ideas)
            enhanced_ideas = len([idea for idea in ideas if idea.get('keyword_research_enhanced', False)])
            
            progress_percentage = round((enhanced_ideas / total_ideas) * 100, 1) if total_ideas > 0 else 0
            
            return jsonify({
                "success": True,
                "progress": {
                    "total_ideas": total_ideas,
                    "enhanced_ideas": enhanced_ideas,
                    "remaining_ideas": total_ideas - enhanced_ideas,
                    "progress_percentage": progress_percentage,
                    "is_complete": enhanced_ideas == total_ideas,
                    "last_updated": datetime.now().isoformat()
                }
            })
        else:
            return jsonify({"error": "Failed to get progress"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/keyword-research/summary/<analysis_id>', methods=['GET'])
def get_keyword_research_summary(analysis_id):
    """Get keyword research summary for dashboard display"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id required"}), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({"error": "Invalid UUID format"}), 400
        
        # Get enhanced blog ideas for summary
        phase2_storage = Phase2SupabaseStorage()
        phase2_storage.set_user_context(user_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            blog_ideas = loop.run_until_complete(phase2_storage.get_blog_ideas(analysis_id, user_id))
        finally:
            loop.close()
        
        if not blog_ideas:
            return jsonify({"error": "No blog ideas found"}), 404
        
        # Calculate summary metrics
        enhanced_ideas = [idea for idea in blog_ideas if idea.get('keyword_research_enhanced', False)]
        
        total_search_volume = 0
        total_keywords = 0
        avg_difficulty = 0
        difficulty_scores = []
        
        for idea in enhanced_ideas:
            keyword_research_data = idea.get('keyword_research_data')
            if isinstance(keyword_research_data, str) and keyword_research_data:
                try:
                    data = json.loads(keyword_research_data)
                    total_search_volume += data.get('total_search_volume', 0)
                    difficulty_scores.append(data.get('average_difficulty', 0))
                    
                    # Count keywords
                    primary_data = data.get('primary_keywords_data', [])
                    secondary_data = data.get('secondary_keywords_data', [])
                    total_keywords += len(primary_data) + len(secondary_data)
                    
                except:
                    pass
        
        if difficulty_scores:
            avg_difficulty = round(sum(difficulty_scores) / len(difficulty_scores), 1)
        
        summary = {
            "analysis_id": analysis_id,
            "total_ideas": len(blog_ideas),
            "enhanced_ideas": len(enhanced_ideas),
            "enhancement_percentage": round((len(enhanced_ideas) / len(blog_ideas)) * 100, 1),
            "keyword_metrics": {
                "total_keywords": total_keywords,
                "total_search_volume": total_search_volume,
                "average_difficulty": avg_difficulty,
                "keywords_per_idea": round(total_keywords / len(enhanced_ideas), 1) if enhanced_ideas else 0
            },
            "quality_metrics": {
                "average_seo_score": round(sum(idea.get('seo_optimization_score', 0) for idea in blog_ideas) / len(blog_ideas), 1),
                "average_traffic_potential": round(sum(idea.get('traffic_potential_score', 0) for idea in blog_ideas) / len(blog_ideas), 1),
                "high_quality_ideas": len([idea for idea in blog_ideas if idea.get('overall_quality_score', 0) >= 80])
            },
            "ready_for_export": len(enhanced_ideas) > 0,
            "last_updated": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/api/v2/keyword-research/export/<analysis_id>', methods=['GET'])
def export_keyword_analysis_final(analysis_id):
    """Export keyword analysis - Final version that handles all data types"""
    try:
        print(f"🔄 Export request received for analysis: {analysis_id}")
        
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            print("❌ Missing user_id parameter")
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        print(f"👤 User ID: {user_id}")
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
            print("✅ UUIDs validated successfully")
        except ValueError as e:
            print(f"❌ Invalid UUID format: {e}")
            return jsonify({
                "success": False,
                "error": "Invalid user_id or analysis_id format"
            }), 400
        
        # Initialize Phase2 storage
        try:
            phase2_storage = Phase2SupabaseStorage()
            print("✅ Phase2 storage initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Phase2 storage: {e}")
            return jsonify({
                "success": False,
                "error": f"Storage initialization failed: {str(e)}"
            }), 500
        
        # Get blog ideas - this will get ALL fields from your Supabase table
        print("🔍 Fetching blog ideas...")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                blog_ideas = loop.run_until_complete(phase2_storage.get_blog_ideas(analysis_id, user_id))
                print(f"✅ Found {len(blog_ideas) if blog_ideas else 0} blog ideas")
            finally:
                loop.close()
                
        except Exception as e:
            print(f"❌ Failed to fetch blog ideas: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to fetch blog ideas: {str(e)}"
            }), 500
        
        if not blog_ideas:
            print("❌ No blog ideas found")
            return jsonify({
                "success": False,
                "error": "No blog ideas found for this analysis"
            }), 404
        
        print(f"📊 Processing {len(blog_ideas)} blog ideas for export...")
        
        # Process each idea and extract ALL keyword data
        export_data = []
        ideas_with_enhanced_data = 0
        ideas_with_basic_data = 0
        ideas_with_no_data = 0
        
        for idea in blog_ideas:
            print(f"🔍 Processing: {idea.get('title', 'Unknown')[:50]}...")
            
            # Get enhanced keyword data (these might be JSON strings or already parsed)
            enhanced_primary = idea.get('enhanced_primary_keywords')
            enhanced_secondary = idea.get('enhanced_secondary_keywords') 
            keyword_research_data = idea.get('keyword_research_data')
            keyword_research_enhanced = idea.get('keyword_research_enhanced', False)
            
            # Parse enhanced data if it's a JSON string
            if isinstance(enhanced_primary, str) and enhanced_primary and enhanced_primary != 'null':
                try:
                    enhanced_primary = json.loads(enhanced_primary)
                except:
                    enhanced_primary = []
            elif not enhanced_primary:
                enhanced_primary = []
                
            if isinstance(enhanced_secondary, str) and enhanced_secondary and enhanced_secondary != 'null':
                try:
                    enhanced_secondary = json.loads(enhanced_secondary)
                except:
                    enhanced_secondary = []
            elif not enhanced_secondary:
                enhanced_secondary = []
                
            if isinstance(keyword_research_data, str) and keyword_research_data and keyword_research_data != 'null':
                try:
                    keyword_research_data = json.loads(keyword_research_data)
                except:
                    keyword_research_data = {}
            elif not keyword_research_data:
                keyword_research_data = {}
            
            # Get basic keyword data
            primary_keywords = idea.get('primary_keywords', [])
            secondary_keywords = idea.get('secondary_keywords', [])
            
            # Parse basic keywords if they're JSON strings
            if isinstance(primary_keywords, str) and primary_keywords and primary_keywords != 'null':
                try:
                    primary_keywords = json.loads(primary_keywords)
                except:
                    primary_keywords = primary_keywords.split(',') if primary_keywords else []
            elif not primary_keywords:
                primary_keywords = []
                
            if isinstance(secondary_keywords, str) and secondary_keywords and secondary_keywords != 'null':
                try:
                    secondary_keywords = json.loads(secondary_keywords)
                except:
                    secondary_keywords = secondary_keywords.split(',') if secondary_keywords else []
            elif not secondary_keywords:
                secondary_keywords = []
            
            # Determine data status
            has_enhanced_data = (
                enhanced_primary or 
                enhanced_secondary or 
                keyword_research_data.get('total_search_volume', 0) > 0 or
                keyword_research_enhanced
            )
            
            has_basic_data = primary_keywords or secondary_keywords
            
            print(f"   Enhanced data: {bool(has_enhanced_data)}")
            print(f"   Basic data: {bool(has_basic_data)}")
            print(f"   Enhanced flag: {keyword_research_enhanced}")
            print(f"   Enhanced primary: {len(enhanced_primary) if enhanced_primary else 0}")
            print(f"   Enhanced secondary: {len(enhanced_secondary) if enhanced_secondary else 0}")
            print(f"   Research data volume: {keyword_research_data.get('total_search_volume', 0)}")
            
            # Base row data for this idea
            base_row = {
                'Blog Idea': idea.get('title', ''),
                'Content Format': idea.get('content_format', ''),
                'Quality Score': idea.get('overall_quality_score', 0),
                'SEO Score': idea.get('seo_optimization_score', 0),
                'Viral Potential': idea.get('viral_potential_score', 0),
                'Business Impact': idea.get('business_impact_score', 0),
                'Audience Alignment': idea.get('audience_alignment_score', 0),
                'Feasibility': idea.get('content_feasibility_score', 0),
                'Traffic Potential': idea.get('traffic_potential_score', 0),
                'Competition Score': idea.get('competition_score', 0),
                'Difficulty Level': idea.get('difficulty_level', ''),
                'Word Count': idea.get('estimated_word_count', 0),
                'Reading Time': idea.get('estimated_reading_time', 0),
                'Enhancement Status': '',
                'Keywords Enhanced': keyword_research_enhanced
            }
            
            # Process enhanced keyword data first (highest priority)
            if has_enhanced_data:
                ideas_with_enhanced_data += 1
                
                # Export enhanced primary keywords
                if enhanced_primary:
                    for i, kw_data in enumerate(enhanced_primary):
                        if isinstance(kw_data, dict):
                            row = base_row.copy()
                            row.update({
                                'Keyword Type': 'Primary (Enhanced)',
                                'Keyword': kw_data.get('keyword', ''),
                                'Keyword Position': i + 1,
                                'Search Volume': kw_data.get('search_volume', 0),
                                'Difficulty': kw_data.get('keyword_difficulty', 0),
                                'CPC': f"${kw_data.get('cpc', 0):.2f}",
                                'Competition': kw_data.get('competition', ''),
                                'Intent': kw_data.get('search_intent', ''),
                                'Source': kw_data.get('source_tool', 'Enhanced'),
                                'Enhancement Status': 'Enhanced with Research Data'
                            })
                            export_data.append(row)
                
                # Export enhanced secondary keywords
                if enhanced_secondary:
                    for i, kw_data in enumerate(enhanced_secondary):
                        if isinstance(kw_data, dict):
                            row = base_row.copy()
                            row.update({
                                'Keyword Type': 'Secondary (Enhanced)',
                                'Keyword': kw_data.get('keyword', ''),
                                'Keyword Position': i + 1,
                                'Search Volume': kw_data.get('search_volume', 0),
                                'Difficulty': kw_data.get('keyword_difficulty', 0),
                                'CPC': f"${kw_data.get('cpc', 0):.2f}",
                                'Competition': kw_data.get('competition', ''),
                                'Intent': kw_data.get('search_intent', ''),
                                'Source': kw_data.get('source_tool', 'Enhanced'),
                                'Enhancement Status': 'Enhanced with Research Data'
                            })
                            export_data.append(row)
                
                # If enhanced flag is set but no individual keywords, create summary row
                if keyword_research_enhanced and not enhanced_primary and not enhanced_secondary:
                    row = base_row.copy()
                    row.update({
                        'Keyword Type': 'Enhanced Summary',
                        'Keyword': 'Keywords Enhanced (Details Missing)',
                        'Keyword Position': 0,
                        'Search Volume': keyword_research_data.get('total_search_volume', 0),
                        'Difficulty': keyword_research_data.get('average_difficulty', 0),
                        'CPC': f"${keyword_research_data.get('average_cpc', 0):.2f}",
                        'Competition': 'Mixed',
                        'Intent': 'Mixed',
                        'Source': 'Enhancement Process',
                        'Enhancement Status': 'Enhanced (Summary Only)'
                    })
                    export_data.append(row)
                    
            # Process basic keyword data (if no enhanced data available)
            elif has_basic_data:
                ideas_with_basic_data += 1
                
                # Export basic primary keywords
                for i, keyword in enumerate(primary_keywords):
                    if keyword and keyword.strip():
                        row = base_row.copy()
                        row.update({
                            'Keyword Type': 'Primary (Basic)',
                            'Keyword': keyword.strip(),
                            'Keyword Position': i + 1,
                            'Search Volume': 'Unknown',
                            'Difficulty': 'Unknown',
                            'CPC': 'Unknown',
                            'Competition': 'Unknown',
                            'Intent': 'Unknown',
                            'Source': 'Blog Generation',
                            'Enhancement Status': 'Basic Keywords - Needs Research'
                        })
                        export_data.append(row)
                
                # Export basic secondary keywords (first 5)
                for i, keyword in enumerate(secondary_keywords[:5]):
                    if keyword and keyword.strip():
                        row = base_row.copy()
                        row.update({
                            'Keyword Type': 'Secondary (Basic)',
                            'Keyword': keyword.strip(),
                            'Keyword Position': i + 1,
                            'Search Volume': 'Unknown',
                            'Difficulty': 'Unknown', 
                            'CPC': 'Unknown',
                            'Competition': 'Unknown',
                            'Intent': 'Unknown',
                            'Source': 'Blog Generation',
                            'Enhancement Status': 'Basic Keywords - Needs Research'
                        })
                        export_data.append(row)
                        
            # No keyword data at all
            else:
                ideas_with_no_data += 1
                row = base_row.copy()
                row.update({
                    'Keyword Type': 'No Keywords',
                    'Keyword': 'N/A - Needs Keyword Research',
                    'Keyword Position': 0,
                    'Search Volume': 0,
                    'Difficulty': 'Unknown',
                    'CPC': '$0.00',
                    'Competition': 'Unknown',
                    'Intent': 'Unknown',
                    'Source': 'N/A',
                    'Enhancement Status': 'No Keywords - Needs Research'
                })
                export_data.append(row)
        
        print(f"📊 EXPORT SUMMARY:")
        print(f"   Ideas with enhanced data: {ideas_with_enhanced_data}")
        print(f"   Ideas with basic data: {ideas_with_basic_data}")
        print(f"   Ideas with no data: {ideas_with_no_data}")
        print(f"   Total export rows: {len(export_data)}")
        
        if not export_data:
            print("❌ No data to export")
            return jsonify({
                "success": False,
                "error": "No data available for export"
            }), 404
        
        # Create CSV using pandas
        try:
            df = pd.DataFrame(export_data)
            csv_content = df.to_csv(index=False)
            print("✅ CSV generated successfully")
            print(f"📄 CSV preview (first 300 chars): {csv_content[:300]}...")
        except Exception as e:
            print(f"❌ CSV generation failed: {e}")
            return jsonify({
                "success": False,
                "error": f"CSV generation failed: {str(e)}"
            }), 500
        
        # Create file response
        try:
            csv_bytes = io.BytesIO(csv_content.encode('utf-8'))
            
            # Enhanced filename with data type indicator
            data_type = "enhanced" if ideas_with_enhanced_data > 0 else "basic"
            filename = f'blog_keywords_{data_type}_{analysis_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            print(f"📁 Sending file: {filename} ({len(csv_content)} bytes)")
            
            return send_file(
                csv_bytes,
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )
            
        except Exception as e:
            print(f"❌ File creation failed: {e}")
            return jsonify({
                "success": False,
                "error": f"File creation failed: {str(e)}"
            }), 500
        
    except Exception as e:
        print(f"❌ Unexpected error in export endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": f"Export failed: {str(e)}",
            "debug_info": "Check server logs for detailed error information"
        }), 500


# BONUS: Add a quick check endpoint to see what's actually in your enhanced fields
@app.route('/api/v2/keyword-research/check-enhanced-data/<analysis_id>', methods=['GET'])
def check_enhanced_data(analysis_id):
    """Quick check to see what's in the enhanced keyword fields"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id required"}), 400
        
        # Direct Supabase query to see raw data
        phase2_storage = Phase2SupabaseStorage()
        phase2_storage.set_user_context(user_id)
        
        # Get first few ideas and show their enhanced fields
        result = phase2_storage._execute_query(
            'GET', 
            f'blog_ideas?trend_analysis_id=eq.{analysis_id}&user_id=eq.{user_id}&select=id,title,enhanced_primary_keywords,enhanced_secondary_keywords,keyword_research_data,keyword_research_enhanced&limit=3'
        )
        
        if result['success']:
            return jsonify({
                "success": True,
                "sample_enhanced_data": result['data'],
                "note": "This shows raw data from Supabase enhanced keyword fields"
            })
        else:
            return jsonify({"error": result.get('error')}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v2/keyword-research/debug/<analysis_id>', methods=['GET'])
def debug_keyword_data_structure(analysis_id):
    """Debug endpoint to inspect the actual data structure in the database"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id or analysis_id format"
            }), 400
        
        # Get blog ideas
        phase2_storage = Phase2SupabaseStorage()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            blog_ideas = loop.run_until_complete(phase2_storage.get_blog_ideas(analysis_id, user_id))
        finally:
            loop.close()
        
        if not blog_ideas:
            return jsonify({
                "success": False,
                "error": "No blog ideas found"
            }), 404
        
        # Analyze the first few ideas to understand data structure
        debug_info = {
            "total_ideas": len(blog_ideas),
            "analysis_id": analysis_id,
            "user_id": user_id,
            "sample_data_structures": []
        }
        
        # Analyze first 3 ideas
        for i, idea in enumerate(blog_ideas[:3]):
            idea_debug = {
                "idea_index": i,
                "title": idea.get('title', 'Unknown'),
                "available_fields": list(idea.keys()),
                "keyword_fields_analysis": {}
            }
            
            # Check each keyword-related field
            keyword_fields = [
                'enhanced_primary_keywords',
                'enhanced_secondary_keywords', 
                'keyword_research_data',
                'primary_keywords',
                'secondary_keywords',
                'seo_optimization_score',
                'traffic_potential_score',
                'keyword_research_enhanced'
            ]
            
            for field in keyword_fields:
                value = idea.get(field)
                if value is not None:
                    idea_debug["keyword_fields_analysis"][field] = {
                        "type": type(value).__name__,
                        "value_preview": str(value)[:200] if len(str(value)) > 200 else str(value),
                        "is_empty": not bool(value),
                        "length": len(value) if hasattr(value, '__len__') else 'N/A'
                    }
                else:
                    idea_debug["keyword_fields_analysis"][field] = {
                        "type": "NoneType",
                        "value_preview": "None",
                        "is_empty": True,
                        "length": 0
                    }
            
            debug_info["sample_data_structures"].append(idea_debug)
        
        # Summary statistics
        enhanced_count = 0
        basic_keywords_count = 0
        no_keywords_count = 0
        
        for idea in blog_ideas:
            enhanced_primary = idea.get('enhanced_primary_keywords')
            enhanced_secondary = idea.get('enhanced_secondary_keywords')
            primary = idea.get('primary_keywords')
            secondary = idea.get('secondary_keywords')
            
            has_enhanced = bool(enhanced_primary or enhanced_secondary)
            has_basic = bool(primary or secondary)
            
            if has_enhanced:
                enhanced_count += 1
            elif has_basic:
                basic_keywords_count += 1
            else:
                no_keywords_count += 1
        
        debug_info["summary_statistics"] = {
            "ideas_with_enhanced_keywords": enhanced_count,
            "ideas_with_basic_keywords_only": basic_keywords_count,
            "ideas_with_no_keywords": no_keywords_count,
            "enhancement_success_rate": f"{(enhanced_count / len(blog_ideas)) * 100:.1f}%"
        }
        
        return jsonify({
            "success": True,
            "debug_info": debug_info
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Debug failed: {str(e)}"
        }), 500

############

 # ADD THIS VERIFICATION ENDPOINT TO YOUR noodl_server.py

@app.route('/api/v2/keyword-research/verify-enhancement/<analysis_id>', methods=['GET'])
def verify_enhancement_data(analysis_id):
    """Verify that enhancement data was properly saved"""
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required as query parameter"
            }), 400
        
        # Validate UUIDs
        try:
            uuid.UUID(user_id)
            uuid.UUID(analysis_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user_id or analysis_id format"
            }), 400
        
        # Get blog ideas
        phase2_storage = Phase2SupabaseStorage()
        phase2_storage.set_user_context(user_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            blog_ideas = loop.run_until_complete(phase2_storage.get_blog_ideas(analysis_id, user_id))
        finally:
            loop.close()
        
        if not blog_ideas:
            return jsonify({
                "success": False,
                "error": "No blog ideas found"
            }), 404
        
        # Analyze enhancement status
        enhancement_analysis = {
            "total_ideas": len(blog_ideas),
            "analysis_id": analysis_id,
            "user_id": user_id,
            "enhancement_status": {},
            "detailed_breakdown": [],
            "verification_timestamp": datetime.now().isoformat()
        }
        
        enhanced_count = 0
        basic_keywords_count = 0
        no_keywords_count = 0
        
        # Check each idea for enhancement data
        for i, idea in enumerate(blog_ideas[:5]):  # Show details for first 5 ideas
            # Check for enhanced data
            enhanced_primary = idea.get('enhanced_primary_keywords', [])
            enhanced_secondary = idea.get('enhanced_secondary_keywords', [])
            keyword_research_data = idea.get('keyword_research_data', {})
            keyword_research_enhanced = idea.get('keyword_research_enhanced', False)
            
            # Check for basic data
            primary_keywords = idea.get('primary_keywords', [])
            secondary_keywords = idea.get('secondary_keywords', [])
            
            # Determine status
            has_enhanced_data = bool(enhanced_primary or enhanced_secondary or keyword_research_data or keyword_research_enhanced)
            has_basic_data = bool(primary_keywords or secondary_keywords)
            
            if has_enhanced_data:
                status = "Enhanced"
                enhanced_count += 1
            elif has_basic_data:
                status = "Basic Keywords Only"
                basic_keywords_count += 1
            else:
                status = "No Keywords"
                no_keywords_count += 1
            
            # Detailed breakdown for first 5 ideas
            idea_detail = {
                "idea_index": i,
                "title": idea.get('title', 'Unknown')[:50],
                "status": status,
                "enhancement_data": {
                    "keyword_research_enhanced": keyword_research_enhanced,
                    "enhanced_primary_count": len(enhanced_primary) if enhanced_primary else 0,
                    "enhanced_secondary_count": len(enhanced_secondary) if enhanced_secondary else 0,
                    "has_research_data": bool(keyword_research_data),
                    "total_search_volume": keyword_research_data.get('total_search_volume', 0) if keyword_research_data else 0,
                    "seo_score": idea.get('seo_optimization_score', 0),
                    "traffic_score": idea.get('traffic_potential_score', 0)
                },
                "basic_data": {
                    "primary_keywords_count": len(primary_keywords) if primary_keywords else 0,
                    "secondary_keywords_count": len(secondary_keywords) if secondary_keywords else 0,
                    "sample_primary": primary_keywords[:2] if primary_keywords else [],
                    "sample_secondary": secondary_keywords[:2] if secondary_keywords else []
                }
            }
            
            enhancement_analysis["detailed_breakdown"].append(idea_detail)
        
        # Count remaining ideas
        for idea in blog_ideas[5:]:
            enhanced_primary = idea.get('enhanced_primary_keywords', [])
            enhanced_secondary = idea.get('enhanced_secondary_keywords', [])
            keyword_research_data = idea.get('keyword_research_data', {})
            keyword_research_enhanced = idea.get('keyword_research_enhanced', False)
            primary_keywords = idea.get('primary_keywords', [])
            secondary_keywords = idea.get('secondary_keywords', [])
            
            has_enhanced_data = bool(enhanced_primary or enhanced_secondary or keyword_research_data or keyword_research_enhanced)
            has_basic_data = bool(primary_keywords or secondary_keywords)
            
            if has_enhanced_data:
                enhanced_count += 1
            elif has_basic_data:
                basic_keywords_count += 1
            else:
                no_keywords_count += 1
        
        # Summary statistics
        enhancement_analysis["enhancement_status"] = {
            "ideas_with_enhanced_keywords": enhanced_count,
            "ideas_with_basic_keywords_only": basic_keywords_count,
            "ideas_with_no_keywords": no_keywords_count,
            "enhancement_success_rate": f"{(enhanced_count / len(blog_ideas)) * 100:.1f}%",
            "enhancement_working": enhanced_count > 0
        }
        
        # Recommendations
        if enhanced_count == 0:
            enhancement_analysis["recommendations"] = [
                "No enhanced keyword data found",
                "Check if keyword enhancement process completed successfully",
                "Verify Supabase table has enhanced keyword columns",
                "Re-run keyword enhancement with debug enabled"
            ]
        elif enhanced_count < len(blog_ideas) / 2:
            enhancement_analysis["recommendations"] = [
                f"Partial enhancement detected ({enhanced_count}/{len(blog_ideas)} ideas)",
                "Some ideas may need re-enhancement",
                "Check for any errors in the enhancement process"
            ]
        else:
            enhancement_analysis["recommendations"] = [
                f"Enhancement successful! {enhanced_count}/{len(blog_ideas)} ideas enhanced",
                "Data is ready for export",
                "Enhancement working properly"
            ]
        
        return jsonify({
            "success": True,
            "verification": enhancement_analysis
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Verification failed: {str(e)}"
        }), 500






# ============================================================================
# ADD THIS ROUTE LISTING ENDPOINT FOR DEBUGGING
# ============================================================================

@app.route('/api/v2/debug/routes', methods=['GET'])
def list_all_routes():
    """List all registered routes for debugging"""
    routes = []
    for rule in app.url_map.iter_rules():
        if 'keyword-research' in rule.rule:
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
    
    return jsonify({
        "keyword_research_routes": routes,
        "total_routes": len(list(app.url_map.iter_rules()))
    })

@app.route('/')
def enhanced_index_with_keyword_research():
    return jsonify({
        "service": "Enhanced Trend Research + Blog Idea Generation + Keyword Research - Noodl Integration Server",
        "version": "2.4.0 RLS + Phase 2 + Keyword Research",
        "status": "operational",
        "features": [
            "Phase 1: Trend Research & Market Intelligence",
            "Phase 2: Blog Idea Generation & Content Strategy", 
            "Phase 3: Manual Keyword Research Integration",
            "RLS (Row Level Security) Support",
            "User-Scoped Data Access",
            "Multi-Tool Keyword Import (Ahrefs, SEMrush, Moz, etc.)",
            "Keyword Enhancement & Optimization",
            "SEO Opportunity Analysis",
            "Advanced Error Handling"
        ],
        "keyword_research_endpoints": {
            "GET /api/v2/keyword-research/instructions/<tool>": "Get import instructions for keyword tools",
            "GET /api/v2/keyword-research/template/<tool>": "Download CSV template for keyword data",
            "POST /api/v2/keyword-research/upload": "Upload and parse keyword research file",
            "POST /api/v2/keyword-research/enhance-blog-ideas": "Enhance blog ideas with keyword data",
            "POST /api/v2/keyword-research/opportunities-report": "Generate keyword opportunities report",
            "GET /api/v2/keyword-research/export/<analysis_id>": "Export keyword analysis to CSV",
            "GET /api/v2/keyword-research/health": "Keyword research health check"
        },
        "supported_keyword_tools": [
            "Ahrefs Keywords Explorer",
            "SEMrush Keyword Magic Tool", 
            "Moz Keyword Explorer",
            "Ubersuggest",
            "KWFinder",
            "Custom CSV Format"
        ],
        "keyword_workflow": {
            "step1": "GET /api/v2/keyword-research/instructions/{tool} - Get export instructions",
            "step2": "Export keyword data from your tool using instructions",
            "step3": "POST /api/v2/keyword-research/upload - Upload and validate keyword file",
            "step4": "POST /api/v2/keyword-research/enhance-blog-ideas - Enhance blog ideas with keywords",
            "step5": "GET /api/v2/keyword-research/export/{analysis_id} - Export final analysis"
        }
    })


# ============================================================================
# STARTUP MESSAGE UPDATE - Add this to your main execution block
# ============================================================================

def print_enhanced_startup_with_keywords():
    """Enhanced startup message with keyword research information"""
    print("🚀 Starting Enhanced Noodl Integration Server (RLS + Phase 2 + Keyword Research)...")
    print("=" * 80)
    print("📡 Server URL: http://localhost:8001")
    print("🎯 Phase 1 Endpoint: http://localhost:8001/api/v2/enhanced-trend-research")
    print("💡 Phase 2 Endpoint: http://localhost:8001/api/v2/generate-blog-ideas/<analysis_id>")
    print("🔑 Keyword Research: http://localhost:8001/api/v2/keyword-research/")
    print("📊 Export Keywords: http://localhost:8001/api/v2/keyword-research/export/<analysis_id>")
    print("🔍 Health Checks: http://localhost:8001/api/v2/health | /api/v2/keyword-research/health")
    print("📚 API Docs: http://localhost:8001/")
    print("=" * 80)
    print("🔑 KEYWORD RESEARCH FEATURES:")
    print("   ✅ Ahrefs, SEMrush, Moz integration")
    print("   ✅ CSV template generation")
    print("   ✅ Data validation & quality checks")
    print("   ✅ Blog idea enhancement with keywords")
    print("   ✅ SEO opportunity analysis")
    print("   ✅ Export & reporting")
    print("=" * 80)
    print("📊 SUPPORTED TOOLS:")
    print("   🔍 Ahrefs Keywords Explorer")
    print("   🔍 SEMrush Keyword Magic Tool")
    print("   🔍 Moz Keyword Explorer")
    print("   🔍 Ubersuggest")
    print("   🔍 KWFinder")
    print("   🔍 Custom CSV format")
    print("=" * 80)
    print("🔄 COMPLETE WORKFLOW:")
    print("   1. Phase 1: POST /api/v2/enhanced-trend-research")
    print("   2. Select: PATCH /api/v2/topics/{id}/select")
    print("   3. Phase 2: POST /api/v2/generate-blog-ideas/{analysis_id}")
    print("   4. Keywords: GET /api/v2/keyword-research/instructions/{tool}")
    print("   5. Upload: POST /api/v2/keyword-research/upload")
    print("   6. Enhance: POST /api/v2/keyword-research/enhance-blog-ideas")
    print("   7. Export: GET /api/v2/keyword-research/export/{analysis_id}")
    print("=" * 80)
    print("💰 AFFILIATE RESEARCH ENDPOINTS:")
    print("   🔍 POST /api/v2/affiliate-research - Research affiliate offers")
    print("   📊 POST /api/v2/affiliate-research/validate - Quick profitability check")
    print("   🎯 POST /api/v2/affiliate-research/subtopics - Generate subtopics")
    print("   ❤️ GET /api/v2/affiliate-research/health - Health check")
    print("=" * 80)
    print("🎮 Ready for complete trend analysis + blog generation + keyword optimization!")

# ============================================================================
# LINKUP-BASED AFFILIATE RESEARCH ENDPOINTS
# ============================================================================

import asyncio
import os

@app.route('/api/v2/affiliate-research', methods=['POST'])
def affiliate_research_endpoint():
    """Linkup-based affiliate research endpoint"""
    try:
        from linkup_affiliate_research import linkup_affiliate_research
        from supabase_affiliate_storage import affiliate_storage
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400
        
        # Extract and validate user_id
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400
        
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
        
        print(f"🔍 Linkup research for topic: {topic}")
        
        # Run research asynchronously
        async def run_research():
            from linkup_affiliate_research import linkup_affiliate_research
            research_data = await linkup_affiliate_research.search_affiliate_programs(topic, subtopics)
            
            # Store in Supabase if user_id provided
            if user_id and user_id != "test-user-123":
                from supabase_affiliate_storage import affiliate_storage
                await affiliate_storage.store_affiliate_research(
                    topic=topic,
                    user_id=user_id,
                    research_data=research_data
                )
            
            return research_data
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            research_data = loop.run_until_complete(run_research())
        finally:
            loop.close()
        
        # Check profitability
        analysis = research_data['profitability_analysis']
        should_proceed = int(analysis['score']) >= int(min_commission_threshold)
        
        return jsonify({
            "success": True,
            "affiliate_research": research_data,
            "should_proceed": should_proceed,
            "threshold_check": {
                "min_required": min_commission_threshold,
                "actual_score": analysis['score'],
                "threshold_met": should_proceed
            }
        })
        
    except ImportError as e:
        logger.error(f"❌ Linkup modules not available: {e}")
        return jsonify({
            "success": False,
            "error": "Linkup-based affiliate research not available",
            "fallback": "Using mock data instead"
        }), 503
    except Exception as e:
        logger.error(f"❌ Affiliate research failed: {e}")
        return jsonify({
            "success": False,
            "error": f"Affiliate research failed: {str(e)}"
        }), 500

@app.route('/api/v2/affiliate-research/validate', methods=['POST'])
def validate_affiliate_profitability():
    """Quick validation of topic profitability"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400
        
        user_id = data.get('user_id')
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({
                "success": False,
                "error": "Topic is required"
            }), 400
        
        async def run_validation():
            from linkup_affiliate_research import linkup_affiliate_research
            research_data = await linkup_affiliate_research.search_affiliate_programs(topic, subtopics=[topic])
            
            analysis = research_data['profitability_analysis']
            return {
                "topic": topic,
                "is_profitable": analysis['level'] in ["good", "excellent"],
                "profitability_score": analysis['score'],
                "level": analysis['level'],
                "total_programs": analysis['total_programs'],
                "avg_commission_rate": analysis['avg_commission_rate'],
                "recommendation": "proceed" if analysis['level'] in ["good", "excellent"] else "consider_alternatives"
            }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(run_validation())
        finally:
            loop.close()
        
        return jsonify({
            "success": True,
            **result
        })
        
    except ImportError as e:
        return jsonify({
            "success": False,
            "error": "Linkup modules not available",
            "fallback": "Using mock validation"
        }), 503
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Validation failed: {str(e)}"
        }), 500

@app.route('/api/v2/affiliate-research/health', methods=['GET'])
def affiliate_health_check():
    """Health check for affiliate research"""
    try:
        # Check if Linkup API key is available
        linkup_key = os.getenv('LINKUP_API_KEY')
        
        response = {
            "status": "healthy" if linkup_key else "degraded",
            "timestamp": datetime.now().isoformat(),
            "linkup_api_configured": bool(linkup_key),
            "features": [
                "linkup_web_search",
                "affiliate_program_discovery",
                "profitability_analysis",
                "supabase_storage"
            ]
        }
        
        if not linkup_key:
            response["warning"] = "Linkup API key not configured - using mock data"
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 503

# Update your main execution to use the new startup message
if __name__ == "__main__":
    print_enhanced_startup_with_keywords()
    app.run(host='0.0.0.0', port=8001, debug=True)