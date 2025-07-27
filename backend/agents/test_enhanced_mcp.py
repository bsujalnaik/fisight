import asyncio
import json
from mcp_service import mcp_service

async def test_enhanced_mcp():
    """Test the enhanced MCP service with all available data sources."""
    print("🧪 Testing Enhanced MCP Service")
    print("=" * 50)
    
    user_id = "test_user_123"
    
    # Test all available MCP data sources
    data_sources = [
        ("Net Worth", mcp_service.fetch_net_worth),
        ("Bank Transactions", mcp_service.fetch_bank_transactions),
        ("Credit Report", mcp_service.fetch_credit_report),
        ("EPF Details", mcp_service.fetch_epf_details),
        ("Mutual Fund Transactions", mcp_service.fetch_mf_transactions),
        ("Stock Transactions", mcp_service.fetch_stock_transactions),
        ("Portfolio (Comprehensive)", mcp_service.fetch_portfolio),
        ("Capital Gains", mcp_service.fetch_capital_gains),
        ("Income Tax", mcp_service.fetch_income_tax),
        ("Tax Planning", mcp_service.fetch_tax_planning),
        ("Tax Info", mcp_service.fetch_tax_info)
    ]
    
    results = {}
    
    for source_name, fetch_function in data_sources:
        print(f"\n📊 Testing {source_name}...")
        try:
            result = await fetch_function(user_id)
            if 'error' not in result:
                print(f"✅ {source_name}: Success")
                results[source_name] = {
                    'status': 'success',
                    'data_keys': list(result.keys()) if isinstance(result, dict) else 'N/A'
                }
            else:
                print(f"❌ {source_name}: {result['error']}")
                results[source_name] = {
                    'status': 'error',
                    'error': result['error']
                }
        except Exception as e:
            print(f"❌ {source_name}: Exception - {e}")
            results[source_name] = {
                'status': 'exception',
                'error': str(e)
            }
    
    # Test comprehensive portfolio summary
    print(f"\n🎯 Testing Comprehensive Portfolio Summary...")
    try:
        from portfolio.agent import generate_portfolio_summary
        portfolio_summary = await generate_portfolio_summary(user_id)
        if 'error' not in portfolio_summary:
            print(f"✅ Portfolio Summary: Success")
            print(f"   - Total Value: ₹{portfolio_summary.get('total_value', 0):,}")
            print(f"   - Holdings Count: {portfolio_summary.get('holdings_count', 0)}")
            print(f"   - Data Sources: {portfolio_summary.get('data_sources', [])}")
            print(f"   - Data Quality: {portfolio_summary.get('data_quality', {}).get('completeness_percentage', 0)}%")
            results['Portfolio Summary'] = {
                'status': 'success',
                'summary': portfolio_summary
            }
        else:
            print(f"❌ Portfolio Summary: {portfolio_summary['error']}")
            results['Portfolio Summary'] = {
                'status': 'error',
                'error': portfolio_summary['error']
            }
    except Exception as e:
        print(f"❌ Portfolio Summary: Exception - {e}")
        results['Portfolio Summary'] = {
            'status': 'exception',
            'error': str(e)
        }
    
    # Summary
    print(f"\n📋 Test Summary:")
    print("-" * 30)
    successful = sum(1 for r in results.values() if r['status'] == 'success')
    total = len(results)
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    # Save detailed results
    with open('enhanced_mcp_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to 'enhanced_mcp_test_results.json'")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_enhanced_mcp()) 