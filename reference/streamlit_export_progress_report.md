# Streamlit 1.48.0 export progress without layout artifacts

**The `@st.dialog` decorator is your best solution.** It creates a true modal overlay that floats above your page, completely isolating progress indicators from your chart layout. Both `st.dialog` and `st.fragment` are stable (non-experimental) in Streamlit 1.48.0 and support `st.download_button` inside them. Your current pattern fails because `st.status` inside a button handler inserts into the page flow during rerun, displacing elements below it - dialogs and fragments prevent this entirely.

## How st.dialog solves your layout artifacts

The `@st.dialog` decorator (stable since v1.37) creates a **modal overlay** that renders on top of your page rather than inserting into the document flow. This is the key distinction: progress indicators, status containers, and download buttons inside a dialog exist in a separate layer and cannot affect your charts' positions.

Dialogs inherit fragment-like behavior - when users interact with widgets inside the dialog, only the dialog function reruns, not your entire script. This means your charts render once and remain untouched while the export progresses.

```python
import streamlit as st
import time
import pandas as pd
import io

@st.dialog("Exporting Data", width="medium")
def export_dialog(data):
    """Modal overlay - nothing here affects main page layout"""
    
    with st.status("Preparing export...", expanded=True) as status:
        st.write("Processing records...")
        time.sleep(1)
        
        st.write("Generating Excel file...")
        # Your actual Excel generation here
        buffer = io.BytesIO()
        data.to_excel(buffer, index=False, engine='openpyxl')
        excel_data = buffer.getvalue()
        time.sleep(1)
        
        status.update(label="Export complete!", state="complete", expanded=False)
    
    st.success("✅ Your file is ready")
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download Excel",
            data=excel_data,
            file_name="export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            on_click="ignore"  # Prevents rerun when downloading
        )
    with col2:
        if st.button("Close"):
            st.rerun()  # Closes dialog

# Main app - charts render once, unaffected by export
st.title("Sales Dashboard")
chart_data = pd.DataFrame({"month": range(12), "sales": [100, 120, 140, 130, 150, 170, 160, 180, 200, 190, 210, 230]})
st.line_chart(chart_data.set_index("month"))

if st.button("🚀 Export Report", type="primary"):
    export_dialog(chart_data)  # Opens modal overlay

st.dataframe(chart_data)  # Also unaffected by export
```

Setting `dismissible=False` prevents users from closing the dialog mid-export by clicking outside, pressing ESC, or clicking the X button - useful for ensuring the export completes.

## The st.fragment approach for inline progress

If you prefer the progress to appear inline rather than in a modal, `@st.fragment` isolates the export section so that only it reruns when the button is clicked. Charts and other elements **outside the fragment are preserved** during fragment reruns - they won't redraw or shift.

```python
import streamlit as st
import time
import pandas as pd

# Charts OUTSIDE the fragment - remain stable during export
st.title("Dashboard")
chart_data = pd.DataFrame({"x": range(10), "y": [i**2 for i in range(10)]})
st.line_chart(chart_data.set_index("x"))

@st.fragment
def export_section(data):
    """Only this section reruns - rest of page is frozen"""
    
    if "export_data" not in st.session_state:
        st.session_state.export_data = None
    
    if st.button("📥 Export Data"):
        with st.status("Generating export...", expanded=True) as status:
            st.write("Processing...")
            time.sleep(2)
            st.session_state.export_data = data.to_csv().encode('utf-8')
            status.update(label="Ready!", state="complete", expanded=False)
        
        st.rerun(scope="fragment")  # Rerun only this fragment
    
    if st.session_state.export_data:
        st.download_button(
            "⬇️ Download CSV",
            data=st.session_state.export_data,
            file_name="export.csv",
            on_click="ignore"
        )

export_section(chart_data)

# More content below fragment - also unaffected
st.write("Additional dashboard content here...")
```

The critical distinction: `st.rerun(scope="fragment")` triggers only the fragment to rerun, leaving everything else untouched. However, this scoped rerun only works **during a fragment rerun**, not during a full-app rerun.

## Session state patterns for fragment/dialog workflows

Both approaches require session state to persist data across reruns. Since fragment return values are ignored during fragment reruns, always store export results in `st.session_state`:

```python
# Initialize at app start
if "export_state" not in st.session_state:
    st.session_state.export_state = "idle"  # idle | running | complete
    st.session_state.export_bytes = None

@st.fragment
def managed_export(data):
    if st.session_state.export_state == "idle":
        if st.button("Generate Export"):
            st.session_state.export_state = "running"
            st.rerun(scope="fragment")
    
    elif st.session_state.export_state == "running":
        with st.spinner("Generating..."):
            result = expensive_export(data)
            st.session_state.export_bytes = result
            st.session_state.export_state = "complete"
            st.rerun(scope="fragment")
    
    elif st.session_state.export_state == "complete":
        st.download_button("Download", st.session_state.export_bytes)
        if st.button("Reset"):
            st.session_state.export_state = "idle"
            st.session_state.export_bytes = None
            st.rerun(scope="fragment")
```

## Why your current pattern causes artifacts

Your current code places `st.status` inside the button handler, which inserts new DOM elements into the page flow **during the rerun**. Streamlit renders top-to-bottom, and when `st.status` suddenly appears (or expands), it pushes everything below it down - including your charts.

The **callback timing** compounds this: `on_click` callbacks execute before the page renders, meaning any UI elements created there appear before the script re-executes from the top. This explains why placing progress at the top makes the page "go dark" - the status container renders first, potentially blocking or disrupting the layout before charts are drawn.

## Alternative patterns worth considering

**Pre-generation with caching** works well if your export data doesn't change frequently:

```python
@st.cache_data(show_spinner=False)  # Disable automatic spinner
def generate_export(data_hash):
    return expensive_generation()

# Generate on page load, download is instant
csv_data = generate_export(hash(tuple(data.values.flatten())))
st.download_button("Download", csv_data)
```

**The st.empty placeholder** reserves layout space before operations begin, preventing shift:

```python
export_area = st.empty()  # Reserves space

if st.button("Export"):
    with export_area.container():
        with st.status("Working...") as status:
            do_work()
            status.update(state="complete")
        st.download_button("Download", result)
```

## Technical specifics for Streamlit 1.48.0

| Feature | Status in 1.48.0 | Notes |
|---------|------------------|-------|
| `@st.dialog` | Stable | Use without `experimental_` prefix |
| `@st.fragment` | Stable | Use without `experimental_` prefix |
| `st.download_button` in dialog | ✅ Works | Dialog inherits fragment behavior |
| `st.rerun(scope="fragment")` | ✅ Available | Only from within fragment during fragment rerun |
| `on_click="ignore"` | ✅ Available | Prevents download button from triggering rerun |
| `dismissible` param on dialog | ✅ Available | Control whether users can close dialog |

The experimental versions (`@st.experimental_dialog`, `@st.experimental_fragment`) were removed in v1.49.0, confirming these APIs are production-ready in 1.48.0.

## Recommended solution for your use case

Given your 2-3 second export with charts that shift, **use `@st.dialog`** with the non-dismissible pattern:

```python
@st.dialog("Preparing Export", width="medium", dismissible=False)
def export_with_progress():
    progress = st.progress(0, "Initializing...")
    
    for i, step in enumerate(["Loading data", "Processing", "Formatting", "Finalizing"]):
        progress.progress((i + 1) * 25, f"{step}...")
        time.sleep(0.5)  # Your actual work here
    
    progress.empty()
    st.success("Export ready!")
    st.download_button("📥 Download", data=result, on_click="ignore")
    
    if st.button("Close"):
        st.rerun()

if st.button("Export"):
    export_with_progress()
```

This keeps your charts completely undisturbed, shows clear progress in an overlay, and presents the download button without any layout disruption.
