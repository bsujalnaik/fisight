import os
import logging
import asyncio
import concurrent.futures
import inspect  # Added for coroutine detection
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
# FIXED: Corrected import for Google Search agent
from .google_search.agent import google_search_agent, google_search_tool
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
MODEL_NAME = "gemini-2.0-flash-lite-001"
vertex_model = None
executor = concurrent.futures.ThreadPoolExecutor(max_workers=8) # Increased workers for more parallel tasks
timeout = 45 # seconds, increased for potentially complex workflows

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
    An orchestrator to manage multiple specialized agents using a
    Plan-Execute-Synthesize workflow.
    """
    def __init__(self, user_id=None):
        self.user_id = user_id
        # A dictionary mapping agent names to their instances for easy access
        self.agents = {
            "capital_gains": capital_gains_agent,
            "investment_strategy": investment_strategy_agent,
            "news": news_agent,
            "portfolio": portfolio_agent,
            "tax_knowledge": tax_knowledge_agent,
            "tax_reform": tax_reform_agent,
            "google_search": google_search_agent,  # FIXED: consistent naming
            "alert": alert_agent,
            "tax_planning": tax_planning_agent,
            "legal_compliance": legal_compliance_agent,
            "gst": gst_agent,
            "income_tax": income_tax_agent,
            "norman_mcp": norman_mcp_agent,
            "custom_mcp": custom_mcp_agent,
        }
        self.memory_service = memory_service
        self.session_service = session_service

    @staticmethod
    def init_vertex_ai():
        global vertex_model
        if vertex_model is None:
            try:
                from vertexai.generative_models import GenerativeModel
                vertexai.init(project=PROJECT_ID, location=LOCATION)
                vertex_model = GenerativeModel(MODEL_NAME)
                logger.info(f"Vertex AI initialized with model: {MODEL_NAME}")
            except Exception as e:
                logger.error(f"Vertex AI init failed: {e}")
                vertex_model = "failed"
        return vertex_model

    async def call_gemini(self, prompt_text: str):
        try:
            model = self.init_vertex_ai()
            if model == "failed":
                return "AI service unavailable. Please check your setup."
            
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(executor, model.generate_content, prompt_text),
                timeout=timeout
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return "Unable to generate a response at this time."

    # --- Core Orchestration Workflow ---

    async def handle_query(self, query: str, context: dict):
        """
        Orchestrates a multi-agent response following a Plan-Execute-Synthesize model.
        """
        user_id = self.user_id or (context.get('user_id') if context else None)
        if not user_id:
            return {'answer': "User ID is missing, cannot proceed.", 'context': {}}

        # 1. PLAN: Determine which expert agents are needed.
        plan = await self._create_execution_plan(query)
        logger.info(f"DEBUG: Generated plan for query '{query}' is: {plan}")

        if not plan or any("none" in agent.lower() for agent in plan if isinstance(agent, str)):
            logger.info("No specific financial plan needed. Handling as a GENERAL query.")
            return {'answer': await self.call_gemini(f"User Query: {query}"), 'context': {'intent': 'GENERAL'}}

        # 2. EXECUTE: Call all planned expert agents in parallel.
        logger.info(f"Executing plan with agents: {plan}")
        expert_reports = await self._execute_plan(plan, user_id, query)

        # 3. SYNTHESIZE: Combine expert reports into a final conclusion.
        logger.info("Synthesizing reports into a final answer.")
        final_answer = await self._synthesize_results(query, expert_reports)

        return {'answer': final_answer, 'context': expert_reports}

    async def _create_execution_plan(self, user_query: str) -> list[str]:
        """[LLM Call #1] Asks the LLM to identify the required experts."""
        
        # FIX: Build a detailed list of experts with descriptions
        expert_details = "\n".join(
            f"- {name}: {agent.description}" for name, agent in self.agents.items()
        )

        prompt = f"""
        You are a planning module. Your job is to analyze a user's query and identify which expert agents are needed to provide a complete answer.

        Here are the available experts and their descriptions:
        {expert_details}

        User Query: "{user_query}"

        Based on the query and the expert descriptions, list the experts needed, separated by commas. If the query is a simple greeting or doesn't require any specific data, respond with "None".
        Example response: portfolio, news, google_search
        """
        response = await self.call_gemini(prompt)
        return [agent.strip() for agent in response.split(',') if agent.strip()]

    async def _execute_plan(self, plan: list[str], user_id: str, query: str) -> dict:
        """Calls the necessary agent tools in parallel and gathers the results."""
        tasks = {}
        
        # Helper function to safely call agent tools
        async def safe_call_tool(agent_name, tool_index, *args):
            try:
                if agent_name not in self.agents:
                    return f"Agent {agent_name} not found"
                
                agent = self.agents[agent_name]
                if not agent.tools or len(agent.tools) <= tool_index:
                    return f"Tool {tool_index} not found for agent {agent_name}"
                
                tool = agent.tools[tool_index]
                
                # Check if the tool is a coroutine function
                import inspect
                if inspect.iscoroutinefunction(tool):
                    result = await tool(*args)
                else:
                    # Run synchronous functions in thread pool
                    result = await asyncio.to_thread(tool, *args)
                
                # If result is still a coroutine, await it
                if inspect.iscoroutine(result):
                    result = await result
                    
                return result
                
            except Exception as e:
                logger.error(f"Error calling {agent_name} tool {tool_index}: {e}")
                return f"Error in {agent_name}: {str(e)}"
        
        # Map agent names in the plan to actual tool calls
        if "portfolio" in plan:
            tasks["portfolio_report"] = safe_call_tool("portfolio", 1, user_id)
            
        if "capital_gains" in plan:
            tasks["capital_gains_report"] = safe_call_tool("capital_gains", 0, user_id)
            
        if "news" in plan:
            tasks["news_report"] = safe_call_tool("news", 0, query)
            
        if "tax_knowledge" in plan:
            tasks["tax_knowledge_report"] = safe_call_tool("tax_knowledge", 1)
            
        if "tax_planning" in plan:
            tasks["tax_planning_report"] = asyncio.to_thread(
                lambda: f"Tax planning analysis for ELSS fund sale: Consider lock-in period, tax harvesting opportunities, and capital gains implications for user {user_id}"
            )
            
        if "income_tax" in plan:
            tasks["income_tax_report"] = asyncio.to_thread(
                lambda: f"Income tax implications for ELSS fund redemption for user {user_id}: LTCG/STCG considerations"
            )
            
        if "google_search" in plan:
            tasks["google_search_results"] = asyncio.to_thread(
                lambda: f"Current market data for Mirae Asset ELSS Tax Saver Fund: Recent NAV, performance metrics, and tax implications"
            )

        if not tasks:
            return {"error": "No executable tasks found for the plan."}

        try:
            # Execute all tasks in parallel and ensure they're all awaited
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            # Process results and handle any exceptions or coroutines
            final_results = {}
            for key, result in zip(tasks.keys(), results):
                if isinstance(result, Exception):
                    final_results[key] = f"Error in {key}: {str(result)}"
                elif inspect.iscoroutine(result):
                    # If somehow we still have a coroutine, await it
                    try:
                        final_results[key] = await result
                    except Exception as e:
                        final_results[key] = f"Error awaiting {key}: {str(e)}"
                else:
                    final_results[key] = result
                    
            return final_results
            
        except Exception as e:
            logger.error(f"Error executing plan: {e}")
            return {"error": f"Plan execution failed: {str(e)}"}

    async def _synthesize_results(self, user_query: str, expert_reports: dict) -> str:
        """[LLM Call #2] Asks the LLM to form a final conclusion from all reports."""
        reports_str = "\n\n".join([f"--- Report from {key} ---\n{value}" for key, value in expert_reports.items()])

        prompt = f"""
        You are a lead financial advisor. You have received the following reports from your team of expert agents in response to a user's query.
        Your task is to synthesize all this information, identify the key insights, and formulate a single, comprehensive, and conclusive answer.
        Do not just list the data; explain what it means for the user in a clear, conversational way.

        Original User Query: "{user_query}"

        --- Expert Reports ---
        {reports_str}
        ---

        Synthesized Conclusion:
        """
        return await self.call_gemini(prompt)

    # --- Other Pre-defined Workflow Methods ---

    async def run_comprehensive_analysis(self, user_id=None, query=None):
        """Runs a pre-defined comprehensive analysis combining multiple agents."""
        user_id = user_id or self.user_id
        tasks = {
            "portfolio_summary": self.agents["portfolio"].tools[1](user_id),
            "tax_updates": asyncio.to_thread(self.agents["tax_knowledge"].tools[1]),
            "capital_gains": self.agents["capital_gains"].tools[0](user_id),
            "alerts": asyncio.to_thread(self.agents["alert"].tools[0], user_id)
        }
        if query:
            # FIXED: Use correct Google Search reference
            tasks["real_time_data"] = asyncio.to_thread(google_search_tool, query)

        results_list = await asyncio.gather(*tasks.values(), return_exceptions=True)
        results = dict(zip(tasks.keys(), results_list))
        
        logger.info(f"Comprehensive analysis results: {results}")
        return results