# Portfolio MCP Integration Guide

## Overview

This implementation connects the PortfolioOverview component to the MCP (Model Context Protocol) server using a specialized portfolio agent. The system provides real-time portfolio data analysis with AI-powered insights.

## Architecture

### 🔗 **Backend Integration**
- **Portfolio Agent**: Specialized agent for portfolio analysis
- **MCP Service**: Real-time data fetching from financial institutions
- **Vertex AI**: AI-powered portfolio analysis and insights
- **FastAPI Endpoint**: `/portfolio` endpoint for frontend communication

### 🎯 **Frontend Integration**
- **PortfolioOverview Component**: React component for displaying portfolio data
- **Real-time Updates**: Automatic data refresh and status updates
- **Error Handling**: Graceful fallback to mock data when MCP is unavailable

## Key Features

### 📊 **Real-time Portfolio Data**
- Live connection to MCP server for financial data
- Automatic data parsing and formatting
- Asset allocation analysis
- Holdings breakdown with performance metrics

### 🤖 **AI-Powered Analysis**
- Portfolio performance analysis
- Risk assessment and recommendations
- Asset allocation optimization suggestions
- Market trend analysis

### 🔄 **Robust Error Handling**
- Automatic fallback to mock data
- Connection retry logic
- User-friendly error messages
- Development mode with test data

## Implementation Details

### 1. Backend Portfolio Agent (`backend/agents/portfolio/agent.py`)

```python
async def generate_portfolio_summary(user_id: str) -> dict:
    """
    Generates a portfolio summary by passing raw MCP data to a Gemini model on Vertex AI.
    """
    try:
        # 1. Fetch raw data from MCP service
        portfolio_data = await fetch_portfolio_from_mcp(user_id)
        
        # 2. Use Vertex AI for analysis
        model = GenerativeModel(MODEL_NAME)
        prompt = create_analysis_prompt(portfolio_data)
        response = await model.generate_content_async(prompt)
        
        # 3. Parse and return structured data
        return json.loads(response.text)
        
    except Exception as e:
        return {'error': f'Portfolio analysis failed: {str(e)}'}
```

**Key Features:**
- Real-time MCP data fetching
- AI-powered portfolio analysis
- Structured JSON response
- Comprehensive error handling

### 2. FastAPI Portfolio Endpoint (`backend/app.py`)

```python
@app.post("/portfolio", response_model=PortfolioResponse)
async def portfolio_endpoint(request: PortfolioRequest):
    """Portfolio endpoint that connects to MCP server with portfolio agent"""
    try:
        # Use the portfolio agent to fetch and analyze data
        if request.action == "summary":
            result = await portfolio_agent.generate_portfolio_summary(request.user_id)
        else:
            result = await portfolio_agent.handle_query(
                f"Provide {request.action} for my portfolio", 
                context={"user_id": request.user_id}
            )
        
        return PortfolioResponse(
            success=True,
            data=result,
            message="Portfolio data retrieved successfully"
        )
        
    except Exception as e:
        return PortfolioResponse(
            success=False,
            data={},
            message=f"Failed to retrieve portfolio data: {str(e)}"
        )
```

**Key Features:**
- RESTful API design
- Structured request/response models
- Multiple action types (summary, analysis, recommendations)
- Comprehensive error handling

### 3. Frontend PortfolioOverview Component (`src/components/PortfolioOverview.tsx`)

```typescript
const fetchPortfolioData = useCallback(async () => {
  try {
    // Use the new portfolio endpoint with MCP integration
    const response = await fetch(`${API_BASE_URL}/portfolio`, {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: "demo_user",
        action: "summary"
      }),
    });

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || 'Failed to fetch portfolio data');
    }

    // Process the portfolio data from the agent
    const portfolioData = data.data;
    
    // Convert agent data to component format
    const processedAssets = convertAssetAllocation(portfolioData.asset_allocation);
    const formattedHoldings = formatHoldings(portfolioData.holdings);
    
    setPortfolioData({
      totalValue: portfolioData.total_value,
      assets: processedAssets,
      holdings: formattedHoldings
    });
    
  } catch (error) {
    // Fallback to mock data
    setPortfolioData(getMockPortfolioData());
  }
}, []);
```

**Key Features:**
- Real-time data fetching
- Data format conversion
- Error handling with fallback
- Automatic refresh logic

## Data Flow

### 1. **User Request**
```
Frontend → /portfolio endpoint → Portfolio Agent → MCP Service
```

### 2. **Data Processing**
```
MCP Raw Data → Portfolio Agent → Vertex AI Analysis → Structured JSON
```

### 3. **Response Delivery**
```
Structured Data → FastAPI → Frontend → PortfolioOverview Component
```

## MCP Data Structure

### Raw MCP Response
```json
{
  "fetch_net_worth": {
    "netWorthResponse": {
      "totalNetWorthValue": {"units": 500000},
      "assetValues": [
        {"netWorthAttribute": "ASSET_TYPE_MUTUAL_FUND", "value": {"units": 200000}},
        {"netWorthAttribute": "ASSET_TYPE_EQUITY", "value": {"units": 150000}}
      ]
    },
    "accountDetailsBulkResponse": {
      "accountDetailsMap": {
        "account1": {
          "accountDetails": {"accInstrumentType": "ACC_INSTRUMENT_TYPE_EQUITIES"},
          "equitySummary": {"holdingsInfo": [...]}
        }
      }
    }
  }
}
```

### Processed Portfolio Data
```json
{
  "total_value": 500000,
  "holdings_count": 15,
  "asset_allocation": {
    "Mutual Fund": 200000,
    "Equity": 150000,
    "Savings": 100000,
    "EPF": 30000,
    "NPS": 20000
  },
  "holdings": [
    {
      "name": "HDFC Bank",
      "type": "Equity",
      "value": 50000,
      "gain": 5000
    }
  ],
  "top_performers": [...],
  "risk_metrics": {...},
  "recommendations": [...]
}
```

## Testing

### 1. **Test Script** (`backend/test_portfolio_mcp.py`)
```bash
cd backend
python test_portfolio_mcp.py
```

**Tests:**
- MCP connection verification
- Portfolio endpoint functionality
- Data processing accuracy
- Error handling scenarios

### 2. **Manual Testing**
1. Start the backend server: `python app.py`
2. Start the frontend: `npm run dev`
3. Navigate to `/portfolio` in the browser
4. Check browser console for connection logs
5. Verify data loading and display

### 3. **Expected Behavior**
- ✅ Real-time portfolio data loading
- ✅ Asset allocation charts
- ✅ Holdings table with performance metrics
- ✅ AI-powered insights and recommendations
- ✅ Graceful fallback to mock data on errors

## Configuration

### Environment Variables
```env
# MCP Configuration
MCP_LOGIN_URL=http://localhost:8087/login
MCP_TOOL_URL=http://localhost:8087/mcp/stream
MCP_SESSION_ID=mcp-session-594e48ea-fea1-40ef-8c52-7552dd9272af
MCP_PHONE_NUMBER=2121212121
MCP_OTP=123456

# Vertex AI Configuration
PROJECT_ID=finsight-agentic-ai
LOCATION=us-central1
MODEL_NAME=gemini-2.0-flash-lite-001
```

### API Endpoints
```typescript
// Portfolio endpoint
POST /portfolio
{
  "user_id": "demo_user",
  "action": "summary" | "analysis" | "recommendations"
}

// Response
{
  "success": true,
  "data": {
    "total_value": 500000,
    "holdings": [...],
    "asset_allocation": {...}
  },
  "message": "Portfolio data retrieved successfully"
}
```

## Error Handling

### 1. **MCP Connection Errors**
- Automatic retry logic
- Fallback to cached data
- User-friendly error messages

### 2. **Data Processing Errors**
- Graceful degradation
- Mock data fallback
- Detailed error logging

### 3. **Frontend Errors**
- Loading states
- Error boundaries
- Retry mechanisms

## Performance Optimization

### 1. **Caching Strategy**
- MCP data caching (60 seconds TTL)
- Portfolio analysis caching
- Frontend state management

### 2. **Connection Pooling**
- Reusable HTTP sessions
- Connection timeouts
- Automatic cleanup

### 3. **Data Compression**
- Efficient JSON serialization
- Minimal payload sizes
- Gzip compression

## Security Considerations

### 1. **Data Protection**
- Secure MCP authentication
- User session management
- Data encryption in transit

### 2. **API Security**
- Input validation
- Rate limiting
- CORS configuration

### 3. **Error Information**
- Sanitized error messages
- No sensitive data in logs
- Secure error handling

## Troubleshooting

### Common Issues

1. **MCP Connection Failed**
   - Check MCP server status
   - Verify login credentials
   - Check network connectivity

2. **Portfolio Data Not Loading**
   - Check backend server logs
   - Verify MCP data availability
   - Check frontend console errors

3. **AI Analysis Not Working**
   - Verify Vertex AI configuration
   - Check API quotas and limits
   - Review error logs

### Debug Commands
```bash
# Test MCP connection
curl -X POST http://localhost:8087/login \
  -d "phoneNumber=2121212121&otp=123456"

# Test portfolio endpoint
curl -X POST http://localhost:8000/portfolio \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user", "action": "summary"}'

# Check backend logs
tail -f backend/app.log
```

## Future Enhancements

### 1. **Advanced Analytics**
- Portfolio rebalancing recommendations
- Tax optimization strategies
- Risk-adjusted return analysis

### 2. **Real-time Updates**
- WebSocket connections
- Push notifications
- Live market data integration

### 3. **Enhanced AI Features**
- Personalized investment advice
- Market trend predictions
- Portfolio optimization algorithms

### 4. **Multi-platform Support**
- Mobile app integration
- API for third-party tools
- Webhook notifications

## Conclusion

The Portfolio MCP Integration provides a robust, scalable solution for real-time portfolio analysis with AI-powered insights. The system handles complex financial data processing while maintaining excellent user experience through intelligent error handling and fallback mechanisms.

The integration successfully bridges the gap between raw financial data and actionable investment insights, making it easy for users to understand and optimize their portfolios. 