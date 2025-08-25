-- Enhanced Affiliate Program Storage Schema Updates
-- Run these SQL commands in your Supabase SQL editor

-- ================================================
-- 1. Add program_hash column for deduplication
-- ================================================
ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS program_hash TEXT UNIQUE;

-- ================================================
-- 2. Create indexes for faster searches
-- ================================================
CREATE INDEX IF NOT EXISTS idx_affiliate_programs_search_query 
ON affiliate_programs USING gin(to_tsvector('english', search_query));

CREATE INDEX IF NOT EXISTS idx_affiliate_programs_hash 
ON affiliate_programs(program_hash);

-- ================================================
-- 3. Create research_program_links table
-- ================================================
CREATE TABLE IF NOT EXISTS research_program_links (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    research_session_id UUID REFERENCES affiliate_research_sessions(id) ON DELETE CASCADE,
    program_id UUID REFERENCES affiliate_programs(id) ON DELETE CASCADE,
    link_type TEXT CHECK (link_type IN ('existing', 'new', 'reused')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(research_session_id, program_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_research_program_links_session 
ON research_program_links(research_session_id);

CREATE INDEX IF NOT EXISTS idx_research_program_links_program 
ON research_program_links(program_id);

-- ================================================
-- 4. Create affiliate_research_sessions table
-- ================================================
CREATE TABLE IF NOT EXISTS affiliate_research_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    subtopic TEXT,
    existing_programs_count INTEGER DEFAULT 0,
    new_programs_count INTEGER DEFAULT 0,
    reused_programs_count INTEGER DEFAULT 0,
    total_programs INTEGER DEFAULT 0,
    profitability_score INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_affiliate_research_sessions_user 
ON affiliate_research_sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_affiliate_research_sessions_topic 
ON affiliate_research_sessions(topic);

CREATE INDEX IF NOT EXISTS idx_affiliate_research_sessions_created 
ON affiliate_research_sessions(created_at);

-- ================================================
-- 5. Update existing affiliate_programs table structure
-- ================================================
-- Add search_query column if not exists
ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS search_query TEXT;

-- Add user_id column if not exists (for RLS compatibility)
ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- Add created_at and updated_at columns
ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add extracted_at column for affiliate programs
ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add missing columns that the code references
ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS subtopic TEXT;

ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS program_name TEXT;

ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS company_name TEXT;

ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS signup_url TEXT;

ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS commission_rate TEXT;

ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS description TEXT;

ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS product_categories TEXT[];

ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS cookie_duration TEXT;

ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS payout_threshold TEXT;

-- Add unique_id column that's being referenced
ALTER TABLE affiliate_programs 
ADD COLUMN IF NOT EXISTS unique_id TEXT;

-- ================================================
-- 6. ******** Create triggers for updated_at timestamps

-- ERROR:  42710: trigger "update_affiliate_programs_updated_at" for relation "affiliate_programs" already exists
-- ================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

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

-- ================================================
-- 7. Enable RLS on new tables
-- ================================================
ALTER TABLE affiliate_research_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_program_links ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view own research sessions" 
ON affiliate_research_sessions FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own research sessions" 
ON affiliate_research_sessions FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own program links" 
ON research_program_links FOR SELECT 
USING (
    research_session_id IN (
        SELECT id FROM affiliate_research_sessions 
        WHERE user_id = auth.uid()
    )
);

CREATE POLICY "Users can insert own program links" 
ON research_program_links FOR INSERT 
WITH CHECK (
    research_session_id IN (
        SELECT id FROM affiliate_research_sessions 
        WHERE user_id = auth.uid()
    )
);

-- ================================================
-- 8. Verify schema updates
-- ================================================
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name IN ('affiliate_programs', 'affiliate_research_sessions', 'research_program_links')
ORDER BY table_name, column_name;