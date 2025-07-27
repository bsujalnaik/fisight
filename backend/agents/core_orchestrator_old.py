import os
import logging
import asyncio
import concurrent.futures
import vertexai

from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.memory import VertexAiMemoryBankService
from google.adk.sessions import VertexAiSessionService

# Assuming these agents are correctly defined in their respective files
from .capital_gains.agent import capital_gains_agent
from .investment_strategy.agent import investment_strategy_agent
from .news.agent import news_agent
from .norman_mcp.agent import norman_mcp_agent
from .custom_mcp.agent import custom_mcp_agent
from .income_tax.agent import income_tax_agent
from .legal_compliance.agent import legal_compliance_agent
from .gst.agent import gst_agent
from .tax_planning.agent import tax_planning_agent
from .tax_knowledge.agent import tax_knowledge_agent
from .tax_reform.agent import tax_reform_agent
from .portfolio.agent import portfolio_agent
from .alert.agent import alert_agent
from .google_search.agent import Google_Search_agent
from .mcp_service import MCPService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example: Add a memory tool to an agent
capital_gains_agent.tools.append(PreloadMemoryTool())

def delegate_to_news_agent(tickers):
    """A simple function to delegate a call to another agent's tool."""
    return news_agent.tools[0](tickers)
capital_gains_agent.tools.append(delegate_to_news_agent)

# --- Global Configuration ---
PROJECT_ID = "finsight-agentic-ai"
LOCATION = "us-central1"
# Ensure you are using a valid and available model name
MODEL_NAME = "gemini-1.5-flash-001" 
vertex_model = None
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
timeout = 30 # seconds

# --- Service Initialization ---
memory_service = VertexAiMemoryBankService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=MODEL_NAME
)
session_service = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=MODEL_NAME
)


class CoreOrchestratorAgent:
    """
    An orchestrator to manage multiple specialized agents and workflows.
    """
    def __init__(self, user_id=None):
        self.capital_gains_agent = capital_gains_agent
        self.investment_strategy_agent = investment_strategy_agent
        self.news_agent = news_agent
        self.norman_mcp_agent = norman_mcp_agent
        self.custom_mcp_agent = custom_mcp_agent
        self.income_tax_agent = income_tax_agent
        self.legal_compliance_agent = legal_compliance_agent
        self.gst_agent = gst_agent
        self.tax_planning_agent = tax_planning_agent
        self.tax_knowledge_agent = tax_knowledge_agent
        self.tax_reform_agent = tax_reform_agent
        self.portfolio_agent = portfolio_agent
        self.alert_agent = alert_agent
        self.Google Search_agent = Google Search_agent
        self.user_id = user_id
        self.memory_service = memory_service
        self.session_service = session_service

    @staticmethod
    def init_vertex_ai():
        global vertex_model
        if vertex_model is None:
            try:
                # Use the recommended import path
                from vertexai.generative_models import GenerativeModel
                vertexai.init(project=PROJECT_ID, location=LOCATION)
                vertex_model = GenerativeModel(MODEL_NAME)
                logger.info(f"Vertex AI initialized with model: {MODEL_NAME}")
            except Exception as e:
                logger.error(f"Vertex AI init failed: {e}")
                vertex_model = "failed"
        return vertex_model

    async def call_gemini(self, context, prompt_text):
        try:
            model = self.init_vertex_ai()
            if model == "failed":
                return "AI service unavailable. Please check your setup."
            
            loop = asyncio.get_event_loop()
            try:
                response = await asyncio.wait_for(
                    loop.run_in_executor(executor, model.generate_content, prompt_text),
                    timeout=timeout
                )
                return response.text.strip()
            except asyncio.TimeoutError:
                return "The response is taking longer than expected. Please try again."
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return "Unable to generate a response at this time."

    def _build_prompt(self, context, user_query):
        # This prompt is now used specifically for FINANCIAL queries
        return (
            f"User Query: {user_query}\n\n"
            f"Relevant Context:\n"
            f"Portfolio Summary: {context.get('portfolio')}\n"
            f"Stock Data: {context.get('stock_data')}\n"
            f"Latest News: {context.get('news')}\n"
            f"Tax Reforms: {context.get('tax_reforms')}\n\n"
            "Based on the user's query and the provided context, please answer in a helpful, conversational, and concise way."
        )
    
    async def _get_query_intent(self, user_query: str) -> str:
        """Uses a quick LLM call to classify the user's intent."""
        try:
            model = self.init_vertex_ai()
            if model == "failed":
                return "GENERAL"  # Default to general if AI is down

            prompt = f"""
            Analyze the user's query and classify its intent.
            Respond with only one word: FINANCIAL or GENERAL.

            - FINANCIAL queries relate to stocks, portfolio, taxes, investments, market news, or specific financial analysis.
            - GENERAL queries are conversational greetings, questions not related to finance, or small talk.

            User Query: "{user_query}"
            """
            response = await model.generate_content_async(prompt)
            intent = response.text.strip().upper()
            
            logger.info(f"Detected intent: {intent} for query: '{user_query}'")
            return "FINANCIAL" if "FINANCIAL" in intent else "GENERAL"

        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            return "GENERAL"  # Default to general on error

    async def _fetch_financial_context(self, user_id: str) -> dict:
        """Gathers all financial context from various tools."""
        context_bundle = {}
        try:
            logger.info("Fetching financial context...")
            portfolio = await self.portfolio_agent.tools[1](user_id) if self.portfolio_agent else {}
            context_bundle['portfolio'] = portfolio
            
            tickers = [h.get('name') for h in portfolio.get('holdings', [])] if isinstance(portfolio, dict) and portfolio.get('holdings') else []
            if tickers:
                context_bundle['stock_data'] = self.investment_strategy_agent.tools[1](tickers) if self.investment_strategy_agent else {}
                context_bundle['news'] = self.news_agent.tools[0](tickers) if self.news_agent else {}

            context_bundle['tax_reforms'] = self.tax_reform_agent.tools[0]() if self.tax_reform_agent else {}
        except Exception as e:
            logger.error(f"Error fetching financial context: {e}")
            context_bundle['error'] = "Failed to retrieve some financial data."
        return context_bundle

    async def handle_query(self, query: str, context: dict):
        """Handles the user query by first determining intent and then acting accordingly."""
        user_id = self.user_id or (context.get('user_id') if context else None)
        
        intent = await self._get_query_intent(query)
        
        if intent == 'GENERAL':
            logger.info("Handling as a GENERAL query.")
            prompt = f"User Query: {query}\n\nPlease answer in a helpful, conversational, and concise way."
            answer = await self.call_gemini({}, prompt)
            return {'answer': answer, 'context': {'intent': 'GENERAL'}}

        elif intent == 'FINANCIAL':
            logger.info("Handling as a FINANCIAL query.")
            financial_context = await self._fetch_financial_context(user_id)
            prompt = self._build_prompt(financial_context, query)
            answer = await self.call_gemini(financial_context, prompt)
            return {'answer': answer, 'context': financial_context}

    # --- Existing Workflow and Tool-Calling Methods ---

    async def ask_capital_gains(self, user_id=None):
        """Calls the fetch_capital_gains_from_mcp tool via the agent."""
        user_id = user_id or self.user_id
        try:
            result = await self.capital_gains_agent.tools[0](user_id)
            logger.info(f"Capital Gains Tool Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error calling capital_gains_agent tool: {e}")
            return {"error": str(e)}

    async def get_portfolio_summary(self, user_id=None):
        """Get comprehensive portfolio summary using the enhanced portfolio agent."""
        user_id = user_id or self.user_id
        try:
            # Assumes generate_portfolio_summary is the second tool
            result = await self.portfolio_agent.tools[1](user_id)
            logger.info(f"Portfolio Summary Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error calling portfolio summary tool: {e}")
            return {"error": str(e)}

    async def fetch_real_time_data(self, query=None):
        """Fetch real-time data using the Google Search agent."""
        try:
            if query:
                result = self.Google Search_agent.tools[0](query)  # search_google
            else:
                result = self.Google Search_agent.tools[2]()  # fetch_tax_updates
            logger.info(f"Real-time Data Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error calling Google Search agent tool: {e}")
            return {"error": str(e)}
    
    async def run_comprehensive_analysis(self, user_id=None, query=None):
        """Runs a comprehensive analysis combining multiple agents."""
        user_id = user_id or self.user_id
        tasks = {
            "portfolio_summary": self.get_portfolio_summary(user_id),
            "tax_updates": asyncio.to_thread(self.tax_knowledge_agent.tools[1]),
            "tax_trends": asyncio.to_thread(self.tax_knowledge_agent.tools[2]),
            "capital_gains": self.ask_capital_gains(user_id),
            "alerts": asyncio.to_thread(self.alert_agent.tools[0], user_id)
        }
        if query:
            tasks["real_time_data"] = self.fetch_real_time_data(query)

        results_list = await asyncio.gather(*tasks.values(), return_exceptions=True)
        results = dict(zip(tasks.keys(), results_list))
        
        logger.info(f"Comprehensive analysis results: {results}")
        return results
        
    async def run_parallel_workflow(self, user_id=None, tickers=None):
        """Runs a parallel workflow using direct agent tool calls and asyncio.gather."""
        user_id = user_id or self.user_id
        tickers = tickers or []
        
        tasks = [
            self.capital_gains_agent.tools[0](user_id),
            self.portfolio_agent.tools[0](user_id),
            asyncio.to_thread(self.investment_strategy_agent.tools[1], tickers),
            asyncio.to_thread(self.news_agent.tools[0], tickers)
        ]
        
        task_keys = ['capital_gains', 'portfolio', 'stock_data', 'news']
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        results = dict(zip(task_keys, results_list))

        logger.info(f"Parallel workflow results: {results}")
        return results

    async def create_session(self, app_name, user_id=None):
        """Creates a session using VertexAiSessionService."""
        user_id = user_id or self.user_id
        try:
            session = await self.session_service.create_session(app_name=app_name, user_id=user_id)
            logger.info(f"Created session: {session}")
            return session
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return {"error": str(e)}

    async def add_session_to_memory(self, session):
        """Adds a session to memory using VertexAiMemoryBankService."""
        try:
            await self.memory_service.add_session_to_memory(session)
            logger.info(f"Session added to memory: {session}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Error adding session to memory: {e}")
            return {"error": str(e)}