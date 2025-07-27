import requests
from google.adk.agents import Agent
from .prompt import NEWS_PROMPT, NEWS_SYSTEM_PROMPT

def fetch_news_for_tickers(tickers: list) -> dict:
    # TODO: Implement actual news API call for the given tickers
    # Example: response = requests.get(f"https://newsapi.org/v2/everything?q={ticker}")
    # return response.json()
    return {'error': 'News API fetch not implemented'}

news_agent = Agent(
    name="news_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about stock news.",
    instruction=NEWS_PROMPT,
    tools=[fetch_news_for_tickers]
) 