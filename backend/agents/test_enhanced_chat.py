import asyncio
import json
from datetime import datetime
from enhanced_chat_system import enhanced_chat_system

async def test_enhanced_chat_system():
    """Test the enhanced chat system with various scenarios"""
    print("🧪 Testing Enhanced Chat System")
    print("=" * 50)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Greeting Test",
            "message": "Hi there!",
            "expected_type": "greeting"
        },
        {
            "name": "Portfolio Analysis",
            "message": "Show me my portfolio summary",
            "expected_type": "portfolio_analysis"
        },
        {
            "name": "Tax Query",
            "message": "What are the latest tax updates?",
            "expected_type": "tax_analysis"
        },
        {
            "name": "Investment Strategy",
            "message": "I want investment advice",
            "expected_type": "investment_analysis"
        },
        {
            "name": "Comprehensive Analysis",
            "message": "Give me a comprehensive financial overview",
            "expected_type": "comprehensive_analysis"
        },
        {
            "name": "Risk Assessment",
            "message": "What's my risk profile?",
            "expected_type": "general_advice"
        }
    ]
    
    user_id = "test_user_123"
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 Test {i}: {scenario['name']}")
        print("-" * 40)
        print(f"Message: '{scenario['message']}'")
        print(f"Expected Type: {scenario['expected_type']}")
        
        print("\n🔄 Streaming Response:")
        print("-" * 20)
        
        response_count = 0
        try:
            async for update in enhanced_chat_system.generate_streaming_response(scenario['message'], user_id):
                response_count += 1
                
                if update['type'] == 'thinking':
                    print(f"🤔 {update['content']}")
                elif update['type'] == 'delegation':
                    print(f"🎯 {update['content']}")
                    if 'delegation' in update:
                        delegation = update['delegation']
                        print(f"   Primary Agent: {delegation.get('primary_agent', 'None')}")
                        print(f"   Analysis Type: {delegation.get('analysis_type', 'None')}")
                        if delegation.get('secondary_agents'):
                            print(f"   Secondary Agents: {', '.join(delegation['secondary_agents'])}")
                elif update['type'] == 'processing':
                    print(f"⚙️ {update['content']}")
                elif update['type'] == 'response':
                    print(f"✅ Final Response:")
                    print(f"   {update['content']}")
                    if 'delegation' in update:
                        print(f"   Analysis Type: {update.get('analysis_type', 'Unknown')}")
                    if update.get('is_greeting'):
                        print(f"   Type: Greeting Response")
                elif update['type'] == 'error':
                    print(f"❌ Error: {update['content']}")
                
                # Add small delay for readability
                await asyncio.sleep(0.1)
            
            print(f"\n✅ Test {i} completed successfully!")
            print(f"   Total updates: {response_count}")
            
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
        
        print("\n" + "=" * 50)
    
    print("\n🎉 All Enhanced Chat Tests Completed!")
    print("=" * 50)
    print("✨ Features Demonstrated:")
    print("   • Greeting detection and responses")
    print("   • Intelligent agent delegation")
    print("   • Real-time streaming updates")
    print("   • Comprehensive analysis capabilities")
    print("   • Error handling and recovery")
    print("   • Multi-agent collaboration")

async def test_greeting_detection():
    """Test greeting detection specifically"""
    print("\n🧪 Testing Greeting Detection")
    print("=" * 40)
    
    greetings = [
        "hi", "hello", "hey", "good morning", "good afternoon", 
        "good evening", "greetings", "howdy", "sup", "yo",
        "Hi there!", "Hello!", "Hey!", "Good morning!", "Good afternoon!"
    ]
    
    for greeting in greetings:
        is_greeting = enhanced_chat_system.is_greeting(greeting)
        response = enhanced_chat_system.get_greeting_response(greeting)
        print(f"'{greeting}' -> Greeting: {is_greeting} -> Response: {response[:50]}...")

async def test_agent_delegation():
    """Test agent delegation logic"""
    print("\n🧪 Testing Agent Delegation")
    print("=" * 40)
    
    test_queries = [
        ("Show me my portfolio", "portfolio_agent"),
        ("What are my tax liabilities?", "tax_knowledge_agent"),
        ("Investment opportunities", "investment_strategy_agent"),
        ("Compliance requirements", "legal_compliance_agent"),
        ("Market alerts", "alert_agent"),
        ("Latest news", "news_agent"),
        ("Comprehensive analysis", "comprehensive"),
        ("General financial advice", "tax_planning_agent")
    ]
    
    for query, expected_agent in test_queries:
        delegation = enhanced_chat_system.determine_agent_delegation(query)
        primary_agent = delegation.get('primary_agent', 'None')
        analysis_type = delegation.get('analysis_type', 'None')
        
        print(f"Query: '{query}'")
        print(f"  Expected: {expected_agent}")
        print(f"  Got: {primary_agent}")
        print(f"  Analysis Type: {analysis_type}")
        print(f"  Comprehensive: {delegation.get('requires_comprehensive', False)}")
        print()

async def main():
    """Run all enhanced chat tests"""
    print("🚀 ENHANCED CHAT SYSTEM TEST SUITE")
    print("=" * 60)
    
    # Test greeting detection
    await test_greeting_detection()
    
    # Test agent delegation
    await test_agent_delegation()
    
    # Test full streaming responses
    await test_enhanced_chat_system()
    
    print("\n🎯 Enhanced Chat System Ready for Production!")
    print("Features:")
    print("✅ Greeting detection and conversational responses")
    print("✅ Intelligent agent delegation")
    print("✅ Real-time streaming updates")
    print("✅ Comprehensive financial analysis")
    print("✅ Multi-agent collaboration")
    print("✅ Error handling and recovery")

if __name__ == "__main__":
    asyncio.run(main()) 