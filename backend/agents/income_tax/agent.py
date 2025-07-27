from google.adk.agents import Agent
from ..mcp_service import MCPService
from .prompt import INCOME_TAX_PROMPT, INCOME_TAX_SYSTEM_PROMPT

async def fetch_income_tax_from_mcp(user_id: str) -> dict:
    """Fetch income tax data from MCP using the real service"""
    try:
        result = await MCPService.fetch_income_tax(user_id)
        return result
    except Exception as e:
        return {'error': f'Income tax fetch failed: {str(e)}'}

income_tax_agent = Agent(
    name="income_tax_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about income tax.",
    instruction=INCOME_TAX_PROMPT,
    tools=[fetch_income_tax_from_mcp]
) 