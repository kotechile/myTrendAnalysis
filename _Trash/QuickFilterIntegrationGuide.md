# 🚀 Quick Filter Integration Guide

## Overview
This guide explains how to connect quick filter buttons to the enhanced TrendAnalysis_Noodl.txt function, enabling real-time filtering of trending topics and content opportunities.

## Button Configuration

### Required Button Outputs
Each quick filter button must have **4 outputs**:
1. **clicked** (boolean) - Triggered when button is clicked
2. **filterType** (string) - Always set to `"quickFilter"`
3. **filterValue** (string) - Filter identifier (see available filters below)
4. **targetTable** (string) - Either `"topics"` or `"opportunities"`

### Available Quick Filters

#### Topics Quick Filters
- `all` - Show all topics
- `highPotential` - Topics with viral potential 80+
- `highMonetization` - Topics with monetization score 70+
- `quickWins` - Topics with viral potential 60+ AND low competition
- `selected` - Only selected topics

#### Opportunities Quick Filters
- `all` - Show all opportunities
- `quickWins` - Opportunities with difficulty ≤40 AND high engagement
- `highValue` - Opportunities with high engagement potential
- `highMonetization` - Opportunities with monetization score 70+
- `selected` - Only selected opportunities

## Noodl Function Integration

### Function Node Inputs
Connect your button outputs to these function inputs:
- **filterType** - Connect from button's `filterType` output
- **filterValue** - Connect from button's `filterValue` output
- **targetTable** - Connect from button's `targetTable` output

### Function Outputs
Use these filtered outputs in your UI:
- **FilteredTrendingTopics** - Filtered topics for display
- **FilteredContentOpportunities** - Filtered opportunities for display
- **FilteredTopicsTableData** - Table-ready filtered topics
- **FilteredOpportunitiesTableData** - Table-ready filtered opportunities
- **FilteredTopicsCount** - Number of topics after filtering
- **FilteredOpportunitiesCount** - Number of opportunities after filtering

## UI Updates Required

### 1. Update Data Sources
Replace these in your UI components:
- `TrendingTopicsList` → `FilteredTrendingTopics`
- `ContentOpportunitiesList` → `FilteredContentOpportunities`
- `TrendingTopicsTableData` → `FilteredTopicsTableData`
- `ContentOpportunitiesTableData` → `FilteredOpportunitiesTableData`

### 2. Update Badge Counts
Use these for filter badge counts:
- `FilteredTopicsCount` instead of total topics count
- `FilteredOpportunitiesCount` instead of total opportunities count

### 3. Filter Badge Visual States
The function automatically updates filter badges with:
- Active/inactive states
- Current item counts
- Visual indicators for selected filters

## Example Button Configurations

### High Potential Topics Button
```
Button Configuration:
- clicked: boolean (trigger on click)
- filterType: "quickFilter"
- filterValue: "highPotential"
- targetTable: "topics"
```

### Quick Wins Opportunities Button
```
Button Configuration:
- clicked: boolean (trigger on click)
- filterType: "quickFilter"
- filterValue: "quickWins"
- targetTable: "opportunities"
```

### Selected Items Filter
```
Button Configuration:
- clicked: boolean (trigger on click)
- filterType: "quickFilter"
- filterValue: "selected"
- targetTable: "topics"  // or "opportunities"
```

## Connection Diagram

```
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│   Quick Filter  │    │  TrendAnalysis      │    │      UI         │
│     Button      │───▶│  Function Node      │───▶│   Components    │
│                 │    │                     │    │                 │
│ - clicked       │    │ - filterType        │    │ - Filtered data │
│ - filterType    │    │ - filterValue       │    │ - Badge counts  │
│ - filterValue   │    │ - targetTable       │    │ - Active states │
│ - targetTable   │    │                     │    │                 │
└─────────────────┘    └─────────────────────┘    └─────────────────┘
```

## Testing Checklist

### Button Setup
- [ ] Each button has 4 required outputs
- [ ] filterType is always "quickFilter"
- [ ] filterValue matches available filters
- [ ] targetTable is correctly set
- [ ] clicked trigger works on click

### Function Integration
- [ ] All 3 inputs are connected from buttons
- [ ] Function executes on button click
- [ ] Filtered outputs update correctly
- [ ] Badge counts reflect filtered data
- [ ] Visual states update properly

### UI Updates
- [ ] Data sources use filtered outputs
- [ ] Badge counts use filtered counts
- [ ] Active filter states are visible
- [ ] Filter results display correctly
- [ ] No performance issues with filtering

## Troubleshooting

### Common Issues
1. **Filters not applying**: Check button output connections
2. **Badge counts wrong**: Verify using filtered counts
3. **UI not updating**: Ensure using filtered outputs
4. **Function not triggering**: Check clicked trigger connection

### Debug Information
The function provides these debug outputs:
- `FilteredTopicsCount` and `FilteredOpportunitiesCount` for verification
- Console logs for filter application
- Active filter state in quickFilters array