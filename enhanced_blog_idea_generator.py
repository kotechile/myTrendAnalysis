#!/usr/bin/env python3
"""
Enhanced Blog Idea Generator with Automatic Keyword Modifier Integration
Automatically adds non-niche specific modifiers to blog ideas during generation
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

# Import existing components
from blog_idea_generator import BlogIdeaGenerationEngine
from keyword_modifier_enhancer import KeywordModifierEnhancer
from auto_modifier_integration import AutoModifierIntegrator

class EnhancedBlogIdeaGenerator(BlogIdeaGenerationEngine):
    """
    Enhanced blog idea generator with automatic keyword modifier enhancement
    Automatically adds modifier keywords to blog ideas during generation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.modifier_enhancer = KeywordModifierEnhancer()
        self.auto_integrator = AutoModifierIntegrator()
        self.logger = logging.getLogger(__name__)
    
    async def generate_enhanced_blog_ideas(
        self,
        analysis_id: str,
        user_id: str,
        llm_config: Dict[str, Any],
        generation_config: Dict[str, Any] = None,
        linkup_api_key: Optional[str] = None,
        include_modifiers: bool = False
    ) -> Dict[str, Any]:
        """
        Generate blog ideas with context-aware keyword generation only
        
        Args:
            analysis_id: Phase 1 analysis ID
            user_id: User identifier
            llm_config: LLM configuration
            generation_config: Generation parameters
            linkup_api_key: Optional Linkup API key
            include_modifiers: Whether to automatically add modifier keywords
        
        Returns:
            Enhanced blog ideas with modifier keywords ready for keyword tools
        """
        
        self.logger.info(f"🚀 Starting enhanced blog idea generation for analysis: {analysis_id}")
        
        try:
            # Step 1: Generate regular blog ideas using existing engine
            self.logger.info("💡 Generating blog ideas...")
            base_result = await self.generate_comprehensive_blog_ideas(
                analysis_id=analysis_id,
                user_id=user_id,
                llm_config=llm_config,
                generation_config=generation_config,
                linkup_api_key=linkup_api_key
            )
            
            if not include_modifiers:
                self.logger.info("📋 Returning base ideas without modifiers")
                return base_result
            
            # Step 2: Automatically enhance with modifier keywords
            self.logger.info("🔍 Enhancing ideas with keyword modifiers...")
            
            # Convert blog ideas to format compatible with auto integrator
            blog_ideas_for_enhancement = []
            for idea in base_result.get('blog_ideas', []):
                enhanced_idea = {
                    'id': str(uuid.uuid4()),
                    'title': idea.get('title', ''),
                    'description': idea.get('description', ''),
                    'content_format': idea.get('content_format', 'blog_post'),
                    'primary_keywords': idea.get('primary_keywords', []),
                    'secondary_keywords': idea.get('secondary_keywords', []),
                    'difficulty_level': idea.get('difficulty_level', 'intermediate'),
                    'overall_quality_score': idea.get('overall_quality_score', 70)
                }
                blog_ideas_for_enhancement.append(enhanced_idea)
            
            # Step 3: Apply automatic modifier enhancement
            enhanced_ideas = self.auto_integrator.enhance_blog_ideas_with_modifiers(
                blog_ideas_for_enhancement
            )
            
            # Step 4: Generate CSV export for keyword tools
            csv_data = self.auto_integrator.generate_keyword_export_csv(enhanced_ideas)
            
            # Step 5: Update result with enhanced data
            enhanced_result = base_result.copy()
            enhanced_result['blog_ideas'] = enhanced_ideas
            enhanced_result['keyword_enhancement'] = {
                'total_enhanced_ideas': len(enhanced_ideas),
                'total_keyword_opportunities': sum(idea.get('total_keyword_opportunities', 0) for idea in enhanced_ideas),
                'modifier_categories_used': list(set().union(*[idea.get('modifier_categories_used', []) for idea in enhanced_ideas])),
                'csv_ready_for_tools': True,
                'csv_filename': f'enhanced_keywords_{analysis_id}.csv'
            }
            
            # Step 6: Save CSV file
            csv_filename = f'enhanced_keywords_{analysis_id}.csv'
            with open(csv_filename, 'w') as f:
                f.write(csv_data)
            
            self.logger.info(f"✅ Enhanced blog idea generation completed: {len(enhanced_ideas)} ideas")
            self.logger.info(f"📊 Generated {len(csv_data.splitlines())-1} keywords in {csv_filename}")
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced blog idea generation failed: {e}")
            # Fallback to base generation
            return await self.generate_comprehensive_blog_ideas(
                analysis_id=analysis_id,
                user_id=user_id,
                llm_config=llm_config,
                generation_config=generation_config,
                linkup_api_key=linkup_api_key
            )

class KeywordWorkflowManager:
    """
    Manages the complete workflow from blog idea generation to keyword tool integration
    """
    
    def __init__(self):
        self.enhanced_generator = EnhancedBlogIdeaGenerator()
        self.logger = logging.getLogger(__name__)
    
    async def complete_workflow(
        self,
        analysis_id: str,
        user_id: str,
        llm_config: Dict[str, Any],
        generation_config: Dict[str, Any] = None,
        linkup_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: blog ideas → keyword enhancement → tool-ready exports
        
        Returns:
            Complete workflow results including tool-ready exports
        """
        
        self.logger.info(f"🔄 Starting complete workflow for analysis: {analysis_id}")
        
        # Generate enhanced blog ideas
        result = await self.enhanced_generator.generate_enhanced_blog_ideas(
            analysis_id=analysis_id,
            user_id=user_id,
            llm_config=llm_config,
            generation_config=generation_config,
            linkup_api_key=linkup_api_key,
            include_modifiers=True
        )
        
        # Prepare tool-specific exports
        workflow_result = {
            'enhanced_blog_ideas': result.get('blog_ideas', []),
            'content_calendar': result.get('content_calendar', {}),
            'strategic_insights': result.get('strategic_insights', {}),
            'success_predictions': result.get('success_predictions', {}),
            'keyword_enhancement': result.get('keyword_enhancement', {}),
            'tool_exports': self._prepare_tool_exports(result),
            'next_steps': self._generate_next_steps(result)
        }
        
        self.logger.info("✅ Complete workflow finished successfully")
        return workflow_result
    
    def _prepare_tool_exports(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare exports for different keyword tools"""
        
        csv_filename = result.get('keyword_enhancement', {}).get('csv_filename', 'enhanced_keywords.csv')
        
        return {
            'ahrefs': {
                'filename': csv_filename,
                'format': 'csv',
                'columns': ['Keyword', 'Source_Idea', 'Content_Type', 'Search_Intent'],
                'instructions': 'Upload to Ahrefs Keywords Explorer > Import Keywords'
            },
            'semrush': {
                'filename': csv_filename,
                'format': 'csv', 
                'columns': ['Keyword', 'Source_Idea', 'Content_Type', 'Search_Intent'],
                'instructions': 'Upload to SEMrush Keyword Magic Tool > Import Keywords'
            },
            'moz': {
                'filename': csv_filename,
                'format': 'csv',
                'columns': ['Keyword', 'Source_Idea', 'Content_Type', 'Search_Intent'],
                'instructions': 'Upload to Moz Keyword Explorer > Import Keywords'
            }
        }
    
    def _generate_next_steps(self, result: Dict[str, Any]) -> List[str]:
        """Generate next steps for user workflow"""
        
        return [
            "1. Upload the generated CSV file to your preferred keyword tool (Ahrefs, SEMrush, or Moz)",
            "2. Filter keywords based on your criteria (volume > 100, difficulty < 50)",
            "3. Export the filtered results back to CSV",
            "4. Use the /api/v2/keyword-research/upload endpoint to process keyword data",
            "5. Review enhanced blog ideas and their associated keyword opportunities",
            "6. Begin content creation using the provided content calendar"
        ]

# API wrapper for easy integration
def create_enhanced_workflow_api():
    """Create API endpoints for enhanced workflow"""
    
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    app = FastAPI(title="Enhanced Blog Idea Generator", version="2.0")
    workflow_manager = KeywordWorkflowManager()
    
    class GenerationRequest(BaseModel):
        analysis_id: str
        user_id: str
        llm_config: Dict[str, Any]
        generation_config: Optional[Dict[str, Any]] = None
        linkup_api_key: Optional[str] = None
        include_modifiers: bool = True
    
    @app.post("/api/v2/blog-ideas/generate-enhanced")
    async def generate_enhanced_blog_ideas(request: GenerationRequest):
        """Generate enhanced blog ideas with automatic keyword modifiers"""
        try:
            result = await workflow_manager.complete_workflow(
                analysis_id=request.analysis_id,
                user_id=request.user_id,
                llm_config=request.llm_config,
                generation_config=request.generation_config,
                linkup_api_key=request.linkup_api_key
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v2/blog-ideas/download-csv/{analysis_id}")
    async def download_keyword_csv(analysis_id: str):
        """Download CSV file with keyword suggestions for keyword tools"""
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

# Usage example
async def main():
    """Example usage of enhanced blog idea generator"""
    
    import os
    
    # Test configuration
    llm_config = {
        'provider': 'openai',
        'model': 'gpt-4o-mini',
        'api_key': os.getenv('OPENAI_API_KEY')
    }
    
    if not llm_config['api_key']:
        print("❌ OPENAI_API_KEY environment variable not set")
        return
    
    # Initialize workflow manager
    workflow = KeywordWorkflowManager()
    
    # Test with sample data
    test_analysis_id = "test-analysis-2024"
    test_user_id = "test-user-001"
    
    print("🚀 Testing enhanced blog idea generation...")
    
    try:
        result = await workflow.complete_workflow(
            analysis_id=test_analysis_id,
            user_id=test_user_id,
            llm_config=llm_config
        )
        
        print("✅ Enhanced generation completed!")
        print(f"📊 Generated {len(result['enhanced_blog_ideas'])} enhanced blog ideas")
        print(f"🔍 Created {result['keyword_enhancement']['total_keyword_opportunities']} keyword opportunities")
        print(f"💾 CSV file saved: {result['keyword_enhancement']['csv_filename']}")
        
        # Show sample results
        print("\n🎯 Top 3 Enhanced Blog Ideas:")
        for i, idea in enumerate(result['enhanced_blog_ideas'][:3], 1):
            print(f"{i}. {idea.get('title', '')}")
            enhanced_keywords = idea.get('enhanced_primary_keywords', [])[:3]
            print(f"   Keywords: {', '.join(enhanced_keywords)}")
        
        print("\n📋 Next Steps:")
        for step in result['next_steps']:
            print(f"   {step}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    # Run async main
    asyncio.run(main())