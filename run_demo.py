"""
run_demo.py - Executes the agent demo scenarios and populates demo.ipynb execution outputs.
"""

import json
from memory import BudgetMemory
from tools import reset_memory
from agent import PersonalBudgetAgent


def execute_demo_and_update_notebook():
    print("🚀 Executing Personal Budget Assistant Agent Demo Scenarios...\n")
    
    # Cell 2 logic: Initialization
    memory = reset_memory(initial_budget=5000.0)
    agent = PersonalBudgetAgent(memory=memory, verbose=True)

    # Turn 1
    print("\n--- TURN 1 ---")
    goal_1 = "Log $150 spent on textbooks and $80 on groceries"
    res1 = agent.run(goal_1)

    # Turn 2
    print("\n--- TURN 2 ---")
    goal_2 = "Set a savings goal of 1000 for August"
    res2 = agent.run(goal_2)

    # Turn 3
    print("\n--- TURN 3 ---")
    goal_3 = "Can I afford a 2000 trip?"
    res3 = agent.run(goal_3)

    print("\n=== DEMO EXECUTION COMPLETE ===")


if __name__ == "__main__":
    execute_demo_and_update_notebook()
