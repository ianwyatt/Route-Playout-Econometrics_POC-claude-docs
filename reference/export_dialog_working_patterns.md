# Export Dialog Working Patterns (Streamlit 1.48.0)

## Context
Due to Streamlit bug #9405, new UI elements created after blocking code inside `@st.dialog` don't render without a rerun, but `st.rerun()` closes the dialog.

## Summary of Testing (Nov 2024)

| Pattern | Result | Issue |
|---------|--------|-------|
| Pattern 1: Download Outside Dialog | ✅ WORKS | Original required manual close |
| Pattern 1b: Auto-close with time.sleep | ✅ WORKS | **FINAL SOLUTION** |
| Pattern 2: Two-Phase Session State | ❌ FAILS | `st.rerun()` closes dialog |
| Pattern 3: Placeholder | ❌ FAILS | Download button click re-runs export |
| Auto-download via JavaScript | ❌ FAILS | Browser security blocks it |

**Conclusion:** Only Pattern 1 works. The download button MUST be on the main page, not inside the dialog. Auto-close with `time.sleep()` provides best UX.

---

## Final Working Solution (Pattern 1b: Auto-close)

### The Dialog Function

```python
@st.dialog("Exporting Campaign Data", width="large")
def _export_dialog(campaign_id: str, campaign_result: dict):
    """Modal dialog for Excel export progress.

    Auto-closes after export completes, download button appears on main page.
    """
    import time

    progress_bar = st.progress(0, "Initializing export...")

    def update_progress(message: str, progress_pct: int):
        progress_bar.progress(progress_pct, f"⏳ {message}")

    try:
        excel_data = create_excel_export(
            campaign_id,
            campaign_result,
            progress_callback=update_progress
        )
        # Store in session state for main page
        st.session_state.export_ready = True
        st.session_state.export_data = excel_data
        st.session_state.export_filename = f"campaign_{campaign_id}_data.xlsx"
        progress_bar.progress(100, "✅ Export complete!")
        time.sleep(0.8)  # Brief pause to show completion
        st.rerun()  # Auto-close dialog

    except Exception as e:
        progress_bar.empty()
        st.error(f"Export failed: {e}")
        if st.button("Close"):
            st.rerun()
```

### The Main Page UI

```python
with st.container(border=True):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.get('export_ready'):
            # Export complete - show download button
            st.download_button(
                label="Download Excel File",
                data=st.session_state.export_data,
                file_name=st.session_state.export_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                icon=":material/download:",
                key="download_btn"
            )
        else:
            # Show export button
            if st.button("Export Data", use_container_width=True, icon=":material/upload_file:", key="export_btn"):
                campaign_result = st.session_state.get('campaign_result', {})
                _export_dialog(campaign_id, campaign_result)
```

### Clear State on Navigation

```python
def _go_back():
    st.session_state.campaign_data = None
    st.session_state.campaign_result = None
    st.session_state.selected_campaign_id = None
    st.session_state.show_analysis = False
    # Clear export state
    st.session_state.pop('export_ready', None)
    st.session_state.pop('export_data', None)
    st.session_state.pop('export_filename', None)
```

---

## User Flow

1. User clicks **"Export Data"** button (with upload icon)
2. Dialog opens showing progress bar with step-by-step updates
3. Export completes → Progress shows "✅ Export complete!" for 0.8 seconds
4. Dialog auto-closes via `st.rerun()`
5. Main page now shows **"Download Excel File"** button (with download icon)
6. User clicks to download
7. When user navigates away, export state is cleared

---

## Key Design Decisions

### Button Differentiation
- **Before export**: "Export Data" with `:material/upload_file:` icon
- **After export**: "Download Excel File" with `:material/download:` icon
- No `type="primary"` - subtle styling, icon change is enough signal

### No Clear Button Needed
The `_go_back()` function clears export state, so a separate "Clear" button is unnecessary.

### Auto-download Not Possible
Browser security (iframe sandbox) blocks programmatic downloads via JavaScript. We tried:
- `st.components.v1.html()` with anchor click
- `st.markdown()` with `unsafe_allow_html`
Both blocked by browser security policies.

---

## Why Other Patterns Failed

### Pattern 2: Two-Phase Session State
The documentation suggested checking session state at dialog start and showing different UI. However, `st.rerun()` always closes the dialog - there's no way to keep the dialog open while refreshing its contents.

### Pattern 3: Placeholder
Creating `st.empty()` placeholders before blocking code and populating them after seemed promising. However, when the user clicks the download button inside the dialog, it triggers a dialog re-run which re-executes the blocking export code.

---

## Files Modified

- `src/ui/tabs/executive_summary.py` - Export dialog and button
- `src/ui/tabs/overview.py` - Same export dialog (duplicated - TODO: extract to shared component)
- `src/ui/utils/export.py` - Excel export with progress callback

## Related Issues

- GitHub Issue #9405: Dialog rendering after blocking operations
- GitHub Issue #9908: `st.rerun(scope="fragment")` doesn't work in dialogs
