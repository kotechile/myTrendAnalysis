# Linkup Affiliate Research Integration Guide

## Overview
This guide helps you integrate the new Linkup-based affiliate research system that provides real web search results instead of mock data.

## Setup Instructions

### 1. Environment Variables
Add these to your `.env` file:

```bash
# Linkup API Configuration
LINKUP_API_KEY=your_linkup_api_key_here

# Supabase Configuration (if not already set)
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### 2. Database Setup
Run the SQL schema to create the required tables:

```bash
# Connect to your Supabase database and run:
psql -h your-db-host -U postgres -d postgres -f supabase_affiliate_schema.sql
```

### 3. Install Dependencies
```bash
pip install aiohttp
# Ensure supabase-py is installed
pip install supabase
```

## Usage Examples

### Basic Research
```python
from affiliate_research_api_updated import linkup_affiliate_api

# Research affiliate programs for a topic
result = await linkup_affiliate_api.research_affiliate_offers(
    topic="fitness equipment",
    user_id="your-user-id",
    subtopics=["home gym", "protein supplements", "workout gear"]
)

print(f"Found {result['affiliate_research']['total_programs']} programs")
print(f"Profitability score: {result['affiliate_research']['profitability_analysis']['score']}")
```

### Quick Validation
```python
# Quick profitability check
validation = await linkup_affiliate_api.validate_topic_profitability(
    topic="digital marketing",
    user_id="your-user-id"
)

if validation['is_profitable']:
    print("✅ Topic has good affiliate potential")
else:
    print("⚠️ Consider alternative topics")
```

## API Endpoints

### POST /api/v2/affiliate-research
Research affiliate programs for a given topic.

**Request:**
```json
{
  "user_id": "uuid-string",
  "topic": "fitness equipment",
  "subtopics": ["home gym", "supplements"],
  "min_commission_threshold": 30,
  "use_cached": true
}
```

**Response:**
```json
{
  "success": true,
  "cached": false,
  "affiliate_research": {
    "topic": "fitness equipment",
    "subtopics": [...],
    "programs": [...],
    "total_programs": 15,
    "profitability_analysis": {
      "score": 75,
      "level": "good",
      "reason": "Strong program variety..."
    }
  },
  "should_proceed": true,
  "threshold_check": {...}
}
```

### POST /api/v2/affiliate-research/validate
Quick validation endpoint for checking topic profitability.

**Request:**
```json
{
  "user_id": "uuid-string",
  "topic": "digital marketing"
}
```

**Response:**
```json
{
  "success": true,
  "topic": "digital marketing",
  "is_profitable": true,
  "profitability_score": 68,
  "level": "good",
  "recommendation": "proceed"
}
```

## Database Schema

### Tables Created:
- `affiliate_programs` - Stores unique affiliate programs
- `affiliate_research_sessions` - Stores research sessions
- `affiliate_session_programs` - Links programs to sessions
- `affiliate_profitability_analysis` - Stores profitability analysis

### Key Features:
- **Deduplication**: Programs are deduplicated using MD5 hashes
- **Caching**: Recent research (7 days) is cached to avoid API costs
- **RLS**: Row-level security ensures users only see their own data
- **Performance**: Optimized indexes for fast queries

## Integration with Noodl Server

### 1. Update noodl_server.py
Replace the import in your noodl_server.py:

```python
# OLD:
# from affiliate_research_api import affiliate_research

# NEW:
from affiliate_research_api_updated import affiliate_research
```

### 2. Update Configuration
Ensure your environment variables are set in the Noodl server configuration.

## Testing

### Test the Integration
```bash
# Test the API directly
curl -X POST http://localhost:8001/api/v2/affiliate-research \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "topic": "home fitness",
    "min_commission_threshold": 25
  }'
```

### Expected Response
```json
{
  "success": true,
  "cached": false,
  "affiliate_research": {
    "topic": "home fitness",
    "programs": [...],
    "profitability_analysis": {
      "score": 78,
      "level": "good"
    }
  }
}
```

## Cost Management

### Linkup API Usage:
- Each research query uses 1-2 Linkup API calls
- Subtopics are limited to 5 to control costs
- Results are cached for 7 days to avoid repeated searches

### Caching Strategy:
- Recent research is cached in Supabase
- Use `use_cached: true` to leverage caching
- Cache automatically expires after 7 days

## Troubleshooting

### Common Issues:

1. **Linkup API Key Missing**
   - Error: "Linkup API key not found"
   - Solution: Set LINKUP_API_KEY environment variable

2. **Supabase Connection Error**
   - Error: "Supabase connection failed"
   - Solution: Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY

3. **No Programs Found**
   - Error: Research returns empty results
   - Solution: Try more specific topics or check Linkup API status

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration from Mock Data

If you're currently using the mock data system, you can:

1. Keep the existing endpoints for backward compatibility
2. Gradually migrate by updating imports
3. The new system maintains the same API interface

The new Linkup-based system provides real, actionable affiliate program data instead of simulated results.