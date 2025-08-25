#!/usr/bin/env python3
"""
Linkup-based Affiliate Research API
Uses Linkup API to search for real affiliate opportunities
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import hashlib
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkupAffiliateResearch:
    """Real affiliate research using Linkup API"""
    
    def __init__(self, linkup_api_key: str = None):
        self.linkup_api_key = linkup_api_key or os.getenv('LINKUP_API_KEY')
        
        if not self.linkup_api_key:
            logger.error("❌ LINKUP_API_KEY not found in environment variables")
            self.linkup_api_key = "missing-key"
        else:
            logger.info("✅ LINKUP_API_KEY found")
            
        self.base_url = "https://api.linkup.so/v1"
        self.headers = {
            'Authorization': f'Bearer {self.linkup_api_key}',
            'Content-Type': 'application/json'
        }
        
    async def search_affiliate_programs(self, topic: str, subtopics: List[str] = None) -> Dict[str, Any]:
        """Search for real affiliate programs using Linkup"""
        
        if not subtopics:
            subtopics = await self._generate_subtopics_from_linkup(topic)
        
        all_programs = []
        search_results = []
        
        for subtopic in subtopics[:5]:  # Limit to 5 subtopics to avoid rate limits
            try:
                programs = await self._search_single_subtopic(subtopic)
                if programs:
                    all_programs.extend(programs)
                    search_results.append({
                        'subtopic': subtopic,
                        'programs_found': len(programs),
                        'programs': programs
                    })
            except Exception as e:
                logger.error(f"Error searching for {subtopic}: {e}")
                continue
        
        # Deduplicate programs based on unique identifiers
        unique_programs = self._deduplicate_programs(all_programs)
        
        # Generate profitability analysis
        profitability_analysis = self._analyze_profitability(unique_programs, subtopics)
        
        return {
            'topic': topic,
            'subtopics': subtopics,
            'programs': unique_programs,
            'total_programs': len(unique_programs),
            'search_results': search_results,
            'profitability_analysis': profitability_analysis,
            'research_timestamp': datetime.now().isoformat(),
            'source': 'linkup_api'
        }
    
    async def _search_single_subtopic(self, subtopic: str) -> List[Dict[str, Any]]:
        """Search for affiliate programs for a single subtopic"""
        
        search_query = f"{subtopic} affiliate program"
        
        payload = {
            "q": search_query,
            "depth": "standard",
            "outputType": "searchResults",
            "includeRawContent": True,
            "maxResults": 5  # Reduced to avoid rate limits
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_affiliate_programs(data, subtopic)
                else:
                    error_text = await response.text()
                    logger.error(f"Linkup API error: {response.status} - {error_text}")
                    logger.error(f"Request URL: {response.url}")
                    logger.error(f"Headers: {self.headers}")
                    logger.error(f"Payload: {payload}")
                    return []
    
    async def _generate_subtopics_from_linkup(self, topic: str) -> List[str]:
        """Generate subtopics using Linkup search"""
        
        search_query = f"{topic} subtopics niches popular categories"
        
        payload = {
            "q": search_query,
            "depth": "standard",
            "outputType": "searchResults",
            "maxResults": 5
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._extract_subtopics_from_results(data, topic)
                else:
                    # Fallback to basic subtopics
                    return [f"{topic} tools", f"{topic} courses", f"{topic} software"]
    
    def _parse_affiliate_programs(self, search_data: Dict[str, Any], subtopic: str) -> List[Dict[str, Any]]:
        """Parse Linkup search results for affiliate programs"""
        
        programs = []
        
        if not search_data.get('results'):
            return programs
        
        for result in search_data['results']:
            content = result.get('content', '') + ' ' + result.get('raw_content', '')
            
            # Extract affiliate program information
            program_data = self._extract_program_info(content, result, subtopic)
            if program_data:
                programs.append(program_data)
        
        return programs
    
    def _extract_program_info(self, content: str, result: Dict[str, Any], subtopic: str) -> Optional[Dict[str, Any]]:
        """Extract structured affiliate program information from search content"""
        
        content_lower = content.lower()
        
        # Look for commission patterns
        commission_patterns = [
            r'(\d+(?:\.\d+)?)%\s*commission',
            r'commission\s*:\s*\$?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)%\s*per\s*(?:sale|conversion)',
            r'earn\s*\$?(\d+(?:\.\d+)?)\s*(?:per|for each)',
            r'(\d+(?:\.\d+)?)%\s*rev\s*share'
        ]
        
        commission_rate = None
        commission_amount = None
        
        for pattern in commission_patterns:
            import re
            match = re.search(pattern, content_lower)
            if match:
                value = float(match.group(1))
                if value <= 100:  # Likely percentage
                    commission_rate = value
                else:  # Likely dollar amount
                    commission_amount = value
                break
        
        # Look for cookie duration
        cookie_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:day|days)\s*cookie',
            r'cookie\s*duration\s*:?\s*(\d+(?:\.\d+)?)\s*(?:day|days)',
            r'(\d+(?:\.\d+)?)\s*day\s*tracking'
        ]
        
        cookie_duration = None
        for pattern in cookie_patterns:
            match = re.search(pattern, content_lower)
            if match:
                cookie_duration = f"{match.group(1)} days"
                break
        
        # Extract program name and network
        title = result.get('title', '')
        url = result.get('url', '')
        
        # Enhanced program name extraction
        if not title or title.strip() in ['...', '']:
            # Extract from URL or content
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '')
            title = domain.split('.')[0].replace('-', ' ').title()
            
            # Try to extract from content if available
            if content and len(content) > 20:
                # Look for potential program names in content
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) > 10 and len(line) < 100 and any(keyword in line.lower() for keyword in ['program', 'affiliate', 'partner']):
                        title = line[:60].strip()
                        break
        
        # If still empty, use fallback
        if not title or title.strip() in ['...', '']:
            title = f"{subtopic.title()} Affiliate Program"
        
        # Determine network from URL
        network = self._identify_network(url)
        
        # Don't skip if commission data exists, even if it's 0 - let the user see all programs
        return {
            'id': self._generate_program_id(title, url),
            'network': network,
            'program_name': title,
            'description': str(result.get('description', content[:200]))[:500] or f"Affiliate program for {subtopic}",
            'commission_rate': float(commission_rate or 0),
            'commission_amount': float(commission_amount or 0),
            'cookie_duration': str(cookie_duration or '30 days'),
            'program_url': str(url),
            'subtopic': str(subtopic),
            'approval_required': bool('approval' in content_lower or 'apply' in content_lower),
            'promotional_materials': self._detect_promotional_materials(content_lower),
            'extraction_confidence': float(self._calculate_confidence(content, commission_rate, cookie_duration)),
            'source_url': str(url),
            'extracted_at': str(datetime.now().isoformat())
        }
    
    def _identify_network(self, url: str) -> str:
        """Identify affiliate network from URL"""
        url_lower = url.lower()
        network_mapping = {
            'amazon': 'amazon',
            'shareasale': 'shareasale',
            'clickbank': 'clickbank',
            'cj.com': 'cj',
            'impact.com': 'impact',
            'rakuten': 'rakuten',
            'partnerize': 'partnerize',
            'refersion': 'refersion',
            'impactradius': 'impact'
        }
        
        for key, network in network_mapping.items():
            if key in url_lower:
                return network
        
        return 'other'
    
    def _detect_promotional_materials(self, content: str) -> List[str]:
        """Detect available promotional materials"""
        materials = []
        
        if any(word in content for word in ['banner', 'creative', 'graphic']):
            materials.append('banners')
        if any(word in content for word in ['text link', 'textlink']):
            materials.append('text_links')
        if any(word in content for word in ['email template', 'email creative']):
            materials.append('email_templates')
        if any(word in content for word in ['social media', 'social creative']):
            materials.append('social_media_kit')
        if any(word in content for word in ['product feed', 'data feed']):
            materials.append('product_feeds')
        
        return materials
    
    def _calculate_confidence(self, content: str, commission_rate, cookie_duration) -> float:
        """Calculate confidence score for extracted information"""
        confidence = 0.0
        
        if commission_rate:
            confidence += 0.4
        if cookie_duration:
            confidence += 0.3
        if any(word in content.lower() for word in ['affiliate', 'partner', 'commission']):
            confidence += 0.2
        if len(content) > 200:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_subtopics_from_results(self, search_data: Dict[str, Any], topic: str) -> List[str]:
        """Extract subtopics from search results"""
        # This is a simplified extraction - in practice, you'd use more sophisticated NLP
        subtopics = []
        
        if not search_data.get('results'):
            return [f"{topic} tools", f"{topic} courses", f"{topic} software"]
        
        # Common subtopic patterns
        patterns = [
            f"{topic} software",
            f"{topic} tools",
            f"{topic} courses",
            f"{topic} training",
            f"{topic} books",
            f"best {topic}",
            f"{topic} for beginners",
            f"{topic} reviews"
        ]
        
        # Use patterns as fallback
        return patterns[:6]
    
    def _deduplicate_programs(self, programs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate programs based on unique identifiers"""
        seen = set()
        unique_programs = []
        
        for program in programs:
            # Create unique identifier
            identifier = f"{program.get('network', '')}_{program.get('program_name', '')}"
            identifier_hash = hashlib.md5(identifier.encode()).hexdigest()
            
            if identifier_hash not in seen:
                seen.add(identifier_hash)
                program['unique_id'] = identifier_hash
                unique_programs.append(program)
        
        return unique_programs
    
    def _generate_program_id(self, title: str, url: str) -> str:
        """Generate unique program ID from title and URL"""
        identifier = f"{title}_{url}"
        return hashlib.md5(identifier.encode()).hexdigest()[:16]

    def _analyze_profitability(self, programs: List[Dict[str, Any]], subtopics: List[str]) -> Dict[str, Any]:
        """Analyze overall profitability of affiliate programs"""
        
        if not programs:
            return {
                'score': 0,
                'level': 'poor',
                'reason': 'No affiliate programs found',
                'total_programs': 0,
                'avg_commission_rate': 0,
                'avg_commission_amount': 0,
                'high_value_programs': 0,
                'networks_represented': 0
            }
        
        # Calculate metrics
        total_programs = len(programs)
        avg_commission_rate = sum(float(p.get('commission_rate', 0)) for p in programs) / total_programs
        avg_commission_amount = sum(float(p.get('commission_amount', 0)) for p in programs) / total_programs
        high_value_programs = len([p for p in programs if float(p.get('commission_rate', 0)) >= 20])
        networks_represented = len(set(p.get('network', '') for p in programs))
        
        # Scoring system
        score = 0
        score += min(total_programs * 3, 25)  # Up to 25 points for program volume
        score += min(avg_commission_rate * 1.5, 25)  # Up to 25 points for commission rate
        score += min(avg_commission_amount / 10, 20)  # Up to 20 points for commission amount
        score += min(high_value_programs * 3, 15)  # Up to 15 points for high-value programs
        score += min(networks_represented * 5, 15)  # Up to 15 points for network diversity
        
        score = int(score)
        
        # Determine level
        if score >= 70:
            level = 'excellent'
            reason = 'Strong program variety with high commissions'
        elif score >= 50:
            level = 'good'
            reason = 'Decent program availability with moderate commissions'
        elif score >= 30:
            level = 'moderate'
            reason = 'Limited programs or lower commission rates'
        else:
            level = 'poor'
            reason = 'Few programs or very low commissions'
        
        return {
            'score': int(score),
            'level': level,
            'reason': reason,
            'total_programs': int(total_programs),
            'avg_commission_rate': float(round(avg_commission_rate, 2)),
            'avg_commission_amount': float(round(avg_commission_amount, 2)),
            'high_value_programs': int(high_value_programs),
            'networks_represented': int(networks_represented),
            'subtopics_covered': len(subtopics)
        }

# Global instance
linkup_affiliate_research = LinkupAffiliateResearch()