# Excel Export UI Issue - Layout Artifacts During Generation

## Issue Summary

When clicking the "Download Data (Excel)" button, the export progress indicator (`st.status()`) causes layout artifacts - specifically charts appearing in wrong positions on the page during the export process.

## Current Streamlit Version

**Streamlit 1.48.0** (supports `st.dialog` 1.34+ and `st.fragment` 1.33+)

## The Problem

Streamlit renders the entire page top-to-bottom on every interaction (rerun). When we display progress feedback during a button click:

### Approach 1: Status inside button handler (current)
```python
if st.button("Download"):
    with st.status("Generating..."):
        # export logic
```
**Result**: Layout artifacts - charts render in wrong positions because `st.status()` appears at the button's position in the layout, disrupting elements above/below.

### Approach 2: Status at TOP of function
```python
def render_tab():
    if st.session_state.get('export_requested'):
        with st.status("Generating..."):
            # export logic
    # ... rest of page
```
**Result**: Page goes dark during export - the status shows before any other UI has rendered.

### Approach 3: on_click callback
```python
def _generate():
    st.session_state.export_requested = True

st.button("Download", on_click=_generate)
```
**Result**: Same as Approach 2 - callbacks run BEFORE the page rerenders.

## Root Cause

Streamlit's synchronous, top-to-bottom execution model means:
1. We cannot show progress on an "already rendered" page
2. Any UI element appears at its position in the script execution
3. Long-running operations block the entire render

## Potential Solutions

### 1. `st.dialog` (Modal Popup)
- Available in Streamlit 1.34+
- Creates a modal overlay that doesn't affect page layout
- Export runs inside the modal

### 2. `st.fragment` (Partial Reruns)
- Available in Streamlit 1.33+
- Allows only part of the page to rerun
- Could isolate the export button/status from the rest of the page

### 3. `st.toast()` (Quick Fix)
- Simple notification in corner
- No layout impact
- Minimal feedback (just text, no progress indicator)

### 4. CSS Overlay
- Custom styling to position status as floating overlay
- Hacky but possible

## Files Affected

- `src/ui/tabs/executive_summary.py` - Export button section (lines 320-353)
- `src/ui/tabs/overview.py` - Export button section (lines 156-187)

## Current Quick Fix

Using `st.toast()` for notification while researching proper modal/fragment solution.
