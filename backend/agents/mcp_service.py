import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MCPService:
    def __init__(self):
        # MCP Configuration
        self.MCP_LOGIN_URL = "https://finsight-agentic-ai.uc.r.appspot.com/login?sessionId=mcp-session-594e48ea-fea1-40ef-8c52-7552dd9272af"
        self.MCP_TOOL_URL = "https://finsight-agentic-ai.uc.r.appspot.com/mcp/stream"
        self.MCP_SESSION_ID = "mcp-session-594e48ea-fea1-40ef-8c52-7552dd9272af"
        self.MCP_PHONE_NUMBER = "2121212121"
        self.MCP_OTP = "123456"
        # Session management
        self.aiohttp_session = None
        self.login_status = {"logged_in": False, "timestamp": 0}
        self.cache = {}
        self.CACHE_TTL = 60

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.aiohttp_session is None:
            timeout_config = aiohttp.ClientTimeout(total=3)
            self.aiohttp_session = aiohttp.ClientSession(timeout=timeout_config)

    async def _login(self) -> bool:
        """Fast MCP login with minimal retry"""
        current_time = time.time()
        
        # Check if login is recent (within 5 minutes)
        if self.login_status["logged_in"] and (current_time - self.login_status["timestamp"]) < 300:
            return True
        
        await self._ensure_session()
        
        try:
            data = {"phoneNumber": self.MCP_PHONE_NUMBER, "otp": self.MCP_OTP}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            async with self.aiohttp_session.post(self.MCP_LOGIN_URL, data=data, headers=headers) as resp:
                if resp.status == 200:
                    self.login_status = {"logged_in": True, "timestamp": current_time}
                    logger.info("MCP login successful")
                    return True
                else:
                    logger.warning(f"MCP login failed: {resp.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"MCP login error: {e}")
            return False

    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        if not await self._login():
            return {"error": "Login failed"}
        
        await self._ensure_session()
        
        headers = {"Content-Type": "application/json", "Mcp-Session-Id": self.MCP_SESSION_ID}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments or {}}
        }
        
        for attempt in range(2):
            try:
                async with asyncio.timeout(3):
                    async with self.aiohttp_session.post(self.MCP_TOOL_URL, json=payload, headers=headers) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            logger.info(f"MCP tool {tool_name} called successfully")
                            return result
                        elif resp.status == 401:
                            self.login_status["logged_in"] = False
                            if await self._login():
                                continue
                        else:
                            logger.warning(f"MCP tool {tool_name} failed: {resp.status}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"MCP tool {tool_name} timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"MCP tool {tool_name} error on attempt {attempt + 1}: {e}")
            
            if attempt == 0:
                await asyncio.sleep(0.5)
        
        return {"error": f"Failed to call MCP tool {tool_name}"}

    def _extract_financial_data(self, mcp_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract financial data from MCP response"""
        try:
            json_string = mcp_data.get('result', {}).get('content', [{}])[0].get('text')
            if not json_string:
                logger.warning("Could not find financial data text in MCP response.")
                return None

            financial_payload = json.loads(json_string)
            if financial_payload.get('status') == 'login_required':
                logger.error("MCP returned 'login_required'. The session is not authenticated.")
                return {"error": "MCP Login Required", "details": financial_payload}
            logger.info("Successfully parsed financial data payload.")
            return financial_payload
            
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            logger.error(f"Data extraction error: {e}")
            return None

    # In mcpservice.py

    async def fetch_net_worth(self, user_id: str) -> Dict[str, Any]:
        """Fetch net worth data from MCP"""
        cache_key = f"net_worth_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning net worth data from cache.")
            return self.cache[cache_key]["data"]

        # This line is now in the correct place
        result = await self._call_mcp_tool("fetch_net_worth", arguments={"user_id": user_id})

        if "error" not in result:
            financial_data = self._extract_financial_data(result)
            if financial_data:
                self.cache[cache_key] = {"data": financial_data, "timestamp": current_time}
                return financial_data
        
        return {"error": "Failed to fetch net worth data"}

    async def fetch_bank_transactions(self, user_id: str) -> Dict[str, Any]:
        """Fetch bank transactions data from MCP"""
        cache_key = f"bank_transactions_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning bank transactions data from cache.")
            return self.cache[cache_key]["data"]
            

        result = await self._call_mcp_tool("fetch_bank_transactions", arguments={"user_id": user_id})
        if "error" not in result:
            financial_data = self._extract_financial_data(result)
            if financial_data:
                self.cache[cache_key] = {"data": financial_data, "timestamp": current_time}
                return financial_data
        
        return {"error": "Failed to fetch bank transactions data"}

    async def fetch_credit_report(self, user_id: str) -> Dict[str, Any]:
        """Fetch credit report data from MCP"""
        cache_key = f"credit_report_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning credit report data from cache.")
            return self.cache[cache_key]["data"]

        result = await self._call_mcp_tool("fetch_credit_report", arguments={"user_id": user_id})
        if "error" not in result:
            financial_data = self._extract_financial_data(result)
            if financial_data:
                self.cache[cache_key] = {"data": financial_data, "timestamp": current_time}
                return financial_data
        
        return {"error": "Failed to fetch credit report data"}

    async def fetch_epf_details(self, user_id: str) -> Dict[str, Any]:
        """Fetch EPF details data from MCP"""
        cache_key = f"epf_details_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning EPF details data from cache.")
            return self.cache[cache_key]["data"]

        result = await self._call_mcp_tool("fetch_epf_details", arguments={"user_id": user_id})
        if "error" not in result:
            financial_data = self._extract_financial_data(result)
            if financial_data:
                self.cache[cache_key] = {"data": financial_data, "timestamp": current_time}
                return financial_data
        
        return {"error": "Failed to fetch EPF details data"}

    async def fetch_mf_transactions(self, user_id: str) -> Dict[str, Any]:
        """Fetch mutual fund transactions data from MCP"""
        cache_key = f"mf_transactions_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning mutual fund transactions data from cache.")
            return self.cache[cache_key]["data"]

        result = await self._call_mcp_tool("fetch_mf_transactions", arguments={"user_id": user_id})
        if "error" not in result:
            financial_data = self._extract_financial_data(result)
            if financial_data:
                self.cache[cache_key] = {"data": financial_data, "timestamp": current_time}
                return financial_data
        
        return {"error": "Failed to fetch mutual fund transactions data"}

    async def fetch_stock_transactions(self, user_id: str) -> Dict[str, Any]:
        """Fetch stock transactions data from MCP"""
        cache_key = f"stock_transactions_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning stock transactions data from cache.")
            return self.cache[cache_key]["data"]

        result = await self._call_mcp_tool("fetch_stock_transactions", arguments={"user_id": user_id})
        if "error" not in result:
            financial_data = self._extract_financial_data(result)
            if financial_data:
                self.cache[cache_key] = {"data": financial_data, "timestamp": current_time}
                return financial_data
        
        return {"error": "Failed to fetch stock transactions data"}

    async def fetch_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Fetch comprehensive portfolio data from MCP (combines multiple sources)"""
        cache_key = f"portfolio_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning portfolio data from cache.")
            return self.cache[cache_key]["data"]

        # Fetch all portfolio-related data
        portfolio_data = {}
        
        # Net worth
        net_worth = await self.fetch_net_worth(user_id)
        if "error" not in net_worth:
            portfolio_data["fetch_net_worth"] = net_worth
        
        # Stock transactions
        stock_transactions = await self.fetch_stock_transactions(user_id)
        if "error" not in stock_transactions:
            portfolio_data["fetch_stock_transactions"] = stock_transactions
        
        # Mutual fund transactions
        mf_transactions = await self.fetch_mf_transactions(user_id)
        if "error" not in mf_transactions:
            portfolio_data["fetch_mf_transactions"] = mf_transactions
        
        # EPF details
        epf_details = await self.fetch_epf_details(user_id)
        if "error" not in epf_details:
            portfolio_data["fetch_epf_details"] = epf_details
        
        if portfolio_data:
            self.cache[cache_key] = {"data": portfolio_data, "timestamp": current_time}
            return portfolio_data
        
        return {"error": "Failed to fetch portfolio data"}

    async def fetch_capital_gains(self, user_id: str) -> Dict[str, Any]:
        """Fetch capital gains data from MCP (based on stock transactions)"""
        cache_key = f"capital_gains_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning capital gains data from cache.")
            return self.cache[cache_key]["data"]

        # Get stock transactions to calculate capital gains
        stock_transactions = await self.fetch_stock_transactions(user_id)
        if "error" not in stock_transactions:
            # Calculate capital gains from stock transactions
            capital_gains_data = self._calculate_capital_gains_from_transactions(stock_transactions)
            self.cache[cache_key] = {"data": capital_gains_data, "timestamp": current_time}
            return capital_gains_data
        
        return {"error": "Failed to fetch capital gains data"}

    def _calculate_capital_gains_from_transactions(self, stock_transactions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate capital gains from stock transactions"""
        try:
            transactions = stock_transactions.get('transactions', [])
            
            # Group transactions by stock
            stock_groups = {}
            for transaction in transactions:
                symbol = transaction.get('symbol', 'UNKNOWN')
                if symbol not in stock_groups:
                    stock_groups[symbol] = []
                stock_groups[symbol].append(transaction)
            
            # Calculate gains for each stock
            capital_gains = {
                'short_term_gains': 0,
                'long_term_gains': 0,
                'total_gains': 0,
                'stock_wise_gains': {},
                'tax_liability': {
                    'short_term_tax': 0,
                    'long_term_tax': 0,
                    'total_tax': 0
                }
            }
            
            for symbol, symbol_transactions in stock_groups.items():
                # Calculate gains for this stock
                gains = self._calculate_stock_gains(symbol_transactions)
                capital_gains['stock_wise_gains'][symbol] = gains
                capital_gains['short_term_gains'] += gains.get('short_term_gains', 0)
                capital_gains['long_term_gains'] += gains.get('long_term_gains', 0)
            
            capital_gains['total_gains'] = capital_gains['short_term_gains'] + capital_gains['long_term_gains']
            
            # Calculate tax liability (simplified)
            capital_gains['tax_liability']['short_term_tax'] = capital_gains['short_term_gains'] * 0.15  # 15% STCG
            capital_gains['tax_liability']['long_term_tax'] = capital_gains['long_term_gains'] * 0.10   # 10% LTCG
            capital_gains['tax_liability']['total_tax'] = (
                capital_gains['tax_liability']['short_term_tax'] + 
                capital_gains['tax_liability']['long_term_tax']
            )
            
            return capital_gains
            
        except Exception as e:
            logger.error(f"Error calculating capital gains: {e}")
            return {"error": f"Failed to calculate capital gains: {str(e)}"}

    def _calculate_stock_gains(self, transactions: list) -> Dict[str, Any]:
        """Calculate gains for a specific stock"""
        try:
            # Simplified calculation - in reality, this would be more complex
            total_buy_value = 0
            total_sell_value = 0
            
            for transaction in transactions:
                if transaction.get('type') == 'BUY':
                    total_buy_value += transaction.get('amount', 0)
                elif transaction.get('type') == 'SELL':
                    total_sell_value += transaction.get('amount', 0)
            
            net_gain = total_sell_value - total_buy_value
            
            # Simplified: assume all gains are short-term for demo
            return {
                'short_term_gains': max(0, net_gain),
                'long_term_gains': 0,
                'total_gains': max(0, net_gain)
            }
            
        except Exception as e:
            logger.error(f"Error calculating stock gains: {e}")
            return {'short_term_gains': 0, 'long_term_gains': 0, 'total_gains': 0}

    async def fetch_income_tax(self, user_id: str) -> Dict[str, Any]:
        """Fetch income tax data from MCP (combines multiple sources)"""
        cache_key = f"income_tax_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning income tax data from cache.")
            return self.cache[cache_key]["data"]

        # Combine data from multiple sources for income tax calculation
        income_tax_data = {}
        
        # Bank transactions for income sources
        bank_transactions = await self.fetch_bank_transactions(user_id)
        if "error" not in bank_transactions:
            income_tax_data["fetch_bank_transactions"] = bank_transactions
        
        # EPF details for deductions
        epf_details = await self.fetch_epf_details(user_id)
        if "error" not in epf_details:
            income_tax_data["fetch_epf_details"] = epf_details
        
        # Credit report for additional income sources
        credit_report = await self.fetch_credit_report(user_id)
        if "error" not in credit_report:
            income_tax_data["fetch_credit_report"] = credit_report
        
        if income_tax_data:
            self.cache[cache_key] = {"data": income_tax_data, "timestamp": current_time}
            return income_tax_data
        
        return {"error": "Failed to fetch income tax data"}

    async def fetch_tax_planning(self, user_id: str) -> Dict[str, Any]:
        """Fetch tax planning data from MCP"""
        cache_key = f"tax_planning_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning tax planning data from cache.")
            return self.cache[cache_key]["data"]

        # Combine multiple data sources for tax planning
        tax_planning_data = {}
        
        # Get portfolio data
        portfolio = await self.fetch_portfolio(user_id)
        if "error" not in portfolio:
            tax_planning_data["portfolio"] = portfolio
        
        # Get income tax data
        income_tax = await self.fetch_income_tax(user_id)
        if "error" not in income_tax:
            tax_planning_data["income_tax"] = income_tax
        
        # Get capital gains data
        capital_gains = await self.fetch_capital_gains(user_id)
        if "error" not in capital_gains:
            tax_planning_data["capital_gains"] = capital_gains
        
        if tax_planning_data:
            self.cache[cache_key] = {"data": tax_planning_data, "timestamp": current_time}
            return tax_planning_data
        
        return {"error": "Failed to fetch tax planning data"}

    async def fetch_tax_info(self, user_id: str) -> Dict[str, Any]:
        """Fetch general tax info from MCP"""
        cache_key = f"tax_info_{user_id}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and (current_time - self.cache[cache_key].get("timestamp", 0)) < self.CACHE_TTL:
            logger.info("Returning tax info data from cache.")
            return self.cache[cache_key]["data"]

        # Combine all tax-related data
        tax_info_data = {}
        
        # Get all available tax data
        portfolio = await self.fetch_portfolio(user_id)
        if "error" not in portfolio:
            tax_info_data["portfolio"] = portfolio
        
        income_tax = await self.fetch_income_tax(user_id)
        if "error" not in income_tax:
            tax_info_data["income_tax"] = income_tax
        
        capital_gains = await self.fetch_capital_gains(user_id)
        if "error" not in capital_gains:
            tax_info_data["capital_gains"] = capital_gains
        
        if tax_info_data:
            self.cache[cache_key] = {"data": tax_info_data, "timestamp": current_time}
            return tax_info_data
        
        return {"error": "Failed to fetch tax info data"}

    async def close(self):
        """Close the aiohttp session"""
        if self.aiohttp_session:
            await self.aiohttp_session.close()

# Global MCP service instance
mcp_service = MCPService() 
