# 🧭 OPTIMET-BCN — State Manager Developer Guide

This document explains how to use the **StateManager** utility in the OPTIMET-BCN Streamlit project.

The goal is to let every tab keep its own state (like selected filters or parameters), share values with other tabs when necessary, and avoid losing data when switching views.

---

## ⚙️ What It Does

Streamlit apps rerun from top to bottom each time a widget changes.  
Without special handling, this resets all variables.  

`StateManager` solves that by:
- 🧩 giving each tab its own “namespace” inside `st.session_state`
- 🔗 letting tabs read or copy variables from one another
- 💾 saving the current state to disk (optional)
- 🧰 showing everything in a debug panel for developers

---

## 1️⃣ Basic Setup

At the top of your tab file (for example, `tabs/1_data_explorer.py`):

```python
from utils.state_manager import StateManager

def show():
    # Create a state manager for this tab
    state = StateManager("data_explorer")

    # Initialize defaults (only if not already set)
    state.init({
        "selected_dataset": "movilidad_municipios",
        "selected_city": "Barcelona"
    })
