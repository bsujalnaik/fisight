from google.adk.agents import Agent
from ..mcp_service import MCPService
from .prompt import TAX_PLANNING_PROMPT, TAX_PLANNING_SYSTEM_PROMPT

async def fetch_tax_planning_from_mcp(user_id: str) -> dict:
    """Fetch tax planning data from MCP using the real service"""
    try:
        result = await MCPService.fetch_tax_planning(user_id)
        return result
    except Exception as e:
        return {'error': f'Tax planning fetch failed: {str(e)}'}

tax_planning_agent = Agent(
    name="tax_planning_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about tax planning.",
    instruction=TAX_PLANNING_PROMPT,
    tools=[fetch_tax_planning_from_mcp]
) 