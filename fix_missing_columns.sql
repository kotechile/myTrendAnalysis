-- Fix all missing columns in affiliate_programs table
-- Run this in Supabase SQL editor

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
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add missing columns to affiliate_research_sessions
ALTER TABLE affiliate_research_sessions 
ADD COLUMN IF NOT EXISTS subtopic TEXT,
ADD COLUMN IF NOT EXISTS existing_programs_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS new_programs_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS reused_programs_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_programs INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS profitability_score INTEGER,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add missing columns to research_program_links
ALTER TABLE research_program_links 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Refresh the schema cache
SELECT 'Schema updated successfully' as status;