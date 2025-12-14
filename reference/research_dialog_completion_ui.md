# Research Request: Streamlit Dialog Not Showing Completion UI After Synchronous Operation

## Environment
- Streamlit 1.48.0
- Python 3.11
- macOS

## The Problem

We have a `@st.dialog` decorated function that runs an Excel export (2-3 seconds). The progress bar updates correctly during the export, but **after the export completes, the completion UI (st.success, st.download_button) does NOT render**.

The user reports seeing:
1. Dialog opens
2. Progress bar updates during export
3. "Says Completed" (unclear where this text comes from)
4. Download button looks exactly the same as before - no success message visible

## Current Code (Simplified Pattern)

This matches the Streamlit documentation pattern exactly:

```python
@st.dialog("Exporting Campaign Data", width="large")
def _export_dialog(campaign_id: str, campaign_result: dict):
    """Modal dialog for Excel export."""

    # Progress bar with initial text
    progress_bar = st.progress(0, "Initializing export...")

    def update_progress(message: str, progress_pct: int):
        progress_bar.progress(progress_pct, f"⏳ {message}")

    try:
        # This takes 2-3 seconds and calls update_progress multiple times
        excel_data = create_excel_export(
            campaign_id,
            campaign_result,
            progress_callback=update_progress
        )
        # Clear progress bar after completion
        progress_bar.empty()

        # Show completion UI - THIS DOES NOT APPEAR
        st.success("Export Complete! Your file is ready for download.")

        st.download_button(
            label="Download Excel File",
            data=excel_data,
            file_name=f"campaign_{campaign_id}_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

    except Exception as e:
        progress_bar.empty()
        st.error(f"Export failed: {e}")

    if st.button("Close", use_container_width=True):
        st.rerun()


# Called from main page when user clicks export button:
if st.button("Download Data (Excel)"):
    _export_dialog(campaign_id, campaign_result)
```

## What We've Tried

### 1. Session State Pattern
Used session state to track export completion and only generate once:
```python
if st.session_state.dialog_export_data is None:
    # Run export, store in session state
    st.session_state.dialog_export_data = excel_data
    st.rerun()  # <-- This closes the dialog!

if st.session_state.dialog_export_data:
    st.success("Complete!")
    st.download_button(...)
```
**Result:** `st.rerun()` closes the dialog entirely

### 2. Remove st.rerun() - Let Code Fall Through
```python
if st.session_state.dialog_export_data is None:
    excel_data = create_excel_export(...)
    st.session_state.dialog_export_data = excel_data
    # Don't rerun - fall through to completion UI

if st.session_state.dialog_export_data:
    st.success("Complete!")  # <-- Does not appear
    st.download_button(...)
```
**Result:** Completion UI does not render

### 3. Simplified Synchronous Pattern (Current)
Removed all session state, matches docs exactly (code shown above)
**Result:** Same issue - completion UI does not render

### 4. Various UI Elements Tried
- `st.balloons()` - didn't appear
- `st.markdown("### ✅ Export Complete!")` - didn't appear
- `st.success("...")` - didn't appear
- Changed download button label - no visible change

## Key Observations

1. **Progress bar works** - Updates are visible during the 2-3 second export
2. **`progress_bar.empty()` seems to work** - Progress bar disappears
3. **Completion UI doesn't render** - st.success, st.download_button changes not visible
4. **User sees "Completed"** - But we don't have text that says just "Completed" in our code
5. **No exceptions thrown** - Export completes successfully, file data is generated

## Questions for Research

1. **Does `@st.dialog` have a known issue with rendering content after a synchronous blocking operation completes?**

2. **Is there something about the Streamlit execution model inside dialogs that prevents new UI elements from appearing after long-running code?**

3. **Does the dialog need to "refresh" somehow after the export, without using `st.rerun()` (which closes it)?**

4. **Is `st.rerun(scope="fragment")` supposed to work inside `@st.dialog` since dialogs "inherit fragment-like behavior"?**

5. **Are there alternative patterns for showing a download button in a dialog after generating data?**

6. **Could there be a timing/rendering issue where the completion UI is rendered but immediately overwritten or hidden?**

## What We Need

A working pattern for:
1. User clicks button → Dialog opens
2. Progress shown during 2-3 second operation
3. After completion: Progress clears, success message + download button appear
4. User downloads file
5. User clicks Close → Dialog closes

## Reference Documentation

We previously found this pattern in Streamlit docs, but it's not working for us:

```python
@st.dialog("Preparing Export", width="medium")
def export_with_progress():
    progress = st.progress(0, "Initializing...")

    for i, step in enumerate(["Loading", "Processing", "Formatting"]):
        progress.progress((i + 1) * 33, f"{step}...")
        time.sleep(0.5)

    progress.empty()
    st.success("Export ready!")
    st.download_button("Download", data=result)

    if st.button("Close"):
        st.rerun()
```

The difference might be that our export is a single long-running function call vs. a loop with multiple `time.sleep()` calls. Could that matter?
