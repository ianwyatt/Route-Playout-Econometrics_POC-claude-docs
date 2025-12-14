# Streamlit st.tabs State Preservation: Workarounds and Solutions

**The `default` parameter added in Streamlit 1.50.0 (September 2025) provides partial relief**, but st.tabs still lacks full state control - no on_change callback, no way to read which tab is active, and no conditional rendering. The feature request for complete state management (GitHub #6004 with 238+ upvotes) remains open with "likely" status but no timeline. Here are proven workarounds ranging from native solutions to JavaScript injection.

---

## The New `default` Parameter Offers Limited But Useful Control

Streamlit 1.50.0 introduced a `default` parameter that lets you specify which tab appears initially:

```python
import streamlit as st

# Store tab preference in session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Enter Campaign ID"

tab1, tab2 = st.tabs(
    ["Browse Campaigns", "Enter Campaign ID"],
    default=st.session_state.active_tab
)

with tab2:
    campaign_id = st.text_input("Campaign ID", key="campaign_input")
    if campaign_id:
        st.session_state.active_tab = "Enter Campaign ID"  # Remember tab
        # Process input...
```

**Critical limitation**: This only sets the *initial* tab - it doesn't automatically track user clicks or expose which tab is currently selected. You must manually update session state, which requires user interaction with widgets inside each tab to know they're there.

---

## st.segmented_control Is the Official Recommendation

Streamlit's documentation explicitly recommends `st.segmented_control` when you need conditional rendering or state awareness:

```python
import streamlit as st

selection = st.segmented_control(
    "Navigation",
    options=["Browse Campaigns", "Enter Campaign ID"],
    selection_mode="single",
    default="Browse Campaigns",
    key="tab_selection"  # Persists across reruns automatically
)

# Conditional rendering - only selected content executes
if selection == "Browse Campaigns":
    st.header("Browse Campaigns")
    # Campaign browsing UI...
elif selection == "Enter Campaign ID":
    st.header("Enter Campaign ID")
    campaign_id = st.text_input("Enter ID")
    if campaign_id:
        st.write(f"Looking up campaign: {campaign_id}")
```

Key advantages:
- **Returns the selected value**
- Supports session state via the `key` parameter
- Only renders the active section's content

The visual style differs from tabs (pill-shaped buttons) but provides full state control.

---

## CSS-Styled st.radio Creates Tab-Like Appearance with Full State

This community solution mimics tab styling while leveraging radio button's native state management:

```python
import streamlit as st

def styled_tabs(tab_names, default_index=0):
    """Radio buttons styled to look like tabs"""
    active_tab = st.radio(
        "", 
        tab_names, 
        index=default_index, 
        horizontal=True, 
        label_visibility="collapsed"
    )
    child_index = tab_names.index(active_tab) + 1
    
    st.markdown(f"""
        <style type="text/css">
        div[role=radiogroup] {{
            border-bottom: 2px solid rgba(49, 51, 63, 0.1);
        }}
        div[role=radiogroup] > label > div:first-of-type {{
            display: none;
        }}
        div[role=radiogroup] {{
            flex-direction: row;
            gap: 0;
        }}
        div[role=radiogroup] label {{
            padding: 0.5em 1em;
            border-radius: 4px 4px 0 0;
            cursor: pointer;
        }}
        div[role=radiogroup] label:nth-child({child_index}) {{
            border-bottom: 2px solid rgb(255, 75, 75);
        }}
        div[role=radiogroup] label:nth-child({child_index}) p {{
            color: rgb(255, 75, 75);
            font-weight: 600;
        }}
        </style>
    """, unsafe_allow_html=True)
    return active_tab

# Usage
selected = styled_tabs(["Browse Campaigns", "Enter Campaign ID"])

if selected == "Browse Campaigns":
    st.write("Campaign browser content")
elif selected == "Enter Campaign ID":
    campaign_id = st.text_input("Campaign ID")
    # Enter key triggers rerun but tab stays selected!
```

This approach **completely solves the Enter key problem** - the radio button maintains its state across reruns, and the CSS makes it visually indistinguishable from native tabs.

---

## Third-Party Packages Provide Production-Ready Stateful Tabs

### extra-streamlit-components TabBar

```python
# pip install extra-streamlit-components
import streamlit as st
import extra_streamlit_components as stx

chosen_id = stx.tab_bar(data=[
    stx.TabBarItemData(
        id="browse", 
        title="Browse Campaigns", 
        description="View all campaigns"
    ),
    stx.TabBarItemData(
        id="enter", 
        title="Enter Campaign ID", 
        description="Direct lookup"
    ),
], default="browse")

if chosen_id == "browse":
    st.write("Browse content")
elif chosen_id == "enter":
    campaign_id = st.text_input("Campaign ID")
    # Tab stays selected on rerun
```

### streamlit-option-menu

```python
# pip install streamlit-option-menu
from streamlit_option_menu import option_menu

selected = option_menu(
    None,
    ["Browse Campaigns", "Enter Campaign ID"],
    icons=['folder', 'search'],
    orientation="horizontal",
    key="main_menu"
)
```

Both packages **return the selected tab value** and persist state across reruns, fully solving the original problem.

---

## JavaScript Injection Can Programmatically Switch Tabs

For situations where you need to force-select a tab after a rerun, inject JavaScript via `components.html()`:

```python
import streamlit as st
from streamlit.components.v1 import html

def switch_to_tab(tab_index):
    """Inject JS to click a specific tab after rerun"""
    js = f"""
    <script>
    (function() {{
        function clickTab() {{
            var tabs = window.parent.document.querySelectorAll('button[role="tab"]');
            if (tabs.length > {tab_index}) {{
                tabs[{tab_index}].click();
                return true;
            }}
            return false;
        }}
        clickTab();
        setTimeout(clickTab, 100);
        setTimeout(clickTab, 500);
    }})();
    </script>
    """
    html(js, height=0)

# Track which tab should be active
if 'target_tab' not in st.session_state:
    st.session_state.target_tab = 0

tab1, tab2 = st.tabs(["Browse Campaigns", "Enter Campaign ID"])

with tab2:
    campaign_id = st.text_input("Campaign ID")
    if campaign_id:
        st.session_state.target_tab = 1  # Stay on tab 2

# Force switch to remembered tab
if st.session_state.target_tab == 1:
    switch_to_tab(1)
```

**Caveats**: JavaScript runs in an iframe with limited parent DOM access; timing can be finicky; may flash briefly during switch. This is a workaround, not a clean solution.

---

## @st.fragment Reduces Unnecessary Reruns

The `@st.fragment` decorator (Streamlit 1.37.0+) creates isolated rerun scopes, potentially minimizing tab-switching side effects:

```python
import streamlit as st

@st.fragment
def campaign_input_section():
    """This section reruns independently"""
    campaign_id = st.text_input("Campaign ID", key="frag_input")
    if campaign_id:
        st.write(f"Processing: {campaign_id}")
    return campaign_id

tab1, tab2 = st.tabs(["Browse Campaigns", "Enter Campaign ID"])

with tab1:
    st.write("Browse campaigns here")

with tab2:
    result = campaign_input_section()
```

Fragments don't directly solve tab state, but they can prevent widgets inside tabs from triggering full page reruns that exacerbate the issue.

---

## Recommended Solution Hierarchy

| Scenario | Best Solution |
|----------|---------------|
| Need full state control + native appearance | CSS-styled `st.radio` |
| Okay with different visual style | `st.segmented_control` (official) |
| Want drop-in replacement with state | `extra-streamlit-components` TabBar |
| Simple default tab needed | Use `default` parameter |
| Must use native st.tabs | Combine `default` + JS injection |

---

## Conclusion

The core limitation - **st.tabs not exposing or accepting active tab state** - remains unresolved in native Streamlit despite 238+ votes on GitHub issue #6004. The September 2025 `default` parameter helps with initial state but doesn't track user navigation. 

For your two-tab interface with text input, the **CSS-styled st.radio approach** offers the best balance of native appearance and complete state preservation. If visual consistency with st.tabs isn't critical, `st.segmented_control` is the officially sanctioned path forward. Third-party packages like `extra-streamlit-components` provide fully stateful tab implementations if you can accept the external dependency.

---

## References

- GitHub Issue #6004: https://github.com/streamlit/streamlit/issues/6004
- Streamlit 1.50.0 Release Notes: https://docs.streamlit.io/develop/quick-reference/release-notes/2025
- st.tabs Documentation: https://docs.streamlit.io/develop/api-reference/layout/st.tabs
- st.fragment Documentation: https://docs.streamlit.io/develop/concepts/architecture/fragments
- extra-streamlit-components: https://github.com/Mohamed-512/Extra-Streamlit-Components
- streamlit-option-menu: https://github.com/victoryhb/streamlit-option-menu
