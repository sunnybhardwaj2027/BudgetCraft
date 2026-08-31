"""
test_agent.py - Comprehensive Unit & Integration Tests for Personal Budget Assistant Agent

Verifies:
1. Tool execution & memory updates (add_expense, get_summary, set_savings_goal, check_affordability).
2. Agent ReAct multi-step reasoning and plan execution.
3. Conversational memory persistence across turns.
"""

import sys
from memory import BudgetMemory
from tools import reset_memory, add_expense, get_summary, set_savings_goal, check_affordability
from agent import PersonalBudgetAgent


def test_tools_and_memory():
    """Test standard tool functions and memory state modifications."""
    mem = reset_memory(initial_budget=5000.0)
    
    # 1. Add expenses
    res1 = add_expense(item="Textbooks", amount=150.0, category="shopping")
    assert res1["status"] == "success"
    assert res1["category_total"] == 150.0
    assert res1["remaining_balance"] == 4850.0

    res2 = add_expense(item="Groceries", amount=80.0, category="food")
    assert res2["status"] == "success"
    assert res2["remaining_balance"] == 4770.0

    # 2. Get summary
    sum_res = get_summary()
    assert sum_res["total_spent"] == 230.0
    assert sum_res["remaining_balance"] == 4770.0
    assert sum_res["category_breakdown"]["shopping"] == 150.0
    assert sum_res["category_breakdown"]["food"] == 80.0

    # 3. Set savings goal
    sg_res = set_savings_goal(target_amount=1000.0, month="August")
    assert sg_res["status"] == "success"
    assert sg_res["is_achievable"] is True

    # 4. Check affordability
    aff_res = check_affordability(expense_name="Weekend Trip", cost=2000.0)
    assert aff_res["verdict"] == "AFFORDABLE"
    assert aff_res["balance_after_purchase"] == 2770.0

    aff_expensive = check_affordability(expense_name="Luxury Cruise", cost=4000.0)
    assert aff_expensive["verdict"] == "WARNING_AFFORDABLE_BUT_COMPROMISES_SAVINGS"
    print("✅ test_tools_and_memory PASSED")


def test_agent_react_loop():
    """Test agent ReAct multi-step planning and tool execution."""
    mem = reset_memory(initial_budget=5000.0)
    agent = PersonalBudgetAgent(memory=mem, verbose=False)

    # Goal 1: Log expenses
    goal1 = "Log $150 spent on textbooks and $80 on groceries"
    res1 = agent.run(goal1)
    
    assert len(res1["trace_steps"]) >= 2  # Multi-step!
    assert any(t["action"] == "add_expense" for t in res1["trace_steps"])
    assert any(t["action"] == "get_summary" for t in res1["trace_steps"])
    assert "4770.00" in res1["final_answer"]

    # Goal 2: Set savings goal
    goal2 = "Set a savings goal of 1000 for August"
    res2 = agent.run(goal2)
    assert any(t["action"] == "set_savings_goal" for t in res2["trace_steps"])

    # Goal 3: Multi-step affordability query using memory from Turn 1 and Turn 2
    goal3 = "Can I afford a 2000 trip?"
    res3 = agent.run(goal3)
    assert any(t["action"] == "check_affordability" for t in res3["trace_steps"])
    assert "AFFORDABLE" in res3["final_answer"] or "affordable" in res3["final_answer"].lower()

    # Turn history memory check
    history_ctx = mem.get_conversation_context()
    assert "Turn 1" in history_ctx
    assert "Turn 2" in history_ctx
    assert "Turn 3" in history_ctx
    print("✅ test_agent_react_loop PASSED")


if __name__ == "__main__":
    print("Running test suite...")
    test_tools_and_memory()
    test_agent_react_loop()
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
