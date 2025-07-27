from google.adk.agents import Agent
from google.adk.tools import google_search

# Define the prompt for the Google Search agent
GOOGLE_SEARCH_PROMPT = """
You are a Google Search specialist agent. Your role is to:

1. Use the google_search tool to find current, accurate information from the web
2. Focus on real-time data, news, and market information
3. Provide comprehensive search results for financial queries
4. Search for tax updates, policy changes, and regulatory information
5. Find current stock prices, market data, and financial news

When given a query, use the google_search tool to find the most relevant and current information available.
Return the information in a structured format that is useful for financial analysis.
"""

# Custom functions for specific search tasks
async def fetch_market_data(ticker: str) -> dict:
    """
    Prepare market data query for a specific ticker.
    This function prepares the query - the actual search is handled by the agent.
    """
    try:
        query = f"{ticker} stock price current market data financial news"
        return {
            'ticker': ticker,
            'query': query,
            'data_type': 'market_data',
            'status': 'query_prepared',
            'search_type': 'financial'
        }
    except Exception as e:
        return {
            'ticker': ticker,
            'error': f'Market data query preparation failed: {str(e)}',
            'data_type': 'market_data'
        }

async def fetch_tax_updates() -> dict:
    """
    Prepare tax updates query.
    This function prepares the query - the actual search is handled by the agent.
    """
    try:
        query = "latest Indian tax updates 2025 policy changes income tax GST"
        return {
            'query': query,
            'data_type': 'tax_updates',
            'status': 'query_prepared',
            'search_type': 'regulatory'
        }
    except Exception as e:
        return {
            'error': f'Tax updates query preparation failed: {str(e)}',
            'data_type': 'tax_updates'
        }

async def fetch_financial_news(topic: str = "market") -> dict:
    """
    Prepare financial news query.
    """
    try:
        query = f"latest {topic} financial news India stock market today"
        return {
            'topic': topic,
            'query': query,
            'data_type': 'financial_news',
            'status': 'query_prepared',
            'search_type': 'news'
        }
    except Exception as e:
        return {
            'topic': topic,
            'error': f'Financial news query preparation failed: {str(e)}',
            'data_type': 'financial_news'
        }

# Simple wrapper function that your orchestrator expects
def google_search_tool(query: str) -> str:
    """
    Wrapper function for Google search compatibility with orchestrator.
    This is a simple placeholder that indicates a search would be performed.
    The actual search logic is handled by the ADK agent and google_search tool.
    """
    return f"Google Search would be executed for query: '{query}'"

# Create the main Google Search agent
google_search_agent = Agent(
    name="google_search_agent",
    model="gemini-2.0-flash",  # Required model for google_search tool
    description="Agent to fetch real-time data from the internet using Google Search for financial and tax information",
    instruction=GOOGLE_SEARCH_PROMPT,
    tools=[google_search]  # Only the built-in google_search tool (ADK limitation)
)

# For backward compatibility with existing code
Google_Search_agent = google_search_agent

# Export all necessary components
__all__ = [
    'google_search_agent', 
    'Google_Search_agent', 
    'google_search_tool',
    'fetch_market_data', 
    'fetch_tax_updates',
    'fetch_financial_news',
    'GOOGLE_SEARCH_PROMPT'
]