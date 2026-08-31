"""
memory.py - State & Conversational Memory for Personal Budget Assistant Agent

Maintains both structured domain state (expenses, category totals, savings goals, monthly budget)
and conversational turn-by-turn memory across the session.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class BudgetMemory:
    """
    Stateful memory component for the Personal Budget Assistant Agent.
    Retains expense logs, budget parameters, savings targets, and message turn history.
    """

    def __init__(self, initial_budget: float = 5000.0):
        self.monthly_budget: float = initial_budget
        self.savings_goal: Optional[Dict[str, Any]] = None
        self.expenses: List[Dict[str, Any]] = []
        self.conversation_history: List[Dict[str, Any]] = []
        self.category_budgets: Dict[str, float] = {
            "food": 1500.0,
            "housing": 1500.0,
            "transport": 500.0,
            "entertainment": 500.0,
            "shopping": 500.0,
            "utilities": 500.0,
            "other": 500.0
        }

    def log_expense(self, item: str, amount: float, category: str) -> Dict[str, Any]:
        """Record an expense entry and update state."""
        category = category.lower().strip()
        entry = {
            "item": item,
            "amount": round(float(amount), 2),
            "category": category,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.expenses.append(entry)
        
        category_total = self.get_category_total(category)
        total_spent = self.get_total_spent()
        remaining_balance = round(self.monthly_budget - total_spent, 2)
        category_limit = self.category_budgets.get(category, 500.0)
        is_overspent = category_total > category_limit

        return {
            "status": "success",
            "message": f"Logged expense '{item}' of ${amount:.2f} under category '{category}'.",
            "logged_entry": entry,
            "category_total": category_total,
            "category_limit": category_limit,
            "is_overspent": is_overspent,
            "remaining_balance": remaining_balance
        }

    def get_category_total(self, category: str) -> float:
        """Calculate total amount spent in a given category."""
        cat = category.lower().strip()
        return round(sum(e["amount"] for e in self.expenses if e["category"] == cat), 2)

    def get_total_spent(self) -> float:
        """Calculate total spending across all categories."""
        return round(sum(e["amount"] for e in self.expenses), 2)

    def get_summary(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a detailed financial summary.
        If category is provided, returns specific details for that category.
        Otherwise, returns overall budget summary and breakdown.
        """
        total_spent = self.get_total_spent()
        remaining_balance = round(self.monthly_budget - total_spent, 2)
        
        # Category breakdown
        category_totals = {}
        overspent_categories = []
        for e in self.expenses:
            cat = e["category"]
            category_totals[cat] = category_totals.get(cat, 0.0) + e["amount"]
        
        for cat, total in category_totals.items():
            category_totals[cat] = round(total, 2)
            limit = self.category_budgets.get(cat, 500.0)
            if total > limit:
                overspent_categories.append({
                    "category": cat,
                    "spent": round(total, 2),
                    "limit": limit,
                    "exceeded_by": round(total - limit, 2)
                })

        if category:
            cat = category.lower().strip()
            cat_total = category_totals.get(cat, 0.0)
            cat_limit = self.category_budgets.get(cat, 500.0)
            items = [e for e in self.expenses if e["category"] == cat]
            return {
                "scope": "category",
                "category": cat,
                "total_spent": cat_total,
                "limit": cat_limit,
                "is_overspent": cat_total > cat_limit,
                "item_count": len(items),
                "items": items
            }

        return {
            "scope": "overall",
            "monthly_budget": self.monthly_budget,
            "total_spent": total_spent,
            "remaining_balance": remaining_balance,
            "savings_goal": self.savings_goal,
            "category_breakdown": category_totals,
            "overspent_categories": overspent_categories,
            "total_expenses_logged": len(self.expenses)
        }

    def set_savings_goal(self, target_amount: float, month: str) -> Dict[str, Any]:
        """Set a savings goal target."""
        target_amount = round(float(target_amount), 2)
        self.savings_goal = {
            "target": target_amount,
            "month": month
        }
        total_spent = self.get_total_spent()
        remaining_balance = round(self.monthly_budget - total_spent, 2)
        affordable_savings = round(remaining_balance - target_amount, 2)

        return {
            "status": "success",
            "message": f"Savings goal of ${target_amount:.2f} set for {month}.",
            "target_amount": target_amount,
            "month": month,
            "current_remaining_balance": remaining_balance,
            "balance_after_savings": affordable_savings,
            "is_achievable": affordable_savings >= 0
        }

    def check_affordability(self, expense_name: str, cost: float) -> Dict[str, Any]:
        """
        Agentic calculation to determine if a future expense (e.g. a trip or big purchase)
        is affordable based on remaining balance and active savings goals.
        """
        cost = round(float(cost), 2)
        total_spent = self.get_total_spent()
        current_balance = round(self.monthly_budget - total_spent, 2)
        balance_after_purchase = round(current_balance - cost, 2)
        
        savings_target = self.savings_goal["target"] if self.savings_goal else 0.0
        available_after_savings = round(current_balance - savings_target, 2)
        can_afford_with_savings = balance_after_purchase >= savings_target
        can_afford_basic = balance_after_purchase >= 0

        if can_afford_with_savings:
            verdict = "AFFORDABLE"
            explanation = (
                f"Yes! The purchase '{expense_name}' (${cost:.2f}) is affordable. "
                f"After spending ${cost:.2f}, you will have ${balance_after_purchase:.2f} remaining, "
                f"which still satisfies your savings target of ${savings_target:.2f}."
            )
        elif can_afford_basic:
            verdict = "WARNING_AFFORDABLE_BUT_COMPROMISES_SAVINGS"
            deficit = round(savings_target - balance_after_purchase, 2)
            explanation = (
                f"Caution! You can cover '{expense_name}' (${cost:.2f}) with remaining funds (${current_balance:.2f}), "
                f"leaving ${balance_after_purchase:.2f}. However, this falls ${deficit:.2f} short of your "
                f"savings target (${savings_target:.2f})."
            )
        else:
            verdict = "UNAFFORDABLE"
            deficit = round(cost - current_balance, 2)
            explanation = (
                f"No! You cannot afford '{expense_name}' (${cost:.2f}). "
                f"Your remaining balance is ${current_balance:.2f}, leaving a deficit of ${deficit:.2f}."
            )

        return {
            "expense_name": expense_name,
            "cost": cost,
            "current_balance": current_balance,
            "balance_after_purchase": balance_after_purchase,
            "savings_target": savings_target,
            "verdict": verdict,
            "explanation": explanation
        }

    def record_turn(self, user_query: str, agent_response: str, tool_calls_made: List[Dict[str, Any]]):
        """Save conversation turn into turn memory."""
        self.conversation_history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "user": user_query,
            "agent": agent_response,
            "tool_calls": tool_calls_made
        })

    def get_conversation_context(self) -> str:
        """Format prior conversation history for memory read-back."""
        if not self.conversation_history:
            return "No previous turns in this session."
        
        lines = []
        for idx, turn in enumerate(self.conversation_history, 1):
            tools_str = ", ".join([t["tool"] for t in turn.get("tool_calls", [])]) if turn.get("tool_calls") else "None"
            lines.append(f"Turn {idx}:")
            lines.append(f"  User: {turn['user']}")
            lines.append(f"  Tools Used: {tools_str}")
            lines.append(f"  Agent: {turn['agent']}")
        return "\n".join(lines)
