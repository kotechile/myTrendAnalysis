#!/usr/bin/env python3
"""
Supabase storage for affiliate research data with deduplication - UPDATED
Uses working_supabase_integration pattern for compatibility
"""

import asyncio
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import hashlib
import logging
import json

# Import the working pattern
from working_supabase_integration import RLSSupabaseStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseAffiliateStorage(RLSSupabaseStorage):
    """Handles storage of affiliate research data using the working RLS pattern"""
    
    def __init__(self, user_id: Optional[str] = None):
        super().__init__(user_id)
        logger.info("✅ Affiliate storage initialized with RLS pattern")
        
    async def store_affiliate_research(self, 
                                     topic: str,
                                     user_id: str,
                                     research_data: Dict[str, Any],
                                     analysis_id: str = None) -> str:
        """Store complete affiliate research results with all relationships"""
        
        if not analysis_id:
            analysis_id = str(uuid.uuid4())
        
        # Set user context for RLS
        self.set_user_context(user_id)
        
        try:
            logger.info(f"💾 Starting complete affiliate research storage for topic: {topic}")
            logger.info(f"📊 Research data keys: {list(research_data.keys())}")
            logger.info(f"📈 Programs count: {len(research_data.get('programs', []))}")
            logger.info(f"💰 Analysis: {research_data.get('profitability_analysis', {}).get('score', 'N/A')}")
            
            # 1. Store research session
            logger.info("📝 Step 1: Creating research session...")
            session_id = await self._store_research_session(analysis_id, topic, user_id, research_data)
            logger.info(f"✅ Research session created: {session_id}")
            
            # 2. Store programs and create links
            logger.info("🔄 Step 2: Storing programs and creating links...")
            stored_programs = 0
            linked_programs = 0
            
            for program in research_data.get('programs', []):
                program_id = await self._store_or_update_program(program, user_id)
                if program_id:
                    stored_programs += 1
                    # Link program to session
                    await self._link_program_to_session(session_id, program_id, program)
                    linked_programs += 1
                    logger.debug(f"🔗 Linked program {program_id} to session {session_id}")
            
            logger.info(f"✅ Stored {stored_programs} programs, linked {linked_programs} to session")
            
            # 3. Store profitability analysis
            logger.info("📊 Step 3: Storing profitability analysis...")
            await self._store_profitability_analysis(session_id, research_data.get('profitability_analysis', {}))
            logger.info("✅ Profitability analysis stored")
            
            # 4. Verify storage
            logger.info("🔍 Step 4: Verifying storage...")
            verification = await self.get_affiliate_research_by_topic(topic, user_id)
            if verification:
                logger.info(f"✅ Verification complete - session: {verification['session']['id']}")
                logger.info(f"✅ Programs: {len(verification['programs'])}")
                logger.info(f"✅ Analysis: {verification['analysis'] is not None}")
            else:
                logger.warning("⚠️ Verification failed - data not found")
            
            return analysis_id
            
        except Exception as e:
            logger.error(f"❌ Error storing affiliate research: {e}", exc_info=True)
            return str(e)
    
    async def _store_research_session(self, 
                                    analysis_id: str, 
                                    topic: str, 
                                    user_id: str, 
                                    research_data: Dict[str, Any]) -> str:
        """Store research session record using RLS pattern"""
        
        # Use only the columns that actually exist in the table
        session_data = {
            'id': analysis_id,
            'user_id': user_id,  # Use API's user_id - should exist in user_profile
            'topic': topic,
            'subtopics': json.dumps(research_data.get('subtopics', [])),
            'total_programs': research_data.get('total_programs', 0),
            'profitability_score': research_data['profitability_analysis'].get('score', 0),
            'profitability_level': research_data['profitability_analysis'].get('level', 'unknown'),
            'research_timestamp': research_data.get('research_timestamp', datetime.now().isoformat()),
            'source': research_data.get('source', 'linkup_api'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        result = self._execute_query('POST', 'affiliate_research_sessions', session_data)
        
        if result['success']:
            logger.info(f"✅ Research session created with user_id from API: {analysis_id}")
            return analysis_id
        else:
            raise Exception(f"Failed to create research session: {result.get('error')}")
    
    async def _store_or_update_program(self, program: Dict[str, Any], user_id: str) -> Optional[str]:
        """Store or update affiliate program with deduplication using RLS pattern"""
        
        # Generate unique identifier for deduplication
        program_hash = self._generate_program_hash(program)
        
        # Check if program already exists
        existing = self._execute_query('GET', f'affiliate_programs?program_hash=eq.{program_hash}&select=id')
        
        program_data = {
            'program_hash': program_hash,
            'network': program.get('network', 'unknown'),
            'program_name': program.get('program_name', ''),
            'description': program.get('description', ''),
            'commission_rate': program.get('commission_rate', 0),
            'commission_amount': program.get('commission_amount', 0),
            'cookie_duration': program.get('cookie_duration', ''),
            'program_url': program.get('program_url', ''),
            'approval_required': bool(program.get('approval_required', False)),
            'promotional_materials': json.dumps(program.get('promotional_materials', [])),
            'extraction_confidence': program.get('extraction_confidence', 0),
            'source_url': program.get('source_url', ''),
            'last_updated': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if existing['success'] and existing['data']:
            # Update existing program
            program_id = existing['data'][0]['id']
            result = self._execute_query('PATCH', f'affiliate_programs?id=eq.{program_id}', program_data)
            if not result['success']:
                logger.warning(f"⚠️ Failed to update program: {result.get('error')}")
                return None
        else:
            # Create new program
            program_id = str(uuid.uuid4())
            program_data['id'] = program_id
            result = self._execute_query('POST', 'affiliate_programs', program_data)
            if not result['success']:
                logger.warning(f"⚠️ Failed to create program: {result.get('error')}")
                return None
        
        return program_id
    
    def _generate_program_hash(self, program: Dict[str, Any]) -> str:
        """Generate unique hash for program deduplication"""
        
        # Create unique identifier from network + program name + URL
        identifier = f"{program.get('network', '')}_{program.get('program_name', '')}_{program.get('program_url', '')}"
        return hashlib.md5(identifier.encode()).hexdigest()
    
    async def _link_program_to_session(self, 
                                     session_id: str, 
                                     program_id: str, 
                                     program: Dict[str, Any]):
        """Link program to research session with relationship data using RLS pattern"""
        
        link_data = {
            'id': str(uuid.uuid4()),
            'research_session_id': session_id,
            'affiliate_program_id': program_id,
            'subtopic': program.get('subtopic', ''),
            'relevance_score': program.get('extraction_confidence', 0),
            'created_at': datetime.now().isoformat()
        }
        
        result = self._execute_query('POST', 'affiliate_session_programs', link_data)
        if not result['success']:
            logger.warning(f"⚠️ Failed to link program to session: {result.get('error')}")
    
    async def _store_program_simple(self, program: Dict[str, Any]) -> Optional[str]:
        """Store affiliate program without user constraints"""
        
        # Generate unique identifier for deduplication
        program_hash = self._generate_program_hash(program)
        
        # Check if program already exists
        existing = self._execute_query('GET', f'affiliate_programs?program_hash=eq.{program_hash}&select=id')
        
        program_data = {
            'program_hash': program_hash,
            'network': program.get('network', 'unknown'),
            'program_name': program.get('program_name', ''),
            'description': program.get('description', ''),
            'commission_rate': program.get('commission_rate', 0),
            'commission_amount': program.get('commission_amount', 0),
            'cookie_duration': program.get('cookie_duration', ''),
            'program_url': program.get('program_url', ''),
            'approval_required': bool(program.get('approval_required', False)),
            'promotional_materials': json.dumps(program.get('promotional_materials', [])),
            'extraction_confidence': program.get('extraction_confidence', 0),
            'source_url': program.get('source_url', ''),
            'last_updated': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if existing['success'] and existing['data']:
            # Update existing program
            program_id = existing['data'][0]['id']
            result = self._execute_query('PATCH', f'affiliate_programs?id=eq.{program_id}', program_data)
            if not result['success']:
                logger.warning(f"⚠️ Failed to update program: {result.get('error')}")
                return None
        else:
            # Create new program
            program_id = str(uuid.uuid4())
            program_data['id'] = program_id
            result = self._execute_query('POST', 'affiliate_programs', program_data)
            if not result['success']:
                logger.warning(f"⚠️ Failed to create program: {result.get('error')}")
                return None
        
        return program_id
    
    async def _store_profitability_analysis(self, 
                                          session_id: str, 
                                          analysis: Dict[str, Any]):
        """Store profitability analysis data using RLS pattern"""
        
        analysis_data = {
            'id': str(uuid.uuid4()),
            'research_session_id': session_id,
            'profitability_score': analysis.get('score', 0),
            'profitability_level': analysis.get('level', 'unknown'),
            'total_programs': analysis.get('total_programs', 0),
            'avg_commission_rate': analysis.get('avg_commission_rate', 0),
            'avg_commission_amount': analysis.get('avg_commission_amount', 0),
            'high_value_programs': analysis.get('high_value_programs', 0),
            'networks_represented': analysis.get('networks_represented', 0),
            'subtopics_covered': analysis.get('subtopics_covered', 0),
            'created_at': datetime.now().isoformat()
        }
        
        result = self._execute_query('POST', 'affiliate_profitability_analysis', analysis_data)
        if not result['success']:
            logger.warning(f"⚠️ Failed to store profitability analysis: {result.get('error')}")
    
    async def get_affiliate_research_by_topic(self, topic: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve existing affiliate research for a topic using RLS pattern"""
        
        # Set user context for RLS
        self.set_user_context(user_id)
        
        try:
            # Get research session with user_id from user_profile
            session_response = self._execute_query(
                'GET', 
                f'affiliate_research_sessions?topic=eq.{topic}&user_id=eq.{user_id}&select=*&order=created_at.desc&limit=1'
            )
            
            if not session_response['success'] or not session_response['data']:
                return None
            
            session = session_response['data'][0]
            
            # Get programs for this session
            programs_response = self._execute_query(
                'GET',
                f'affiliate_session_programs?research_session_id=eq.{session["id"]}&select=*,affiliate_programs(*)'
            )
            
            # Get profitability analysis
            analysis_response = self._execute_query(
                'GET',
                f'affiliate_profitability_analysis?research_session_id=eq.{session["id"]}&select=*'
            )
            
            # Parse JSON fields
            programs = []
            if programs_response['success'] and programs_response['data']:
                for p in programs_response['data']:
                    program = p['affiliate_programs']
                    # Parse JSON fields
                    if program.get('promotional_materials'):
                        try:
                            program['promotional_materials'] = json.loads(program['promotional_materials'])
                        except (json.JSONDecodeError, ValueError):
                            program['promotional_materials'] = []
                    programs.append(program)
            
            return {
                'session': session,
                'programs': programs,
                'analysis': analysis_response['data'][0] if analysis_response['success'] and analysis_response['data'] else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error retrieving affiliate research: {e}")
            return None
    
    async def get_recent_research(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent affiliate research for a user using RLS pattern"""
        
        # Set user context for RLS
        self.set_user_context(user_id)
        
        try:
            cutoff_date = datetime.now().isoformat()
            
            response = self._execute_query(
                'GET',
                f'affiliate_research_sessions?user_id=eq.{user_id}&select=*&order=created_at.desc'
            )
            
            if response['success']:
                return response['data']
            else:
                logger.warning(f"⚠️ Failed to get recent research: {response.get('error')}")
                return []
            
        except Exception as e:
            logger.error(f"❌ Error retrieving recent research: {e}")
            return []
    
    async def delete_old_research(self, user_id: str, days_to_keep: int = 30) -> int:
        """Delete old research data to manage storage using RLS pattern"""
        
        # Set user context for RLS
        self.set_user_context(user_id)
        
        try:
            cutoff_date = datetime.now().isoformat()
            
            # Get old sessions
            old_sessions = self._execute_query(
                'GET',
                f'affiliate_research_sessions?user_id=eq.{user_id}&select=id'
            )
            
            if not old_sessions['success']:
                logger.warning(f"⚠️ Failed to get old sessions: {old_sessions.get('error')}")
                return 0
            
            session_ids = [s['id'] for s in old_sessions['data']]
            
            if session_ids:
                # Delete related data with user context
                for session_id in session_ids:
                    # Delete session programs
                    self._execute_query(
                        'DELETE',
                        f'affiliate_session_programs?research_session_id=eq.{session_id}'
                    )
                    
                    # Delete profitability analysis
                    self._execute_query(
                        'DELETE',
                        f'affiliate_profitability_analysis?research_session_id=eq.{session_id}'
                    )
                    
                    # Delete session
                    self._execute_query(
                        'DELETE',
                        f'affiliate_research_sessions?id=eq.{session_id}&user_id=eq.{user_id}'
                    )
            
            deleted_count = len(session_ids)
            logger.info(f"✅ Deleted {deleted_count} old research sessions")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error deleting old research: {e}")
            return 0

# Global instance
affiliate_storage = SupabaseAffiliateStorage()