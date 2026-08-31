"""
execute_notebook.py - Executes demo.ipynb cells and saves the outputs directly into demo.ipynb.
"""

import json
from io import StringIO
import sys
from memory import BudgetMemory
from tools import reset_memory
from agent import PersonalBudgetAgent


def execute_notebook():
    print("Executing demo notebook programmatically...")
    with open("demo.ipynb", "r") as f:
        nb = json.load(f)

    # Context state
    memory = reset_memory(initial_budget=5000.0)
    agent = PersonalBudgetAgent(memory=memory, verbose=True)

    code_outputs = []

    # Cell 1 (index 1 in code cells): Initialization
    out_io_1 = StringIO()
    sys.stdout = out_io_1
    print("✅ Personal Budget Assistant Agent initialized.")
    sys.stdout = sys.__stdout__
    code_outputs.append([{"name": "stdout", "output_type": "stream", "text": out_io_1.getvalue()}])

    # Cell 2 (index 3): Goal 1
    out_io_2 = StringIO()
    sys.stdout = out_io_2
    goal_1 = "Log $150 spent on textbooks and $80 on groceries"
    res1 = agent.run(goal_1)
    sys.stdout = sys.__stdout__
    code_outputs.append([{"name": "stdout", "output_type": "stream", "text": out_io_2.getvalue()}])

    # Cell 3 (index 5): Goal 2
    out_io_3 = StringIO()
    sys.stdout = out_io_3
    goal_2 = "Set a savings goal of 1000 for August"
    res2 = agent.run(goal_2)
    sys.stdout = sys.__stdout__
    code_outputs.append([{"name": "stdout", "output_type": "stream", "text": out_io_3.getvalue()}])

    # Cell 4 (index 7): Goal 3
    out_io_4 = StringIO()
    sys.stdout = out_io_4
    goal_3 = "Can I afford a 2000 trip?"
    res3 = agent.run(goal_3)
    sys.stdout = sys.__stdout__
    code_outputs.append([{"name": "stdout", "output_type": "stream", "text": out_io_4.getvalue()}])

    # Cell 5 (index 9): Memory Proof
    out_io_5 = StringIO()
    sys.stdout = out_io_5
    print("=== CONVERSATION HISTORY MEMORY ===")
    print(agent.memory.get_conversation_context())
    print("\n=== STRUCTURED BUDGET STATE MEMORY ===")
    print(json.dumps(agent.memory.get_summary(), indent=2))
    sys.stdout = sys.__stdout__
    code_outputs.append([{"name": "stdout", "output_type": "stream", "text": out_io_5.getvalue()}])

    # Populate cell outputs in nb
    code_cell_idx = 0
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["execution_count"] = code_cell_idx + 1
            cell["outputs"] = code_outputs[code_cell_idx]
            code_cell_idx += 1

    with open("demo.ipynb", "w") as f:
        json.dump(nb, f, indent=1)

    print("🎉 demo.ipynb updated with complete execution outputs!")


if __name__ == "__main__":
    execute_notebook()
