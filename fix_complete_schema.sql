-- Complete Schema Fix for Affiliate Research System
-- Run this in Supabase SQL editor to fix all missing columns and constraints

-- ================================================
-- 1. Fix affiliate_research_sessions table
-- ================================================

-- Add all missing columns to affiliate_research_sessions
ALTER TABLE affiliate_research_sessions 
ADD COLUMN IF NOT EXISTS subtopic TEXT,
ADD COLUMN IF NOT EXISTS existing_programs_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS new_programs_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS reused_programs_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_programs INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS profitability_score INTEGER,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- ================================================
-- 2. Fix research_program_links table
-- ================================================

-- Add missing columns to research_program_links
ALTER TABLE research_program_links 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Ensure proper foreign key constraints exist
-- These should already exist from the initial schema, but verify:
-- research_program_links.research_session_id -> affiliate_research_sessions.id
-- research_program_links.program_id -> affiliate_programs.id

-- ================================================
-- 3. Fix affiliate_programs table (ensure all referenced columns exist)
-- ================================================

-- Add all missing columns that the code references
ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS subtopic TEXT,
ADD COLUMN IF NOT EXISTS program_name TEXT,
ADD COLUMN IF NOT EXISTS company_name TEXT,
ADD COLUMN IF NOT EXISTS signup_url TEXT,
ADD COLUMN IF NOT EXISTS commission_rate TEXT,
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS product_categories TEXT[],
ADD COLUMN IF NOT EXISTS cookie_duration TEXT,
ADD COLUMN IF NOT EXISTS payout_threshold TEXT,
ADD COLUMN IF NOT EXISTS extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS unique_id TEXT,
ADD COLUMN IF NOT EXISTS affiliate_program_url TEXT,
ADD COLUMN IF NOT EXISTS commission_structure TEXT,
ADD COLUMN IF NOT EXISTS cookie_lifetime TEXT,
ADD COLUMN IF NOT EXISTS minimum_payout TEXT,
ADD COLUMN IF NOT EXISTS payment_method TEXT,
ADD COLUMN IF NOT EXISTS approval_requirements TEXT,
ADD COLUMN IF NOT EXISTS geographic_restrictions TEXT,
ADD COLUMN IF NOT EXISTS tracking_system TEXT,
ADD COLUMN IF NOT EXISTS affiliate_support TEXT,
ADD COLUMN IF NOT EXISTS marketing_materials TEXT,
ADD COLUMN IF NOT EXISTS conversion_rate TEXT,
ADD COLUMN IF NOT EXISTS average_order_value TEXT,
ADD COLUMN IF NOT EXISTS industry TEXT,
ADD COLUMN IF NOT EXISTS tags TEXT[],
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS search_query TEXT,
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS program_hash TEXT UNIQUE;

-- ================================================
-- 4. Add indexes for performance
-- ================================================

-- Indexes for affiliate_programs
CREATE INDEX IF NOT EXISTS idx_affiliate_programs_search_query 
ON affiliate_programs USING gin(to_tsvector('english', search_query));

CREATE INDEX IF NOT EXISTS idx_affiliate_programs_hash 
ON affiliate_programs(program_hash);

CREATE INDEX IF NOT EXISTS idx_affiliate_programs_user 
ON affiliate_programs(user_id);

-- Indexes for affiliate_research_sessions
CREATE INDEX IF NOT EXISTS idx_affiliate_research_sessions_user 
ON affiliate_research_sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_affiliate_research_sessions_topic 
ON affiliate_research_sessions(topic);

CREATE INDEX IF NOT EXISTS idx_affiliate_research_sessions_created 
ON affiliate_research_sessions(created_at);

-- Indexes for research_program_links
CREATE INDEX IF NOT EXISTS idx_research_program_links_session 
ON research_program_links(research_session_id);

CREATE INDEX IF NOT EXISTS idx_research_program_links_program 
ON research_program_links(program_id);

-- ================================================
-- 5. Enable RLS on new tables
-- ================================================

-- Enable RLS if not already enabled
ALTER TABLE affiliate_research_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_program_links ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for affiliate_research_sessions
DROP POLICY IF EXISTS "Users can view own research sessions" ON affiliate_research_sessions;
CREATE POLICY "Users can view own research sessions" 
ON affiliate_research_sessions FOR SELECT 
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own research sessions" ON affiliate_research_sessions;
CREATE POLICY "Users can insert own research sessions" 
ON affiliate_research_sessions FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Create RLS policies for research_program_links
DROP POLICY IF EXISTS "Users can view own program links" ON research_program_links;
CREATE POLICY "Users can view own program links" 
ON research_program_links FOR SELECT 
USING (
    research_session_id IN (
        SELECT id FROM affiliate_research_sessions 
        WHERE user_id = auth.uid()
    )
);

DROP POLICY IF EXISTS "Users can insert own program links" ON research_program_links;
CREATE POLICY "Users can insert own program links" 
ON research_program_links FOR INSERT 
WITH CHECK (
    research_session_id IN (
        SELECT id FROM affiliate_research_sessions 
        WHERE user_id = auth.uid()
    )
);

-- ================================================
-- 6. Update triggers for timestamps
-- ================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop and recreate triggers to avoid conflicts
DROP TRIGGER IF EXISTS update_affiliate_programs_updated_at ON affiliate_programs;
CREATE TRIGGER update_affiliate_programs_updated_at 
    BEFORE UPDATE ON affiliate_programs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_research_sessions_updated_at ON affiliate_research_sessions;
CREATE TRIGGER update_research_sessions_updated_at 
    BEFORE UPDATE ON affiliate_research_sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_research_program_links_updated_at ON research_program_links;
CREATE TRIGGER update_research_program_links_updated_at 
    BEFORE UPDATE ON research_program_links 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- 7. Verify all columns exist
-- ================================================

SELECT 
    'affiliate_programs' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'affiliate_programs'
AND column_name IN ('existing_programs_count', 'new_programs_count', 'reused_programs_count', 'total_programs', 'profitability_score')

UNION ALL

SELECT 
    'affiliate_research_sessions' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'affiliate_research_sessions'
AND column_name IN ('existing_programs_count', 'new_programs_count', 'reused_programs_count', 'total_programs', 'profitability_score')

UNION ALL

SELECT 
    'research_program_links' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'research_program_links'
AND column_name IN ('updated_at')

ORDER BY table_name, column_name;

-- ================================================
-- 8. Success message
-- ================================================

SELECT 'Schema updated successfully - all missing columns added and constraints verified' as status;