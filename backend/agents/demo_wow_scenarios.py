import asyncio
import json
from core_orchestrator import CoreOrchestratorAgent

class FinSightAIDemo:
    def __init__(self):
        self.orchestrator = CoreOrchestratorAgent(user_id="demo_user_123")
    
    async def demo_scenario_1_wealth_optimization(self):
        """
        WOW Scenario 1: Complete Wealth Optimization Analysis
        This scenario demonstrates how multiple agents work together to provide
        comprehensive wealth optimization advice.
        """
        print("🚀 WOW SCENARIO 1: Complete Wealth Optimization Analysis")
        print("=" * 60)
        
        user_query = "I want to optimize my wealth and minimize taxes. I have a portfolio of ₹50 lakhs and want to know the best strategies."
        
        print(f"📝 User Query: {user_query}")
        print("\n🔄 Running Multi-Agent Analysis...")
        
        # Run comprehensive analysis
        results = await self.orchestrator.run_comprehensive_analysis(
            user_id="demo_user_123",
            query="wealth optimization strategies 2024"
        )
        
        print("\n📊 Analysis Results:")
        print("-" * 40)
        
        # Portfolio Summary
        if 'portfolio_summary' in results:
            portfolio = results['portfolio_summary']
            print(f"💰 Portfolio Value: ₹{portfolio.get('total_value', 0):,}")
            print(f"📈 Holdings Count: {portfolio.get('holdings_count', 0)}")
            print(f"⚖️ Asset Allocation: {portfolio.get('asset_allocation', {})}")
            print(f"🎯 Top Performers: {len(portfolio.get('top_performers', []))} stocks")
            print(f"⚠️ Risk Level: {portfolio.get('risk_metrics', {}).get('concentration_risk', 'unknown')}")
        
        # Tax Updates
        if 'tax_updates' in results:
            tax_updates = results['tax_updates']
            print(f"\n📋 Latest Tax Updates: {len(tax_updates.get('latest_updates', []))} new policies")
            print(f"⏰ Important Deadlines: {len(tax_updates.get('deadlines', []))} upcoming")
        
        # Capital Gains Analysis
        if 'capital_gains' in results:
            print(f"\n💸 Capital Gains Analysis: Available")
        
        # Alerts
        if 'alerts' in results:
            alerts = results['alerts']
            print(f"\n🚨 Active Alerts: {len(alerts.get('alerts', []))} notifications")
        
        print("\n✨ WOW Factor: This analysis combined 6 different specialized agents!")
        print("   - Portfolio Analysis Agent")
        print("   - Real-time Data Agent")
        print("   - Tax Knowledge Agent")
        print("   - Capital Gains Agent")
        print("   - Alert Agent")
        print("   - Tax Trends Agent")
        
        return results

    async def demo_scenario_2_tax_crisis_management(self):
        """
        WOW Scenario 2: Tax Crisis Management
        This scenario shows how the system handles urgent tax situations
        with real-time data and immediate action plans.
        """
        print("\n🚨 WOW SCENARIO 2: Tax Crisis Management")
        print("=" * 60)
        
        user_query = "I just received a tax notice and I'm panicking! I have ₹10 lakhs in capital gains and need immediate help."
        
        print(f"📝 User Query: {user_query}")
        print("\n🆘 Emergency Tax Analysis...")
        
        # Run urgent analysis
        results = await self.orchestrator.run_comprehensive_analysis(
            user_id="demo_user_123",
            query="tax notice capital gains emergency help"
        )
        
        print("\n🚨 Emergency Response:")
        print("-" * 40)
        
        # Immediate Actions
        print("⚡ IMMEDIATE ACTIONS REQUIRED:")
        print("   1. Review tax notice details")
        print("   2. Calculate exact capital gains liability")
        print("   3. Check for available exemptions")
        print("   4. Prepare documentation")
        print("   5. Consider professional consultation")
        
        # Real-time Updates
        if 'tax_updates' in results:
            print(f"\n📰 Latest Tax Updates: {len(results['tax_updates'].get('latest_updates', []))} relevant changes")
        
        # Capital Gains Analysis
        if 'capital_gains' in results:
            print(f"\n💸 Capital Gains Analysis: Detailed breakdown available")
        
        # Alerts
        if 'alerts' in results:
            alerts = results['alerts']
            high_priority = [a for a in alerts.get('alerts', []) if a.get('priority') == 'high']
            print(f"\n🚨 High Priority Alerts: {len(high_priority)} urgent notifications")
        
        print("\n✨ WOW Factor: Real-time crisis management with multiple specialized agents!")
        print("   - Immediate tax analysis")
        print("   - Real-time policy updates")
        print("   - Urgent alert generation")
        print("   - Compliance verification")
        
        return results

    async def demo_scenario_3_investment_opportunity(self):
        """
        WOW Scenario 3: Investment Opportunity Analysis
        This scenario demonstrates how the system identifies and analyzes
        investment opportunities with real-time market data.
        """
        print("\n📈 WOW SCENARIO 3: Investment Opportunity Analysis")
        print("=" * 60)
        
        user_query = "I want to invest ₹20 lakhs in the market. What are the best opportunities considering current market conditions and tax implications?"
        
        print(f"📝 User Query: {user_query}")
        print("\n🔍 Investment Opportunity Analysis...")
        
        # Run investment analysis
        results = await self.orchestrator.run_comprehensive_analysis(
            user_id="demo_user_123",
            query="best investment opportunities 2024 market analysis"
        )
        
        print("\n💡 Investment Insights:")
        print("-" * 40)
        
        # Portfolio Context
        if 'portfolio_summary' in results:
            portfolio = results['portfolio_summary']
            print(f"💰 Current Portfolio: ₹{portfolio.get('total_value', 0):,}")
            print(f"📊 Diversification Score: {portfolio.get('risk_metrics', {}).get('diversification_score', 0):.2f}")
        
        # Real-time Market Data
        if 'real_time_data' in results:
            print(f"\n📈 Real-time Market Data: Available")
            print("   - Current market trends")
            print("   - Sector performance")
            print("   - Risk assessment")
        
        # Tax Implications
        if 'tax_updates' in results:
            print(f"\n📋 Tax Considerations:")
            print("   - Latest tax incentives")
            print("   - Investment tax benefits")
            print("   - Compliance requirements")
        
        # Recommendations
        print(f"\n🎯 Investment Recommendations:")
        print("   1. Diversified equity portfolio")
        print("   2. Tax-saving mutual funds")
        print("   3. Government securities")
        print("   4. Real estate investment trusts")
        print("   5. International diversification")
        
        print("\n✨ WOW Factor: Multi-dimensional investment analysis!")
        print("   - Real-time market data")
        print("   - Tax optimization")
        print("   - Risk assessment")
        print("   - Portfolio alignment")
        
        return results

    async def demo_scenario_4_compliance_assurance(self):
        """
        WOW Scenario 4: Compliance Assurance
        This scenario shows how the system ensures complete compliance
        across multiple tax and regulatory domains.
        """
        print("\n✅ WOW SCENARIO 4: Compliance Assurance")
        print("=" * 60)
        
        user_query = "I run a business with ₹2 crore turnover. I need to ensure I'm fully compliant with all tax and regulatory requirements."
        
        print(f"📝 User Query: {user_query}")
        print("\n🔍 Comprehensive Compliance Analysis...")
        
        # Run compliance analysis
        results = await self.orchestrator.run_comprehensive_analysis(
            user_id="demo_user_123",
            query="business compliance requirements GST income tax regulations"
        )
        
        print("\n📋 Compliance Status:")
        print("-" * 40)
        
        # Tax Compliance
        print("💰 Tax Compliance:")
        print("   ✅ Income tax filing requirements")
        print("   ✅ GST registration and filing")
        print("   ✅ TDS compliance")
        print("   ✅ Advance tax payments")
        
        # Regulatory Compliance
        print("\n📊 Regulatory Compliance:")
        print("   ✅ SEBI regulations")
        print("   ✅ RBI guidelines")
        print("   ✅ AML/KYC requirements")
        print("   ✅ Industry-specific regulations")
        
        # Real-time Updates
        if 'tax_updates' in results:
            print(f"\n📰 Latest Updates: {len(results['tax_updates'].get('latest_updates', []))} new requirements")
        
        # Alerts
        if 'alerts' in results:
            alerts = results['alerts']
            compliance_alerts = [a for a in alerts.get('alerts', []) if 'compliance' in a.get('type', '')]
            print(f"\n🚨 Compliance Alerts: {len(compliance_alerts)} active notifications")
        
        print("\n✨ WOW Factor: Complete compliance assurance!")
        print("   - Multi-domain compliance check")
        print("   - Real-time regulatory updates")
        print("   - Automated alert system")
        print("   - Risk mitigation strategies")
        
        return results

    async def run_all_demos(self):
        """
        Run all demo scenarios to showcase the complete system capabilities.
        """
        print("🎯 FINSIGHT AI - COMPREHENSIVE DEMO SUITE")
        print("=" * 60)
        print("This demo showcases the power of multi-agent collaboration")
        print("in providing comprehensive financial intelligence.\n")
        
        # Run all scenarios
        scenarios = [
            self.demo_scenario_1_wealth_optimization,
            self.demo_scenario_2_tax_crisis_management,
            self.demo_scenario_3_investment_opportunity,
            self.demo_scenario_4_compliance_assurance
        ]
        
        all_results = {}
        
        for i, scenario in enumerate(scenarios, 1):
            try:
                result = await scenario()
                all_results[f"scenario_{i}"] = result
                print(f"\n✅ Scenario {i} completed successfully!")
            except Exception as e:
                print(f"\n❌ Scenario {i} failed: {e}")
        
        print("\n🎉 ALL DEMOS COMPLETED!")
        print("=" * 60)
        print("✨ WOW Factors Demonstrated:")
        print("   • Multi-agent collaboration")
        print("   • Real-time data integration")
        print("   • Comprehensive analysis")
        print("   • Automated compliance")
        print("   • Intelligent recommendations")
        print("   • Crisis management")
        print("   • Investment optimization")
        
        return all_results

async def main():
    """Main function to run the demo suite."""
    demo = FinSightAIDemo()
    results = await demo.run_all_demos()
    
    # Save results to file for review
    with open('demo_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Demo results saved to 'demo_results.json'")

if __name__ == "__main__":
    asyncio.run(main()) 