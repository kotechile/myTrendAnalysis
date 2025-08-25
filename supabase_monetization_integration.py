#!/usr/bin/env python3
"""
Supabase Monetization Integration
Handles storage and retrieval of monetization analysis data in Supabase
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

import aiohttp
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseMonetizationIntegration:
    """Integration layer for monetization data with Supabase"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client"""
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.logger = logging.getLogger(__name__)
    
    async def store_monetization_analysis(self, 
                                        blog_idea_id: str,
                                        monetization_analysis: Dict[str, Any],
                                        analysis_id: Optional[str] = None) -> Dict[str, Any]:
        """Store monetization analysis results in Supabase"""
        
        try:
            analysis_id = analysis_id or str(uuid4())
            
            # Prepare data for monetization_analytics table
            analytics_data = {
                "id": str(uuid4()),
                "blog_idea_id": blog_idea_id,
                "analysis_id": analysis_id,
                "monetization_score": monetization_analysis["overall_monetization_score"],
                "estimated_annual_revenue": monetization_analysis["estimated_annual_revenue"],
                "monetization_priority": monetization_analysis["monetization_priority"],
                "confidence_score": 85,  # Default confidence for now
                
                # Revenue breakdown
                "affiliate_revenue": monetization_analysis["affiliate_opportunities"]["estimated_annual_revenue"],
                "digital_product_revenue": monetization_analysis["digital_product_opportunities"]["estimated_annual_revenue"],
                "service_revenue": monetization_analysis["service_opportunities"]["estimated_annual_revenue"],
                "lead_generation_revenue": monetization_analysis["lead_generation_opportunities"]["estimated_annual_revenue"],
                
                # Detailed analysis
                "affiliate_analysis": monetization_analysis["affiliate_opportunities"],
                "digital_product_analysis": monetization_analysis["digital_product_opportunities"],
                "service_analysis": monetization_analysis["service_opportunities"],
                "lead_generation_analysis": monetization_analysis["lead_generation_opportunities"],
                "monetization_strategy": monetization_analysis["monetization_strategy"]
            }
            
            # Insert into monetization_analytics
            response = self.supabase.table("monetization_analytics").insert(analytics_data).execute()
            
            # Update the blog_ideas table with summary fields
            update_data = {
                "monetization_score": monetization_analysis["overall_monetization_score"],
                "estimated_annual_revenue": monetization_analysis["estimated_annual_revenue"],
                "monetization_priority": monetization_analysis["monetization_priority"],
                "monetization_analysis": monetization_analysis,
                "revenue_breakdown": {
                    "affiliate": monetization_analysis["affiliate_opportunities"]["estimated_annual_revenue"],
                    "digital_product": monetization_analysis["digital_product_opportunities"]["estimated_annual_revenue"],
                    "service": monetization_analysis["service_opportunities"]["estimated_annual_revenue"],
                    "lead_generation": monetization_analysis["lead_generation_opportunities"]["estimated_annual_revenue"]
                },
                "monetization_strategy": monetization_analysis["monetization_strategy"]
            }
            
            self.supabase.table("blog_ideas").update(update_data).eq("id", blog_idea_id).execute()
            
            # Store recommendations
            await self._store_recommendations(blog_idea_id, monetization_analysis["monetization_strategy"])
            
            self.logger.info(f"✅ Monetization analysis stored for blog idea {blog_idea_id}")
            return {"success": True, "analysis_id": analysis_id}
            
        except Exception as e:
            self.logger.error(f"❌ Error storing monetization analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def _store_recommendations(self, blog_idea_id: str, strategy: Dict[str, Any]) -> None:
        """Store monetization recommendations"""
        
        try:
            recommendations = []
            
            # Immediate actions
            for action in strategy.get("immediate_actions", []):
                recommendations.append({
                    "id": str(uuid4()),
                    "blog_idea_id": blog_idea_id,
                    "recommendation_type": "immediate",
                    "priority": "high",
                    "action_text": action,
                    "estimated_impact": "High immediate revenue potential",
                    "implementation_complexity": "Low",
                    "estimated_revenue_boost": 1000,
                    "confidence_level": 80
                })
            
            # 30-day plan
            for action in strategy.get("30_day_plan", []):
                recommendations.append({
                    "id": str(uuid4()),
                    "blog_idea_id": blog_idea_id,
                    "recommendation_type": "30_day",
                    "priority": "high",
                    "action_text": action,
                    "estimated_impact": "Medium to high revenue potential",
                    "implementation_complexity": "Medium",
                    "estimated_revenue_boost": 5000,
                    "confidence_level": 75
                })
            
            # 90-day plan
            for action in strategy.get("90_day_plan", []):
                recommendations.append({
                    "id": str(uuid4()),
                    "blog_idea_id": blog_idea_id,
                    "recommendation_type": "90_day",
                    "priority": "medium",
                    "action_text": action,
                    "estimated_impact": "High revenue potential",
                    "implementation_complexity": "Medium",
                    "estimated_revenue_boost": 10000,
                    "confidence_level": 70
                })
            
            # Long-term strategy
            for action in strategy.get("long_term_strategy", []):
                recommendations.append({
                    "id": str(uuid4()),
                    "blog_idea_id": blog_idea_id,
                    "recommendation_type": "long_term",
                    "priority": "medium",
                    "action_text": action,
                    "estimated_impact": "Long-term revenue growth",
                    "implementation_complexity": "High",
                    "estimated_revenue_boost": 25000,
                    "confidence_level": 65
                })
            
            if recommendations:
                self.supabase.table("monetization_recommendations").insert(recommendations).execute()
                
        except Exception as e:
            self.logger.error(f"❌ Error storing recommendations: {e}")
    
    async def get_monetization_dashboard(self, topic: Optional[str] = None, 
                                       limit: int = 50) -> List[Dict[str, Any]]:
        """Get monetization dashboard data"""
        
        try:
            query = self.supabase.table("monetization_dashboard").select("*")
            
            if topic:
                query = query.eq("topic", topic)
            
            response = query.limit(limit).execute()
            
            return response.data or []
            
        except Exception as e:
            self.logger.error(f"❌ Error getting monetization dashboard: {e}")
            return []
    
    async def get_monetization_summary(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Get monetization summary statistics"""
        
        try:
            query = self.supabase.table("monetization_summary").select("*")
            
            if topic:
                query = query.eq("topic", topic)
                response = query.single().execute()
            else:
                response = query.execute()
                return response.data or []
            
            return response.data or {}
            
        except Exception as e:
            self.logger.error(f"❌ Error getting monetization summary: {e}")
            return {}
    
    async def get_top_monetizable_ideas(self, topic: Optional[str] = None, 
                                      limit: int = 10) -> List[Dict[str, Any]]:
        """Get top monetizable blog ideas"""
        
        try:
            query = self.supabase.table("blog_ideas").select(
                "id, title, topic, content_format, difficulty_level, monetization_score, "
                "estimated_annual_revenue, monetization_priority, created_at"
            )
            
            if topic:
                query = query.eq("topic", topic)
            
            response = query.order("estimated_annual_revenue", desc=True).limit(limit).execute()
            
            return response.data or []
            
        except Exception as e:
            self.logger.error(f"❌ Error getting top monetizable ideas: {e}")
            return []
    
    async def get_recommendations_by_blog_idea(self, blog_idea_id: str) -> List[Dict[str, Any]]:
        """Get monetization recommendations for a specific blog idea"""
        
        try:
            response = self.supabase.table("monetization_recommendations").select("*").eq("blog_idea_id", blog_idea_id).order("priority", desc=True).execute()
            
            return response.data or []
            
        except Exception as e:
            self.logger.error(f"❌ Error getting recommendations: {e}")
            return []
    
    async def update_recommendation_status(self, recommendation_id: str, 
                                         status: str, 
                                         completed_at: Optional[datetime] = None) -> Dict[str, Any]:
        """Update recommendation status"""
        
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            if status == "completed" and completed_at:
                update_data["completed_at"] = completed_at.isoformat()
            
            response = self.supabase.table("monetization_recommendations").update(update_data).eq("id", recommendation_id).execute()
            
            return {"success": True, "data": response.data}
            
        except Exception as e:
            self.logger.error(f"❌ Error updating recommendation status: {e}")
            return {"success": False, "error": str(e)}
    
    async def store_performance_data(self, blog_idea_id: str, 
                                   performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store actual performance data"""
        
        try:
            performance_record = {
                "id": str(uuid4()),
                "blog_idea_id": blog_idea_id,
                **performance_data,
                "last_updated": datetime.now().isoformat()
            }
            
            response = self.supabase.table("monetization_performance").insert(performance_record).execute()
            
            return {"success": True, "data": response.data}
            
        except Exception as e:
            self.logger.error(f"❌ Error storing performance data: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_performance_comparison(self, blog_idea_id: str) -> Dict[str, Any]:
        """Compare estimated vs actual performance"""
        
        try:
            # Get estimated data
            idea_data = self.supabase.table("blog_ideas").select("estimated_annual_revenue, monetization_score").eq("id", blog_idea_id).single().execute()
            
            # Get actual performance
            performance_data = self.supabase.table("monetization_performance").select("*").eq("blog_idea_id", blog_idea_id).order("last_updated", desc=True).limit(1).execute()
            
            if not idea_data.data or not performance_data.data:
                return {}
            
            estimated = idea_data.data
            actual = performance_data.data[0]
            
            return {
                "estimated_revenue": estimated.get("estimated_annual_revenue", 0),
                "actual_revenue": actual.get("actual_revenue", 0),
                "revenue_accuracy": (actual.get("actual_revenue", 0) / max(estimated.get("estimated_annual_revenue", 1), 1)) * 100,
                "traffic_accuracy": (actual.get("actual_traffic", 0) / max(actual.get("estimated_monthly_traffic", 1), 1)) * 100,
                "conversion_rate": actual.get("conversion_rate", 0),
                "revenue_sources": actual.get("revenue_sources", {})
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting performance comparison: {e}")
            return {}


# Convenience functions for async usage
async def store_monetization_data(blog_idea_id: str, 
                                monetization_analysis: Dict[str, Any],
                                supabase_url: str,
                                supabase_key: str) -> Dict[str, Any]:
    """Convenience function to store monetization data"""
    
    integration = SupabaseMonetizationIntegration(supabase_url, supabase_key)
    return await integration.store_monetization_analysis(blog_idea_id, monetization_analysis)


async def get_monetization_insights(supabase_url: str, 
                                  supabase_key: str,
                                  topic: Optional[str] = None) -> Dict[str, Any]:
    """Get comprehensive monetization insights"""
    
    integration = SupabaseMonetizationIntegration(supabase_url, supabase_key)
    
    dashboard = await integration.get_monetization_dashboard(topic)
    summary = await integration.get_monetization_summary(topic)
    top_ideas = await integration.get_top_monetizable_ideas(topic)
    
    return {
        "dashboard": dashboard,
        "summary": summary,
        "top_ideas": top_ideas
    }


if __name__ == "__main__":
    import os
    
    async def test_integration():
        """Test the Supabase integration"""
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL and SUPABASE_KEY environment variables required")
            return
        
        integration = SupabaseMonetizationIntegration(supabase_url, supabase_key)
        
        # Test data
        test_analysis = {
            "overall_monetization_score": 85,
            "estimated_annual_revenue": 50000,
            "monetization_priority": "High Priority - Immediate Implementation",
            "affiliate_opportunities": {
                "estimated_annual_revenue": 20000,
                "score": 90
            },
            "digital_product_opportunities": {
                "estimated_annual_revenue": 15000,
                "score": 80
            },
            "service_opportunities": {
                "estimated_annual_revenue": 10000,
                "score": 75
            },
            "lead_generation_opportunities": {
                "estimated_annual_revenue": 5000,
                "score": 70
            },
            "monetization_strategy": {
                "immediate_actions": ["Join affiliate programs"],
                "30_day_plan": ["Create lead magnet"],
                "90_day_plan": ["Launch digital product"]
            }
        }
        
        # Test storage
        result = await integration.store_monetization_analysis(
            blog_idea_id="test-blog-idea-123",
            monetization_analysis=test_analysis
        )
        
        print("Integration test result:", result)
    
    asyncio.run(test_integration())