# New API Endpoint Documentation

## `/api/v2/affiliate-research/get-by-analysis`

### Overview
This new endpoint retrieves affiliate research data from the 4-table database structure (affiliate_research_sessions, affiliate_programs, affiliate_session_programs, affiliate_profitability_analysis) and returns it in the format expected by the Noodl frontend.

### Method
GET

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `trend_analysis_id` | string (UUID) | Yes | The analysis ID from the trend analysis |
| `user_id` | string (UUID) | Yes | The user ID for RLS (Row Level Security) |

### Response Format
```json
{
  "success": true,
  "affiliate_research_data": {
    "topic": "fitness",
    "subtopics": ["home workouts", "gym equipment", "protein supplements"],
    "programs": [
      {
        "id": "program-uuid",
        "network": "amazon",
        "program_name": "Premium Fitness Guide",
        "description": "Comprehensive fitness training program",
        "commission_rate": 4.5,
        "commission_amount": 13.5,
        "cookie_duration": "24 hours",
        "program_url": "https://example.com/fitness-guide",
        "approval_required": false,
        "promotional_materials": ["banners", "text_links"],
        "extraction_confidence": 0.85,
        "source_url": "https://amazon.com/fitness-guide"
      }
    ],
    "overall_assessment": {
      "score": 75,
      "level": "good",
      "reason": "Strong offer volume with moderate commissions",
      "total_programs": 12,
      "avg_commission_rate": 15.5,
      "avg_commission_amount": 45.2,
      "high_value_programs": 3,
      "networks_represented": 4
    },
    "recommendations": [
      "Based on 12 affiliate programs analyzed",
      "Average commission rate: 15.5%",
      "Profitability level: good"
    ]
  },
  "trend_analysis_id": "your-trend-analysis-id",
  "retrieved_at": "2024-01-15T10:30:00Z"
}
```

### Error Responses

#### Missing Parameters
```json
{
  "success": false,
  "error": "trend_analysis_id parameter is required"
}
```

#### Invalid UUID Format
```json
{
  "success": false,
  "error": "Invalid UUID format for trend_analysis_id or user_id"
}
```

#### No Data Found
```json
{
  "success": false,
  "error": "No affiliate research data found for the given trend_analysis_id",
  "trend_analysis_id": "your-trend-analysis-id",
  "user_id": "your-user-id"
}
```

### Usage Example

#### cURL
```bash
curl -X GET "http://localhost:5000/api/v2/affiliate-research/get-by-analysis?trend_analysis_id=123e4567-e89b-12d3-a456-426614174000&user_id=123e4567-e89b-12d3-a456-426614174001"
```

#### JavaScript (Noodl)
```javascript
async function getAffiliateResearch(trendAnalysisId, userId) {
  try {
    const response = await fetch(`/api/v2/affiliate-research/get-by-analysis?trend_analysis_id=${trendAnalysisId}&user_id=${userId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.affiliate_research_data;
  } catch (error) {
    console.error('Error fetching affiliate research:', error);
    return null;
  }
}

// Usage
const affiliateData = await getAffiliateResearch('your-analysis-id', 'your-user-id');
if (affiliateData) {
  // Use affiliateData.topic, affiliateData.programs, etc.
  console.log('Affiliate profitability score:', affiliateData.overall_assessment.score);
}
```

### Integration with Noodl

This endpoint is specifically designed to work with the Noodl frontend's expected format. The returned data structure matches what would normally be stored in `analysisInfo.metadata.affiliate_research_data`, allowing seamless integration with existing Noodl functions.

### Database Structure

The endpoint queries the following 4-table structure:

1. **affiliate_research_sessions** - Stores research session metadata
2. **affiliate_programs** - Stores individual affiliate program details
3. **affiliate_session_programs** - Links programs to sessions
4. **affiliate_profitability_analysis** - Stores profitability analysis results

### Error Handling
- Returns 400 for missing or invalid parameters
- Returns 404 when no data is found (graceful handling)
- Returns 500 for server errors
- All responses include proper JSON formatting and error messages