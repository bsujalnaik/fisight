from google.adk.agents import Agent
from .prompt import NORMAN_MCP_PROMPT, NORMAN_MCP_SYSTEM_PROMPT

def fetch_norman_mcp_data(user_id: str) -> dict:
    """Fetch data from Norman MCP server"""
    # TODO: Implement actual Norman MCP server connection
    # This would connect to the Norman MCP server and fetch financial data
    return {
        'connection_status': 'connected',
        'data_retrieved': True,
        'financial_data': {
            'portfolio_value': 500000,
            'transactions': 25,
            'last_updated': '2024-01-15T10:30:00Z'
        },
        'performance_metrics': {
            'response_time': '150ms',
            'data_quality': 'high',
            'cache_hit_rate': '85%'
        }
    }

norman_mcp_agent = Agent(
    name="norman_mcp_agent",
    model="gemini-2.0-flash",
    description="Agent to handle Norman MCP server interactions.",
    instruction=NORMAN_MCP_PROMPT,
    tools=[fetch_norman_mcp_data]
) 