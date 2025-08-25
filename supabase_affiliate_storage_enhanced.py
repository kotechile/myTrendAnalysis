#!/usr/bin/env python3
"""
Enhanced Supabase storage for affiliate research with reuse strategy
Implements database-first search with deduplication and linking
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

class EnhancedSupabaseAffiliateStorage(RLSSupabaseStorage):
    """Enhanced storage with database-first search and deduplication"""
    
    def __init__(self, user_id: Optional[str] = None):
        super().__init__(user_id)
        logger.info("✅ Enhanced affiliate storage initialized with reuse strategy")
    
    async def get_existing_affiliate_programs(
        self, 
        search_query: str, 
        user_id: str,
        match_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Find existing affiliate programs for a search query
        Uses fuzzy matching on search queries and program names
        """
        self.set_user_context(user_id)
        
        try:
            logger.info(f"🔍 Searching existing affiliate programs for: {search_query}")
            
            # Create search variations
            search_terms = search_query.lower().split()
            
            # Ensure user_id is proper UUID format
            user_uuid = self._ensure_uuid(user_id)
            
            # Search by exact match first using HTTP API
            encoded_query = search_query.replace(" ", "%20")
            exact_endpoint = f"affiliate_programs?user_id=eq.{user_uuid}&search_query=ilike.*{encoded_query}*&select=*"
            exact_match = self._execute_query('GET', exact_endpoint)
            
            programs = exact_match.get('data', []) if exact_match.get('success') else []
            
            # If no exact matches, search by keywords
            if not programs:
                # Use OR conditions for keyword search with proper format
                or_conditions = []
                for term in search_terms:
                    encoded_term = term.replace(" ", "%20")
                    or_conditions.append(f"search_query.ilike.*{encoded_term}*")
                
                if or_conditions:
                    keyword_endpoint = f"affiliate_programs?user_id=eq.{user_uuid}&or=({','.join(or_conditions)})&select=*"
                    keyword_results = self._execute_query('GET', keyword_endpoint)
                    programs = keyword_results.get('data', []) if keyword_results.get('success') else []
            
            logger.info(f"📊 Found {len(programs)} existing programs")
            return programs
            
        except Exception as e:
            logger.error(f"❌ Error finding existing programs: {e}")
            return []
    
    def _generate_program_hash(self, program_data: Dict[str, Any]) -> str:
        """Generate unique hash for program deduplication"""
        key_fields = [
            program_data.get('program_name', ''),
            program_data.get('company_name', ''),
            program_data.get('signup_url', '')
        ]
        key_string = '|'.join([str(f).lower().strip() for f in key_fields])
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _ensure_uuid(self, id_str: str) -> str:
        """Ensure proper UUID format"""
        try:
            # If it's already a UUID, return it
            uuid.UUID(id_str)
            return id_str
        except ValueError:
            # Convert short string to UUID by hashing and creating a deterministic UUID
            hash_obj = hashlib.md5(id_str.encode())
            return str(uuid.UUID(hash_obj.hexdigest()))
    
    async def store_affiliate_program_with_deduplication(
        self, 
        program_data: Dict[str, Any],
        search_query: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Store affiliate program with deduplication and search linking
        """
        self.set_user_context(user_id)
        
        try:
            # Generate program hash for deduplication
            program_hash = self._generate_program_hash(program_data)
            
            # Check if program already exists - ensure user_id is UUID format
            user_uuid = self._ensure_uuid(user_id)
            existing_endpoint = f"affiliate_programs?user_id=eq.{user_uuid}&program_hash=eq.{program_hash}&select=id"
            existing = self._execute_query('GET', existing_endpoint)
            
            if existing.get('success') and existing.get('data'):
                program_id = existing['data'][0]['id']
                logger.info(f"📋 Reusing existing program: {program_data.get('program_name')}")
                
                # Update search query to include new search terms
                update_data = {
                    'search_query': f"{search_query} | {program_data.get('search_query', '')}"
                }
                update_endpoint = f"affiliate_programs?id=eq.{program_id}"
                self._execute_query('PATCH', update_endpoint, update_data)
                
                return {'action': 'reused', 'program_id': program_id}
            
            # Store new program with hash - ensure proper UUID for id
            enriched_data = {
                **program_data,
                'id': self._ensure_uuid(str(uuid.uuid4())),  # Generate proper UUID
                'user_id': user_id,
                'search_query': search_query,
                'program_hash': program_hash,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self._execute_query('POST', 'affiliate_programs', enriched_data)
            
            if result.get('success') and result.get('data'):
                program_id = result['data'][0]['id']
                logger.info(f"✅ Stored new program: {program_data.get('program_name')}")
                return {'action': 'created', 'program_id': program_id}
            
            return {'action': 'failed', 'error': 'No data returned from insert'}
            
        except Exception as e:
            logger.error(f"❌ Error storing program: {e}")
            return {'action': 'failed', 'error': str(e)}
    
    async def store_affiliate_research_with_reuse(
        self, 
        topic: str,
        user_id: str,
        research_data: Dict[str, Any],
        analysis_id: str = None
    ) -> Dict[str, Any]:
        """
        Store affiliate research with database-first approach
        """
        if not analysis_id:
            analysis_id = str(uuid.uuid4())
        
        self.set_user_context(user_id)
        
        try:
            logger.info(f"🔄 Starting enhanced affiliate research storage for topic: {topic}")
            
            # 1. First, find existing programs
            existing_programs = await self.get_existing_affiliate_programs(topic, user_id)
            
            # 2. Process new programs with deduplication
            new_programs = []
            reused_programs = []
            
            for program in research_data.get('programs', []):
                result = await self.store_affiliate_program_with_deduplication(
                    program, topic, user_id
                )
                
                if result['action'] == 'reused':
                    reused_programs.append(result['program_id'])
                elif result['action'] == 'created':
                    new_programs.append(result['program_id'])
            
            # 3. Store research session with linking
            session_data = {
                'id': self._ensure_uuid(analysis_id),  # Ensure proper UUID format
                'user_id': self._ensure_uuid(user_id),
                'topic': topic,
                'existing_programs_count': len(existing_programs),
                'new_programs_count': len(new_programs),
                'reused_programs_count': len(reused_programs),
                'total_programs': len(existing_programs) + len(new_programs),
                'profitability_score': research_data.get('profitability_analysis', {}).get('score', 0),
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self._execute_query('POST', 'affiliate_research_sessions', session_data)
            
            # 4. Link programs to this research session
            # Ensure all program IDs are proper UUIDs
            existing_ids = [self._ensure_uuid(p['id']) for p in existing_programs]
            new_ids = [self._ensure_uuid(str(pid)) for pid in new_programs]  # Ensure UUID format
            all_program_ids = existing_ids + new_ids
            
            links_to_insert = []
            for program_id in all_program_ids:
                link_type = 'existing' if program_id in existing_ids else 'new'
                links_to_insert.append({
                    'id': self._ensure_uuid(str(uuid.uuid4())),  # Generate UUID for link ID
                    'research_session_id': analysis_id,
                    'program_id': program_id,
                    'link_type': link_type,
                    'created_at': datetime.utcnow().isoformat()
                })
            
            if links_to_insert:
                self._execute_query('POST', 'research_program_links', links_to_insert)
            
            logger.info(f"✅ Research session stored with {len(existing_programs)} existing, {len(new_programs)} new, {len(reused_programs)} reused programs")
            
            return {
                'analysis_id': analysis_id,
                'existing_programs': len(existing_programs),
                'new_programs': len(new_programs),
                'reused_programs': len(reused_programs),
                'total_programs': len(all_program_ids)
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced storage failed: {e}")
            return {'error': str(e)}
    
    async def get_affiliate_programs_by_topic(
        self, 
        topic: str, 
        user_id: str,
        include_reused: bool = True
    ) -> Dict[str, Any]:
        """
        Get all affiliate programs for a topic, including reused ones
        """
        self.set_user_context(user_id)
        
        try:
            # Get programs linked to this topic's research sessions using HTTP API
            user_uuid = self._ensure_uuid(user_id)
            encoded_topic = topic.replace(" ", "%20")
            endpoint = f"affiliate_programs?user_id=eq.{user_uuid}&search_query=ilike.*{encoded_topic}*&select=*"
            result = self._execute_query('GET', endpoint)
            
            programs = result.get('data', []) if result.get('success') else []
            
            # Group by source - fix datetime timezone issue
            from datetime import timezone
            
            existing = []
            new = []
            
            for p in programs:
                created_at = p.get('created_at')
                if created_at:
                    try:
                        # Handle both formats: with and without timezone info
                        if created_at.endswith('Z'):
                            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            created_dt = datetime.fromisoformat(created_at)
                            if created_dt.tzinfo is None:
                                created_dt = created_dt.replace(tzinfo=timezone.utc)
                        
                        # Make current time timezone-aware
                        now_utc = datetime.now(timezone.utc)
                        
                        # Check if program is older than 1 day
                        if (now_utc - created_dt).days > 1:
                            existing.append(p)
                        else:
                            new.append(p)
                    except (ValueError, TypeError) as e:
                        # If datetime parsing fails, treat as new
                        new.append(p)
                else:
                    # If no created_at, treat as new
                    new.append(p)
            
            return {
                'programs': programs,
                'count': len(programs),
                'existing_count': len(existing),
                'new_count': len(new),
                'reuse_rate': len(existing) / max(1, len(programs))
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting programs by topic: {e}")
            return {'programs': [], 'count': 0, 'error': str(e)}


# Supabase Schema Updates Required
SUPABASE_SCHEMA_UPDATES = [
    """
    -- Add program_hash column for deduplication
    ALTER TABLE affiliate_programs 
    ADD COLUMN IF NOT EXISTS program_hash TEXT UNIQUE;
    
    -- Create index for faster searches
    CREATE INDEX IF NOT EXISTS idx_affiliate_programs_search_query 
    ON affiliate_programs USING gin(to_tsvector('english', search_query));
    
    -- Create index for program hash
    CREATE INDEX IF NOT EXISTS idx_affiliate_programs_hash 
    ON affiliate_programs(program_hash);
    """,
    
    """
    -- Create research_program_links table for many-to-many relationships
    CREATE TABLE IF NOT EXISTS research_program_links (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        research_session_id UUID REFERENCES affiliate_research_sessions(id) ON DELETE CASCADE,
        program_id UUID REFERENCES affiliate_programs(id) ON DELETE CASCADE,
        link_type TEXT CHECK (link_type IN ('existing', 'new', 'reused')),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(research_session_id, program_id)
    );
    
    -- Create index for faster lookups
    CREATE INDEX IF NOT EXISTS idx_research_program_links_session 
    ON research_program_links(research_session_id);
    
    CREATE INDEX IF NOT EXISTS idx_research_program_links_program 
    ON research_program_links(program_id);
    """,
    
    """
    -- Create affiliate_research_sessions table for tracking research history
    CREATE TABLE IF NOT EXISTS affiliate_research_sessions (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID,
        topic TEXT NOT NULL,
        existing_programs_count INTEGER DEFAULT 0,
        new_programs_count INTEGER DEFAULT 0,
        reused_programs_count INTEGER DEFAULT 0,
        total_programs INTEGER DEFAULT 0,
        profitability_score INTEGER,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
    );
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_affiliate_research_sessions_user 
    ON affiliate_research_sessions(user_id);
    
    CREATE INDEX IF NOT EXISTS idx_affiliate_research_sessions_topic 
    ON affiliate_research_sessions(topic);
    
    CREATE INDEX IF NOT EXISTS idx_affiliate_research_sessions_created 
    ON affiliate_research_sessions(created_at);
    """
]

# Usage Instructions
def get_usage_instructions():
    return """
    ## Usage Instructions:
    
    1. **Run the schema updates** in Supabase SQL editor
    2. **Replace imports** in your main system:
       from supabase_affiliate_storage_enhanced import EnhancedSupabaseAffiliateStorage
    
    3. **Usage pattern**:
    
    ```python
    storage = EnhancedSupabaseAffiliateStorage(user_id)
    
    # Search existing programs first
    existing = await storage.get_existing_affiliate_programs('home security', user_id)
    
    # Store with deduplication
    result = await storage.store_affiliate_research_with_reuse(
        topic='home security',
        user_id=user_id,
        research_data={...}
    )
    
    # Get programs for specific topic
    programs = await storage.get_affiliate_programs_by_topic('home security', user_id)
    ```
    """

if __name__ == "__main__":
    print("Enhanced Supabase Affiliate Storage with Reuse Strategy")
    print("=" * 50)
    print("\nRequired SQL Updates:")
    for i, sql in enumerate(SUPABASE_SCHEMA_UPDATES, 1):
        print(f"\n{i}. {sql}")
    
    print("\n" + get_usage_instructions())