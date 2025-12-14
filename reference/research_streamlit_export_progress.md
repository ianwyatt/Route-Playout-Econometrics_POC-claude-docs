# Research Request: Streamlit Export Progress UI

## Context

I have a Streamlit 1.48.0 application with an Excel export button. The export takes 2-3 seconds and I want to show progress feedback to the user without causing layout artifacts.

## The Problem

When I show `st.status()` or `st.spinner()` during the export:
- If placed inside the button handler: causes layout artifacts (charts appear in wrong positions)
- If placed at top of function: page goes dark (nothing rendered yet)
- Using `on_click` callback: same as above (callbacks run before page renders)

## What I Need

Research the best approach using Streamlit 1.48.0 features:

### 1. `st.dialog` approach
- How to use `@st.dialog` decorator for a modal export progress
- Can I show progress inside a dialog while export runs?
- Example code for triggering dialog from button click

### 2. `st.fragment` approach
- How to use `@st.fragment` to isolate the export button/status
- Can fragments prevent layout artifacts during rerun?
- Example of fragment with button + status that doesn't affect rest of page

### 3. Any other Streamlit patterns for long-running operations with progress feedback

## Current Code Pattern

```python
# In render function, at the bottom after charts
with st.container(border=True):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if 'export_excel_data' in st.session_state and st.session_state.export_excel_data:
            st.download_button(
                label="Download Data (Excel)",
                data=st.session_state.export_excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            if st.button("Download Data (Excel)"):
                with st.status("Generating Excel export...", expanded=True) as status:
                    # This causes layout artifacts!
                    excel_data = create_excel_export(campaign_id, campaign_result)
                    st.session_state.export_excel_data = excel_data
                st.rerun()
```

## Desired Behavior

1. User clicks "Download Data (Excel)" button
2. Progress indicator shows WITHOUT disrupting page layout
3. Export completes
4. Button becomes download button
5. Minimal page "flash" or disruption

## Key Questions

1. Does `st.dialog` work for showing export progress in an overlay?
2. Can `st.fragment` isolate just the export section from full page reruns?
3. Is there a recommended pattern for long-running button actions with progress?
