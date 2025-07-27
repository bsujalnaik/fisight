from google.adk.agents import Agent
from ..mcp_service import MCPService
from .prompt import CAPITAL_GAINS_PROMPT, CAPITAL_GAINS_SYSTEM_PROMPT

async def fetch_capital_gains_from_mcp(user_id: str) -> dict:
    """Fetch capital gains data from MCP using the real service"""
    try:
        result = await MCPService.fetch_capital_gains(user_id)
        return result
    except Exception as e:
        return {'error': f'Capital gains fetch failed: {str(e)}'}

capital_gains_agent = Agent(
    name="capital_gains_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about capital gains.",
    instruction=CAPITAL_GAINS_PROMPT,
    tools=[fetch_capital_gains_from_mcp]
) 