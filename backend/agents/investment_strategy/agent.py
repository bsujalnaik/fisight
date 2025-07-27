from google.adk.agents import Agent
from .prompt import INVESTMENT_STRATEGY_PROMPT, INVESTMENT_STRATEGY_SYSTEM_PROMPT

def fetch_portfolio_from_mcp(user_id: str) -> dict:
    # TODO: Implement actual MCP server call to fetch portfolio for user_id
    return {'error': 'MCP portfolio fetch not implemented'}

def fetch_realtime_stock_data(tickers: list) -> dict:
    # TODO: Implement actual real-time stock data fetch (external API or MCP stock server)
    return {'error': 'Real-time stock fetch not implemented'}

investment_strategy_agent = Agent(
    name="investment_strategy_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about investment strategy and stocks.",
    instruction=INVESTMENT_STRATEGY_PROMPT,
    tools=[fetch_portfolio_from_mcp, fetch_realtime_stock_data]
) 