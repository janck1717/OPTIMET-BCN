

"""
Example Tab Template
--------------------
Copy this file into /tabs/ as a starting point for your module.
It demonstrates the recommended use of the StateManager.
"""

import streamlit as st
from utils.state_manager import StateManager


def show():
    # 1️⃣ Create a state manager for this tab
    state = StateManager("example_tab")

    # 2️⃣ Initialize default variables
    state.init({
        "selected_option": "A",
        "threshold": 0.5,
        "auto_refresh": False,
    })

    # 3️⃣ Build UI
    st.header("📊 Example Tab")
    st.info("Demonstration of how to use the StateManager in your own module.")

    option = st.selectbox(
        "Choose an option:",
        ["A", "B", "C"],
        index=["A", "B", "C"].index(state.get("selected_option"))
    )

    threshold = st.slider("Threshold", 0.0, 1.0, state.get("threshold"))
    auto_refresh = st.checkbox("Auto refresh", value=state.get("auto_refresh"))

    # 4️⃣ Update stored state
    state.set("selected_option", option)
    state.set("threshold", threshold)
    state.set("auto_refresh", auto_refresh)

    # 5️⃣ Display current state for reference
    st.subheader("Current State (This Tab)")
    st.json(state.get_all())

    # 6️⃣ Example of cross-tab access
    explorer_city = state.get_from_tab("data_explorer", "selected_city", default="N/A")
    st.caption(f"City selected in Data Explorer: {explorer_city}")

    # 7️⃣ Optional debug panel
    StateManager.debug_view()
