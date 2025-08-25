# Affiliate Research Integration Guide

## Overview
This guide explains how to integrate the new affiliate offer research functionality into your Noodl frontend application. The system adds profitability validation as the FIRST step before trend analysis.

## New Workflow

### Phase 0: Affiliate Offer Research (NEW)
Before analyzing trends, the system now automatically researches affiliate offers to validate topic profitability.

### Complete Workflow
1. **Phase 0**: Research affiliate offers for profitability
2. **Phase 1**: Enhanced trend research & market intelligence  
3. **Phase 2**: Blog idea generation & content strategy
4. **Phase 3**: Manual keyword research integration

## API Endpoints

### 1. Main Enhanced Trend Research
**POST** `/api/v2/enhanced-trend-research`

**New Parameters:**
- `min_affiliate_score` (optional): Minimum profitability score (0-100) to proceed. Default: 30

**Response Changes:**
- Now includes `affiliate_research_data` with offer analysis
- Includes `profitability_score` and `profitability_level`
- May return cancellation if topic is not profitable

### 2. Dedicated Affiliate Research
**POST** `/api/v2/affiliate-research`

**Request Body:**
```json
{
  "user_id": "uuid-from-noodl",
  "topic": "fitness for beginners",
  "subtopics": ["home workouts", "protein supplements"],
  "min_commission_threshold": 25
}
```

**Response:**
```json
{
  "success": true,
  "affiliate_research": {
    "topic": "fitness for beginners",
    "subtopics": [...],
    "offers": [...],
    "profitability_analysis": {...},
    "overall_assessment": {
      "score": 75,
      "level": "good",
      "reason": "Strong offer volume with good commissions"
    },
    "recommendations": [...]
  },
  "should_proceed": true
}
```

### 3. Quick Validation
**POST** `/api/v2/affiliate-research/validate`

**Use Case:** Quick check before starting full analysis

### 4. Subtopic Generation
**POST** `/api/v2/affiliate-research/subtopics`

**Use Case:** Split broad topics into profitable subtopics

## Integration Examples

### Example 1: Basic Integration (Recommended)
```javascript
// In Noodl frontend
const response = await fetch('/api/v2/enhanced-trend-research', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: "digital marketing",
    user_id: userId,
    llm_config: { api_key: openaiKey, provider: "openai" },
    min_affiliate_score: 40 // Higher threshold
  })
});

const result = await response.json();

if (result.success) {
  // Proceed with Phase 2
  console.log("Topic profitable! Score:", result.metadata.profitability_score);
} else {
  // Handle cancellation
  console.log("Topic not profitable:", result.cancellation_reason);
  console.log("Suggestions:", result.recommendations);
}
```

### Example 2: Custom Profitability Threshold
```javascript
const response = await fetch('/api/v2/enhanced-trend-research', {
  method: 'POST',
  body: JSON.stringify({
    topic: "home gardening",
    user_id: userId,
    llm_config: { api_key: openaiKey },
    min_affiliate_score: 20 // Lower threshold for testing
  })
});
```

### Example 3: Pre-Validation
```javascript
// Validate before full analysis
const validation = await fetch('/api/v2/affiliate-research/validate', {
  method: 'POST',
  body: JSON.stringify({
    topic: "vegan recipes",
    user_id: userId
  })
});

const validationResult = await validation.json();

if (validationResult.is_profitable) {
  // Proceed with full analysis
  const analysis = await fetch('/api/v2/enhanced-trend-research', {
    method: 'POST',
    body: JSON.stringify({
      topic: "vegan recipes",
      user_id: userId,
      llm_config: { api_key: openaiKey }
    })
  });
}
```

### Example 4: Topic Refinement
```javascript
// Get subtopics for broad topic
const subtopics = await fetch('/api/v2/affiliate-research/subtopics', {
  method: 'POST',
  body: JSON.stringify({
    topic: "technology",
    user_id: userId
  })
});

const subtopicsResult = await subtopics.json();
// Use most profitable subtopic
const profitableSubtopic = subtopicsResult.subtopics[0];
```

## Profitability Scoring System

### Scoring Criteria (0-100 points)
- **Offer Volume**: Up to 30 points for number of available offers
- **Commission Value**: Up to 30 points for average commission amounts
- **High-Value Offers**: Up to 25 points for offers >= 30% commission
- **Subtopic Coverage**: Up to 15 points for topic breadth

### Levels
- **Excellent (70-100)**: Strong monetization potential
- **Good (50-69)**: Decent potential with strategic approach
- **Moderate (30-49)**: Limited but workable
- **Poor (0-29)**: Not recommended

## Handling Cancellations

When a topic is cancelled due to poor profitability, the response includes:

```json
{
  "success": false,
  "error": "Analysis cancelled due to poor affiliate opportunity",
  "cancellation_reason": "Topic profitability score 15 below threshold 30",
  "affiliate_research": {...},
  "recommendations": [
    "Try a more specific subtopic",
    "Explore related niches with better commission potential",
    "Lower the minimum affiliate score threshold"
  ]
}
```

## Noodl Frontend Updates

### 1. Add Profitability Display
```javascript
// Display profitability score in Noodl
const profitability = result.metadata.profitability_score;
const level = result.metadata.profitability_level;

if (profitability) {
  Noodl.setVariable('profitabilityScore', profitability);
  Noodl.setVariable('profitabilityLevel', level);
}
```

### 2. Handle Cancellations
```javascript
// In Noodl node
if (!result.success && result.cancellation_reason) {
  Noodl.setVariable('errorMessage', result.cancellation_reason);
  Noodl.setVariable('suggestions', result.recommendations.join('\n'));
  // Show suggestions to user
}
```

### 3. Allow Threshold Adjustment
```javascript
// Let users adjust profitability threshold
const threshold = Noodl.getVariable('minProfitabilityThreshold') || 30;
const response = await fetch('/api/v2/enhanced-trend-research', {
  method: 'POST',
  body: JSON.stringify({
    topic: currentTopic,
    user_id: userId,
    llm_config: { api_key: openaiKey },
    min_affiliate_score: threshold
  })
});
```

## Testing

### Test Topics
- **High Profitability**: "digital marketing", "fitness equipment", "software tools"
- **Medium Profitability**: "home organization", "personal development"
- **Low Profitability**: "abstract philosophy", "local community events"

### Test Commands
```bash
# Test affiliate research
curl -X POST http://localhost:8001/api/v2/affiliate-research \
  -H "Content-Type: application/json" \
  -d '{"topic": "fitness", "user_id": "test-user-id"}'

# Test with custom threshold
curl -X POST http://localhost:8001/api/v2/enhanced-trend-research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "digital marketing",
    "user_id": "test-user-id",
    "llm_config": {"api_key": "your-openai-key"},
    "min_affiliate_score": 50
  }'
```

## Migration from Existing System

1. **No Breaking Changes**: Existing calls to `/api/v2/enhanced-trend-research` continue to work
2. **Optional Parameters**: New parameters are optional with sensible defaults
3. **Backward Compatible**: Responses include new data without breaking existing parsing
4. **Graceful Fallback**: If affiliate research fails, system proceeds with trend analysis

## Troubleshooting

### Common Issues
1. **Module Not Found**: Ensure `affiliate_research_api.py` is in same directory
2. **Timeout**: Increase `min_affiliate_score` or use pre-validation
3. **Poor Results**: Try more specific subtopics or adjust threshold

### Debug Mode
Set `min_affiliate_score: 0` to always proceed (for testing purposes)