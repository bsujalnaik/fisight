import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
from .core_orchestrator import CoreOrchestratorAgent

logger = logging.getLogger(__name__)

class EnhancedChatSystem:
    def __init__(self):
        self.orchestrator = None
        self.greeting_patterns = [
            "hi", "hello", "hey", "good morning", "good afternoon", 
            "good evening", "greetings", "howdy", "sup", "yo"
        ]
        self.finance_keywords = [
            "portfolio", "investment", "tax", "capital gains", "income", 
            "wealth", "money", "financial", "stock", "mutual fund", "epf",
            "gst", "compliance", "risk", "returns", "profit", "loss",
            "budget", "savings", "expenses", "income tax", "deduction"
        ]
        
    async def initialize_orchestrator(self, user_id: str):
        """Initialize the orchestrator for a user"""
        if not self.orchestrator or self.orchestrator.user_id != user_id:
            self.orchestrator = CoreOrchestratorAgent(user_id=user_id)
            logger.info(f"Initialized orchestrator for user: {user_id}")
    
    def is_greeting(self, message: str) -> bool:
        """Check if the message is a greeting"""
        message_lower = message.lower().strip()
        return any(greeting in message_lower for greeting in self.greeting_patterns)
    
    def contains_finance_keywords(self, message: str) -> bool:
        """Check if the message contains finance-related keywords"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.finance_keywords)
    
    def get_greeting_response(self, message: str) -> str:
        """Generate a conversational greeting response"""
        greetings = [
            "Hello! 👋 How can I help you today?",
            "Hi there! 😊 What would you like to know?",
            "Hey! 👋 Great to see you. What's on your mind?",
            "Hello! 🌟 How may I assist you?",
            "Hi! ✨ What can I help you with today?"
        ]
        
        # Add some variety based on time of day
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greetings.append("Good morning! ☀️ How can I help you today?")
        elif 12 <= hour < 17:
            greetings.append("Good afternoon! 🌤️ What would you like to know?")
        elif 17 <= hour < 22:
            greetings.append("Good evening! 🌙 How may I assist you?")
        else:
            greetings.append("Hello! 🌙 What can I help you with?")
        
        import random
        return random.choice(greetings)
    
    def determine_agent_delegation(self, message: str) -> Dict[str, Any]:
        """Determine which agent(s) to delegate to based on the message"""
        message_lower = message.lower()
        
        # Initialize delegation plan
        delegation = {
            "primary_agent": None,
            "secondary_agents": [],
            "analysis_type": "general",
            "requires_comprehensive": False
        }
        
        # Portfolio-related queries
        if any(word in message_lower for word in ["portfolio", "holdings", "investments", "assets"]):
            delegation["primary_agent"] = "portfolio_agent"
            delegation["analysis_type"] = "portfolio_analysis"
            
        # Tax-related queries
        elif any(word in message_lower for word in ["tax", "income tax", "capital gains", "deduction", "gst"]):
            delegation["primary_agent"] = "tax_knowledge_agent"
            delegation["secondary_agents"].extend(["capital_gains_agent", "income_tax_agent"])
            delegation["analysis_type"] = "tax_analysis"
            
        # Investment strategy
        elif any(word in message_lower for word in ["investment", "strategy", "opportunity", "market"]):
            delegation["primary_agent"] = "investment_strategy_agent"
            delegation["secondary_agents"].append("google_search_agent")
            delegation["analysis_type"] = "investment_analysis"
            
        # Risk and compliance
        elif any(word in message_lower for word in ["risk", "compliance", "legal", "regulation"]):
            delegation["primary_agent"] = "legal_compliance_agent"
            delegation["analysis_type"] = "compliance_analysis"
            
        # Alerts and monitoring
        elif any(word in message_lower for word in ["alert", "monitor", "watch", "track"]):
            delegation["primary_agent"] = "alert_agent"
            delegation["analysis_type"] = "alert_analysis"
            
        # News and market updates
        elif any(word in message_lower for word in ["news", "market", "update", "trend"]):
            delegation["primary_agent"] = "news_agent"
            delegation["secondary_agents"].append("google_search_agent")
            delegation["analysis_type"] = "news_analysis"
            
        # Comprehensive analysis
        elif any(word in message_lower for word in ["comprehensive", "complete", "full", "overview", "summary"]):
            delegation["requires_comprehensive"] = True
            delegation["analysis_type"] = "comprehensive_analysis"
            
        # General financial advice
        else:
            delegation["primary_agent"] = "tax_planning_agent"
            delegation["secondary_agents"].extend(["portfolio_agent", "investment_strategy_agent"])
            delegation["analysis_type"] = "general_advice"
        
        return delegation
    
    async def generate_streaming_response(self, message: str, user_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate a streaming response with real-time updates"""
        
        # Step 1: Initialize orchestrator
        await self.initialize_orchestrator(user_id)
        
        # Step 2: Check if it's a greeting
        if self.is_greeting(message):
            response = self.get_greeting_response(message)
            yield {
                "type": "thinking",
                "content": "Processing your greeting...",
                "timestamp": datetime.now().isoformat()
            }
            await asyncio.sleep(0.5)  # Simulate thinking time
            
            yield {
                "type": "response",
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "is_greeting": True
            }
            return
        
        # Step 3: Determine agent delegation
        delegation = self.determine_agent_delegation(message)
        
        yield {
            "type": "thinking",
            "content": "Analyzing your request...",
            "timestamp": datetime.now().isoformat()
        }
        await asyncio.sleep(0.3)
        
        yield {
            "type": "delegation",
            "content": f"Delegating to {delegation['primary_agent'] or 'multiple agents'}...",
            "timestamp": datetime.now().isoformat(),
            "delegation": delegation
        }
        await asyncio.sleep(0.5)
        
        # Step 4: Execute analysis based on delegation
        try:
            if delegation["requires_comprehensive"]:
                # Run comprehensive analysis
                yield {
                    "type": "processing",
                    "content": "Running comprehensive financial analysis...",
                    "timestamp": datetime.now().isoformat()
                }
                
                results = await self.orchestrator.run_comprehensive_analysis(
                    user_id=user_id,
                    query=message
                )
                
                yield {
                    "type": "processing",
                    "content": "Compiling results from multiple agents...",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Format comprehensive response
                response = self.format_comprehensive_response(results, message)
                
            else:
                # Run targeted analysis
                yield {
                    "type": "processing",
                    "content": f"Executing {delegation['analysis_type']}...",
                    "timestamp": datetime.now().isoformat()
                }
                
                if delegation["primary_agent"] == "portfolio_agent":
                    results = await self.orchestrator.get_portfolio_summary(user_id)
                    response = self.format_portfolio_response(results, message)
                    
                elif delegation["primary_agent"] == "tax_knowledge_agent":
                    # Get tax updates and trends
                    tax_updates = self.orchestrator.tax_knowledge_agent.tools[1]()
                    tax_trends = self.orchestrator.tax_knowledge_agent.tools[2]()
                    response = self.format_tax_response(tax_updates, tax_trends, message)
                    
                elif delegation["primary_agent"] == "investment_strategy_agent":
                    # Get real-time market data
                    market_data = await self.orchestrator.fetch_real_time_data(message)
                    response = self.format_investment_response(market_data, message)
                    
                else:
                    # Default to general response
                    response = await self.get_general_response(message, user_id)
            
            yield {
                "type": "response",
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "delegation": delegation,
                "analysis_type": delegation["analysis_type"]
            }
            
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield {
                "type": "error",
                "content": f"I encountered an error while processing your request. Please try again.",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def format_comprehensive_response(self, results: Dict[str, Any], original_message: str) -> str:
        """Format comprehensive analysis results"""
        response_parts = []
        
        # Portfolio summary
        if 'portfolio_summary' in results and 'error' not in results['portfolio_summary']:
            portfolio = results['portfolio_summary']
            response_parts.append(f"📊 **Portfolio Overview**: Your portfolio is valued at ₹{portfolio.get('total_value', 0):,} with {portfolio.get('holdings_count', 0)} holdings.")
            
            if portfolio.get('risk_metrics', {}).get('concentration_risk') == 'high':
                response_parts.append("⚠️ **Risk Alert**: Your portfolio shows high concentration risk. Consider diversification.")
        
        # Real-time data
        if 'real_time_data' in results:
            response_parts.append("📈 **Market Update**: Real-time market data has been analyzed for your query.")
        
        # Tax updates
        if 'tax_updates' in results:
            tax_updates = results['tax_updates']
            if 'latest_updates' in tax_updates and tax_updates['latest_updates']:
                response_parts.append(f"📋 **Tax Updates**: {len(tax_updates['latest_updates'])} new tax policies identified.")
        
        # Capital gains
        if 'capital_gains' in results and 'error' not in results['capital_gains']:
            capital_gains = results['capital_gains']
            total_gains = capital_gains.get('total_gains', 0)
            if total_gains > 0:
                response_parts.append(f"💸 **Capital Gains**: Total gains of ₹{total_gains:,} identified.")
        
        # Alerts
        if 'alerts' in results:
            alerts = results['alerts']
            if 'alerts' in alerts and alerts['alerts']:
                high_priority = [a for a in alerts['alerts'] if a.get('priority') == 'high']
                if high_priority:
                    response_parts.append(f"🚨 **High Priority Alerts**: {len(high_priority)} urgent notifications.")
        
        if not response_parts:
            response_parts.append("I've analyzed your financial data comprehensively. Here are the key insights:")
        
        return "\n\n".join(response_parts)
    
    def format_portfolio_response(self, results: Dict[str, Any], original_message: str) -> str:
        """Format portfolio analysis results"""
        if 'error' in results:
            return "I'm unable to access your portfolio data at the moment. Please try again later."
        
        response_parts = []
        
        total_value = results.get('total_value', 0)
        holdings_count = results.get('holdings_count', 0)
        
        response_parts.append(f"📊 **Portfolio Summary**:")
        response_parts.append(f"• Total Value: ₹{total_value:,}")
        response_parts.append(f"• Holdings: {holdings_count} diverse investments")
        
        # Asset allocation
        asset_allocation = results.get('asset_allocation', {})
        if asset_allocation:
            response_parts.append(f"• Asset Allocation: {', '.join([f'{k.title()} (₹{v:,})' for k, v in asset_allocation.items()])}")
        
        # Risk metrics
        risk_metrics = results.get('risk_metrics', {})
        if risk_metrics:
            diversification = risk_metrics.get('diversification_score', 0)
            concentration_risk = risk_metrics.get('concentration_risk', 'unknown')
            response_parts.append(f"• Diversification Score: {diversification:.1%}")
            response_parts.append(f"• Risk Level: {concentration_risk.title()}")
        
        # Recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            response_parts.append(f"\n💡 **Recommendations**:")
            for rec in recommendations[:3]:  # Show top 3
                response_parts.append(f"• {rec}")
        
        return "\n".join(response_parts)
    
    def format_tax_response(self, tax_updates: Dict[str, Any], tax_trends: Dict[str, Any], original_message: str) -> str:
        """Format tax analysis results"""
        response_parts = []
        
        response_parts.append("📋 **Tax Analysis**:")
        
        # Tax updates
        if 'latest_updates' in tax_updates and tax_updates['latest_updates']:
            response_parts.append(f"• {len(tax_updates['latest_updates'])} new tax policies identified")
        
        # Deadlines
        if 'deadlines' in tax_updates and tax_updates['deadlines']:
            response_parts.append(f"• {len(tax_updates['deadlines'])} upcoming deadlines")
        
        # Trends
        if 'trends' in tax_trends and tax_trends['trends']:
            response_parts.append(f"• Key trends: {', '.join(tax_trends['trends'][:3])}")
        
        # Recommendations
        if 'recommendations' in tax_trends and tax_trends['recommendations']:
            response_parts.append(f"\n💡 **Tax Recommendations**:")
            for rec in tax_trends['recommendations'][:2]:
                response_parts.append(f"• {rec}")
        
        return "\n".join(response_parts)
    
    def format_investment_response(self, market_data: Dict[str, Any], original_message: str) -> str:
        """Format investment analysis results"""
        if 'error' in market_data:
            return "I'm unable to fetch real-time market data at the moment. Please try again later."
        
        response_parts = []
        response_parts.append("📈 **Investment Analysis**:")
        
        if 'search_results' in market_data:
            response_parts.append("• Real-time market data analyzed")
            response_parts.append("• Current market trends identified")
        
        response_parts.append("\n💡 **Investment Insights**:")
        response_parts.append("• Consider diversifying across multiple asset classes")
        response_parts.append("• Monitor market trends regularly")
        response_parts.append("• Review your risk tolerance periodically")
        
        return "\n".join(response_parts)
    
    async def get_general_response(self, message: str, user_id: str) -> str:
        """Get a general response for non-specific queries"""
        return f"I understand you're asking about '{message}'. I can help you with portfolio analysis, tax optimization, investment strategies, and more. Could you please be more specific about what you'd like to know?"

# Global chat system instance
enhanced_chat_system = EnhancedChatSystem() 