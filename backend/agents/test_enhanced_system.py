# import asyncio
# from core_orchestrator import CoreOrchestratorAgent

# async def test_enhanced_system():
#     """Test the enhanced system with new capabilities."""
#     print("🧪 Testing Enhanced FinSight AI System")
#     print("=" * 50)
    
#     orchestrator = CoreOrchestratorAgent(user_id="test_user_123")
    
#     # Test 1: Portfolio Summary
#     print("\n📊 Test 1: Portfolio Summary")
#     print("-" * 30)
#     try:
#         portfolio_summary = await orchestrator.get_portfolio_summary("test_user_123")
#         print(f"✅ Portfolio Summary: {portfolio_summary}")
#     except Exception as e:
#         print(f"❌ Portfolio Summary Error: {e}")
    
#     # Test 2: Real-time Data Fetch
#     print("\n🔍 Test 2: Real-time Data Fetch")
#     print("-" * 30)
#     try:
#         real_time_data = await orchestrator.fetch_real_time_data("market trends 2024")
#         print(f"✅ Real-time Data: {real_time_data}")
#     except Exception as e:
#         print(f"❌ Real-time Data Error: {e}")
    
#     # Test 3: Comprehensive Analysis
#     print("\n🎯 Test 3: Comprehensive Analysis")
#     print("-" * 30)
#     try:
#         comprehensive_results = await orchestrator.run_comprehensive_analysis(
#             user_id="test_user_123",
#             query="investment opportunities"
#         )
#         print(f"✅ Comprehensive Analysis: {len(comprehensive_results)} components")
#         for key, value in comprehensive_results.items():
#             print(f"   - {key}: {'✅' if value and 'error' not in str(value) else '❌'}")
#     except Exception as e:
#         print(f"❌ Comprehensive Analysis Error: {e}")
    
#     print("\n🎉 Enhanced System Test Completed!")

# if __name__ == "__main__":
#     asyncio.run(test_enhanced_system()) 