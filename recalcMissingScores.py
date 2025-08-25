#!/usr/bin/env python3
"""
Phase 2 Fix Script - Recalculate Missing Scores
Run this script to fix existing blog ideas with missing or zero scores
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

# Import your corrected components
try:
    from phase2_supabase_storage import Phase2SupabaseStorage
except ImportError:
    from corrected_phase2_storage import Phase2SupabaseStorage

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlogIdeaScoreFixer:
    """Fix missing scores in existing blog ideas"""
    
    def __init__(self):
        self.storage = Phase2SupabaseStorage()
    
    def calculate_viral_potential_score(self, idea: Dict[str, Any], context: Dict[str, Any] = None) -> int:
        """Calculate viral potential score based on idea characteristics"""
        
        score = 50  # Base score
        
        # Title engagement factors
        title = idea.get("title", "").lower()
        if any(word in title for word in ["ultimate", "complete", "secret", "mistake", "hack", "best", "top"]):
            score += 15
        
        if any(word in title for word in ["how to", "guide", "step by step"]):
            score += 10
        
        # Content format bonus
        content_format = idea.get("content_format", "")
        format_bonuses = {
            "listicle": 15,
            "how_to_guide": 10,
            "case_study": 12,
            "comparison": 8,
            "trend_analysis": 5
        }
        score += format_bonuses.get(content_format, 5)
        
        # Source type bonus
        source_type = idea.get("generation_source", "")
        if source_type == "trending_topic":
            score += 15
        elif source_type in ["geographic_insights", "rising_queries"]:
            score += 10
        
        return max(0, min(100, int(score)))
    
    def calculate_seo_optimization_score(self, idea: Dict[str, Any], context: Dict[str, Any] = None) -> int:
        """Calculate SEO optimization score"""
        
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
        
        # Content length optimization
        word_count = idea.get("estimated_word_count", 0)
        if 2000 <= word_count <= 4000:
            score += 15
        elif word_count >= 1500:
            score += 8
        
        # Featured snippet opportunity
        if idea.get("featured_snippet_opportunity", False):
            score += 10
        
        return max(0, min(100, int(score)))
    
    def calculate_audience_alignment_score(self, idea: Dict[str, Any], context: Dict[str, Any] = None) -> int:
        """Calculate audience alignment score"""
        
        score = 60  # Base score
        
        difficulty_level = idea.get("difficulty_level", "intermediate")
        content_format = idea.get("content_format", "")
        
        # Difficulty alignment (assuming professional audience)
        if difficulty_level == "intermediate":
            score += 15
        elif difficulty_level == "advanced":
            score += 10
        elif difficulty_level == "beginner":
            score += 5
        
        # Format alignment for professionals
        if content_format in ["case_study", "trend_analysis", "comparison"]:
            score += 12
        elif content_format in ["how_to_guide", "tutorial"]:
            score += 8
        
        return max(0, min(100, int(score)))
    
    def calculate_content_feasibility_score(self, idea: Dict[str, Any], context: Dict[str, Any] = None) -> int:
        """Calculate content feasibility score"""
        
        score = 65  # Base score
        
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
        
        # Difficulty impact
        difficulty = idea.get("difficulty_level", "intermediate")
        if difficulty == "beginner":
            score += 10
        elif difficulty == "intermediate":
            score += 5
        # Advanced/expert content is harder to create
        
        # Outline completeness
        outline = idea.get("outline", [])
        if len(outline) >= 5:
            score += 10
        elif len(outline) >= 3:
            score += 5
        
        return max(0, min(100, int(score)))
    
    def calculate_business_impact_score(self, idea: Dict[str, Any], context: Dict[str, Any] = None) -> int:
        """Calculate business impact score"""
        
        score = 55  # Base score
        
        # Business value assessment
        business_value = idea.get("business_value", "").lower()
        if any(word in business_value for word in ["lead generation", "conversion", "sales"]):
            score += 20
        
        if any(word in business_value for word in ["authority", "thought leadership", "brand"]):
            score += 12
        
        # Call to action presence
        cta = idea.get("call_to_action", "")
        if cta and len(cta) > 20:
            score += 10
        
        # Content format business impact
        content_format = idea.get("content_format", "")
        business_impact_map = {
            "case_study": 18,
            "how_to_guide": 15,
            "comparison": 15,
            "tool_review": 12,
            "beginner_guide": 10,
            "listicle": 10,
            "trend_analysis": 8
        }
        score += business_impact_map.get(content_format, 8)
        
        return max(0, min(100, int(score)))
    
    async def diagnose_analysis(self, analysis_id: str, user_id: str) -> Dict[str, Any]:
        """Diagnose scoring issues for an analysis"""
        
        logger.info(f"🔍 Diagnosing analysis: {analysis_id}")
        
        try:
            self.storage.set_user_context(user_id)
            
            # Get all blog ideas
            blog_ideas = await self.storage.get_blog_ideas(analysis_id, user_id)
            
            if not blog_ideas:
                return {
                    "analysis_id": analysis_id,
                    "status": "no_ideas",
                    "message": "No blog ideas found for this analysis"
                }
            
            # Check scoring status
            total_ideas = len(blog_ideas)
            ideas_missing_scores = 0
            ideas_with_zero_scores = 0
            
            for idea in blog_ideas:
                overall_score = idea.get("overall_quality_score", 0)
                viral_score = idea.get("viral_potential_score", 0)
                seo_score = idea.get("seo_optimization_score", 0)
                
                if overall_score == 0 or viral_score == 0 or seo_score == 0:
                    ideas_missing_scores += 1
                
                if overall_score == 0:
                    ideas_with_zero_scores += 1
            
            diagnosis = {
                "analysis_id": analysis_id,
                "total_ideas": total_ideas,
                "ideas_missing_scores": ideas_missing_scores,
                "ideas_with_zero_scores": ideas_with_zero_scores,
                "score_coverage_percentage": round(((total_ideas - ideas_missing_scores) / total_ideas) * 100, 1),
                "needs_fixing": ideas_missing_scores > 0,
                "diagnosis_timestamp": datetime.now().isoformat()
            }
            
            if diagnosis["needs_fixing"]:
                logger.warning(f"⚠️ Analysis {analysis_id} has {ideas_missing_scores}/{total_ideas} ideas with missing scores")
            else:
                logger.info(f"✅ Analysis {analysis_id} has all scores present")
            
            return diagnosis
            
        except Exception as e:
            logger.error(f"❌ Failed to diagnose analysis {analysis_id}: {e}")
            return {
                "analysis_id": analysis_id,
                "status": "error",
                "error": str(e)
            }
    
    async def fix_missing_scores(self, analysis_id: str, user_id: str) -> Dict[str, Any]:
        """Fix missing scores for all ideas in an analysis"""
        
        logger.info(f"🔧 Fixing missing scores for analysis: {analysis_id}")
        
        try:
            self.storage.set_user_context(user_id)
            
            # Get all blog ideas
            blog_ideas = await self.storage.get_blog_ideas(analysis_id, user_id)
            
            if not blog_ideas:
                return {
                    "success": False,
                    "error": "No blog ideas found for this analysis"
                }
            
            # Process each idea that needs fixing
            fixed_ideas = []
            skipped_ideas = 0
            
            for idea in blog_ideas:
                # Check if idea needs score fixing
                overall_score = idea.get("overall_quality_score", 0)
                if overall_score > 0:
                    skipped_ideas += 1
                    continue  # Skip ideas that already have scores
                
                try:
                    # Calculate all scores
                    viral_score = self.calculate_viral_potential_score(idea)
                    seo_score = self.calculate_seo_optimization_score(idea)
                    audience_score = self.calculate_audience_alignment_score(idea)
                    feasibility_score = self.calculate_content_feasibility_score(idea)
                    business_score = self.calculate_business_impact_score(idea)
                    
                    # Calculate overall score
                    overall_score = (
                        viral_score * 0.25 +
                        seo_score * 0.25 +
                        audience_score * 0.20 +
                        feasibility_score * 0.15 +
                        business_score * 0.15
                    )
                    
                    # Prepare update data
                    update_data = {
                        "id": idea["id"],
                        "viral_potential_score": viral_score,
                        "seo_optimization_score": seo_score,
                        "audience_alignment_score": audience_score,
                        "content_feasibility_score": feasibility_score,
                        "business_impact_score": business_score,
                        "overall_quality_score": int(overall_score)
                    }
                    
                    fixed_ideas.append(update_data)
                    
                    logger.info(f"📊 Calculated scores for '{idea['title']}': Overall={int(overall_score)}")
                    
                except Exception as e:
                    logger.warning(f"Failed to calculate scores for idea {idea.get('id')}: {e}")
            
            # Bulk update the scores
            if fixed_ideas:
                updated_count = await self.storage.bulk_update_blog_ideas(fixed_ideas, user_id)
                
                logger.info(f"✅ Fixed scores for {updated_count} ideas (skipped {skipped_ideas} that already had scores)")
                
                return {
                    "success": True,
                    "analysis_id": analysis_id,
                    "total_ideas": len(blog_ideas),
                    "ideas_fixed": updated_count,
                    "ideas_skipped": skipped_ideas,
                    "fix_timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "message": "No ideas needed score fixing",
                    "ideas_skipped": skipped_ideas
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to fix scores: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def fix_all_user_analyses(self, user_id: str) -> Dict[str, Any]:
        """Fix scores for all analyses for a user"""
        
        logger.info(f"🔧 Fixing scores for all analyses for user: {user_id}")
        
        try:
            self.storage.set_user_context(user_id)
            
            # Get all blog generation results for user
            all_results = await self.storage.get_all_blog_generation_results(user_id, limit=50)
            
            if not all_results:
                return {
                    "success": True,
                    "message": "No analyses found for user",
                    "user_id": user_id
                }
            
            # Process each analysis
            total_fixed = 0
            analyses_processed = 0
            
            for result in all_results:
                analysis_id = result.get("trend_analysis_id")
                if not analysis_id:
                    continue
                
                # Diagnose first
                diagnosis = await self.diagnose_analysis(analysis_id, user_id)
                
                if diagnosis.get("needs_fixing"):
                    # Fix the scores
                    fix_result = await self.fix_missing_scores(analysis_id, user_id)
                    
                    if fix_result.get("success"):
                        total_fixed += fix_result.get("ideas_fixed", 0)
                        analyses_processed += 1
                        logger.info(f"✅ Fixed {fix_result.get('ideas_fixed', 0)} ideas in analysis {analysis_id}")
                    else:
                        logger.warning(f"⚠️ Failed to fix analysis {analysis_id}: {fix_result.get('error')}")
            
            return {
                "success": True,
                "user_id": user_id,
                "total_analyses_found": len(all_results),
                "analyses_processed": analyses_processed,
                "total_ideas_fixed": total_fixed,
                "fix_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to fix all user analyses: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================================
# CLI INTERFACE
# ============================================================================

async def main():
    """Main CLI interface"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix missing scores in Phase 2 blog ideas")
    parser.add_argument('--user-id', required=True, help='User ID to fix scores for')
    parser.add_argument('--analysis-id', help='Specific analysis ID to fix (optional)')
    parser.add_argument('--diagnose-only', action='store_true', help='Only diagnose, don\'t fix')
    
    args = parser.parse_args()
    
    fixer = BlogIdeaScoreFixer()
    
    try:
        if args.analysis_id:
            # Fix specific analysis
            logger.info(f"🎯 Processing specific analysis: {args.analysis_id}")
            
            if args.diagnose_only:
                result = await fixer.diagnose_analysis(args.analysis_id, args.user_id)
                print(f"\n📊 Diagnosis Results:")
                print(f"Analysis ID: {result.get('analysis_id')}")
                print(f"Total Ideas: {result.get('total_ideas', 0)}")
                print(f"Ideas Missing Scores: {result.get('ideas_missing_scores', 0)}")
                print(f"Score Coverage: {result.get('score_coverage_percentage', 0)}%")
                print(f"Needs Fixing: {result.get('needs_fixing', False)}")
            else:
                diagnosis = await fixer.diagnose_analysis(args.analysis_id, args.user_id)
                
                if diagnosis.get("needs_fixing"):
                    result = await fixer.fix_missing_scores(args.analysis_id, args.user_id)
                    
                    if result.get("success"):
                        print(f"\n✅ Successfully fixed scores!")
                        print(f"Ideas Fixed: {result.get('ideas_fixed', 0)}")
                        print(f"Ideas Skipped: {result.get('ideas_skipped', 0)}")
                    else:
                        print(f"\n❌ Failed to fix scores: {result.get('error')}")
                else:
                    print(f"\n✅ Analysis {args.analysis_id} doesn't need fixing - all scores are present")
        
        else:
            # Fix all analyses for user
            logger.info(f"🔧 Processing all analyses for user: {args.user_id}")
            
            result = await fixer.fix_all_user_analyses(args.user_id)
            
            if result.get("success"):
                print(f"\n✅ Successfully processed all analyses!")
                print(f"Total Analyses Found: {result.get('total_analyses_found', 0)}")
                print(f"Analyses Processed: {result.get('analyses_processed', 0)}")
                print(f"Total Ideas Fixed: {result.get('total_ideas_fixed', 0)}")
            else:
                print(f"\n❌ Failed to process analyses: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        print(f"\n❌ Script failed: {e}")


if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    print("🔧 Phase 2 Score Fixer")
    print("=" * 50)
    print("This script will fix missing scores in your blog ideas.")
    print("Usage examples:")
    print("  python phase2_fix_script.py --user-id your-user-id")
    print("  python phase2_fix_script.py --user-id your-user-id --analysis-id specific-analysis")
    print("  python phase2_fix_script.py --user-id your-user-id --diagnose-only")
    print("")
    
    asyncio.run(main())