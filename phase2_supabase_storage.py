#!/usr/bin/env python3
"""
CORRECTED: Phase 2 Supabase Storage System
Fixed all duplicate methods and ensured proper scoring validation
"""

import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import Phase 1 storage system
from working_supabase_integration import RLSSupabaseStorage

class Phase2SupabaseStorage(RLSSupabaseStorage):
    """Enhanced storage system for Phase 2 blog idea generation results"""
    
    def __init__(self, user_id: Optional[str] = None):
        super().__init__(user_id)
        self.logger = logging.getLogger(__name__)
        
        # Ensure Phase 2 tables exist
        self._ensure_phase2_tables()
    
    def _ensure_phase2_tables(self):
        """Ensure Phase 2 tables exist in Supabase"""
        
        try:
            # Test if tables exist by trying to query them
            test_queries = [
                "blog_ideas?limit=1",
                "content_calendar?limit=1", 
                "blog_generation_results?limit=1"
            ]
            
            for query in test_queries:
                result = self._execute_query('GET', query)
                if not result['success'] and "does not exist" in str(result.get('error', '')):
                    self.logger.warning(f"⚠️ Phase 2 table missing. Please run SQL setup.")
                    break
            
            self.logger.info("✅ Phase 2 tables verified")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not verify Phase 2 tables: {e}")

    def validate_blog_idea_data(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """
        CRITICAL FIX: Validate and ensure all scoring data is present
        """
        
        validation_issues = []
        
        # Required scoring fields
        required_scores = [
            'overall_quality_score', 'viral_potential_score', 'seo_optimization_score',
            'audience_alignment_score', 'content_feasibility_score', 'business_impact_score'
        ]
        
        # Validate all scores are present and in valid range
        for field in required_scores:
            score = idea.get(field)
            if score is None:
                validation_issues.append(f"Missing required field: {field}")
                idea[field] = 50  # Default value
            elif not isinstance(score, (int, float)):
                validation_issues.append(f"Invalid {field} type: {type(score)}")
                idea[field] = 50
            elif not (0 <= score <= 100):
                validation_issues.append(f"Invalid {field} range: {score} (should be 0-100)")
                idea[field] = max(0, min(100, int(score)))
            else:
                # Ensure it's an integer
                idea[field] = int(score)
        
        # Check content format
        content_format = idea.get("content_format")
        valid_formats = [
            'how_to_guide', 'listicle', 'case_study', 'comparison', 'trend_analysis',
            'tutorial', 'review', 'interview', 'opinion', 'news_analysis',
            'resource_roundup', 'checklist', 'template', 'interactive_tool', 'infographic'
        ]
        
        if content_format not in valid_formats:
            validation_issues.append(f"Invalid content_format: '{content_format}' not in {valid_formats}")
            idea["content_format"] = self._normalize_content_format(content_format)
        
        # Check difficulty level
        difficulty_level = idea.get("difficulty_level")
        valid_difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
        
        if difficulty_level not in valid_difficulties:
            validation_issues.append(f"Invalid difficulty_level: '{difficulty_level}' not in {valid_difficulties}")
            idea["difficulty_level"] = self._normalize_difficulty_level(difficulty_level)
        
        # Check priority level
        priority_level = idea.get("priority_level")
        valid_priorities = ['high', 'medium', 'low']
        
        if priority_level and priority_level not in valid_priorities:
            validation_issues.append(f"Invalid priority_level: '{priority_level}' not in {valid_priorities}")
            idea["priority_level"] = "medium"
        
        # Validate estimated word count
        word_count = idea.get("estimated_word_count", 2500)
        if not isinstance(word_count, (int, float)) or word_count <= 0:
            validation_issues.append(f"Invalid estimated_word_count: {word_count}")
            idea["estimated_word_count"] = 2500
        else:
            idea["estimated_word_count"] = int(word_count)
        
        # Validate estimated reading time
        reading_time = idea.get("estimated_reading_time", 10)
        if not isinstance(reading_time, (int, float)) or reading_time <= 0:
            validation_issues.append(f"Invalid estimated_reading_time: {reading_time}")
            idea["estimated_reading_time"] = max(1, int(idea["estimated_word_count"] / 200))
        else:
            idea["estimated_reading_time"] = int(reading_time)
        
        # Log validation issues
        if validation_issues:
            self.logger.warning(f"Validation issues for idea '{idea.get('title', 'Unknown')}': {validation_issues}")
        
        return {
            "is_valid": len(validation_issues) == 0,
            "issues": validation_issues,
            "validated_idea": idea
        }

    def _normalize_content_format(self, content_format_input):
        """Normalize content format to match database constraints"""
        if not content_format_input:
            return "how_to_guide"
        
        # Convert to lowercase for comparison
        format_lower = str(content_format_input).lower()
        
        # Define mapping from various inputs to valid database formats
        format_mapping = {
            # Direct matches
            'how_to_guide': 'how_to_guide',
            'listicle': 'listicle', 
            'case_study': 'case_study',
            'comparison': 'comparison',
            'trend_analysis': 'trend_analysis',
            'tutorial': 'tutorial',
            'review': 'review',
            'interview': 'interview',
            'opinion': 'opinion',
            'news_analysis': 'news_analysis',
            'resource_roundup': 'resource_roundup',
            'checklist': 'checklist',
            'template': 'template',
            'interactive_tool': 'interactive_tool',
            'infographic': 'infographic',
            
            # Common variations and mappings
            'how to guide': 'how_to_guide',
            'how-to guide': 'how_to_guide',
            'guide': 'how_to_guide',
            'step by step guide': 'how_to_guide',
            'beginner guide': 'how_to_guide',
            
            'list': 'listicle',
            'top 10': 'listicle',
            'numbered list': 'listicle',
            'tips list': 'listicle',
            
            'case study': 'case_study',
            'study': 'case_study',
            
            'versus': 'comparison',
            'vs': 'comparison',
            'compare': 'comparison',
            
            'trend report': 'trend_analysis',
            'market analysis': 'trend_analysis',
            
            'product review': 'review',
            'tool review': 'review',
        }
        
        # First try exact match
        if format_lower in format_mapping:
            return format_mapping[format_lower]
        
        # Then try partial matches
        for key, value in format_mapping.items():
            if key in format_lower:
                return value
        
        # Default fallback
        self.logger.warning(f"Could not map content format '{content_format_input}' to valid enum, using 'how_to_guide'")
        return 'how_to_guide'

    def _normalize_difficulty_level(self, difficulty_input):
        """Normalize difficulty level to match database constraints"""
        if not difficulty_input:
            return "intermediate"
        
        difficulty_lower = str(difficulty_input).lower()
        
        # Valid values: 'beginner', 'intermediate', 'advanced', 'expert'
        if difficulty_lower in ['beginner', 'intermediate', 'advanced', 'expert']:
            return difficulty_lower
        
        # Map variations
        difficulty_mapping = {
            'easy': 'beginner',
            'basic': 'beginner',
            'simple': 'beginner',
            'entry level': 'beginner',
            'novice': 'beginner',
            
            'medium': 'intermediate',
            'moderate': 'intermediate',
            'standard': 'intermediate',
            
            'hard': 'advanced',
            'difficult': 'advanced',
            'complex': 'advanced',
            'professional': 'advanced',
            
            'expert level': 'expert',
            'master': 'expert',
            'specialist': 'expert'
        }
        
        if difficulty_lower in difficulty_mapping:
            return difficulty_mapping[difficulty_lower]
        
        # Default fallback
        self.logger.warning(f"Could not map difficulty '{difficulty_input}' to valid enum, using 'intermediate'")
        return "intermediate"

    async def save_blog_generation_results(
        self,
        analysis_id: str,
        user_id: str,
        generation_result: Dict[str, Any],
        llm_config: Dict[str, Any]
    ) -> str:
        """Save complete blog idea generation results with validation"""
        
        if not user_id:
            raise ValueError("user_id is required for RLS")
        
        self.set_user_context(user_id)
        
        try:
            self.logger.info(f"💾 Saving blog generation results for analysis: {analysis_id}")
            
            # Extract data from generation result
            blog_ideas = generation_result.get('blog_ideas', [])
            content_calendar = generation_result.get('content_calendar', {})
            strategic_insights = generation_result.get('strategic_insights', {})
            success_predictions = generation_result.get('success_predictions', {})
            generation_metadata = generation_result.get('generation_metadata', {})
            
            # CRITICAL FIX: Validate all blog ideas have scores before saving
            self.logger.info(f"🔍 Validating {len(blog_ideas)} blog ideas...")
            validated_ideas = []
            
            for idea in blog_ideas:
                validation_result = self.validate_blog_idea_data(idea)
                validated_idea = validation_result["validated_idea"]
                
                if not validation_result["is_valid"]:
                    self.logger.warning(f"Idea validation issues: {validation_result['issues']}")
                
                validated_ideas.append(validated_idea)
            
            self.logger.info(f"✅ Validated {len(validated_ideas)} blog ideas")
            
            # Step 1: Save individual blog ideas with validation
            blog_idea_ids = []
            if validated_ideas:
                blog_idea_ids = await self._save_blog_ideas(
                    analysis_id, user_id, validated_ideas
                )
            
            # Step 2: Save content calendar
            calendar_id = None
            if content_calendar:
                calendar_id = await self._save_content_calendar(
                    analysis_id, user_id, content_calendar
                )
            
            # Step 3: Save generation results summary
            generation_result_id = await self._save_generation_results_summary(
                analysis_id, 
                user_id,
                generation_metadata,
                strategic_insights,
                success_predictions,
                llm_config,
                len(validated_ideas)
            )
            
            self.logger.info(f"✅ Blog generation results saved: {len(validated_ideas)} ideas, calendar, insights")
            
            return generation_result_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save blog generation results: {e}")
            raise

    async def _save_blog_ideas(
        self,
        analysis_id: str,
        user_id: str,
        blog_ideas: List[Dict[str, Any]]
    ) -> List[str]:
        """Save individual blog ideas to database with proper validation"""
        
        try:
            ideas_to_insert = []
            
            for idea in blog_ideas:
                # Validate and filter keywords for relevance to title/description
                validated_idea = self._validate_keywords_relevance(idea)
                
                # Create database record with ALL required fields
                idea_record = {
                    "id": validated_idea.get("id", str(uuid.uuid4())),
                    "user_id": user_id,
                    "trend_analysis_id": analysis_id,
                    
                    # Core blog idea data
                    "title": str(validated_idea.get("title", "Untitled Blog Idea"))[:500],
                    "description": str(validated_idea.get("description", ""))[:1000],
                    "content_format": validated_idea.get("content_format", "how_to_guide"),
                    "difficulty_level": validated_idea.get("difficulty_level", "intermediate"),
                    "estimated_word_count": int(validated_idea.get("estimated_word_count", 2500)),
                    "estimated_reading_time": int(validated_idea.get("estimated_reading_time", 10)),
                    
                    # CRITICAL FIX: All quality scores with validation
                    "overall_quality_score": int(validated_idea.get("overall_quality_score", 50)),
                    "viral_potential_score": int(validated_idea.get("viral_potential_score", 50)),
                    "seo_optimization_score": int(validated_idea.get("seo_optimization_score", 50)),
                    "audience_alignment_score": int(validated_idea.get("audience_alignment_score", 50)),
                    "content_feasibility_score": int(validated_idea.get("content_feasibility_score", 50)),
                    "business_impact_score": int(validated_idea.get("business_impact_score", 50)),
                    
                    # SEO data with JSON serialization
                    "primary_keywords": json.dumps(validated_idea.get("primary_keywords", [])),
                    "secondary_keywords": json.dumps(validated_idea.get("secondary_keywords", [])),
                    "featured_snippet_opportunity": bool(idea.get("featured_snippet_opportunity", False)),
                    
                    # Content structure with JSON serialization
                    "outline": json.dumps(idea.get("outline", [])),
                    "key_points": json.dumps(idea.get("key_points", [])),
                    "engagement_hooks": json.dumps(idea.get("engagement_hooks", [])),
                    "visual_elements": json.dumps(idea.get("visual_elements", [])),
                    
                    # Business data
                    "call_to_action": str(idea.get("call_to_action", ""))[:500],
                    "business_value": str(idea.get("business_value", ""))[:1000],
                    "performance_estimates": json.dumps(idea.get("performance_estimates", {})),
                    
                    # Source tracking
                    "generation_source": str(idea.get("generation_source", ""))[:100],
                    "source_topic_id": idea.get("source_topic_id"),
                    "source_opportunity_id": idea.get("source_opportunity_id"),
                    
                    # User management with defaults
                    "selected": bool(idea.get("selected", False)),
                    "priority_level": idea.get("priority_level", "medium"),
                    "scheduled_publish_date": idea.get("scheduled_publish_date"),
                    "notes": str(idea.get("notes", ""))[:1000],
                    
                    # Metadata
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                # Log scoring data for debugging
                self.logger.debug(f"Saving idea '{idea_record['title']}' with scores: "
                                f"Overall={idea_record['overall_quality_score']}, "
                                f"Viral={idea_record['viral_potential_score']}, "
                                f"SEO={idea_record['seo_optimization_score']}, "
                                f"Audience={idea_record['audience_alignment_score']}, "
                                f"Feasibility={idea_record['content_feasibility_score']}, "
                                f"Business={idea_record['business_impact_score']}")
                
                ideas_to_insert.append(idea_record)
            
            # Insert in batches to avoid payload size limits
            batch_size = 50
            inserted_ids = []
            
            for i in range(0, len(ideas_to_insert), batch_size):
                batch = ideas_to_insert[i:i + batch_size]
                
                self.logger.info(f"💾 Inserting batch {i//batch_size + 1}: {len(batch)} ideas")
                
                result = self._execute_query('POST', 'blog_ideas', batch)
                
                if result['success']:
                    batch_ids = [record["id"] for record in result['data']]
                    inserted_ids.extend(batch_ids)
                    self.logger.info(f"✅ Saved batch of {len(batch)} blog ideas with scores")
                else:
                    self.logger.error(f"❌ Failed to save batch: {result.get('error')}")
                    if batch:
                        self.logger.error(f"First record in failed batch: {batch[0]}")
                    raise Exception(f"Failed to save blog ideas batch: {result.get('error')}")
            
            self.logger.info(f"✅ Saved {len(inserted_ids)} blog ideas with complete scoring data for analysis {analysis_id}")
            return inserted_ids
            
        except Exception as e:
            self.logger.error(f"❌ Error saving blog ideas: {e}")
            raise

    def _validate_keywords_relevance(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and filter keywords based on relevance to title and description"""
        
        title = idea.get("title", "").lower()
        description = idea.get("description", "").lower()
        
        # Get keywords
        primary_keywords = idea.get("primary_keywords", [])
        secondary_keywords = idea.get("secondary_keywords", [])
        
        # Filter primary keywords
        filtered_primary = self._filter_relevant_keywords(primary_keywords, title, description)
        
        # Filter secondary keywords
        filtered_secondary = self._filter_relevant_keywords(secondary_keywords, title, description)
        
        # If too few relevant keywords, generate context-specific ones
        if len(filtered_primary) < 3:
            filtered_primary.extend(self._generate_context_keywords(title, description, 3 - len(filtered_primary)))
        
        if len(filtered_secondary) < 5:
            filtered_secondary.extend(self._generate_context_keywords(title, description, 5 - len(filtered_secondary)))
        
        # Ensure uniqueness and remove empty strings
        filtered_primary = list(set([kw for kw in filtered_primary if kw.strip()]))
        filtered_secondary = list(set([kw for kw in filtered_secondary if kw.strip() and kw not in filtered_primary]))
        
        # Update the idea with filtered keywords
        idea["primary_keywords"] = filtered_primary[:5]  # Max 5 primary keywords
        idea["secondary_keywords"] = filtered_secondary[:8]  # Max 8 secondary keywords
        
        return idea

    def _filter_relevant_keywords(self, keywords: List[str], title: str, description: str) -> List[str]:
        """Filter keywords based on relevance to title and description"""
        if not keywords:
            return []
        
        import re
        
        relevant_keywords = []
        content_text = f"{title} {description}".lower()
        
        # Security-related terms to prioritize
        security_terms = {'security', 'surveillance', 'camera', 'alarm', 'sensor', 'monitor', 'lock', 'protection', 'safety', 'cctv', 'wireless', 'smart', 'digital', 'burglar', 'intrusion', 'theft', 'motion', 'access'}
        
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            if not keyword_lower:
                continue
            
            # Skip extremely generic keywords and problematic phrases
            generic_terms = {
                'guide', 'tips', 'best', 'complete', 'ultimate', 'essential', 'checklist', 'home', 'your', 'for', 'and', 'the', 'a', 'an', 'to', 'of', 'in', 'on', 'at', 'by', 'with', 'from',
                'affordable', 'subscription', 'analytics', 'enhanced', 'seamless', 'case', 'studies', 'study', 'successful', 'musthave', 'must-have', 'into', 'build', 'cases', 'upgrades', '2025', 'smart'}
            keyword_words = set(keyword_lower.split())
            if keyword_words.issubset(generic_terms):
                continue
            
            # Check for security-specific keywords
            keyword_has_security_term = any(term in keyword_lower for term in security_terms)
            
            # Check direct relevance
            if keyword_lower in content_text:
                if keyword_has_security_term or len(keyword_lower.split()) > 1:
                    relevant_keywords.append(keyword)
                continue
            
            # Check word-level relevance with security prioritization
            keyword_words = set(keyword_lower.split())
            content_words = set(content_text.split())
            
            # Security terms get higher priority
            security_in_keyword = sum(1 for kw in keyword_words if kw in security_terms)
            security_in_content = sum(1 for kw in keyword_words if kw in content_words)
            
            # At least 50% relevance OR contains security term
            if (keyword_words and len(keyword_words.intersection(content_words)) >= max(1, len(keyword_words) // 2)) or security_in_keyword > 0:
                relevant_keywords.append(keyword)
        
        return relevant_keywords

    def _generate_context_keywords(self, title: str, description: str, count: int) -> List[str]:
        """Generate context-specific keywords from title and description"""
        if not title or not description:
            return []
        
        import re
        
        # Combine title and description for context extraction
        content = f"{title} {description}".lower()
        
        # Security-specific patterns to extract meaningful keywords
        security_patterns = [
            r'\b(?:security|surveillance|camera|alarm|sensor|monitor|lock|protection|safety)\w*\b',
            r'\b(?:smart\s+(?:security|home|lock|camera|alarm))\b',
            r'\b(?:wireless|digital|smart)\s+(?:security|surveillance|monitoring)\b',
            r'\b(?:home\s+(?:security|surveillance|protection|monitoring))\b',
            r'\b(?:security\s+(?:system|camera|alarm|monitor|device))\b',
            r'\b(?:surveillance\s+(?:camera|system|monitoring))\b',
            r'\b(?:burglar|intrusion|theft|break-in|trespass)\w*\b',
            r'\b(?:motion\s+(?:sensor|detector|alarm))\b',
            r'\b(?:access\s+(?:control|entry|security))\b',
            r'\b(?:cctv|ip\s+camera|night\s+vision|remote\s+monitoring)\b'
        ]
        
        # Extract security-related phrases
        security_keywords = []
        for pattern in security_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            security_keywords.extend(matches)
        
        # Clean and deduplicate
        security_keywords = list(set([kw.strip() for kw in security_keywords if kw.strip()]))
        
        # If we have security keywords, prioritize them
        if security_keywords:
            # Sort by length (prioritize more specific terms)
            security_keywords.sort(key=len, reverse=True)
            return security_keywords[:count]
        
        # Fallback: extract meaningful phrases from content
        # Remove generic and problematic words
        generic_words = {
            'guide', 'tips', 'best', 'complete', 'ultimate', 'essential', 'checklist', 'smart', 'upgrades', '2025', 'home', 'your', 'for', 'and', 'the', 'a', 'an', 'to', 'of', 'in', 'on', 'at', 'by', 'with', 'from',
            'affordable', 'subscription', 'analytics', 'enhanced', 'seamless', 'case', 'studies', 'study', 'successful', 'musthave', 'into', 'build', 'cases', 'security'
        }
        
        # Extract meaningful content words (minimum 3 characters)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content)
        meaningful_words = [word for word in words if word.lower() not in generic_words]
        
        # Create specific multi-word phrases from actual content
        keywords = []
        
        # Generate 2-3 word phrases that actually appear in content
        content_words = content.split()
        for i in range(len(content_words) - 1):
            phrase_parts = []
            for j in range(i, min(i + 3, len(content_words))):
                word = re.sub(r'[^a-zA-Z0-9-]', '', content_words[j]).lower()
                if word and word not in generic_words and len(word) >= 3:
                    phrase_parts.append(word)
                    if len(phrase_parts) >= 2:
                        phrase = ' '.join(phrase_parts)
                        if phrase in content.lower() and phrase not in keywords and len(keywords) < count:
                            keywords.append(phrase)
        
        return keywords[:count]

    async def _save_content_calendar(self, analysis_id: str, user_id: str, content_calendar: Dict[str, Any]) -> str:
        """Save content calendar to database"""
        try:
            calendar_record = {
                "user_id": user_id,
                "trend_analysis_id": analysis_id,
                "publishing_strategy": json.dumps(content_calendar.get("publishing_strategy", {})),
                "priority_scheduling": json.dumps(content_calendar.get("priority_scheduling", {})),
                "seasonal_optimization": json.dumps(content_calendar.get("seasonal_optimization", {})),
                "content_series_opportunities": json.dumps(content_calendar.get("content_series_opportunities", [])),
                "format_distribution": json.dumps(content_calendar.get("format_distribution", {})),
                "estimated_resource_requirements": json.dumps(content_calendar.get("estimated_resource_requirements", {})),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self._execute_query('POST', 'content_calendar', calendar_record)
            
            if result['success'] and result['data']:
                calendar_id = result['data'][0]["id"]
                self.logger.info(f"✅ Saved content calendar with ID: {calendar_id}")
                return calendar_id
            else:
                raise Exception(f"Failed to save content calendar: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error saving content calendar: {e}")
            raise

    async def _save_generation_results_summary(
        self,
        analysis_id: str,
        user_id: str,
        generation_metadata: Dict[str, Any],
        strategic_insights: Dict[str, Any],
        success_predictions: Dict[str, Any],
        llm_config: Dict[str, Any],
        total_ideas: int
    ) -> str:
        """Save generation results summary to database"""
        try:
            results_record = {
                "user_id": user_id,
                "trend_analysis_id": analysis_id,
                "total_ideas_generated": total_ideas,
                "average_quality_score": generation_metadata.get("average_quality_score", 0),
                "processing_time_seconds": generation_metadata.get("processing_time_seconds", 0),
                "llm_provider": llm_config.get("provider", ""),
                "llm_model": llm_config.get("model", ""),
                "strategic_insights": json.dumps(strategic_insights),
                "success_predictions": json.dumps(success_predictions),
                "implementation_recommendations": json.dumps(strategic_insights.get("implementation_recommendations", [])),
                "ideas_by_source": json.dumps(generation_metadata.get("ideas_by_source", {})),
                "quality_tier_distribution": json.dumps(strategic_insights.get("overall_quality_assessment", {}).get("quality_tier_distribution", {})),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self._execute_query('POST', 'blog_generation_results', results_record)
            
            if result['success'] and result['data']:
                result_id = result['data'][0]["id"]
                self.logger.info(f"✅ Saved generation results summary with ID: {result_id}")
                return result_id
            else:
                raise Exception(f"Failed to save generation results: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error saving generation results summary: {e}")
            raise

    # RETRIEVAL METHODS

    async def get_blog_ideas(
        self,
        analysis_id: str,
        user_id: str,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Get blog ideas with optional filtering"""
        
        self.set_user_context(user_id)
        
        try:
            # Build query with filters
            filter_params = f"trend_analysis_id=eq.{analysis_id}&user_id=eq.{user_id}"
            
            if filters:
                if filters.get("content_format"):
                    filter_params += f"&content_format=eq.{filters['content_format']}"
                if filters.get("min_quality_score"):
                    filter_params += f"&overall_quality_score=gte.{filters['min_quality_score']}"
                if filters.get("selected_only"):
                    filter_params += "&selected=eq.true"
                if filters.get("priority_level"):
                    filter_params += f"&priority_level=eq.{filters['priority_level']}"
            
            # Sorting
            sort_by = filters.get("sort_by", "overall_quality_score") if filters else "overall_quality_score"
            sort_order = filters.get("sort_order", "desc") if filters else "desc"
            order_param = f"&order={sort_by}.{sort_order}"
            
            # Limit
            limit = filters.get("limit", 50) if filters else 50
            limit_param = f"&limit={limit}"
            
            endpoint = f"blog_ideas?{filter_params}&select=*{order_param}{limit_param}"
            result = self._execute_query('GET', endpoint)
            
            if result['success']:
                # Parse JSON fields
                blog_ideas = []
                for idea in result['data']:
                    parsed_idea = self._parse_blog_idea_from_db(idea)
                    blog_ideas.append(parsed_idea)
                
                self.logger.info(f"📊 Retrieved {len(blog_ideas)} blog ideas for analysis {analysis_id}")
                return blog_ideas
            else:
                raise Exception(f"Failed to get blog ideas: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error getting blog ideas: {e}")
            raise

    def _parse_blog_idea_from_db(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse blog idea data from database, handling JSON fields"""
        
        try:
            return {
                "id": idea_data.get("id"),
                "trend_analysis_id": idea_data.get("trend_analysis_id"),
                "title": idea_data.get("title", ""),
                "description": idea_data.get("description", ""),
                "content_format": idea_data.get("content_format", ""),
                "difficulty_level": idea_data.get("difficulty_level", ""),
                "estimated_word_count": idea_data.get("estimated_word_count", 0),
                "estimated_reading_time": idea_data.get("estimated_reading_time", 0),
                
                # Quality scores
                "overall_quality_score": idea_data.get("overall_quality_score", 0),
                "viral_potential_score": idea_data.get("viral_potential_score", 0),
                "seo_optimization_score": idea_data.get("seo_optimization_score", 0),
                "audience_alignment_score": idea_data.get("audience_alignment_score", 0),
                "content_feasibility_score": idea_data.get("content_feasibility_score", 0),
                "business_impact_score": idea_data.get("business_impact_score", 0),
                
                # SEO data (parse JSON)
                "primary_keywords": json.loads(idea_data.get("primary_keywords", "[]")),
                "secondary_keywords": json.loads(idea_data.get("secondary_keywords", "[]")),
                "featured_snippet_opportunity": idea_data.get("featured_snippet_opportunity", False),
                
                # Content structure (parse JSON)
                "outline": json.loads(idea_data.get("outline", "[]")),
                "key_points": json.loads(idea_data.get("key_points", "[]")),
                "engagement_hooks": json.loads(idea_data.get("engagement_hooks", "[]")),
                "visual_elements": json.loads(idea_data.get("visual_elements", "[]")),
                
                # Business data
                "call_to_action": idea_data.get("call_to_action", ""),
                "business_value": idea_data.get("business_value", ""),
                "performance_estimates": json.loads(idea_data.get("performance_estimates", "{}")),
                
                # Source tracking
                "generation_source": idea_data.get("generation_source", ""),
                "source_topic_id": idea_data.get("source_topic_id"),
                "source_opportunity_id": idea_data.get("source_opportunity_id"),
                
                # User management
                "selected": idea_data.get("selected", False),
                "priority_level": idea_data.get("priority_level", "medium"),
                "scheduled_publish_date": idea_data.get("scheduled_publish_date"),
                "notes": idea_data.get("notes", ""),
                
                # Metadata
                "created_at": idea_data.get("created_at"),
                "updated_at": idea_data.get("updated_at")
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing blog idea from DB: {e}")
            return idea_data  # Return original if parsing fails

    async def get_blog_ideas_summary(
        self,
        analysis_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get summary statistics for blog ideas with score validation"""
        
        self.set_user_context(user_id)
        
        try:
            # Get all blog ideas for analysis
            blog_ideas = await self.get_blog_ideas(analysis_id, user_id)
            
            if not blog_ideas:
                return {
                    "total_ideas": 0,
                    "selected_ideas": 0,
                    "average_quality_score": 0,
                    "format_distribution": {},
                    "quality_distribution": {},
                    "priority_distribution": {},
                    "scoring_validation": {"all_scores_present": True}
                }
            
            # VALIDATION: Check if all ideas have proper scores
            ideas_with_scores = [i for i in blog_ideas if i.get("overall_quality_score", 0) > 0]
            scoring_health = {
                "total_ideas": len(blog_ideas),
                "ideas_with_scores": len(ideas_with_scores),
                "score_coverage_percentage": round((len(ideas_with_scores) / len(blog_ideas)) * 100, 1),
                "all_scores_present": len(ideas_with_scores) == len(blog_ideas)
            }
            
            # Calculate statistics
            total_ideas = len(blog_ideas)
            selected_ideas = len([idea for idea in blog_ideas if idea.get("selected", False)])
            
            # Use only ideas with valid scores for average calculation
            valid_scores = [i.get("overall_quality_score", 0) for i in blog_ideas if i.get("overall_quality_score", 0) > 0]
            avg_quality = sum(valid_scores) / len(valid_scores) if valid_scores else 0
            
            # Format distribution
            format_counts = {}
            for idea in blog_ideas:
                fmt = idea.get("content_format", "unknown")
                format_counts[fmt] = format_counts.get(fmt, 0) + 1
            
            # Quality distribution
            quality_distribution = {
                "excellent_80_plus": len([i for i in blog_ideas if i.get("overall_quality_score", 0) >= 80]),
                "good_70_to_79": len([i for i in blog_ideas if 70 <= i.get("overall_quality_score", 0) < 80]),
                "decent_60_to_69": len([i for i in blog_ideas if 60 <= i.get("overall_quality_score", 0) < 70]),
                "needs_work_below_60": len([i for i in blog_ideas if i.get("overall_quality_score", 0) < 60])
            }
            
            # Priority distribution
            priority_counts = {}
            for idea in blog_ideas:
                priority = idea.get("priority_level", "medium")
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            return {
                "total_ideas": total_ideas,
                "selected_ideas": selected_ideas,
                "average_quality_score": round(avg_quality, 1),
                "format_distribution": format_counts,
                "quality_distribution": quality_distribution,
                "priority_distribution": priority_counts,
                "analysis_id": analysis_id,
                "summary_generated_at": datetime.utcnow().isoformat(),
                "scoring_validation": scoring_health
            }
            
        except Exception as e:
            self.logger.error(f"Error getting blog ideas summary: {e}")
            return {}

    # REMAINING METHODS
    async def get_blog_idea_by_id(
        self,
        idea_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific blog idea by ID"""
        
        self.set_user_context(user_id)
        
        try:
            result = self._execute_query('GET', f'blog_ideas?id=eq.{idea_id}&user_id=eq.{user_id}&select=*')
            
            if result['success'] and result['data']:
                idea_data = result['data'][0]
                return self._parse_blog_idea_from_db(idea_data)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting blog idea {idea_id}: {e}")
            return None

    async def update_blog_idea_selection(
        self,
        idea_id: str,
        user_id: str,
        selected: bool,
        priority_level: str = None,
        scheduled_date: str = None,
        notes: str = None
    ) -> bool:
        """Update blog idea selection and management fields"""
        
        self.set_user_context(user_id)
        
        try:
            update_data = {
                "selected": selected,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if priority_level:
                update_data["priority_level"] = priority_level
            
            if scheduled_date:
                update_data["scheduled_publish_date"] = scheduled_date
            
            if notes is not None:
                update_data["notes"] = notes
            
            result = self._execute_query(
                'PATCH',
                f'blog_ideas?id=eq.{idea_id}&user_id=eq.{user_id}',
                update_data
            )
            
            if result['success']:
                self.logger.info(f"✅ Updated blog idea {idea_id} selection: {selected}")
                return True
            else:
                raise Exception(f"Failed to update blog idea selection: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error updating blog idea selection: {e}")
            return False

    async def get_content_calendar(
        self,
        analysis_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get content calendar for analysis"""
        
        self.set_user_context(user_id)
        
        try:
            result = self._execute_query('GET', f'content_calendar?trend_analysis_id=eq.{analysis_id}&user_id=eq.{user_id}&select=*')
            
            if result['success'] and result['data']:
                calendar_data = result['data'][0]
                
                # Parse JSON fields
                parsed_calendar = {
                    "id": calendar_data["id"],
                    "trend_analysis_id": calendar_data["trend_analysis_id"],
                    "publishing_strategy": json.loads(calendar_data.get("publishing_strategy", "{}")),
                    "priority_scheduling": json.loads(calendar_data.get("priority_scheduling", "{}")),
                    "seasonal_optimization": json.loads(calendar_data.get("seasonal_optimization", "{}")),
                    "content_series_opportunities": json.loads(calendar_data.get("content_series_opportunities", "[]")),
                    "format_distribution": json.loads(calendar_data.get("format_distribution", "{}")),
                    "estimated_resource_requirements": json.loads(calendar_data.get("estimated_resource_requirements", "{}")),
                    "created_at": calendar_data.get("created_at"),
                    "updated_at": calendar_data.get("updated_at")
                }
                
                return parsed_calendar
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting content calendar: {e}")
            return None

    async def get_strategic_insights(
        self,
        analysis_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get strategic insights and success predictions"""
        
        self.set_user_context(user_id)
        
        try:
            result = self._execute_query('GET', f'blog_generation_results?trend_analysis_id=eq.{analysis_id}&user_id=eq.{user_id}&select=*')
            
            if result['success'] and result['data']:
                results_data = result['data'][0]
                
                # Parse JSON fields
                insights = {
                    "generation_metadata": {
                        "total_ideas_generated": results_data.get("total_ideas_generated", 0),
                        "average_quality_score": float(results_data.get("average_quality_score", 0)),
                        "processing_time_seconds": float(results_data.get("processing_time_seconds", 0)),
                        "llm_provider": results_data.get("llm_provider", ""),
                        "llm_model": results_data.get("llm_model", ""),
                        "created_at": results_data.get("created_at")
                    },
                    "strategic_insights": json.loads(results_data.get("strategic_insights", "{}")),
                    "success_predictions": json.loads(results_data.get("success_predictions", "{}")),
                    "implementation_recommendations": json.loads(results_data.get("implementation_recommendations", "[]")),
                    "ideas_by_source": json.loads(results_data.get("ideas_by_source", "{}")),
                    "quality_tier_distribution": json.loads(results_data.get("quality_tier_distribution", "{}"))
                }
                
                return insights
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting strategic insights: {e}")
            return None

    async def bulk_update_blog_ideas(
        self,
        idea_updates: List[Dict[str, Any]],
        user_id: str
    ) -> int:
        """Bulk update multiple blog ideas"""
        
        self.set_user_context(user_id)
        
        try:
            updated_count = 0
            
            for update in idea_updates:
                idea_id = update.get("id")
                if not idea_id:
                    continue
                
                update_data = {
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                # Add fields that can be updated
                updateable_fields = [
                "selected", "priority_level", "scheduled_publish_date", 
                    "notes", "title", "description",
                    # CRITICAL: Allow updating scores
                    "overall_quality_score", "viral_potential_score", "seo_optimization_score",
                    "audience_alignment_score", "content_feasibility_score", "business_impact_score",
                    
                    # CRITICAL FIX: Add ALL keyword enhancement fields
                    "keyword_research_enhanced",
                    "traffic_potential_score", 
                    "competition_score",
                    "enhanced_primary_keywords",
                    "enhanced_secondary_keywords", 
                    "keyword_research_data",
                    "keyword_suggestions",
                    "content_optimization_tips",
                    "keyword_source_tools",
                    "enhancement_timestamp"
                ]
                print(f"🔧 DEBUG: bulk_update_blog_ideas called")
                print(f"   User ID: {user_id}")
                print(f"   Number of updates: {len(idea_updates)}")

                if idea_updates:
                    sample = idea_updates[0]
                    print(f"   Sample update:")
                    print(f"      ID: {sample.get('id', 'NO ID')}")
                    print(f"      Enhanced flag: {sample.get('keyword_research_enhanced', 'NOT SET')}")
                    print(f"      Traffic score: {sample.get('traffic_potential_score', 'NOT SET')}")
                    print(f"      Primary keywords: {sample.get('enhanced_primary_keywords', 'NOT SET')}")
                    print(f"      Update keys: {list(sample.keys())}")

                
                for field in updateable_fields:
                    if field in update:
                        update_data[field] = update[field]
                        print(f"🔧 Updating idea {idea_id} with data: {update_data}")

                
                result = self._execute_query(
                    'PATCH',
                    f'blog_ideas?id=eq.{idea_id}&user_id=eq.{user_id}',
                    update_data
                )
                
                if result['success']:
                    updated_count += 1
                else:
                    self.logger.warning(f"Failed to update blog idea {idea_id}: {result.get('error')}")
            
            self.logger.info(f"✅ Bulk updated {updated_count} blog ideas")
            return updated_count
            
        except Exception as e:
            self.logger.error(f"Error in bulk update: {e}")
            return 0

    async def delete_blog_idea(
        self,
        idea_id: str,
        user_id: str
    ) -> bool:
        """Delete a blog idea"""
        
        self.set_user_context(user_id)
        
        try:
            result = self._execute_query(
                'DELETE',
                f'blog_ideas?id=eq.{idea_id}&user_id=eq.{user_id}'
            )
            
            if result['success']:
                self.logger.info(f"✅ Deleted blog idea {idea_id}")
                return True
            else:
                raise Exception(f"Failed to delete blog idea: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error deleting blog idea: {e}")
            return False

    async def get_all_blog_generation_results(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get all blog generation results for user"""
        
        self.set_user_context(user_id)
        
        try:
            result = self._execute_query(
                'GET',
                f'blog_generation_results?user_id=eq.{user_id}&select=*&order=created_at.desc&limit={limit}'
            )
            
            if result['success']:
                return result['data']
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting blog generation results: {e}")
            return []


# ============================================================================
# UTILITY FUNCTIONS FOR PHASE 2
# ============================================================================

async def save_blog_generation_to_supabase(
    analysis_id: str,
    user_id: str,
    generation_result: Dict[str, Any],
    llm_config: Dict[str, Any]
) -> str:
    """
    Utility function to save blog generation results to Supabase
    """
    try:
        storage = Phase2SupabaseStorage()
        
        result_id = await storage.save_blog_generation_results(
            analysis_id=analysis_id,
            user_id=user_id,
            generation_result=generation_result,
            llm_config=llm_config
        )
        
        return result_id
        
    except Exception as e:
        logging.getLogger(__name__).error(f"❌ Failed to save blog generation results: {e}")
        raise


# ============================================================================
# TESTING UTILITIES
# ============================================================================

def test_phase2_storage_connection(user_id: str = None):
    """Test Phase 2 storage connection"""
    try:
        storage = Phase2SupabaseStorage()
        
        # Test basic connection
        test_query = storage._execute_query('GET', 'blog_ideas?limit=1')
        
        if test_query['success']:
            print("✅ Phase 2 storage connection successful!")
            
            if user_id:
                # Test user-specific query
                try:
                    uuid.UUID(user_id)
                    import asyncio
                    user_ideas = asyncio.run(storage.get_blog_ideas("test", user_id, {"limit": 5}))
                    print(f"✅ User-specific query successful! Found {len(user_ideas)} ideas for user {user_id}")
                except ValueError:
                    print(f"❌ Invalid user_id format: {user_id}")
                except Exception as e:
                    print(f"⚠️ User query test failed: {e}")
        else:
            print(f"❌ Phase 2 storage connection failed: {test_query.get('error')}")
            
        return test_query['success']
        
    except Exception as e:
        print(f"❌ Phase 2 storage test failed: {e}")
        return False


if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not installed. Make sure environment variables are set manually.")
    
    # Test the Phase 2 storage connection
    print("🧪 Testing Phase 2 Supabase Storage...")
    print("=" * 50)
    test_phase2_storage_connection()