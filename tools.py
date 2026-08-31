"""
tools.py - Python Tool Definitions for Personal Budget Assistant Agent

Contains working Python functions that the Agent calls during its plan-act loop.
Each function modifies or queries the underlying BudgetMemory instance.
"""

from typing import Dict, Any, Optional
from memory import BudgetMemory


# Global memory instance for standard tool calls, or can be passed dynamically
_global_memory = BudgetMemory()

def get_memory_instance() -> BudgetMemory:
    """Access the active BudgetMemory instance."""
    return _global_memory

def reset_memory(initial_budget: float = 5000.0) -> BudgetMemory:
    """Reset the global memory state for fresh execution."""
    global _global_memory
    _global_memory = BudgetMemory(initial_budget=initial_budget)
    return _global_memory


def add_expense(item: str, amount: float, category: str = "other") -> Dict[str, Any]:
    """
    Tool 1: Log an expense entry in the budget manager.
    
    Args:
        item: Description of the purchase/expense (e.g. 'Textbooks', 'Groceries')
        amount: Dollar cost of the item (e.g. 150.50)
        category: Category string ('food', 'housing', 'transport', 'entertainment', 'shopping', 'utilities', 'other')
        
    Returns:
        Dict containing status, logged entry details, updated category total, and remaining balance.
    """
    memory = get_memory_instance()
    return memory.log_expense(item=item, amount=amount, category=category)


def get_summary(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool 2: Get financial budget summary, remaining balance, and spending breakdown.
    
    Args:
        category: Optional category name to filter summary (e.g. 'food'). If None, returns overall summary.
        
    Returns:
        Dict containing total budget, total spent, remaining balance, savings goals, and category breakdown.
    """
    memory = get_memory_instance()
    return memory.get_summary(category=category)


def set_savings_goal(target_amount: float, month: str = "this month") -> Dict[str, Any]:
    """
    Tool 3 (Group of 3 Add-on): Set a savings target amount for a given period.
    
    Args:
        target_amount: Target dollar amount to save (e.g. 1000.0)
        month: Month or period description (e.g. 'August')
        
    Returns:
        Dict containing savings target details and whether current remaining balance supports the goal.
    """
    memory = get_memory_instance()
    return memory.set_savings_goal(target_amount=target_amount, month=month)


def check_affordability(expense_name: str, cost: float) -> Dict[str, Any]:
    """
    Tool 4: Evaluate whether a prospective expense or trip can be afforded given current budget & savings goal.
    
    Args:
        expense_name: Name of planned expense (e.g. 'Miami Trip', 'New Laptop')
        cost: Estimated cost of the purchase (e.g. 2000.0)
        
    Returns:
        Dict containing verdict ('AFFORDABLE', 'UNAFFORDABLE', or 'WARNING'), math breakdown, and explanation.
    """
    memory = get_memory_instance()
    return memory.check_affordability(expense_name=expense_name, cost=cost)


# Tool registry for the agent
AVAILABLE_TOOLS = {
    "add_expense": {
        "func": add_expense,
        "description": "Log an expense entry (item, amount, category).",
        "parameters": {"item": "str", "amount": "float", "category": "str"}
    },
    "get_summary": {
        "func": get_summary,
        "description": "Get financial summary and category breakdown (optional category).",
        "parameters": {"category": "str (optional)"}
    },
    "set_savings_goal": {
        "func": set_savings_goal,
        "description": "Set a target savings goal amount (target_amount, month).",
        "parameters": {"target_amount": "float", "month": "str"}
    },
    "check_affordability": {
        "func": check_affordability,
        "description": "Check if a planned expense/trip is affordable given remaining balance & savings goal.",
        "parameters": {"expense_name": "str", "cost": "float"}
    }
}
