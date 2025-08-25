#!/usr/bin/env python3
"""
Seamless Integration Script for Existing Blog Idea Generation Workflow
Automatically adds modifier keywords without disrupting existing workflow
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from enhanced_blog_idea_generator import EnhancedBlogIdeaGenerator, KeywordWorkflowManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeamlessIntegration:
    """
    Provides seamless integration with existing blog idea generation workflow
    Automatically enhances blog ideas with keyword modifiers without changing API
    """
    
    def __init__(self):
        self.workflow_manager = KeywordWorkflowManager()
        logger.info("🔄 Seamless integration initialized")
    
    async def generate_blog_ideas_with_automatic_modifiers(
        self,
        analysis_id: str,
        user_id: str,
        llm_config: Dict[str, Any],
        generation_config: Dict[str, Any] = None,
        linkup_api_key: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Drop-in replacement for existing blog idea generation
        
        This method has the exact same signature as the original generate_comprehensive_blog_ideas
        but automatically adds keyword modifiers. No changes needed in calling code.
        
        Args:
            Same as original generate_comprehensive_blog_ideas method
            
        Returns:
            Enhanced results with keyword modifiers automatically added
        """
        
        logger.info(f"🚀 Seamless enhancement starting for analysis: {analysis_id}")
        
        # Use the enhanced workflow which includes automatic modifiers
        result = await self.workflow_manager.complete_workflow(
            analysis_id=analysis_id,
            user_id=user_id,
            llm_config=llm_config,
            generation_config=generation_config,
            linkup_api_key=linkup_api_key
        )
        
        # Map to original response format for backward compatibility
        original_format_result = {
            'blog_ideas': result['enhanced_blog_ideas'],
            'content_calendar': result['content_calendar'],
            'strategic_insights': result['strategic_insights'],
            'success_predictions': result['success_predictions'],
            'generation_metadata': result.get('generation_metadata', {}),
            'keyword_enhancement': result.get('keyword_enhancement', {}),
            'tool_exports': result.get('tool_exports', {}),
            'enhanced_keywords_csv': result.get('keyword_enhancement', {}).get('csv_filename')
        }
        
        logger.info(f"✅ Seamless enhancement complete: {len(original_format_result['blog_ideas'])} ideas")
        
        return original_format_result
    
    def get_workflow_summary(self, result: Dict[str, Any]) -> str:
        """Generate human-readable summary of enhancement results"""
        
        summary_parts = []
        
        # Basic stats
        ideas_count = len(result.get('blog_ideas', []))
        enhancement_data = result.get('keyword_enhancement', {})
        total_keywords = enhancement_data.get('total_keyword_opportunities', 0)
        
        summary_parts.append(f"📊 Generated {ideas_count} blog ideas")
        summary_parts.append(f"🔍 Created {total_keywords} keyword opportunities")
        
        # Tool readiness
        if enhancement_data.get('csv_ready_for_tools'):
            csv_file = enhancement_data.get('csv_filename', 'enhanced_keywords.csv')
            summary_parts.append(f"💾 CSV ready: {csv_file}")
        
        # Modifier categories
        categories = enhancement_data.get('modifier_categories_used', [])
        if categories:
            summary_parts.append(f"🎯 Used categories: {', '.join(categories)}")
        
        # Next steps
        tool_exports = result.get('tool_exports', {})
        if tool_exports:
            tools_ready = list(tool_exports.keys())
            summary_parts.append(f"🛠️ Ready for: {', '.join(tools_ready).upper()}")
        
        return "\n".join(summary_parts)

# Single function for drop-in replacement
def create_seamless_integration():
    """
    Create a seamless integration instance
    
    Usage:
        # Replace this in your existing code:
        # from blog_idea_generator import BlogIdeaGenerationEngine
        # engine = BlogIdeaGenerationEngine()
        # result = await engine.generate_comprehensive_blog_ideas(...)
        
        # With this:
        from integrate_with_existing_system import create_seamless_integration
        engine = create_seamless_integration()
        result = await engine.generate_blog_ideas_with_automatic_modifiers(...)
        # Same parameters, enhanced results!
    """
    return SeamlessIntegration()

# Convenience function for direct usage
async def run_enhanced_generation(
    analysis_id: str,
    user_id: str,
    llm_config: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Quick function to run enhanced generation with automatic modifiers
    
    Args:
        analysis_id: Phase 1 analysis ID
        user_id: User identifier
        llm_config: LLM configuration dict
        **kwargs: Additional parameters passed to generation
    
    Returns:
        Enhanced blog ideas with keyword modifiers ready for tools
    """
    
    integration = create_seamless_integration()
    return await integration.generate_blog_ideas_with_automatic_modifiers(
        analysis_id=analysis_id,
        user_id=user_id,
        llm_config=llm_config,
        **kwargs
    )

# API endpoint wrapper for existing systems
def enhance_existing_api():
    """
    Create API endpoints that enhance existing blog idea generation
    """
    
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    app = FastAPI(title="Enhanced Blog Idea API", version="2.0")
    integration = create_seamless_integration()
    
    class GenerationRequest(BaseModel):
        analysis_id: str
        user_id: str
        llm_config: Dict[str, Any]
        generation_config: Optional[Dict[str, Any]] = None
        linkup_api_key: Optional[str] = None
    
    @app.post("/api/v2/blog-ideas/generate")
    async def generate_blog_ideas(request: GenerationRequest):
        """Enhanced blog idea generation with automatic modifiers"""
        try:
            result = await integration.generate_blog_ideas_with_automatic_modifiers(
                analysis_id=request.analysis_id,
                user_id=request.user_id,
                llm_config=request.llm_config,
                generation_config=request.generation_config,
                linkup_api_key=request.linkup_api_key
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v2/blog-ideas/{analysis_id}/keywords")
    async def get_keyword_csv(analysis_id: str):
        """Download keyword CSV for external tools"""
        import os
        filename = f'enhanced_keywords_{analysis_id}.csv'
        if os.path.exists(filename):
            from fastapi.responses import FileResponse
            return FileResponse(
                filename,
                media_type='text/csv',
                filename=f'keywords_for_tools_{analysis_id}.csv'
            )
        else:
            raise HTTPException(status_code=404, detail="CSV file not found")
    
    return app

# Usage examples
async def demonstrate_integration():
    """Demonstrate seamless integration"""
    
    import os
    
    # Test configuration
    llm_config = {
        'provider': 'openai',
        'model': 'gpt-4o-mini',
        'api_key': os.getenv('OPENAI_API_KEY', 'your-api-key-here')
    }
    
    # Initialize seamless integration
    integration = create_seamless_integration()
    
    # This is exactly how you'd call your existing blog idea generator
    # No changes needed in your calling code
    
    print("🔄 Demonstrating seamless integration...")
    print("=" * 50)
    
    try:
        # Use the exact same method signature as before
        result = await integration.generate_blog_ideas_with_automatic_modifiers(
            analysis_id="demo-analysis-2024",
            user_id="demo-user-001",
            llm_config=llm_config,
            generation_config={"min_ideas": 15, "max_ideas": 25}
        )
        
        # Display results
        print("✅ Enhanced generation complete!")
        print(f"📊 {len(result['blog_ideas'])} blog ideas generated")
        
        # Show summary
        summary = integration.get_workflow_summary(result)
        print("\n📋 Workflow Summary:")
        print(summary)
        
        # Show sample enhanced keywords
        if result['blog_ideas']:
            sample_idea = result['blog_ideas'][0]
            enhanced_keywords = sample_idea.get('enhanced_primary_keywords', [])
            print(f"\n🎯 Sample enhanced keywords from first idea:")
            for keyword in enhanced_keywords[:5]:
                print(f"   • {keyword}")
        
        return result
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return None

async def main():
    """Main demonstration"""
    
    print("🚀 Enhanced Blog Idea Generation with Automatic Keyword Modifiers")
    print("This system automatically adds non-niche specific modifiers to your blog ideas")
    print("after they are generated, making them ready for keyword tools like Ahrefs and SEMrush")
    print()
    
    # Run demonstration
    await demonstrate_integration()
    
    print("\n✅ Integration ready!")
    print("\nUsage:")
    print("1. Replace your existing blog idea generator call with:")
    print("   from integrate_with_existing_system import create_seamless_integration")
    print("   engine = create_seamless_integration()")
    print("   result = await engine.generate_blog_ideas_with_automatic_modifiers(...)")
    print("\n2. Same parameters, enhanced results!")
    print("3. CSV files are automatically generated for keyword tools")

if __name__ == "__main__":
    asyncio.run(main())