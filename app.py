"""
app.py - Interactive Streamlit Web UI for BudgetCraft Personal Budget Assistant Agent
"""

import streamlit as st
import json
from memory import BudgetMemory
from tools import reset_memory
from agent import PersonalBudgetAgent

# Page Configuration
st.set_page_config(
    page_title="BudgetCraft | Autonomous AI Budget Agent",
    page_icon="💰",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #4CAF50;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "memory" not in st.session_state:
    st.session_state.memory = reset_memory(initial_budget=5000.0)
if "agent" not in st.session_state:
    st.session_state.agent = PersonalBudgetAgent(memory=st.session_state.memory, verbose=False)
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/budget.png", width=70)
    st.title("BudgetCraft Controls")
    st.caption("CSE476 Agentic AI - Project 1")
    
    st.divider()
    
    # Reset State
    if st.button("🔄 Reset Budget State", use_container_width=True):
        st.session_state.memory = reset_memory(initial_budget=5000.0)
        st.session_state.agent = PersonalBudgetAgent(memory=st.session_state.memory, verbose=False)
        st.session_state.history = []
        st.success("Budget reset to $5,000!")
        st.rerun()

    st.subheader("💡 Example Agent Goals")
    example_prompts = [
        "Log $150 spent on textbooks and $80 on groceries",
        "Set a savings goal of 1000 for August",
        "Can I afford a 2000 trip?",
        "Show my financial summary and categories"
    ]
    for prompt in example_prompts:
        if st.button(prompt, key=f"ex_{prompt}", use_container_width=True):
            st.session_state.preset_prompt = prompt

# Main Dashboard View
st.title("💰 BudgetCraft: Personal Budget Assistant Agent")
st.markdown("An autonomous ReAct agent with **multi-step reasoning**, **tool execution**, and **persistent memory**.")

# Quick Metrics Row
summary = st.session_state.memory.get_summary()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Monthly Budget", f"${summary['monthly_budget']:,.2f}")
with col2:
    st.metric("Total Spent", f"${summary['total_spent']:,.2f}")
with col3:
    st.metric("Remaining Balance", f"${summary['remaining_balance']:,.2f}")
with col4:
    savings_val = f"${summary['savings_goal']['target']:,.2f}" if summary['savings_goal'] else "None"
    st.metric("Savings Goal", savings_val)

st.divider()

# Layout: 2 Columns (Left: Chat & Execution Trace, Right: Live Memory State)
col_left, col_right = st.columns([1.2, 0.8])

with col_left:
    st.subheader("💬 Interact with the Agent")
    
    # Input box with preset fallback
    default_text = st.session_state.pop("preset_prompt", "")
    user_goal = st.text_input("Enter a goal or question for the agent:", value=default_text, placeholder="e.g. Can I afford a 2000 trip?")

    if st.button("🚀 Run Agent Plan-Act Loop", type="primary", use_container_width=True):
        if user_goal.strip():
            with st.spinner("🤖 Agent is planning steps, calling tools, and computing decision..."):
                result = st.session_state.agent.run(user_goal)
                st.session_state.history.append(result)
            st.rerun()

    # Display History & Traces
    if st.session_state.history:
        st.subheader("📜 Agent Execution History & ReAct Traces")
        for idx, turn in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"**Turn: '{turn['user_goal']}'**", expanded=(idx == 1)):
                st.markdown(f"**💡 Final Decision:** {turn['final_answer']}")
                
                st.markdown("##### 🔍 Multi-Step ReAct Trace:")
                for step in turn["trace_steps"]:
                    st.markdown(f"""
                    - **Step {step['step']}:**
                      - 💭 *Thought:* `{step['thought']}`
                      - 🛠️ *Action Tool:* `{step['action']}` with input `{json.dumps(step['input'])}`
                      - 📥 *Observation Result:*
                    """)
                    st.json(step['observation'], expanded=False)

with col_right:
    st.subheader("🧠 Live Memory State")
    
    # Category Breakdown
    st.markdown("##### 📊 Category Spending Breakdown")
    categories = summary.get("category_breakdown", {})
    if categories:
        for cat, amt in categories.items():
            limit = st.session_state.memory.category_budgets.get(cat, 500.0)
            progress = min(amt / limit, 1.0) if limit > 0 else 0.0
            st.write(f"**{cat.capitalize()}**: ${amt:.2f} / ${limit:.2f}")
            st.progress(progress)
    else:
        st.info("No category expenses logged yet.")

    st.markdown("##### 📝 All Logged Expenses")
    if st.session_state.memory.expenses:
        st.dataframe(st.session_state.memory.expenses, use_container_width=True)
    else:
        st.write("No transactions recorded.")

    st.markdown("##### 🗂️ Raw Memory Context")
    with st.expander("View Full JSON Memory State"):
        st.json(summary)
