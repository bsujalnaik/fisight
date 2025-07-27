import asyncio
from core_orchestrator import CoreOrchestratorAgent

async def main():
    user_id = "test_user_123"
    tickers = ["AAPL", "GOOGL"]
    app_name = "test_app"

    orchestrator = CoreOrchestratorAgent(user_id=user_id)

    print("--- Capital Gains Test ---")
    capital_gains_result = await orchestrator.ask_capital_gains(user_id=user_id)
    print(capital_gains_result)

    print("\n--- Sequential Workflow ---")
    seq_results = await orchestrator.run_sequential_workflow(user_id=user_id, tickers=tickers)
    print(seq_results)

    print("\n--- Parallel Workflow ---")
    par_results = await orchestrator.run_parallel_workflow(user_id=user_id, tickers=tickers)
    print(par_results)

    print("\n--- Session Creation ---")
    session = await orchestrator.create_session(app_name=app_name, user_id=user_id)
    print(session)

    print("\n--- Add Session to Memory ---")
    mem_result = await orchestrator.add_session_to_memory(session)
    print(mem_result)

if __name__ == "__main__":
    asyncio.run(main()) 