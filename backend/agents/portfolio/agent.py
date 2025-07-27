# import logging
# import traceback
# from google.adk.agents import Agent
# from ..mcp_service import mcp_service
# from .prompt import PORTFOLIO_PROMPT, PORTFOLIO_SYSTEM_PROMPT


# async def fetch_portfolio_from_mcp(user_id: str) -> dict:
#     """Fetch portfolio data from MCP using the real service"""
#     try:
#         result = await mcp_service.fetch_portfolio(user_id)
#         return result
#     except Exception as e:
#         return {'error': f'Portfolio fetch failed: {str(e)}'}

# async def generate_portfolio_summary(user_id: str) -> dict:
#     """
#     Generate comprehensive portfolio summary from the detailed MCP data structure.
#     """
#     try:
#         # Fetch the comprehensive data which includes the detailed net worth JSON
#         portfolio_data = await mcp_service.fetch_portfolio(user_id)
#         if 'error' in portfolio_data:
#             return portfolio_data

#         # The detailed JSON is expected under the 'fetch_net_worth' key
#         data = portfolio_data.get('fetch_net_worth', {})
#         if not data:
#             return {'error': 'Net worth data is missing or empty.'}

#         summary = {
#             'total_value': 0,
#             'holdings_count': 0,
#             'asset_allocation': {},
#             'top_performers': [],
#             'holdings': [],
#             'risk_metrics': {},
#             'recommendations': [],
#             'data_sources': [],
#             'data_quality': {}
#         }

#         # 1. Parse Total Value
#         net_worth_response = data.get('netWorthResponse', {})
#         total_value_data = net_worth_response.get('totalNetWorthValue', {})
#         summary['total_value'] = int(total_value_data.get('units', 0))

#         # 2. Parse Asset Allocation
#         asset_values = net_worth_response.get('assetValues', [])
#         for asset in asset_values:
#             # Clean up the key name (e.g., "ASSET_TYPE_MUTUAL_FUND" -> "Mutual Fund")
#             key = asset.get('netWorthAttribute', 'UNKNOWN').replace('ASSET_TYPE_', '').replace('_', ' ').title()
#             value = int(asset.get('value', {}).get('units', 0))
#             if value > 0:
#                 summary['asset_allocation'][key] = value

#         # 3. Parse Holdings from different sections
#         holdings = []
#         accounts_map = data.get('accountDetailsBulkResponse', {}).get('accountDetailsMap', {})
#         mf_analytics = data.get('mfSchemeAnalytics', {}).get('schemeAnalytics', [])

#         # Parse Mutual Funds from enriched analytics
#         for mf in mf_analytics:
#             scheme_details = mf.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
#             holdings.append({
#                 'name': mf.get('schemeDetail', {}).get('nameData', {}).get('longName', 'Unknown MF'),
#                 'type': 'Mutual Fund',
#                 'value': int(scheme_details.get('currentValue', {}).get('units', 0))
#             })

#         # Parse Stocks, EPF, NPS from the accounts map
#         for account in accounts_map.values():
#             instrument_type = account.get('accountDetails', {}).get('accInstrumentType')
#             if instrument_type == 'ACC_INSTRUMENT_TYPE_EQUITIES':
#                 equity_summary = account.get('equitySummary', {})
#                 for stock in equity_summary.get('holdingsInfo', []):
#                     holdings.append({
#                         'name': stock.get('issuerName', 'Unknown Equity'),
#                         'type': 'Equity',
#                         'value': int(stock.get('units', 0)) * float(stock.get('lastTradedPrice', {}).get('units', 0))
#                     })
#             elif instrument_type == 'ACC_INSTRUMENT_TYPE_EPF':
#                 holdings.append({
#                     'name': 'EPF Account',
#                     'type': 'EPF',
#                     'value': int(account.get('epfSummary', {}).get('currentBalance', {}).get('units', 0))
#                 })
#             elif instrument_type == 'ACC_INSTRUMENT_TYPE_NPS':
#                 holdings.append({
#                     'name': 'NPS Account',
#                     'type': 'NPS',
#                     'value': int(account.get('npsSummary', {}).get('currentValue', {}).get('units', 0))
#                 })

#         summary['holdings'] = holdings
#         summary['holdings_count'] = len(holdings)

#         # 4. Identify Top Performers (by current value)
#         summary['top_performers'] = sorted(holdings, key=lambda x: x.get('value', 0), reverse=True)[:3]

#         # 5. Calculate Risk Metrics and Recommendations
#         if summary['total_value'] > 0:
#             summary['risk_metrics'] = {
#                 'diversification_score': min(summary['holdings_count'] / 10, 1.0),
#                 'concentration_risk': 'low' if summary['holdings_count'] > 15 else 'medium' if summary['holdings_count'] > 8 else 'high'
#             }
#             if summary['risk_metrics']['concentration_risk'] == 'high':
#                 summary['recommendations'].append('Consider diversifying your portfolio to reduce concentration risk.')

#         # 6. Parse Data Sources
#         summary['data_sources'] = [
#             acc.get('accountDetails', {}).get('fipId', 'Unknown Source') for acc in accounts_map.values()
#         ]
#         possible_sources = 4 # Example value
#         summary['data_quality'] = {
#             'sources_connected': len(summary['data_sources']),
#             'total_possible_sources': possible_sources,
#             'completeness_percentage': (len(summary['data_sources']) / possible_sources) * 100
#         }

#         return summary

#     except Exception as e:
#         # Log the full error for debugging
#         logging.error(f"Portfolio summary generation failed: {e}\n{traceback.format_exc()}")
#         return {'error': f'Portfolio summary generation failed: {str(e)}'}


# portfolio_agent = Agent(
#     name="portfolio_agent",
#     model="gemini-2.0-flash",
#     description="Agent to answer questions about user portfolios and provide comprehensive analysis.",
#     instruction=PORTFOLIO_PROMPT,
#     tools=[fetch_portfolio_from_mcp, generate_portfolio_summary]
# )

import logging
import traceback
import json

# Import the Vertex AI SDK
import vertexai
from vertexai.generative_models import GenerativeModel

from google.adk.agents import Agent
from ..mcp_service import mcp_service
from .prompt import PORTFOLIO_PROMPT

# This helper function remains unchanged
async def fetch_portfolio_from_mcp(user_id: str) -> dict:
    """Fetch portfolio data from MCP using the real service."""
    try:
        result = await mcp_service.fetch_portfolio(user_id)
        return result
    except Exception as e:
        return {'error': f'Portfolio fetch failed: {str(e)}'}

async def generate_portfolio_summary(user_id: str) -> dict:
    """
    Generates a portfolio summary by passing raw MCP data to a Gemini model on Vertex AI.
    """
    try:
        # --- Vertex AI Configuration ---
        # Replace with your specific GCP project and location
        GCP_PROJECT_ID = "finsight-agentic-ai"
        GCP_LOCATION = "us-central1"
        MODEL_NAME = "gemini-2.0-flash-lite-001"

        # Initialize the Vertex AI SDK
        vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
        # -----------------------------

        # 1. Fetch the raw data from the MCP service
        logging.info(f"Fetching portfolio for user: {user_id}")
        portfolio_data = await fetch_portfolio_from_mcp(user_id)
        if 'error' in portfolio_data:
            return portfolio_data  # Return fetch error directly

        # 2. Instantiate the Gemini model from Vertex AI
        # Model names in Vertex AI can be more specific
        model = GenerativeModel(MODEL_NAME)

        # 3. Create a prompt instructing the model to return a structured JSON
        prompt = f"""
        You are a financial data analyst for a leading fintech firm.
        Analyze the following raw portfolio data from our internal systems, provided in JSON format.
        Your task is to extract, calculate, and structure the information into a clean JSON object for our front-end application.

        The output JSON must have this exact structure:
        - 'total_value': A number representing the total net worth.
        - 'holdings_count': An integer for the total number of individual holdings.
        - 'asset_allocation': A dictionary mapping asset types (e.g., 'Mutual Fund', 'Equity') to their total value.
        - 'top_performers': A list of the top 3 holdings by current value. Each item must be a dictionary with 'name', 'type', and 'value'.
        - 'holdings': A complete list of all holdings, where each item is a dictionary with 'name', 'type', and 'value'.

        Here is the raw portfolio data:
        {json.dumps(portfolio_data, indent=2)}
        """

        # 4. Call the Vertex AI model and get the response
        logging.info("Generating summary with Vertex AI...")
        response = await model.generate_content_async(prompt)

        # 5. Parse the model's string response back into a dictionary
        cleaned_json_string = response.text.strip().lstrip("```json").rstrip("```")
        summary = json.loads(cleaned_json_string)

        logging.info("Successfully generated portfolio summary.")
        return summary

    except Exception as e:
        logging.error(f"Vertex AI portfolio summary generation failed: {e}\n{traceback.format_exc()}")
        return {'error': f'Portfolio summary generation failed via Vertex AI: {str(e)}'}


# The agent definition uses the new Vertex AI-powered tool
portfolio_agent = Agent(
    name="portfolio_agent",
    model="gemini-1.5-flash",
    description="Agent to answer questions about user portfolios using Vertex AI for analysis.",
    instruction=PORTFOLIO_PROMPT,
    tools=[fetch_portfolio_from_mcp, generate_portfolio_summary]
)
