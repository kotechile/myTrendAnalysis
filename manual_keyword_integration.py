#!/usr/bin/env python3
"""
Manual Keyword Research Integration System
Allows users to import keyword data from Ahrefs, SEMrush, Moz, and other tools
Then enhances blog ideas with better SEO targeting and keyword suggestions
"""

import csv
import json
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import re
import io

@dataclass
class KeywordData:
    """Structured keyword data from external tools"""
    keyword: str
    search_volume: int
    keyword_difficulty: float
    cpc: float
    competition: str  # 'low', 'medium', 'high'
    search_intent: str  # 'informational', 'commercial', 'navigational', 'transactional'
    trend: str  # 'rising', 'stable', 'declining'
    related_keywords: List[str]
    source_tool: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'keyword': self.keyword,
            'search_volume': self.search_volume,
            'keyword_difficulty': self.keyword_difficulty,
            'cpc': self.cpc,
            'competition': self.competition,
            'search_intent': self.search_intent,
            'trend': self.trend,
            'related_keywords': self.related_keywords,
            'source_tool': self.source_tool
        }

class ManualKeywordResearchIntegration:
    """Manual integration system for keyword research tools"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_tools = ['ahrefs', 'semrush', 'moz', 'ubersuggest', 'kwfinder', 'custom']
        self.imported_keywords = []
        
    def get_import_instructions(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed instructions for exporting data from specific tools"""
        
        instructions = {
            'ahrefs': {
                'tool_name': 'Ahrefs Keywords Explorer',
                'steps': [
                    "1. Go to Keywords Explorer in Ahrefs",
                    "2. Enter your main topic/keyword and run the search",
                    "3. Go to the 'Keyword Ideas' tab",
                    "4. Apply filters: Search Volume > 100, KD < 50 (adjust as needed)",
                    "5. Select relevant keywords (aim for 50-200 keywords)",
                    "6. Click 'Export' and choose 'CSV' format",
                    "7. Make sure to include: Keyword, Volume, KD, CPC, Traffic Potential"
                ],
                'required_columns': [
                    'Keyword', 'Volume', 'KD', 'CPC', 'Traffic potential'
                ],
                'optional_columns': [
                    'Parent topic', 'Last update', 'Clicks', 'Return rate'
                ],
                'export_settings': {
                    'format': 'CSV',
                    'encoding': 'UTF-8',
                    'include_headers': True
                },
                'file_format': 'CSV with comma separator'
            },
            
            'semrush': {
                'tool_name': 'SEMrush Keyword Magic Tool',
                'steps': [
                    "1. Open Keyword Magic Tool in SEMrush",
                    "2. Enter your seed keyword and select target country",
                    "3. Apply filters: Volume > 100, KD% < 60",
                    "4. Use 'Intent' filter to focus on informational keywords",
                    "5. Select relevant keywords (50-200 recommended)",
                    "6. Click 'Export' button",
                    "7. Choose 'Export to CSV' option"
                ],
                'required_columns': [
                    'Keyword', 'Volume', 'KD%', 'CPC', 'Intent'
                ],
                'optional_columns': [
                    'Trend', 'Results', 'SERP Features', 'Timestamp'
                ],
                'export_settings': {
                    'format': 'CSV',
                    'include_all_data': True
                },
                'file_format': 'CSV with semicolon or comma separator'
            },
            
            'moz': {
                'tool_name': 'Moz Keyword Explorer',
                'steps': [
                    "1. Access Keyword Explorer in Moz Pro",
                    "2. Enter your root keyword",
                    "3. Go to 'Keyword Suggestions' tab",
                    "4. Filter by: Monthly Volume > 100, Difficulty < 50",
                    "5. Select relevant keywords for your topic",
                    "6. Click 'Export' and select all keywords",
                    "7. Download as CSV file"
                ],
                'required_columns': [
                    'Keyword', 'Monthly Volume', 'Difficulty', 'Organic CTR'
                ],
                'optional_columns': [
                    'Priority', 'SERP Features', 'Related Keywords'
                ],
                'export_settings': {
                    'format': 'CSV',
                    'include_metrics': True
                },
                'file_format': 'Standard CSV format'
            },
            
            'ubersuggest': {
                'tool_name': 'Ubersuggest Keyword Ideas',
                'steps': [
                    "1. Go to Ubersuggest and enter your main keyword",
                    "2. Click on 'Keyword Ideas' in the left sidebar",
                    "3. Filter results: Search Volume > 100, SEO Difficulty < 40",
                    "4. Select 'Informational' keywords for blog content",
                    "5. Choose relevant keywords (limit to 100-200)",
                    "6. Click 'Export Data' button",
                    "7. Download the CSV file"
                ],
                'required_columns': [
                    'Keyword', 'Vol', 'SD', 'CPC'
                ],
                'optional_columns': [
                    'Paid Difficulty', 'Trend'
                ],
                'export_settings': {
                    'format': 'CSV',
                    'include_trends': True
                },
                'file_format': 'CSV with comma separator'
            },
            
            'custom': {
                'tool_name': 'Custom Keyword Data',
                'steps': [
                    "1. Create a CSV file with your keyword research",
                    "2. Include required columns (see below)",
                    "3. Use the exact column names specified",
                    "4. Save as CSV with UTF-8 encoding",
                    "5. Ensure numeric values are properly formatted"
                ],
                'required_columns': [
                    'keyword', 'search_volume', 'difficulty', 'cpc'
                ],
                'optional_columns': [
                    'competition', 'intent', 'trend', 'related_keywords'
                ],
                'export_settings': {
                    'format': 'CSV',
                    'encoding': 'UTF-8',
                    'separator': 'comma'
                },
                'file_format': 'Custom CSV format (see template below)'
            }
        }
        
        if tool_name.lower() not in instructions:
            return self._get_generic_instructions()
        
        return instructions[tool_name.lower()]
    
    def _get_generic_instructions(self) -> Dict[str, Any]:
        """Generic instructions for any keyword tool"""
        return {
            'tool_name': 'Generic Keyword Research Tool',
            'steps': [
                "1. Export keyword data from your tool in CSV format",
                "2. Include keyword, search volume, difficulty, and CPC columns",
                "3. Make sure file is saved with UTF-8 encoding",
                "4. Use our template format for best results"
            ],
            'required_columns': [
                'keyword', 'search_volume', 'difficulty', 'cpc'
            ],
            'optional_columns': [
                'competition', 'intent', 'trend'
            ],
            'file_format': 'CSV with comma separator'
        }
    
    def generate_csv_template(self, tool_name: str = 'custom') -> str:
        """Generate a CSV template for manual data entry"""
        
        templates = {
            'ahrefs': "Keyword,Volume,KD,CPC,Traffic potential\n"
                     "digital marketing guide,1200,25,2.50,850\n"
                     "content marketing strategy,890,30,3.20,650\n"
                     "social media marketing,2500,45,1.80,1200",
            
            'semrush': "Keyword,Volume,KD%,CPC,Intent\n"
                      "email marketing tips,950,28,2.10,Informational\n"
                      "marketing automation tools,760,35,4.50,Commercial\n"
                      "lead generation strategies,680,32,3.80,Informational",
            
            'moz': "Keyword,Monthly Volume,Difficulty,Organic CTR\n"
                  "SEO best practices,1100,30,0.35\n"
                  "keyword research tools,850,40,0.28\n"
                  "local SEO guide,720,25,0.42",
            
            'custom': "keyword,search_volume,difficulty,cpc,competition,intent,trend\n"
                     "blog writing tips,1500,25,1.20,medium,informational,stable\n"
                     "content calendar template,800,20,0.90,low,informational,rising\n"
                     "copywriting techniques,950,35,2.80,medium,informational,stable"
        }
        
        return templates.get(tool_name.lower(), templates['custom'])
    
    def parse_keyword_file(self, file_content: str, tool_name: str, filename: str = "") -> Tuple[List[KeywordData], List[str]]:
        """Parse uploaded keyword research file"""
        
        self.logger.info(f"📊 Parsing keyword file from {tool_name}")
        
        try:
            # Detect separator
            separator = self._detect_csv_separator(file_content)
            
            # Parse CSV content
            df = pd.read_csv(io.StringIO(file_content), sep=separator)
            
            # Clean column names
            df.columns = [col.strip().lower().replace(' ', '_').replace('%', '_pct') for col in df.columns]
            
            # Parse based on tool
            if tool_name.lower() == 'ahrefs':
                return self._parse_ahrefs_data(df)
            elif tool_name.lower() == 'semrush':
                return self._parse_semrush_data(df)
            elif tool_name.lower() == 'moz':
                return self._parse_moz_data(df)
            elif tool_name.lower() == 'ubersuggest':
                return self._parse_ubersuggest_data(df)
            else:
                return self._parse_custom_data(df)
                
        except Exception as e:
            error_msg = f"Failed to parse keyword file: {str(e)}"
            self.logger.error(error_msg)
            return [], [error_msg]
    
    def _detect_csv_separator(self, content: str) -> str:
        """Detect CSV separator"""
        first_line = content.split('\n')[0] if content else ""
        
        separators = [',', ';', '\t', '|']
        counts = {sep: first_line.count(sep) for sep in separators}
        
        return max(counts, key=counts.get) if max(counts.values()) > 0 else ','
    
    def _parse_ahrefs_data(self, df: pd.DataFrame) -> Tuple[List[KeywordData], List[str]]:
        """Parse Ahrefs export data"""
        keywords = []
        errors = []
        
        # Map Ahrefs columns
        column_mapping = {
            'keyword': ['keyword'],
            'volume': ['volume', 'search_volume'],
            'kd': ['kd', 'keyword_difficulty', 'difficulty'],
            'cpc': ['cpc', 'cost_per_click'],
            'traffic_potential': ['traffic_potential', 'traffic']
        }
        
        # Find actual column names
        actual_columns = self._map_columns(df.columns.tolist(), column_mapping)
        
        for index, row in df.iterrows():
            try:
                keyword_data = KeywordData(
                    keyword=str(row[actual_columns['keyword']]).strip(),
                    search_volume=int(float(str(row[actual_columns['volume']]).replace(',', '') or 0)),
                    keyword_difficulty=float(row[actual_columns['kd']] or 0),
                    cpc=float(row[actual_columns['cpc']] or 0),
                    competition=self._determine_competition_from_kd(float(row[actual_columns['kd']] or 0)),
                    search_intent=self._determine_search_intent(str(row[actual_columns['keyword']])),
                    trend='stable',  # Ahrefs doesn't provide trend data in basic export
                    related_keywords=[],
                    source_tool='ahrefs'
                )
                keywords.append(keyword_data)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        return keywords, errors
    
    def _parse_semrush_data(self, df: pd.DataFrame) -> Tuple[List[KeywordData], List[str]]:
        """Parse SEMrush export data"""
        keywords = []
        errors = []
        
        column_mapping = {
            'keyword': ['keyword'],
            'volume': ['volume', 'search_volume'],
            'kd_pct': ['kd_pct', 'kd%', 'difficulty'],
            'cpc': ['cpc'],
            'intent': ['intent', 'search_intent']
        }
        
        actual_columns = self._map_columns(df.columns.tolist(), column_mapping)
        
        for index, row in df.iterrows():
            try:
                intent = str(row.get(actual_columns.get('intent', ''), 'informational')).lower()
                
                keyword_data = KeywordData(
                    keyword=str(row[actual_columns['keyword']]).strip(),
                    search_volume=int(float(str(row[actual_columns['volume']]).replace(',', '') or 0)),
                    keyword_difficulty=float(row[actual_columns['kd_pct']] or 0),
                    cpc=float(row[actual_columns['cpc']] or 0),
                    competition=self._determine_competition_from_kd(float(row[actual_columns['kd_pct']] or 0)),
                    search_intent=intent if intent in ['informational', 'commercial', 'navigational', 'transactional'] else 'informational',
                    trend='stable',
                    related_keywords=[],
                    source_tool='semrush'
                )
                keywords.append(keyword_data)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        return keywords, errors
    
    def _parse_moz_data(self, df: pd.DataFrame) -> Tuple[List[KeywordData], List[str]]:
        """Parse Moz export data"""
        keywords = []
        errors = []
        
        column_mapping = {
            'keyword': ['keyword'],
            'monthly_volume': ['monthly_volume', 'volume', 'search_volume'],
            'difficulty': ['difficulty', 'keyword_difficulty'],
            'organic_ctr': ['organic_ctr', 'ctr']
        }
        
        actual_columns = self._map_columns(df.columns.tolist(), column_mapping)
        
        for index, row in df.iterrows():
            try:
                # Moz doesn't provide CPC in basic exports, estimate from difficulty
                difficulty = float(row[actual_columns['difficulty']] or 0)
                estimated_cpc = self._estimate_cpc_from_difficulty(difficulty)
                
                keyword_data = KeywordData(
                    keyword=str(row[actual_columns['keyword']]).strip(),
                    search_volume=int(float(str(row[actual_columns['monthly_volume']]).replace(',', '') or 0)),
                    keyword_difficulty=difficulty,
                    cpc=estimated_cpc,
                    competition=self._determine_competition_from_kd(difficulty),
                    search_intent=self._determine_search_intent(str(row[actual_columns['keyword']])),
                    trend='stable',
                    related_keywords=[],
                    source_tool='moz'
                )
                keywords.append(keyword_data)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        return keywords, errors
    
    def _parse_ubersuggest_data(self, df: pd.DataFrame) -> Tuple[List[KeywordData], List[str]]:
        """Parse Ubersuggest export data"""
        keywords = []
        errors = []
        
        column_mapping = {
            'keyword': ['keyword'],
            'vol': ['vol', 'volume', 'search_volume'],
            'sd': ['sd', 'seo_difficulty', 'difficulty'],
            'cpc': ['cpc']
        }
        
        actual_columns = self._map_columns(df.columns.tolist(), column_mapping)
        
        for index, row in df.iterrows():
            try:
                keyword_data = KeywordData(
                    keyword=str(row[actual_columns['keyword']]).strip(),
                    search_volume=int(float(str(row[actual_columns['vol']]).replace(',', '') or 0)),
                    keyword_difficulty=float(row[actual_columns['sd']] or 0),
                    cpc=float(row[actual_columns['cpc']] or 0),
                    competition=self._determine_competition_from_kd(float(row[actual_columns['sd']] or 0)),
                    search_intent=self._determine_search_intent(str(row[actual_columns['keyword']])),
                    trend='stable',
                    related_keywords=[],
                    source_tool='ubersuggest'
                )
                keywords.append(keyword_data)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        return keywords, errors
    
    def _parse_custom_data(self, df: pd.DataFrame) -> Tuple[List[KeywordData], List[str]]:
        """Parse custom format data"""
        keywords = []
        errors = []
        
        required_columns = ['keyword', 'search_volume', 'difficulty', 'cpc']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return [], [f"Missing required columns: {', '.join(missing_columns)}"]
        
        for index, row in df.iterrows():
            try:
                keyword_data = KeywordData(
                    keyword=str(row['keyword']).strip(),
                    search_volume=int(float(str(row['search_volume']).replace(',', '') or 0)),
                    keyword_difficulty=float(row['difficulty'] or 0),
                    cpc=float(row['cpc'] or 0),
                    competition=str(row.get('competition', self._determine_competition_from_kd(float(row['difficulty'] or 0)))),
                    search_intent=str(row.get('intent', self._determine_search_intent(str(row['keyword'])))),
                    trend=str(row.get('trend', 'stable')),
                    related_keywords=str(row.get('related_keywords', '')).split(',') if row.get('related_keywords') else [],
                    source_tool='custom'
                )
                keywords.append(keyword_data)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        return keywords, errors
    
    def _map_columns(self, available_columns: List[str], column_mapping: Dict[str, List[str]]) -> Dict[str, str]:
        """Map available columns to expected columns"""
        mapped = {}
        
        for expected, possible_names in column_mapping.items():
            for possible in possible_names:
                if possible in available_columns:
                    mapped[expected] = possible
                    break
            
            if expected not in mapped and possible_names:
                # Use first available column if exact match not found
                for col in available_columns:
                    if any(possible.lower() in col.lower() for possible in possible_names):
                        mapped[expected] = col
                        break
        
        return mapped
    
    def _determine_competition_from_kd(self, kd_score: float) -> str:
        """Determine competition level from keyword difficulty score"""
        if kd_score <= 30:
            return 'low'
        elif kd_score <= 60:
            return 'medium'
        else:
            return 'high'
    
    def _determine_search_intent(self, keyword: str) -> str:
        """Determine search intent from keyword"""
        keyword_lower = keyword.lower()
        
        # Commercial intent indicators
        commercial_indicators = ['best', 'top', 'review', 'compare', 'vs', 'versus', 'alternative']
        if any(indicator in keyword_lower for indicator in commercial_indicators):
            return 'commercial'
        
        # Transactional intent indicators
        transactional_indicators = ['buy', 'purchase', 'price', 'cost', 'cheap', 'discount', 'deal']
        if any(indicator in keyword_lower for indicator in transactional_indicators):
            return 'transactional'
        
        # Navigational intent indicators
        navigational_indicators = ['login', 'download', 'website', 'official']
        if any(indicator in keyword_lower for indicator in navigational_indicators):
            return 'navigational'
        
        # Default to informational
        return 'informational'
    
    def _estimate_cpc_from_difficulty(self, difficulty: float) -> float:
        """Estimate CPC from keyword difficulty when not available"""
        # Simple estimation: higher difficulty usually means higher CPC
        if difficulty <= 20:
            return round(0.5 + (difficulty * 0.05), 2)
        elif difficulty <= 50:
            return round(1.0 + (difficulty * 0.08), 2)
        else:
            return round(2.0 + (difficulty * 0.1), 2)
    
# COMPLETE FIX: Replace the enhance_blog_ideas_with_keywords method

    def enhance_blog_ideas_with_keywords(
        self, 
        blog_ideas: List[Dict[str, Any]], 
        imported_keywords: List[KeywordData],
        enhancement_config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Enhance blog ideas with imported keyword data - COMPLETELY FIXED VERSION"""
        
        self.logger.info(f"🔍 Enhancing {len(blog_ideas)} blog ideas with {len(imported_keywords)} keywords")
        
        # CRITICAL FIX: Ensure all config values are proper types from the start
        if enhancement_config is None:
            enhancement_config = {}
        
        # Convert ALL config values to proper types immediately
        config = {
            'max_primary_keywords': int(enhancement_config.get('max_primary_keywords', 5)),
            'max_secondary_keywords': int(enhancement_config.get('max_secondary_keywords', 10)),
            'min_search_volume': int(enhancement_config.get('min_search_volume', 100)),
            'max_difficulty': float(enhancement_config.get('max_difficulty', 50)),
            'prefer_informational': bool(enhancement_config.get('prefer_informational', True))
        }
        
        print(f"🔧 Config values converted: {config}")  # Debug log
        
        enhanced_ideas = []
        
        for idea in blog_ideas:
            try:
                enhanced_idea = self._enhance_single_idea(idea, imported_keywords, config)
                enhanced_ideas.append(enhanced_idea)
            except Exception as e:
                self.logger.error(f"Failed to enhance idea '{idea.get('title', 'Unknown')}': {e}")
                print(f"❌ Enhancement error for '{idea.get('title', 'Unknown')}': {e}")  # Debug log
                enhanced_ideas.append(idea)  # Return original if enhancement fails
        
        # Count successfully enhanced ideas
        enhanced_count = len([idea for idea in enhanced_ideas if idea.get('keyword_research_enhanced', False)])
        print(f"✅ Successfully enhanced {enhanced_count} out of {len(blog_ideas)} ideas")
        
        return enhanced_ideas
    
    def _enhance_single_idea(
        self, 
        idea: Dict[str, Any], 
        keywords: List[KeywordData], 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance a single blog idea with keyword data"""
        
        idea_title = idea.get('title', '').lower()
        idea_description = idea.get('description', '').lower()
        existing_keywords = idea.get('primary_keywords', [])
        
        # Find relevant keywords
        relevant_keywords = self._find_relevant_keywords(
            idea_title, idea_description, existing_keywords, keywords, config
        )
        
        if not relevant_keywords:
            self.logger.warning(f"No relevant keywords found for idea: {idea.get('title', 'Unknown')}")
            return idea
        
        # Categorize keywords
        primary_keywords = self._select_primary_keywords(relevant_keywords, config)
        secondary_keywords = self._select_secondary_keywords(relevant_keywords, primary_keywords, config)
        
        # Calculate SEO metrics
        seo_metrics = self._calculate_seo_metrics(primary_keywords, secondary_keywords)
        
        # Generate keyword suggestions
        keyword_suggestions = self._generate_keyword_suggestions(idea_title, relevant_keywords)
        
        # Update the idea
        enhanced_idea = idea.copy()
        enhanced_idea.update({
            # Enhanced keyword data
            'enhanced_primary_keywords': [kw.keyword for kw in primary_keywords],
            'enhanced_secondary_keywords': [kw.keyword for kw in secondary_keywords],
            'keyword_research_data': {
                'primary_keywords_data': [kw.to_dict() for kw in primary_keywords],
                'secondary_keywords_data': [kw.to_dict() for kw in secondary_keywords],
                'total_search_volume': sum(kw.search_volume for kw in primary_keywords + secondary_keywords),
                'average_difficulty': sum(kw.keyword_difficulty for kw in primary_keywords + secondary_keywords) / len(primary_keywords + secondary_keywords) if primary_keywords + secondary_keywords else 0,
                'average_cpc': sum(kw.cpc for kw in primary_keywords + secondary_keywords) / len(primary_keywords + secondary_keywords) if primary_keywords + secondary_keywords else 0
            },
            
            # SEO enhancements
            'seo_optimization_score': min(100, idea.get('seo_optimization_score', 50) + seo_metrics['score_boost']),
            'traffic_potential_score': seo_metrics['traffic_potential'],
            'competition_score': seo_metrics['competition_score'],
            
            # Keyword suggestions
            'keyword_suggestions': keyword_suggestions,
            'content_optimization_tips': self._generate_content_tips(primary_keywords, secondary_keywords),
            
            # Enhanced metadata
            'keyword_research_enhanced': True,
            'keyword_source_tools': list(set(kw.source_tool for kw in relevant_keywords)),
            'enhancement_timestamp': datetime.now().isoformat()
        })
        
        return enhanced_idea
    
    # EXACT FIX for manual_keyword_integration.py
# Replace the _find_relevant_keywords method with this fixed version:

    def _find_relevant_keywords(
        self, 
        title: str, 
        description: str, 
        existing_keywords: List[str], 
        all_keywords: List[KeywordData],
        config: Dict[str, Any]
    ) -> List[KeywordData]:
        """Find keywords relevant to the blog idea"""
        
        relevant = []
        
        # CRITICAL FIX: Convert config values to proper types
        min_search_volume = int(config.get('min_search_volume', 100))
        max_difficulty = float(config.get('max_difficulty', 50))
        prefer_informational = bool(config.get('prefer_informational', True))
        
        # Create search text from title, description, and existing keywords
        search_text = f"{title} {description} {' '.join(existing_keywords)}".lower()
        
        for keyword_data in all_keywords:
            keyword_lower = keyword_data.keyword.lower()
            
            # Check relevance
            relevance_score = 0
            
            # Exact match in title (highest priority)
            if keyword_lower in title:
                relevance_score += 10
            
            # Partial word match in title
            elif any(word in title for word in keyword_lower.split()):
                relevance_score += 7
            
            # Match in description
            elif keyword_lower in description:
                relevance_score += 5
            
            # Match with existing keywords
            elif any(keyword_lower in existing_kw.lower() or existing_kw.lower() in keyword_lower 
                    for existing_kw in existing_keywords):
                relevance_score += 6
            
            # Semantic similarity (simple approach)
            elif any(word in search_text for word in keyword_lower.split() if len(word) > 3):
                relevance_score += 3
            
            # Apply filters with FIXED TYPE COMPARISONS
            if (relevance_score >= 3 and 
                keyword_data.search_volume >= min_search_volume and
                keyword_data.keyword_difficulty <= max_difficulty):
                
                # Prefer informational intent for blog content
                if prefer_informational and keyword_data.search_intent == 'informational':
                    relevance_score += 2
                
                keyword_data.relevance_score = relevance_score
                relevant.append(keyword_data)
        
        # Sort by relevance score and search volume
        relevant.sort(key=lambda x: (getattr(x, 'relevance_score', 0), x.search_volume), reverse=True)
        
        return relevant[:50]  # Limit to top 50 relevant keywords
    
# SLICE FIX for manual_keyword_integration.py
# The error is in the _select_primary_keywords and _select_secondary_keywords methods

# Replace these two methods with the fixed versions:

    def _select_primary_keywords(self, relevant_keywords: List[KeywordData], config: Dict[str, Any]) -> List[KeywordData]:
        """Select the best primary keywords - FIXED VERSION"""
        
        # FIX: Ensure max_primary is an integer
        max_primary = int(config.get('max_primary_keywords', 5))
        
        # Prioritize keywords with:
        # 1. High relevance score
        # 2. Good search volume
        # 3. Manageable difficulty
        # 4. Informational intent
        
        primary_candidates = []
        
        for kw in relevant_keywords:
            score = 0
            
            # Relevance score (0-10)
            score += getattr(kw, 'relevance_score', 0) * 2
            
            # Search volume bonus (0-20)
            if kw.search_volume >= 1000:
                score += 20
            elif kw.search_volume >= 500:
                score += 15
            elif kw.search_volume >= 200:
                score += 10
            elif kw.search_volume >= 100:
                score += 5
            
            # Difficulty penalty
            if kw.keyword_difficulty <= 20:
                score += 15
            elif kw.keyword_difficulty <= 30:
                score += 10
            elif kw.keyword_difficulty <= 40:
                score += 5
            else:
                score -= 5
            
            # Intent bonus
            if kw.search_intent == 'informational':
                score += 10
            elif kw.search_intent == 'commercial':
                score += 5
            
            kw.primary_score = score
            primary_candidates.append(kw)
        
        # Sort by primary score and return top candidates
        primary_candidates.sort(key=lambda x: x.primary_score, reverse=True)
        return primary_candidates[:max_primary]  # max_primary is now guaranteed to be int

    def _select_secondary_keywords(
        self, 
        relevant_keywords: List[KeywordData], 
        primary_keywords: List[KeywordData],
        config: Dict[str, Any]
    ) -> List[KeywordData]:
        """Select the best secondary keywords - FIXED VERSION"""
        
        # FIX: Ensure max_secondary is an integer
        max_secondary = int(config.get('max_secondary_keywords', 10))
        primary_keywords_set = {kw.keyword for kw in primary_keywords}
        
        secondary_candidates = []
        
        for kw in relevant_keywords:
            # Skip if already selected as primary
            if kw.keyword in primary_keywords_set:
                continue
            
            score = 0
            
            # Relevance score (0-10)
            score += getattr(kw, 'relevance_score', 0)
            
            # Search volume bonus (lower threshold for secondary)
            if kw.search_volume >= 500:
                score += 10
            elif kw.search_volume >= 200:
                score += 8
            elif kw.search_volume >= 100:
                score += 5
            elif kw.search_volume >= 50:
                score += 3
            
            # Difficulty is less important for secondary keywords
            if kw.keyword_difficulty <= 40:
                score += 5
            elif kw.keyword_difficulty <= 60:
                score += 2
            
            # Long-tail keyword bonus
            if len(kw.keyword.split()) >= 3:
                score += 5
            
            # Intent variety bonus
            if kw.search_intent in ['commercial', 'transactional']:
                score += 3
            
            kw.secondary_score = score
            secondary_candidates.append(kw)
        
        # Sort by secondary score
        secondary_candidates.sort(key=lambda x: x.secondary_score, reverse=True)
        return secondary_candidates[:max_secondary]  # max_secondary is now guaranteed to be int
    
    
    def _calculate_seo_metrics(self, primary_keywords: List[KeywordData], secondary_keywords: List[KeywordData]) -> Dict[str, Any]:
        """Calculate SEO metrics from selected keywords"""
        
        all_keywords = primary_keywords + secondary_keywords
        
        if not all_keywords:
            return {
                'score_boost': 0,
                'traffic_potential': 50,
                'competition_score': 50
            }
        
        # Calculate total search volume
        total_volume = sum(kw.search_volume for kw in all_keywords)
        
        # Calculate average difficulty
        avg_difficulty = sum(kw.keyword_difficulty for kw in all_keywords) / len(all_keywords)
        
        # Calculate traffic potential (0-100)
        if total_volume >= 5000:
            traffic_potential = 90
        elif total_volume >= 2000:
            traffic_potential = 80
        elif total_volume >= 1000:
            traffic_potential = 70
        elif total_volume >= 500:
            traffic_potential = 60
        else:
            traffic_potential = 50
        
        # Calculate competition score (inverse of difficulty)
        competition_score = max(10, 100 - avg_difficulty)
        
        # Calculate SEO score boost
        score_boost = 0
        if len(primary_keywords) >= 3:
            score_boost += 10
        if len(secondary_keywords) >= 5:
            score_boost += 5
        if avg_difficulty <= 30:
            score_boost += 10
        if total_volume >= 1000:
            score_boost += 5
        
        return {
            'score_boost': int(score_boost),
            'traffic_potential': int(traffic_potential),
            'competition_score': int(competition_score),
            'total_search_volume': total_volume,
            'average_difficulty': round(avg_difficulty, 1)
        }
    
    def _generate_keyword_suggestions(self, title: str, relevant_keywords: List[KeywordData]) -> Dict[str, List[str]]:
        """Generate keyword suggestions for content optimization"""
        
        suggestions = {
            'title_variations': [],
            'header_keywords': [],
            'content_keywords': [],
            'meta_description_keywords': [],
            'related_topics': []
        }
        
        # Extract base topic from title
        base_words = set(title.lower().split())
        
        # Title variations
        for kw in relevant_keywords[:5]:
            if any(word in kw.keyword.lower() for word in base_words):
                suggestions['title_variations'].append(kw.keyword)
        
        # Header keywords (H2, H3 suggestions)
        header_patterns = ['how to', 'best', 'top', 'guide', 'tips', 'strategies', 'benefits']
        for kw in relevant_keywords:
            if any(pattern in kw.keyword.lower() for pattern in header_patterns):
                suggestions['header_keywords'].append(kw.keyword)
        
        # Content keywords (for natural inclusion in text)
        for kw in relevant_keywords[5:15]:
            if kw.search_intent == 'informational' and len(kw.keyword.split()) <= 3:
                suggestions['content_keywords'].append(kw.keyword)
        
        # Meta description keywords (high volume, short)
        for kw in relevant_keywords:
            if kw.search_volume >= 500 and len(kw.keyword.split()) <= 2:
                suggestions['meta_description_keywords'].append(kw.keyword)
        
        # Related topics (for content expansion)
        related_topics = set()
        for kw in relevant_keywords:
            words = kw.keyword.split()
            for word in words:
                if word.lower() not in base_words and len(word) > 3:
                    related_topics.add(word)
        
        suggestions['related_topics'] = list(related_topics)[:10]
        
        # Limit all suggestions
        for key in suggestions:
            suggestions[key] = suggestions[key][:10]
        
        return suggestions
    
    def _generate_content_tips(self, primary_keywords: List[KeywordData], secondary_keywords: List[KeywordData]) -> List[str]:
        """Generate content optimization tips"""
        
        tips = []
        
        if primary_keywords:
            main_keyword = primary_keywords[0].keyword
            tips.append(f"Include '{main_keyword}' in your title, preferably at the beginning")
            tips.append(f"Use '{main_keyword}' in your first paragraph within the first 100 words")
            tips.append(f"Include '{main_keyword}' in at least one H2 heading")
            
            if len(primary_keywords) > 1:
                tips.append(f"Distribute primary keywords ({', '.join([kw.keyword for kw in primary_keywords[:3]])}) naturally throughout the content")
        
        if secondary_keywords:
            tips.append(f"Include secondary keywords in H3 headings and body text")
            tips.append(f"Use variations and synonyms of your keywords to avoid over-optimization")
            
            # Intent-based tips
            commercial_keywords = [kw for kw in secondary_keywords if kw.search_intent == 'commercial']
            if commercial_keywords:
                tips.append(f"Create comparison sections for commercial keywords: {', '.join([kw.keyword for kw in commercial_keywords[:3]])}")
        
        # General SEO tips
        tips.extend([
            "Maintain keyword density between 1-2% for primary keywords",
            "Use long-tail variations naturally in your content",
            "Include keywords in image alt text and captions",
            "Add related keywords to your meta description",
            "Create internal links using keyword anchor text"
        ])
        
        return tips[:8]  # Limit to 8 tips
    
    def generate_keyword_opportunities_report(self, keywords: List[KeywordData]) -> Dict[str, Any]:
        """Generate a comprehensive keyword opportunities report"""
        
        if not keywords:
            return {"error": "No keywords provided for analysis"}
        
        # Categorize keywords by opportunity level
        high_opportunity = []
        medium_opportunity = []
        low_opportunity = []
        
        for kw in keywords:
            # Calculate opportunity score
            opportunity_score = 0
            
            # Search volume factor (0-40 points)
            if kw.search_volume >= 1000:
                opportunity_score += 40
            elif kw.search_volume >= 500:
                opportunity_score += 30
            elif kw.search_volume >= 200:
                opportunity_score += 20
            elif kw.search_volume >= 100:
                opportunity_score += 10
            
            # Difficulty factor (0-30 points, inverse)
            difficulty_points = max(0, 30 - kw.keyword_difficulty)
            opportunity_score += difficulty_points
            
            # CPC factor (0-20 points)
            if kw.cpc >= 3.0:
                opportunity_score += 20
            elif kw.cpc >= 2.0:
                opportunity_score += 15
            elif kw.cpc >= 1.0:
                opportunity_score += 10
            elif kw.cpc >= 0.5:
                opportunity_score += 5
            
            # Intent factor (0-10 points)
            if kw.search_intent == 'informational':
                opportunity_score += 10
            elif kw.search_intent == 'commercial':
                opportunity_score += 8
            elif kw.search_intent == 'transactional':
                opportunity_score += 6
            
            kw.opportunity_score = opportunity_score
            
            # Categorize
            if opportunity_score >= 70:
                high_opportunity.append(kw)
            elif opportunity_score >= 50:
                medium_opportunity.append(kw)
            else:
                low_opportunity.append(kw)
        
        # Sort each category
        high_opportunity.sort(key=lambda x: x.opportunity_score, reverse=True)
        medium_opportunity.sort(key=lambda x: x.opportunity_score, reverse=True)
        low_opportunity.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        # Generate insights
        insights = []
        
        if high_opportunity:
            insights.append(f"Found {len(high_opportunity)} high-opportunity keywords with excellent potential")
            top_keyword = high_opportunity[0]
            insights.append(f"Top opportunity: '{top_keyword.keyword}' ({top_keyword.search_volume:,} volume, {top_keyword.keyword_difficulty:.0f} difficulty)")
        
        if len([kw for kw in keywords if kw.keyword_difficulty <= 30]) >= 5:
            insights.append("Multiple low-competition keywords available for quick wins")
        
        total_volume = sum(kw.search_volume for kw in keywords)
        insights.append(f"Total addressable search volume: {total_volume:,} monthly searches")
        
        avg_difficulty = sum(kw.keyword_difficulty for kw in keywords) / len(keywords)
        if avg_difficulty <= 35:
            insights.append("Overall keyword set has manageable competition levels")
        elif avg_difficulty >= 60:
            insights.append("High competition keywords - consider long-tail alternatives")
        
        return {
            "summary": {
                "total_keywords": len(keywords),
                "high_opportunity": len(high_opportunity),
                "medium_opportunity": len(medium_opportunity), 
                "low_opportunity": len(low_opportunity),
                "total_search_volume": total_volume,
                "average_difficulty": round(avg_difficulty, 1),
                "average_cpc": round(sum(kw.cpc for kw in keywords) / len(keywords), 2)
            },
            
            "top_opportunities": {
                "high_opportunity_keywords": [
                    {
                        "keyword": kw.keyword,
                        "search_volume": kw.search_volume,
                        "difficulty": kw.keyword_difficulty,
                        "cpc": kw.cpc,
                        "opportunity_score": getattr(kw, 'opportunity_score', 0),
                        "intent": kw.search_intent,
                        "competition": kw.competition
                    }
                    for kw in high_opportunity[:10]
                ],
                "quick_wins": [
                    {
                        "keyword": kw.keyword,
                        "search_volume": kw.search_volume,
                        "difficulty": kw.keyword_difficulty,
                        "why_quick_win": f"Low difficulty ({kw.keyword_difficulty:.0f}) with {kw.search_volume:,} searches"
                    }
                    for kw in keywords if kw.keyword_difficulty <= 25 and kw.search_volume >= 200
                ][:5],
                "high_volume_targets": [
                    {
                        "keyword": kw.keyword,
                        "search_volume": kw.search_volume,
                        "difficulty": kw.keyword_difficulty,
                        "potential_traffic": int(kw.search_volume * 0.3)  # Estimated 30% CTR
                    }
                    for kw in sorted(keywords, key=lambda x: x.search_volume, reverse=True)[:5]
                ]
            },
            
            "content_recommendations": self._generate_content_recommendations(keywords),
            
            "insights": insights,
            
            "next_steps": [
                "Prioritize high-opportunity keywords for immediate content creation",
                "Target quick-win keywords for fast ranking improvements", 
                "Create pillar content around high-volume keywords",
                "Develop supporting content for medium-opportunity keywords",
                "Monitor keyword performance and adjust strategy monthly"
            ]
        }
    
    def _generate_content_recommendations(self, keywords: List[KeywordData]) -> Dict[str, List[str]]:
        """Generate content type recommendations based on keywords"""
        
        recommendations = {
            "how_to_guides": [],
            "comparison_posts": [],
            "list_articles": [],
            "beginner_guides": [],
            "tool_reviews": [],
            "case_studies": []
        }
        
        for kw in keywords:
            keyword_lower = kw.keyword.lower()
            
            # How-to guides
            if any(phrase in keyword_lower for phrase in ['how to', 'how do', 'ways to']):
                recommendations["how_to_guides"].append(kw.keyword)
            
            # Comparison posts
            elif any(phrase in keyword_lower for phrase in ['vs', 'versus', 'compare', 'difference between']):
                recommendations["comparison_posts"].append(kw.keyword)
            
            # List articles
            elif any(phrase in keyword_lower for phrase in ['best', 'top', 'list of', 'examples of']):
                recommendations["list_articles"].append(kw.keyword)
            
            # Beginner guides
            elif any(phrase in keyword_lower for phrase in ['beginner', 'introduction to', 'getting started', 'basics']):
                recommendations["beginner_guides"].append(kw.keyword)
            
            # Tool reviews
            elif any(phrase in keyword_lower for phrase in ['review', 'tool', 'software', 'platform']):
                recommendations["tool_reviews"].append(kw.keyword)
            
            # Case studies (commercial intent)
            elif kw.search_intent == 'commercial' and kw.search_volume >= 500:
                recommendations["case_studies"].append(kw.keyword)
        
        # Limit each category
        for category in recommendations:
            recommendations[category] = recommendations[category][:5]
        
        return recommendations
    
    def export_keyword_analysis(self, keywords: List[KeywordData], filename: str = None) -> str:
        """Export keyword analysis to CSV format"""
        
        if not filename:
            filename = f"keyword_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Prepare data for export
        export_data = []
        for kw in keywords:
            export_data.append({
                'Keyword': kw.keyword,
                'Search Volume': kw.search_volume,
                'Keyword Difficulty': kw.keyword_difficulty,
                'CPC': kw.cpc,
                'Competition': kw.competition,
                'Search Intent': kw.search_intent,
                'Trend': kw.trend,
                'Source Tool': kw.source_tool,
                'Opportunity Score': getattr(kw, 'opportunity_score', 0),
                'Related Keywords': '; '.join(kw.related_keywords) if kw.related_keywords else ''
            })
        
        # Convert to CSV
        df = pd.DataFrame(export_data)
        csv_content = df.to_csv(index=False)
        
        self.logger.info(f"📄 Exported {len(keywords)} keywords to {filename}")
        
        return csv_content
    
    def validate_imported_keywords(self, keywords: List[KeywordData]) -> Dict[str, Any]:
        """Validate imported keyword data quality"""
        
        issues = []
        warnings = []
        
        # Check for duplicates
        keyword_set = set()
        duplicates = []
        for kw in keywords:
            if kw.keyword.lower() in keyword_set:
                duplicates.append(kw.keyword)
            keyword_set.add(kw.keyword.lower())
        
        if duplicates:
            warnings.append(f"Found {len(duplicates)} duplicate keywords")
        
        # Check data quality
        zero_volume_count = len([kw for kw in keywords if kw.search_volume == 0])
        if zero_volume_count > 0:
            warnings.append(f"{zero_volume_count} keywords have zero search volume")
        
        high_difficulty_count = len([kw for kw in keywords if kw.keyword_difficulty > 80])
        if high_difficulty_count > len(keywords) * 0.8:
            warnings.append("Over 80% of keywords have very high difficulty (>80)")
        
        # Check for missing data
        missing_cpc_count = len([kw for kw in keywords if kw.cpc == 0])
        if missing_cpc_count > len(keywords) * 0.5:
            warnings.append("Over 50% of keywords missing CPC data")
        
        # Validate search intent distribution
        intent_distribution = {}
        for kw in keywords:
            intent_distribution[kw.search_intent] = intent_distribution.get(kw.search_intent, 0) + 1
        
        if intent_distribution.get('informational', 0) < len(keywords) * 0.3:
            warnings.append("Low percentage of informational keywords (recommended for blog content)")
        
        return {
            "validation_status": "passed" if not issues else "failed",
            "total_keywords": len(keywords),
            "issues": issues,
            "warnings": warnings,
            "statistics": {
                "duplicates_found": len(duplicates),
                "zero_volume_keywords": zero_volume_count,
                "high_difficulty_keywords": high_difficulty_count,
                "missing_cpc_data": missing_cpc_count,
                "intent_distribution": intent_distribution,
                "average_search_volume": sum(kw.search_volume for kw in keywords) / len(keywords) if keywords else 0,
                "average_difficulty": sum(kw.keyword_difficulty for kw in keywords) / len(keywords) if keywords else 0
            },
            "recommendations": self._generate_validation_recommendations(issues, warnings, intent_distribution)
        }
    
    def _generate_validation_recommendations(self, issues: List[str], warnings: List[str], intent_distribution: Dict[str, int]) -> List[str]:
        """Generate recommendations based on validation results"""
        
        recommendations = []
        
        if warnings:
            if "duplicate keywords" in ' '.join(warnings):
                recommendations.append("Remove duplicate keywords to avoid keyword cannibalization")
            
            if "zero search volume" in ' '.join(warnings):
                recommendations.append("Consider removing or replacing keywords with zero search volume")
            
            if "very high difficulty" in ' '.join(warnings):
                recommendations.append("Add more low-competition keywords (difficulty < 30) for quick wins")
            
            if "missing CPC data" in ' '.join(warnings):
                recommendations.append("Try to gather CPC data for better commercial value assessment")
            
            if "Low percentage of informational" in ' '.join(warnings):
                recommendations.append("Add more informational keywords suitable for blog content")
        
        # Intent-based recommendations
        total_keywords = sum(intent_distribution.values())
        if total_keywords > 0:
            informational_pct = (intent_distribution.get('informational', 0) / total_keywords) * 100
            commercial_pct = (intent_distribution.get('commercial', 0) / total_keywords) * 100
            
            if informational_pct > 80:
                recommendations.append("Consider adding some commercial keywords for monetization opportunities")
            elif commercial_pct > 50:
                recommendations.append("High commercial intent - good for conversion-focused content")
        
        if not recommendations:
            recommendations.append("Keyword data quality looks good - proceed with content creation")
        
        return recommendations