"""
state_manager.py
----------------
Unified session state manager for Streamlit apps.
Handles per-tab state, shared state, and persistence if needed.

Usage example:
--------------
from utils.state_manager import StateManager

state = StateManager("visual_plots")  # create manager for this tab
state.init({
    "selected_city": "Barcelona",
    "metric": "total_viajes"
})

city = state.get("selected_city")
state.set("metric", "viajes_diarios")

# Access another tab's state
explorer_city = state.get_from_tab("data_explorer", "selected_city")
"""

import streamlit as st
import json
import os
from typing import Any, Dict


class StateManager:
    """
    Handles Streamlit session state with optional tab-level separation.
    Each tab creates its own instance: state = StateManager("tab_name")
    """

    STATE_FILE = "session_state.json"

    def __init__(self, tab_name: str = "global"):
        """
        Initialize the StateManager for a specific tab or global scope.
        """
        self.tab_name = tab_name

        # Ensure a global dictionary exists
        if "tabs_state" not in st.session_state:
            st.session_state["tabs_state"] = {}

        # Ensure a sub-dict exists for this tab
        if self.tab_name not in st.session_state["tabs_state"]:
            st.session_state["tabs_state"][self.tab_name] = {}

    # -------------------------------------------------------------------------
    # Core operations
    # -------------------------------------------------------------------------

    def init(self, defaults: Dict[str, Any]):
        """
        Initialize this tab's state with default values.
        Only sets keys that are not already defined.
        """
        for key, value in defaults.items():
            if key not in st.session_state["tabs_state"][self.tab_name]:
                st.session_state["tabs_state"][self.tab_name][key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from this tab's state.
        """
        return st.session_state["tabs_state"][self.tab_name].get(key, default)

    def set(self, key: str, value: Any):
        """
        Set or update a value in this tab's state.
        """
        st.session_state["tabs_state"][self.tab_name][key] = value

    def reset(self, keys: list[str] | None = None):
        """
        Reset one or multiple keys (or all if none specified) in this tab.
        """
        if keys:
            for k in keys:
                st.session_state["tabs_state"][self.tab_name].pop(k, None)
        else:
            st.session_state["tabs_state"][self.tab_name] = {}

    def get_all(self) -> Dict[str, Any]:
        """
        Return a copy of the entire tab state.
        """
        return dict(st.session_state["tabs_state"][self.tab_name])

    # -------------------------------------------------------------------------
    # Cross-tab interactions
    # -------------------------------------------------------------------------

    def get_from_tab(self, tab_name: str, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from another tab's state.
        Useful for sharing configurations between tabs.
        """
        return st.session_state["tabs_state"].get(tab_name, {}).get(key, default)

    def copy_from_tab(self, source_tab: str, keys: list[str] | None = None):
        """
        Copy keys from another tab's state into this tab.
        If keys is None, copy the entire state.
        """
        source_state = st.session_state["tabs_state"].get(source_tab, {})
        if keys:
            for k in keys:
                if k in source_state:
                    st.session_state["tabs_state"][self.tab_name][k] = source_state[k]
        else:
            st.session_state["tabs_state"][self.tab_name].update(source_state)

    # -------------------------------------------------------------------------
    # Persistence (optional)
    # -------------------------------------------------------------------------

    @classmethod
    def save_all(cls, filename: str | None = None):
        """
        Save all tabs' state to a JSON file.
        Only saves serializable objects (str, int, float, bool, list, dict).
        """
        filename = filename or cls.STATE_FILE
        data = {}
        for tab, state in st.session_state.get("tabs_state", {}).items():
            data[tab] = {
                k: v for k, v in state.items() if isinstance(v, (str, int, float, bool, list, dict))
            }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_all(cls, filename: str | None = None):
        """
        Load saved state from a JSON file and update the session.
        """
        filename = filename or cls.STATE_FILE
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
            st.session_state["tabs_state"] = data

    # -------------------------------------------------------------------------
    # Debugging
    # -------------------------------------------------------------------------

    @staticmethod
    def debug_view():
        """
        Display the current state in the Streamlit app (for debugging).
        """
        st.sidebar.markdown("### 🧭 Debug: Session State")
        st.sidebar.json(st.session_state.get("tabs_state", {}))
