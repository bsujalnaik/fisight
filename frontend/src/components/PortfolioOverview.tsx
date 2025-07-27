import React, { useState, useEffect, useCallback } from 'react';
import { Wallet, TrendingUp, BarChart3, Gem, PieChart, Loader2, AlertCircle, RefreshCw } from 'lucide-react';

// Replace with your actual API base URL
const API_BASE_URL = 'http://localhost:8000';



const PortfolioOverview = () => {
  // State for portfolio data
  const [portfolioData, setPortfolioData] = useState(null);
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Generate mock performance data
  const generatePerformanceData = (baseValue: number) => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const value = baseValue > 0 ? baseValue : 100000;
    return months.map((month, index) => {
      const variation = (Math.random() - 0.5) * 0.1;
      return {
        month,
        value: Math.round(value * (1 + variation - (index * 0.02)))
      };
    });
  };

  // Function to extract and process MCP data
  const processMcpData = useCallback((mcpResponse) => {
    try {
      let financialData = null;
      
      // Extract financial data from MCP response
      if (mcpResponse?.result?.content?.[0]?.text) {
        financialData = JSON.parse(mcpResponse.result.content[0].text);
      } else if (mcpResponse?.fetch_net_worth) {
        financialData = mcpResponse;
      }

      if (!financialData) {
        throw new Error('No financial data found in response');
      }

      // Process the data structure with safe property access
      const netWorthResponse = financialData.fetch_net_worth?.netWorthResponse || {};
      const totalValueData = netWorthResponse.totalNetWorthValue || {};
      const totalValue = parseInt(String(totalValueData.units || 0));

      // Process asset allocation
      const assetValues = Array.isArray(netWorthResponse.assetValues) ? netWorthResponse.assetValues : [];
      const processedAssets = {
        stocks: 0,
        mutualFunds: 0,
        savings: 0,
        epf: 0,
        nps: 0,
        others: 0
      };

      assetValues.forEach(asset => {
        if (!asset) return;
        const type = String(asset.netWorthAttribute || '');
        const value = parseInt(String(asset.value?.units || 0));
        
        if (type.includes('EQUITY') || type.includes('STOCK')) {
          processedAssets.stocks += value;
        } else if (type.includes('MUTUAL_FUND')) {
          processedAssets.mutualFunds += value;
        } else if (type.includes('BANK') || type.includes('SAVINGS')) {
          processedAssets.savings += value;
        } else if (type.includes('EPF')) {
          processedAssets.epf += value;
        } else if (type.includes('NPS')) {
          processedAssets.nps += value;
        } else {
          processedAssets.others += value;
        }
      });

      // Process individual holdings
      const holdings = [];
      const accountsMap = financialData.fetch_net_worth?.accountDetailsBulkResponse?.accountDetailsMap || {};
      const mfAnalytics = financialData.fetch_net_worth?.mfSchemeAnalytics?.schemeAnalytics || [];

      // Process Mutual Funds
      if (Array.isArray(mfAnalytics)) {
        mfAnalytics.forEach(mf => {
          if (!mf) return;
          const schemeDetails = mf.enrichedAnalytics?.analytics?.schemeDetails || {};
          const schemeDetail = mf.schemeDetail || {};
          holdings.push({
            id: String(schemeDetail.schemeCode || Math.random().toString()),
            name: String(schemeDetail.nameData?.longName || 'Unknown MF'),
            type: 'Mutual Fund',
            value: parseInt(String(schemeDetails.currentValue?.units || 0)),
            gain: parseInt(String(schemeDetails.totalGainValue?.units || 0)),
            symbol: String(schemeDetail.schemeCode || 'N/A')
          });
        });
      }

      // Process other account types
      if (typeof accountsMap === 'object' && accountsMap !== null) {
        Object.values(accountsMap).forEach(account => {
          if (!account || typeof account !== 'object') return;
          
          const accountAny = account as any;
          const accountDetails = accountAny.accountDetails || {};
          const instrumentType = String(accountDetails.accInstrumentType || '');

          if (instrumentType === 'ACC_INSTRUMENT_TYPE_EQUITIES') {
            const equityHoldings = accountAny.equitySummary?.holdingsInfo || [];
            if (Array.isArray(equityHoldings)) {
              equityHoldings.forEach(stock => {
                if (!stock) return;
                const units = parseInt(String(stock.units || 0));
                const price = parseFloat(String(stock.lastTradedPrice?.units || 0));
                holdings.push({
                  id: String(stock.isin || Math.random().toString()),
                  name: String(stock.issuerName || 'Unknown Stock'),
                  type: 'Equity',
                  symbol: String(stock.symbol || 'N/A'),
                  value: Math.round(units * price),
                  gain: parseInt(String(stock.totalGainValue?.units || 0))
                });
              });
            }
          } else if (instrumentType === 'ACC_INSTRUMENT_TYPE_EPF') {
            const epfSummary = accountAny.epfSummary || {};
            holdings.push({
              id: 'epf-' + Math.random().toString(),
              name: 'EPF Account',
              type: 'EPF',
              symbol: 'EPF',
              value: parseInt(String(epfSummary.currentBalance?.units || 0)),
              gain: 0
            });
          } else if (instrumentType === 'ACC_INSTRUMENT_TYPE_NPS') {
            const npsSummary = accountAny.npsSummary || {};
            holdings.push({
              id: 'nps-' + Math.random().toString(),
              name: 'NPS Account',
              type: 'NPS',
              symbol: 'NPS',
              value: parseInt(String(npsSummary.currentValue?.units || 0)),
              gain: parseInt(String(npsSummary.totalGainValue?.units || 0))
            });
          }
        });
      }



      return {
        totalValue,
        processedAssets,
        holdings,
        performanceData: generatePerformanceData(totalValue)
      };

    } catch (error) {
      console.error('Error processing MCP data:', error);
      throw error;
    }
  }, []);

  // Function to fetch portfolio data from backend
  const fetchPortfolioData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('Fetching portfolio data from MCP server...');
      
      // Use the new portfolio endpoint with MCP integration
      const response = await fetch(`${API_BASE_URL}/portfolio`, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: "demo_user",
          action: "summary"
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Portfolio endpoint response:', data);
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to fetch portfolio data');
      }

      // Process the portfolio data from the agent
      const portfolioData = data.data;
      
      // Extract values from the agent response
      const totalValue = portfolioData.total_value || 0;
      const holdings = portfolioData.holdings || [];
      const assetAllocation = portfolioData.asset_allocation || {};
      
      // Convert agent data to our component format
      const processedAssets = {
        stocks: assetAllocation.get('Equity', 0) || 0,
        mutualFunds: assetAllocation.get('Mutual Fund', 0) || 0,
        savings: assetAllocation.get('Savings', 0) || 0,
        epf: assetAllocation.get('EPF', 0) || 0,
        nps: assetAllocation.get('NPS', 0) || 0,
        others: assetAllocation.get('Others', 0) || 0
      };
      
      // Convert holdings to our format
      const formattedHoldings = holdings.map((holding: any, index: number) => ({
        id: String(index + 1),
        name: holding.name || 'Unknown',
        type: holding.type || 'Other',
        symbol: holding.symbol || 'N/A',
        value: holding.value || 0,
        gain: holding.gain || 0
      }));
      
      setPortfolioData({
        totalValue,
        assets: processedAssets,
        holdings: formattedHoldings
      });
      
      // Generate performance data based on total value
      const performanceData = generatePerformanceData(totalValue);
      setPerformanceData(performanceData);
      setLastUpdated(new Date());

    } catch (error) {
      console.error('Error fetching portfolio data:', error);
      setError(error.message);
      
      // Load mock data for development
      console.log('Loading mock data for development...');
      setPortfolioData({
        totalValue: 500000,
        assets: {
          stocks: 200000,
          mutualFunds: 150000,
          savings: 100000,
          epf: 30000,
          nps: 20000,
          others: 0
        },
        holdings: [
          {
            id: '1',
            name: 'Mock Stock 1',
            type: 'Equity',
            symbol: 'MOCK1',
            value: 100000,
            gain: 5000
          },
          {
            id: '2',
            name: 'Mock Mutual Fund',
            type: 'Mutual Fund',
            symbol: 'MOCKMF',
            value: 150000,
            gain: -2000
          }
        ]
      });
      
      setPerformanceData([
        { month: 'Jan', value: 450000 },
        { month: 'Feb', value: 470000 },
        { month: 'Mar', value: 480000 },
        { month: 'Apr', value: 490000 },
        { month: 'May', value: 485000 },
        { month: 'Jun', value: 500000 }
      ]);
      
      setLastUpdated(new Date());
      setError(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchPortfolioData();
  }, [fetchPortfolioData]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(fetchPortfolioData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchPortfolioData]);

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-zinc-950">
        <div className="text-center">
          <Loader2 className="animate-spin text-4xl text-blue-400 mx-auto mb-4" />
          <div className="text-xl text-zinc-200">Loading Portfolio Data...</div>
          <div className="text-sm text-zinc-400 mt-2">Fetching data from MCP server</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-zinc-950">
        <div className="text-center max-w-md">
          <AlertCircle className="text-4xl text-red-400 mx-auto mb-4" />
          <div className="text-xl text-zinc-200 mb-2">Unable to Load Portfolio</div>
          <div className="text-sm text-zinc-400 mb-4">{error}</div>
          <button
            onClick={fetchPortfolioData}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center gap-2 mx-auto"
          >
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      </div>
    );
  }

  // No data state
  if (!portfolioData || !performanceData) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-zinc-950">
        <div className="text-center">
          <div className="text-xl text-zinc-200">No Portfolio Data Available</div>
          <button
            onClick={fetchPortfolioData}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg mt-4"
          >
            Load Data
          </button>
        </div>
      </div>
    );
  }

  // Debug logging
  console.log('Portfolio data:', portfolioData);
  console.log('Performance data:', performanceData);
  console.log('Assets breakdown:', {
    stocks: portfolioData.assets.stocks,
    mutualFunds: portfolioData.assets.mutualFunds,
    savings: portfolioData.assets.savings,
    epf: portfolioData.assets.epf,
    nps: portfolioData.assets.nps,
    total: portfolioData.totalValue
  });
  
  // Check if data is valid
  if (!portfolioData || !performanceData) {
    console.error('Missing data:', { portfolioData, performanceData });
  }

  // Calculate metrics with safety checks
  const totalGain = portfolioData.holdings.reduce((sum, holding) => {
    const gain = typeof holding.gain === 'number' ? holding.gain : 0;
    return sum + gain;
  }, 0);
  
  const dayPerformance = portfolioData.totalValue > 0 
    ? ((totalGain / portfolioData.totalValue) * 100).toFixed(2)
    : '0.00';

  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      <div className="space-y-10 px-2 md:px-0 pt-6 pb-6 md:pt-10 md:pb-10 max-w-7xl mx-auto">
        
        {/* Header with refresh button */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-white">Portfolio Overview</h1>
            {lastUpdated && (
              <p className="text-sm text-zinc-400">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {
                fetch(`${API_BASE_URL}/chat`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ message: "test", user_id: "demo_user" })
                })
                .then(res => {
                  console.log('API test response status:', res.status);
                  return res.json();
                })
                .then(data => console.log('API test response:', data))
                .catch(err => console.error('API test error:', err));
              }}
              className="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-2 rounded-lg text-sm"
            >
              Test API
            </button>
            <button
              onClick={fetchPortfolioData}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Updating...' : 'Refresh'}
            </button>
          </div>
        </div>

        {/* Professional Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Portfolio Value */}
          <div className="bg-zinc-900 rounded-2xl shadow-md p-6 flex items-center border border-zinc-800 min-h-[140px]">
            <div className="flex-1">
              <div className="text-base font-medium text-zinc-200 mb-1">Portfolio Value</div>
              <div className="text-3xl font-extrabold text-white mb-1">
                ₹{portfolioData.totalValue.toLocaleString()}
              </div>
              <div className={`text-base font-semibold ${totalGain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {totalGain >= 0 ? '+' : ''}₹{totalGain.toLocaleString()}
              </div>
            </div>
            <Wallet className="w-8 h-8 text-blue-400 ml-4" />
          </div>

          {/* Day Performance */}
          <div className="bg-zinc-900 rounded-2xl shadow-md p-6 flex items-center border border-zinc-800 min-h-[140px]">
            <div className="flex-1">
              <div className="text-base font-medium text-zinc-200 mb-1">Performance</div>
              <div className="text-3xl font-extrabold text-white mb-1">{dayPerformance}%</div>
              <div className="text-base font-semibold text-zinc-400">Overall Gain</div>
            </div>
            <TrendingUp className="w-8 h-8 text-green-400 ml-4" />
          </div>

          {/* Holdings Count */}
          <div className="bg-zinc-900 rounded-2xl shadow-md p-6 flex items-center border border-zinc-800 min-h-[140px]">
            <div className="flex-1">
              <div className="text-base font-medium text-zinc-200 mb-1">Holdings</div>
              <div className="text-3xl font-extrabold text-white mb-1">{portfolioData.holdings.length}</div>
              <div className="text-base font-semibold text-zinc-400">Assets</div>
            </div>
            <BarChart3 className="w-8 h-8 text-purple-400 ml-4" />
          </div>

          {/* Top Asset */}
          <div className="bg-zinc-900 rounded-2xl shadow-md p-6 flex items-center border border-zinc-800 min-h-[140px]">
            <div className="flex-1">
              <div className="text-base font-medium text-zinc-200 mb-1">Largest Asset</div>
              <div className="text-lg font-extrabold text-white mb-1">
                {(() => {
                  const maxAsset = Object.entries(portfolioData.assets)
                    .filter(([, value]) => typeof value === 'number' && value > 0)
                    .reduce((a, b) => (a[1] > b[1] ? a : b), ['others', 0]);
                  return maxAsset[0].replace(/([A-Z])/g, ' $1').trim();
                })()}
              </div>
              <div className="text-base font-semibold text-zinc-400">
                ₹{Math.max(...Object.values(portfolioData.assets).filter(v => typeof v === 'number')).toLocaleString()}
              </div>
            </div>
            <Gem className="w-8 h-8 text-yellow-400 ml-4" />
          </div>
        </div>

        {/* Asset Allocation & Performance Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          <div className="bg-zinc-900 rounded-2xl shadow-md p-6 border border-zinc-800 flex flex-col items-center relative">
            <div className="text-lg font-semibold text-zinc-200 mb-4 w-full text-center border-b border-zinc-800 pb-2">
              Asset Allocation
            </div>
            
            {/* Simple Donut Chart */}
            <div className="relative w-64 h-64 flex items-center justify-center">
              <div className="relative w-48 h-48">
                {/* Outer ring */}
                <div className="w-full h-full rounded-full border-8 border-blue-500"></div>
                {/* Inner circle for total */}
                <div className="absolute inset-8 bg-zinc-900 rounded-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">₹{(portfolioData.totalValue/100000).toFixed(1)}L</div>
                    <div className="text-sm text-zinc-400">Total</div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Asset Breakdown */}
            <div className="w-full mt-4 space-y-2">
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full mr-2 bg-blue-500"></div>
                  <span className="text-sm text-zinc-300">Stocks</span>
                </div>
                <span className="text-sm text-zinc-300">₹{portfolioData.assets.stocks.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full mr-2 bg-green-500"></div>
                  <span className="text-sm text-zinc-300">Mutual Funds</span>
                </div>
                <span className="text-sm text-zinc-300">₹{portfolioData.assets.mutualFunds.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full mr-2 bg-orange-500"></div>
                  <span className="text-sm text-zinc-300">Savings</span>
                </div>
                <span className="text-sm text-zinc-300">₹{portfolioData.assets.savings.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full mr-2 bg-purple-500"></div>
                  <span className="text-sm text-zinc-300">EPF</span>
                </div>
                <span className="text-sm text-zinc-300">₹{portfolioData.assets.epf.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full mr-2 bg-red-500"></div>
                  <span className="text-sm text-zinc-300">NPS</span>
                </div>
                <span className="text-sm text-zinc-300">₹{portfolioData.assets.nps.toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className="bg-zinc-900 rounded-2xl shadow-md p-6 border border-zinc-800 flex flex-col">
            <div className="text-lg font-semibold text-zinc-200 mb-4 w-full border-b border-zinc-800 pb-2">
              Portfolio Performance
            </div>
            
            {/* Line Chart */}
            <div className="w-full h-64 relative">
              {performanceData && performanceData.length > 0 && (
                <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                  {/* Grid lines */}
                  <defs>
                    <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                      <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#374151" strokeWidth="0.5"/>
                    </pattern>
                  </defs>
                  <rect width="100" height="100" fill="url(#grid)" />
                  
                  {/* Line chart */}
                  <polyline
                    fill="none"
                    stroke="#6366f1"
                    strokeWidth="2"
                    points={performanceData.map((item, index) => {
                      const x = (index / (performanceData.length - 1)) * 100;
                      const maxValue = Math.max(...performanceData.map(d => d.value));
                      const minValue = Math.min(...performanceData.map(d => d.value));
                      const range = maxValue - minValue;
                      const y = 100 - ((item.value - minValue) / range) * 80 - 10;
                      return `${x},${y}`;
                    }).join(' ')}
                  />
                  
                  {/* Data points */}
                  {performanceData.map((item, index) => {
                    const x = (index / (performanceData.length - 1)) * 100;
                    const maxValue = Math.max(...performanceData.map(d => d.value));
                    const minValue = Math.min(...performanceData.map(d => d.value));
                    const range = maxValue - minValue;
                    const y = 100 - ((item.value - minValue) / range) * 80 - 10;
                    return (
                      <circle
                        key={index}
                        cx={x}
                        cy={y}
                        r="2"
                        fill="#6366f1"
                        stroke="#ffffff"
                        strokeWidth="1"
                      />
                    );
                  })}
                  
                  {/* X-axis labels */}
                  {performanceData.map((item, index) => {
                    const x = (index / (performanceData.length - 1)) * 100;
                    return (
                      <text
                        key={index}
                        x={x}
                        y="95"
                        textAnchor="middle"
                        fontSize="3"
                        fill="#9ca3af"
                      >
                        {item.month}
                      </text>
                    );
                  })}
                </svg>
              )}
            </div>
            
            {/* Performance Summary */}
            <div className="mt-4 p-4 bg-zinc-800 rounded-lg">
              <div className="text-sm text-zinc-400 mb-2">Performance Summary</div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-zinc-400">Current Value</div>
                  <div className="text-white font-semibold">₹{performanceData && performanceData[performanceData.length - 1]?.value.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-zinc-400">6-Month Change</div>
                  <div className="text-green-400 font-semibold">
                    +₹{performanceData && (performanceData[performanceData.length - 1]?.value - performanceData[0]?.value).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Holdings Table */}
        <div className="bg-zinc-900 rounded-2xl shadow-md p-6 border border-zinc-800 mb-8">
          <div className="text-lg font-semibold text-zinc-200 mb-4">All Holdings</div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="text-left py-3 px-4 text-zinc-300">Symbol</th>
                  <th className="text-left py-3 px-4 text-zinc-300">Name</th>
                  <th className="text-left py-3 px-4 text-zinc-300">Type</th>
                  <th className="text-right py-3 px-4 text-zinc-300">Value</th>
                  <th className="text-right py-3 px-4 text-zinc-300">Gain/Loss</th>
                </tr>
              </thead>
              <tbody>
                {portfolioData.holdings
                  .sort((a, b) => b.value - a.value)
                  .map((holding, i) => (
                  <tr key={holding.id} className={i % 2 === 0 ? 'bg-zinc-800 hover:bg-zinc-700' : 'hover:bg-zinc-700'}>
                    <td className="py-3 px-4 font-mono text-blue-300">{holding.symbol}</td>
                    <td className="py-3 px-4">{holding.name}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 rounded-full text-xs bg-zinc-700 text-zinc-300">
                        {holding.type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-semibold">
                      ₹{(typeof holding.value === 'number' ? holding.value : 0).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                        (holding.gain || 0) >= 0 ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                      }`}>
                        {(holding.gain || 0) >= 0 ? '+' : ''}₹{(typeof holding.gain === 'number' ? holding.gain : 0).toLocaleString()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioOverview;