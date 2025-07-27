import json
from datetime import datetime

def simulate_enhanced_mcp_data():
    """Simulate enhanced MCP data with all available sources"""
    
    # Simulate comprehensive financial data
    comprehensive_data = {
        "net_worth": {
            "total_net_worth": 5000000,
            "liquid_assets": 2000000,
            "investments": 2500000,
            "real_estate": 500000,
            "last_updated": "2024-01-15T10:30:00Z"
        },
        "bank_transactions": {
            "transactions": [
                {"date": "2024-01-15", "type": "CREDIT", "amount": 75000, "description": "Salary"},
                {"date": "2024-01-14", "type": "DEBIT", "amount": 15000, "description": "Rent"},
                {"date": "2024-01-13", "type": "DEBIT", "amount": 5000, "description": "Utilities"},
                {"date": "2024-01-12", "type": "CREDIT", "amount": 25000, "description": "Freelance Income"}
            ],
            "total_credits": 100000,
            "total_debits": 20000,
            "net_flow": 80000
        },
        "credit_report": {
            "credit_score": 750,
            "credit_limit": 500000,
            "utilization": 0.15,
            "accounts": [
                {"type": "credit_card", "limit": 100000, "balance": 15000},
                {"type": "personal_loan", "limit": 200000, "balance": 50000}
            ],
            "payment_history": "excellent"
        },
        "epf_details": {
            "total_balance": 800000,
            "employer_contribution": 400000,
            "employee_contribution": 400000,
            "interest_rate": 8.1,
            "last_contribution": "2024-01-01"
        },
        "mf_transactions": {
            "transactions": [
                {"fund_name": "HDFC Mid-Cap Opportunities", "type": "PURCHASE", "amount": 50000, "date": "2024-01-10"},
                {"fund_name": "Axis Bluechip Fund", "type": "PURCHASE", "amount": 75000, "date": "2024-01-05"},
                {"fund_name": "SBI Small Cap Fund", "type": "PURCHASE", "amount": 25000, "date": "2024-01-01"}
            ],
            "total_invested": 150000,
            "current_value": 165000,
            "returns": 10.0
        },
        "stock_transactions": {
            "transactions": [
                {"symbol": "HDFCBANK", "type": "BUY", "amount": 100000, "quantity": 100, "date": "2024-01-10"},
                {"symbol": "TCS", "type": "BUY", "amount": 150000, "quantity": 50, "date": "2024-01-05"},
                {"symbol": "RELIANCE", "type": "BUY", "amount": 200000, "quantity": 200, "date": "2024-01-01"},
                {"symbol": "HDFCBANK", "type": "SELL", "amount": 110000, "quantity": 50, "date": "2024-01-12"}
            ],
            "total_invested": 450000,
            "current_value": 480000,
            "returns": 6.7
        }
    }
    
    return comprehensive_data

def generate_enhanced_portfolio_summary(portfolio_data):
    """Generate comprehensive portfolio summary from enhanced MCP data"""
    
    summary = {
        'total_value': 0,
        'holdings_count': 0,
        'asset_allocation': {},
        'top_performers': [],
        'risk_metrics': {},
        'recommendations': [],
        'data_sources': []
    }
    
    # Process net worth data
    if 'net_worth' in portfolio_data:
        net_worth = portfolio_data['net_worth']
        summary['total_value'] = net_worth.get('total_net_worth', 0)
        summary['data_sources'].append('net_worth')
    
    # Process stock transactions
    holdings = []
    if 'stock_transactions' in portfolio_data:
        stock_data = portfolio_data['stock_transactions']
        transactions = stock_data.get('transactions', [])
        
        # Group stock transactions by symbol
        stock_holdings = {}
        for transaction in transactions:
            symbol = transaction.get('symbol', 'UNKNOWN')
            if symbol not in stock_holdings:
                stock_holdings[symbol] = {
                    'name': symbol,
                    'type': 'equity',
                    'value': 0,
                    'return_percentage': 0,
                    'transactions': []
                }
            stock_holdings[symbol]['transactions'].append(transaction)
            stock_holdings[symbol]['value'] += transaction.get('amount', 0)
        
        # Add stock holdings to summary
        for symbol, holding in stock_holdings.items():
            holdings.append(holding)
            summary['holdings_count'] += 1
        
        summary['data_sources'].append('stock_transactions')
    
    # Process mutual fund transactions
    if 'mf_transactions' in portfolio_data:
        mf_data = portfolio_data['mf_transactions']
        mf_transactions = mf_data.get('transactions', [])
        
        # Group MF transactions by fund
        mf_holdings = {}
        for transaction in mf_transactions:
            fund_name = transaction.get('fund_name', 'UNKNOWN')
            if fund_name not in mf_holdings:
                mf_holdings[fund_name] = {
                    'name': fund_name,
                    'type': 'mutual_fund',
                    'value': 0,
                    'return_percentage': 0,
                    'transactions': []
                }
            mf_holdings[fund_name]['transactions'].append(transaction)
            mf_holdings[fund_name]['value'] += transaction.get('amount', 0)
        
        # Add MF holdings to summary
        for fund_name, holding in mf_holdings.items():
            holdings.append(holding)
            summary['holdings_count'] += 1
        
        summary['data_sources'].append('mf_transactions')
    
    # Process EPF details
    if 'epf_details' in portfolio_data:
        epf_data = portfolio_data['epf_details']
        epf_value = epf_data.get('total_balance', 0)
        if epf_value > 0:
            holdings.append({
                'name': 'EPF Account',
                'type': 'epf',
                'value': epf_value,
                'return_percentage': 8.1,  # Typical EPF rate
                'transactions': []
            })
            summary['holdings_count'] += 1
            summary['data_sources'].append('epf_details')
    
    # Calculate asset allocation
    for holding in holdings:
        asset_type = holding.get('type', 'unknown')
        value = holding.get('value', 0)
        if asset_type in summary['asset_allocation']:
            summary['asset_allocation'][asset_type] += value
        else:
            summary['asset_allocation'][asset_type] = value
    
    # Identify top performers (by return percentage)
    sorted_holdings = sorted(holdings, key=lambda x: x.get('return_percentage', 0), reverse=True)
    summary['top_performers'] = sorted_holdings[:3]
    
    # Calculate risk metrics
    total_value = summary['total_value']
    if total_value > 0:
        summary['risk_metrics'] = {
            'diversification_score': min(len(holdings) / 10, 1.0),  # Scale 0-1
            'concentration_risk': 'low' if len(holdings) > 15 else 'medium' if len(holdings) > 8 else 'high',
            'volatility_estimate': 'medium',  # Placeholder for actual calculation
            'data_completeness': len(summary['data_sources']) / 4  # Scale based on available data sources
        }
    
    # Generate recommendations based on portfolio analysis
    if summary['risk_metrics']['concentration_risk'] == 'high':
        summary['recommendations'].append('Consider diversifying your portfolio to reduce concentration risk')
    
    if summary['total_value'] < 100000:
        summary['recommendations'].append('Consider increasing your investment amount for better returns')
    
    if len(summary['data_sources']) < 3:
        summary['recommendations'].append('Connect more financial accounts for comprehensive analysis')
    
    # Add data quality note
    summary['data_quality'] = {
        'sources_connected': len(summary['data_sources']),
        'total_possible_sources': 4,
        'completeness_percentage': (len(summary['data_sources']) / 4) * 100
    }
    
    return summary

def test_enhanced_mcp_capabilities():
    """Test the enhanced MCP capabilities with simulated data"""
    print("🧪 Testing Enhanced MCP Capabilities")
    print("=" * 50)
    
    # Simulate comprehensive MCP data
    portfolio_data = simulate_enhanced_mcp_data()
    
    print("📊 Available Data Sources:")
    print("-" * 30)
    for source in portfolio_data.keys():
        print(f"✅ {source.replace('_', ' ').title()}")
    
    # Generate comprehensive portfolio summary
    print(f"\n🎯 Generating Comprehensive Portfolio Summary...")
    portfolio_summary = generate_enhanced_portfolio_summary(portfolio_data)
    
    print(f"\n📊 Portfolio Summary Results:")
    print("-" * 40)
    print(f"💰 Total Value: ₹{portfolio_summary['total_value']:,}")
    print(f"📈 Holdings Count: {portfolio_summary['holdings_count']}")
    print(f"⚖️ Asset Allocation: {portfolio_summary['asset_allocation']}")
    print(f"🎯 Top Performers: {len(portfolio_summary['top_performers'])} holdings")
    print(f"⚠️ Risk Level: {portfolio_summary['risk_metrics']['concentration_risk']}")
    print(f"📊 Diversification Score: {portfolio_summary['risk_metrics']['diversification_score']:.2f}")
    print(f"📋 Data Sources: {portfolio_summary['data_sources']}")
    print(f"📈 Data Quality: {portfolio_summary['data_quality']['completeness_percentage']}%")
    
    print(f"\n💡 Recommendations:")
    print("-" * 20)
    for rec in portfolio_summary['recommendations']:
        print(f"• {rec}")
    
    # Calculate capital gains from stock transactions
    print(f"\n💸 Capital Gains Analysis:")
    print("-" * 30)
    stock_transactions = portfolio_data['stock_transactions']
    total_buy = sum(t['amount'] for t in stock_transactions['transactions'] if t['type'] == 'BUY')
    total_sell = sum(t['amount'] for t in stock_transactions['transactions'] if t['type'] == 'SELL')
    net_gain = total_sell - total_buy
    
    print(f"   Total Buy Value: ₹{total_buy:,}")
    print(f"   Total Sell Value: ₹{total_sell:,}")
    print(f"   Net Capital Gains: ₹{max(0, net_gain):,}")
    print(f"   Estimated Tax (15% STCG): ₹{max(0, net_gain) * 0.15:,}")
    
    # Income analysis from bank transactions
    print(f"\n💰 Income Analysis:")
    print("-" * 20)
    bank_transactions = portfolio_data['bank_transactions']
    total_credits = bank_transactions['total_credits']
    total_debits = bank_transactions['total_debits']
    net_income = bank_transactions['net_flow']
    
    print(f"   Total Credits: ₹{total_credits:,}")
    print(f"   Total Debits: ₹{total_debits:,}")
    print(f"   Net Income Flow: ₹{net_income:,}")
    
    # Credit health
    print(f"\n💳 Credit Health:")
    print("-" * 15)
    credit_report = portfolio_data['credit_report']
    print(f"   Credit Score: {credit_report['credit_score']}")
    print(f"   Credit Utilization: {credit_report['utilization'] * 100:.1f}%")
    print(f"   Payment History: {credit_report['payment_history']}")
    
    # EPF analysis
    print(f"\n🏦 EPF Analysis:")
    print("-" * 15)
    epf_details = portfolio_data['epf_details']
    print(f"   Total Balance: ₹{epf_details['total_balance']:,}")
    print(f"   Interest Rate: {epf_details['interest_rate']}%")
    print(f"   Last Contribution: {epf_details['last_contribution']}")
    
    print(f"\n✨ Enhanced MCP Capabilities Demonstrated:")
    print("-" * 50)
    print("✅ Multi-source data integration")
    print("✅ Comprehensive portfolio analysis")
    print("✅ Capital gains calculation")
    print("✅ Income flow analysis")
    print("✅ Credit health monitoring")
    print("✅ Retirement planning (EPF)")
    print("✅ Risk assessment and recommendations")
    print("✅ Data quality metrics")
    
    # Save results
    results = {
        'portfolio_data': portfolio_data,
        'portfolio_summary': portfolio_summary,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('enhanced_mcp_demo_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Demo results saved to 'enhanced_mcp_demo_results.json'")
    
    return results

if __name__ == "__main__":
    test_enhanced_mcp_capabilities() 