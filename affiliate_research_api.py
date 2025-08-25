#!/usr/bin/env python3
"""
Affiliate Offer Research API for Noodl Server
Integrates as first step before trend analysis to validate topic profitability
"""

from flask import Flask, request, jsonify
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import re
from urllib.parse import urlparse, urlencode
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AffiliateOfferResearch:
    """Comprehensive affiliate offer research system"""
    
    def __init__(self):
        self.networks = {
            'amazon': {
                'name': 'Amazon Associates',
                'base_url': 'https://affiliate-program.amazon.com',
                'commission_range': '1-10%',
                'cookie_duration': '24 hours',
                'categories': ['electronics', 'books', 'home', 'fashion', 'sports', 'health']
            },
            'cj': {
                'name': 'Commission Junction',
                'base_url': 'https://www.cj.com',
                'commission_range': '3-50%',
                'cookie_duration': '30-90 days',
                'categories': ['technology', 'finance', 'travel', 'retail', 'education']
            },
            'shareasale': {
                'name': 'ShareASale',
                'base_url': 'https://www.shareasale.com',
                'commission_range': '5-30%',
                'cookie_duration': '30-60 days',
                'categories': ['fashion', 'home', 'health', 'technology', 'business']
            },
            'clickbank': {
                'name': 'ClickBank',
                'base_url': 'https://www.clickbank.com',
                'commission_range': '50-75%',
                'cookie_duration': '60 days',
                'categories': ['health', 'fitness', 'education', 'business', 'relationships']
            },
            'impact': {
                'name': 'Impact',
                'base_url': 'https://impact.com',
                'commission_range': '5-50%',
                'cookie_duration': '30-90 days',
                'categories': ['technology', 'fashion', 'travel', 'finance', 'lifestyle']
            }
        }
        
    async def research_affiliate_offers(self, topic: str, subtopics: List[str] = None) -> Dict[str, Any]:
        """Research affiliate offers for topic and subtopics"""
        
        # Split broad topics into subtopics if needed
        if not subtopics:
            subtopics = await self._generate_subtopics(topic)
        
        all_offers = []
        profitability_analysis = {}
        
        # Research offers for each subtopic
        for subtopic in subtopics:
            offers = await self._search_affiliate_offers(subtopic)
            if offers:
                all_offers.extend(offers)
                profitability_analysis[subtopic] = {
                    'offer_count': len(offers),
                    'avg_commission': self._calculate_avg_commission(offers),
                    'high_value_offers': [o for o in offers if float(o.get('commission_rate', 0)) >= 20],
                    'total_monthly_searches': sum(o.get('monthly_searches', 0) for o in offers),
                    'competition_level': self._assess_competition(subtopic, offers)
                }
        
        # Overall profitability assessment
        overall_assessment = self._assess_overall_profitability(profitability_analysis)
        
        return {
            'topic': topic,
            'subtopics': subtopics,
            'offers': all_offers,
            'profitability_analysis': profitability_analysis,
            'overall_assessment': overall_assessment,
            'recommendations': self._generate_recommendations(overall_assessment, all_offers),
            'research_timestamp': datetime.now().isoformat()
        }
    
    async def _generate_subtopics(self, topic: str) -> List[str]:
        """Generate relevant subtopics for broad topics"""
        
        # Common topic mappings
        topic_mappings = {
            'fitness': ['home workouts', 'gym equipment', 'protein supplements', 'yoga accessories', 'running gear'],
            'technology': ['laptops', 'smartphones', 'software', 'gaming', 'smart home', 'accessories'],
            'finance': ['investing', 'budgeting tools', 'credit cards', 'loans', 'insurance', 'tax software'],
            'health': ['supplements', 'fitness equipment', 'healthy cooking', 'mental wellness', 'medical devices'],
            'travel': ['booking platforms', 'travel gear', 'accommodation', 'flights', 'travel insurance', 'activities'],
            'fashion': ['clothing', 'shoes', 'accessories', 'beauty', 'jewelry', 'watches'],
            'education': ['online courses', 'books', 'certifications', 'learning tools', 'tutoring', 'study materials'],
            'home': ['furniture', 'decor', 'kitchen', 'gardening', 'tools', 'organization'],
            'business': ['software', 'marketing tools', 'productivity', 'finance', 'legal', 'consulting'],
            'cooking': ['kitchen appliances', 'cookbooks', 'meal kits', 'specialty ingredients', 'cooking classes']
        }
        
        topic_lower = topic.lower()
        
        # Check for exact matches
        for key, subtopics in topic_mappings.items():
            if key in topic_lower:
                return subtopics
        
        # Generate generic subtopics based on topic length
        if len(topic.split()) <= 2:
            # Broad topic - generate more specific subtopics
            generic_subtopics = [
                f"{topic} for beginners",
                f"{topic} reviews",
                f"{topic} comparison",
                f"{topic} tools",
                f"{topic} courses",
                f"{topic} software"
            ]
            return generic_subtopics
        else:
            # Already specific topic
            return [topic]
    
    async def _search_affiliate_offers(self, subtopic: str) -> List[Dict[str, Any]]:
        """Search for affiliate offers for a specific subtopic"""
        
        offers = []
        
        # Simulate API calls to affiliate networks
        # In production, these would be real API integrations
        
        # Amazon Associates
        amazon_offers = await self._search_amazon_offers(subtopic)
        offers.extend(amazon_offers)
        
        # ShareASale
        shareasale_offers = await self._search_shareasale_offers(subtopic)
        offers.extend(shareasale_offers)
        
        # ClickBank
        clickbank_offers = await self._search_clickbank_offers(subtopic)
        offers.extend(clickbank_offers)
        
        # CJ Affiliate
        cj_offers = await self._search_cj_offers(subtopic)
        offers.extend(cj_offers)
        
        # Impact
        impact_offers = await self._search_impact_offers(subtopic)
        offers.extend(impact_offers)
        
        return offers
    
    async def _search_amazon_offers(self, subtopic: str) -> List[Dict[str, Any]]:
        """Search Amazon Associates offers"""
        # Simulate Amazon search with realistic data
        mock_products = [
            {'name': f'Premium {subtopic.title()} Guide', 'price': 29.99, 'category': 'books'},
            {'name': f'{subtopic.title()} Equipment Set', 'price': 149.99, 'category': 'electronics'},
            {'name': f'{subtopic.title()} Online Course', 'price': 99.99, 'category': 'education'}
        ]
        
        return [
            {
                'network': 'amazon',
                'offer_name': product['name'],
                'description': f'High-quality {subtopic} product with excellent reviews',
                'commission_rate': 4.5,
                'commission_amount': round(product['price'] * 0.045, 2),
                'cookie_duration': '24 hours',
                'product_price': product['price'],
                'category': product['category'],
                'monthly_searches': self._estimate_search_volume(subtopic),
                'competition_level': 'medium',
                'gravity_score': 75,
                'landing_page_url': f'https://amazon.com/{subtopic.replace(" ", "-")}',
                'deep_link_available': True,
                'promotional_materials': ['banners', 'text_links', 'product_feeds'],
                'approval_required': False
            }
            for product in mock_products
        ]
    
    async def _search_shareasale_offers(self, subtopic: str) -> List[Dict[str, Any]]:
        """Search ShareASale offers"""
        mock_offers = [
            {
                'network': 'shareasale',
                'offer_name': f'{subtopic.title()} Masterclass',
                'description': f'Comprehensive training program for {subtopic}',
                'commission_rate': 30,
                'commission_amount': 89.70,
                'cookie_duration': '60 days',
                'product_price': 299.00,
                'category': 'education',
                'monthly_searches': self._estimate_search_volume(subtopic) * 0.8,
                'competition_level': 'low',
                'gravity_score': 65,
                'landing_page_url': f'https://{subtopic.replace(" ", "")}course.com',
                'deep_link_available': True,
                'promotional_materials': ['banners', 'email_templates', 'social_media_kit'],
                'approval_required': True
            }
        ]
        return mock_offers
    
    async def _search_clickbank_offers(self, subtopic: str) -> List[Dict[str, Any]]:
        """Search ClickBank offers"""
        mock_offers = [
            {
                'network': 'clickbank',
                'offer_name': f'{subtopic.title()} Success System',
                'description': f'Proven system to master {subtopic} quickly',
                'commission_rate': 75,
                'commission_amount': 149.25,
                'cookie_duration': '60 days',
                'product_price': 199.00,
                'category': 'self_help',
                'monthly_searches': self._estimate_search_volume(subtopic) * 1.2,
                'competition_level': 'high',
                'gravity_score': 85,
                'landing_page_url': f'https://{subtopic.replace(" ", "")}success.com',
                'deep_link_available': True,
                'promotional_materials': ['sales_pages', 'email_swipes', 'banner_ads'],
                'approval_required': False
            }
        ]
        return mock_offers
    
    async def _search_cj_offers(self, subtopic: str) -> List[Dict[str, Any]]:
        """Search CJ Affiliate offers"""
        mock_offers = [
            {
                'network': 'cj',
                'offer_name': f'Professional {subtopic.title()} Tools',
                'description': f'Enterprise-grade tools for {subtopic} professionals',
                'commission_rate': 20,
                'commission_amount': 59.80,
                'cookie_duration': '45 days',
                'product_price': 299.00,
                'category': 'software',
                'monthly_searches': self._estimate_search_volume(subtopic) * 0.6,
                'competition_level': 'medium',
                'gravity_score': 70,
                'landing_page_url': f'https://{subtopic.replace(" ", "")}tools.com',
                'deep_link_available': True,
                'promotional_materials': ['product_feeds', 'text_links', 'banners'],
                'approval_required': True
            }
        ]
        return mock_offers
    
    async def _search_impact_offers(self, subtopic: str) -> List[Dict[str, Any]]:
        """Search Impact offers"""
        mock_offers = [
            {
                'network': 'impact',
                'offer_name': f'{subtopic.title()} Certification Program',
                'description': f'Industry-recognized certification for {subtopic} expertise',
                'commission_rate': 25,
                'commission_amount': 124.75,
                'cookie_duration': '30 days',
                'product_price': 499.00,
                'category': 'education',
                'monthly_searches': self._estimate_search_volume(subtopic) * 0.7,
                'competition_level': 'low',
                'gravity_score': 80,
                'landing_page_url': f'https://{subtopic.replace(" ", "")}certification.com',
                'deep_link_available': True,
                'promotional_materials': ['course_catalog', 'promotional_videos', 'landing_pages'],
                'approval_required': False
            }
        ]
        return mock_offers
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate monthly search volume for a keyword"""
        # Simple estimation based on keyword length and common terms
        base_volume = 1000
        
        # Increase for high-value terms
        high_value_terms = ['software', 'course', 'training', 'system', 'program', 'tool', 'guide']
        for term in high_value_terms:
            if term in keyword.lower():
                base_volume *= 2
        
        # Adjust for specificity
        word_count = len(keyword.split())
        if word_count > 3:
            base_volume *= 0.5  # Long-tail keywords have lower volume
        elif word_count == 1:
            base_volume *= 5    # Broad keywords have higher volume
            
        return int(base_volume)
    
    def _calculate_avg_commission(self, offers: List[Dict[str, Any]]) -> float:
        """Calculate average commission across offers"""
        if not offers:
            return 0.0
        return sum(o.get('commission_amount', 0) for o in offers) / len(offers)
    
    def _assess_competition(self, subtopic: str, offers: List[Dict[str, Any]]) -> str:
        """Assess competition level for a subtopic"""
        offer_count = len(offers)
        high_commission_count = len([o for o in offers if float(o.get('commission_rate', 0)) >= 30])
        
        if offer_count >= 10 and high_commission_count >= 3:
            return 'high'
        elif offer_count >= 5 and high_commission_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _assess_overall_profitability(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall profitability across all subtopics"""
        if not analysis:
            return {'score': 0, 'level': 'poor', 'reason': 'No offers found'}
        
        total_offers = sum(data['offer_count'] for data in analysis.values())
        avg_commission = sum(data['avg_commission'] for data in analysis.values()) / len(analysis)
        high_value_count = sum(len(data['high_value_offers']) for data in analysis.values())
        
        # Scoring system
        score = 0
        score += min(total_offers * 5, 30)  # Up to 30 points for offer volume
        score += min(avg_commission / 10, 30)  # Up to 30 points for commission value
        score += min(high_value_count * 10, 25)  # Up to 25 points for high-value offers
        score += min(len(analysis) * 5, 15)  # Up to 15 points for subtopic coverage
        
        score = int(score)
        
        if score >= 70:
            level = 'excellent'
            reason = 'Strong offer volume, high commissions, and good subtopic coverage'
        elif score >= 50:
            level = 'good'
            reason = 'Decent offer volume with moderate commissions'
        elif score >= 30:
            level = 'moderate'
            reason = 'Limited offers or lower commission rates'
        else:
            level = 'poor'
            reason = 'Very few offers or extremely low commissions'
        
        return {
            'score': score,
            'level': level,
            'reason': reason,
            'total_offers': total_offers,
            'avg_commission': avg_commission,
            'high_value_offers': high_value_count,
            'subtopics_covered': len(analysis)
        }
    
    def _generate_recommendations(self, assessment: Dict[str, Any], offers: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on assessment"""
        recommendations = []
        
        if assessment['level'] == 'excellent':
            recommendations.append("✅ Proceed with topic - excellent affiliate opportunities available")
            recommendations.append("🎯 Focus on high-commission offers with strong promotional materials")
            recommendations.append("📈 Consider creating comparison content for competing products")
        elif assessment['level'] == 'good':
            recommendations.append("⚠️ Topic has potential - proceed with strategic approach")
            recommendations.append("🔍 Research specific high-commission subtopics more deeply")
            recommendations.append("💡 Consider narrowing focus to most profitable subtopics")
        elif assessment['level'] == 'moderate':
            recommendations.append("⚠️ Limited profitability - consider topic refinement")
            recommendations.append("🎯 Focus on subtopics with highest commission potential")
            recommendations.append("💰 Consider combining with other monetization methods")
        else:
            recommendations.append("❌ Poor profitability - consider alternative topics")
            recommendations.append("🔄 Suggest exploring related but more profitable niches")
            recommendations.append("📊 Look for higher-value products/services in this space")
        
        # Network-specific recommendations
        networks = list(set(offer['network'] for offer in offers))
        if 'clickbank' in networks:
            recommendations.append("💡 ClickBank offers high commissions - focus on digital products")
        if 'amazon' in networks:
            recommendations.append("📦 Amazon offers broad product range - good for review content")
        if len(networks) > 2:
            recommendations.append("🌐 Multiple networks available - diversify income sources")
        
        return recommendations

def create_affiliate_research_app():
    app = Flask(__name__)
    affiliate_research = AffiliateOfferResearch()

    # ===========================================================================#
    # AFFILIATE RESEARCH ENDPOINTS
    # ===========================================================================#

    @app.route('/api/v2/affiliate-research', methods=['POST'])
    def research_affiliate_offers():
        """Research affiliate offers for a given topic"""
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
            max_subtopics = data.get('max_subtopics', 10)
            
            print(f"🔍 Researching affiliate offers for topic: {topic}")
            
            # Run affiliate research
            async def run_research():
                return await affiliate_research.research_affiliate_offers(topic, subtopics)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(run_research())
            finally:
                loop.close()
            
            # Check profitability threshold
            should_proceed = int(result['overall_assessment']['score']) >= int(min_commission_threshold)
            
            response_data = {
                "success": True,
                "affiliate_research": result,
                "should_proceed": should_proceed,
                "threshold_check": {
                    "min_required": min_commission_threshold,
                    "actual_score": result['overall_assessment']['score'],
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

    @app.route('/api/v2/affiliate-research/subtopics', methods=['POST'])
    def generate_subtopics():
        """Generate relevant subtopics for a broad topic"""
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
            
            # Generate subtopics
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                subtopics = loop.run_until_complete(affiliate_research._generate_subtopics(topic))
            finally:
                loop.close()
            
            return jsonify({
                "success": True,
                "topic": topic,
                "subtopics": subtopics,
                "subtopic_count": len(subtopics),
                "user_id": user_id
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Subtopic generation failed: {str(e)}"
            }), 500

    @app.route('/api/v2/affiliate-research/validate', methods=['POST'])
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
            
            # Quick validation with limited subtopics
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(affiliate_research.research_affiliate_offers(topic, max_subtopics=3))
            finally:
                loop.close()
            
            # Return simplified validation
            return jsonify({
                "success": True,
                "topic": topic,
                "is_profitable": result['overall_assessment']['level'] in ['good', 'excellent'],
                "profitability_score": result['overall_assessment']['score'],
                "level": result['overall_assessment']['level'],
                "total_offers": result['overall_assessment']['total_offers'],
                "avg_commission": result['overall_assessment']['avg_commission'],
                "user_id": user_id
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Validation failed: {str(e)}"
            }), 500

    @app.route('/api/v2/affiliate-research/health', methods=['GET'])
    def affiliate_research_health_check():
        """Health check for affiliate research functionality"""
        try:
            # Test functionality
            test_topic = "fitness"
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(affiliate_research.research_affiliate_offers(test_topic))
                is_healthy = len(result['offers']) > 0
            finally:
                loop.close()
            
            return jsonify({
                "status": "healthy" if is_healthy else "degraded",
                "timestamp": datetime.now().isoformat(),
                "affiliate_research_version": "v1.0",
                "test_result": {
                    "test_topic": test_topic,
                    "offers_found": len(result['offers']) if is_healthy else 0,
                    "functionality_test": "passed" if is_healthy else "failed"
                },
                "supported_networks": list(affiliate_research.networks.keys()),
                "features": [
                    "affiliate_offer_research",
                    "topic_profitability_analysis",
                    "subtopic_generation",
                    "profitability_thresholds",
                    "cancellation_recommendations"
                ]
            })
            
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }), 503
    return app

if __name__ == '__main__':
    app = create_affiliate_research_app()
    app.run(host='0.0.0.0', port=8001, debug=True)
