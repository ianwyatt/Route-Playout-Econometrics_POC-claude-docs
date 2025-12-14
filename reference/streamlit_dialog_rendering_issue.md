# Why Streamlit dialogs fail to render UI after blocking operations

**Streamlit's execution model batches all UI updates until script completion**, which creates a fundamental limitation for showing new UI elements after synchronous blocking operations inside dialogs. Your issue is a **confirmed, open bug** (GitHub #9405) with no current fix, but several working patterns exist to achieve your desired UX.

The core problem: while progress bar updates work because they modify an existing element in-place via callbacks during execution, `st.success()` and `st.download_button()` are *new elements* that should appear after the blocking code. However, the dialog's fragment-inherited behavior prevents these from rendering properly without a deliberate state management pattern.

## The technical root cause

Streamlit's architecture requires the **full script execution to complete before sending UI updates to the frontend**. Inside `@st.dialog`, this creates specific issues because dialogs inherit behavior from `st.fragment` - widget interactions trigger only a dialog-scoped rerun, not a full app rerun.

Here's what happens in your code flow:

1. Dialog opens, progress bar element is created
2. `create_excel_export()` runs, progress callbacks update the existing progress bar element (works because it's modifying an existing element)
3. `progress_bar.empty()` clears the progress bar (works)
4. `st.success()` and `st.download_button()` are called, attempting to render new elements
5. **The dialog function completes, but no rerun is triggered to send the new elements to the frontend**

The critical insight is that progress bar updates work because you're calling `progress_bar.progress()` on an *already-created element*, while `st.success()` and `st.download_button()` are trying to create *new elements* after the blocking operation - and without a rerun, these never appear.

## Why st.rerun(scope="fragment") doesn't work

You correctly suspected that `st.rerun(scope="fragment")` might solve this since dialogs "inherit fragment-like behavior." Unfortunately, **this is a known limitation** documented in GitHub Issue #9908: calling `st.rerun(scope="fragment")` from within a dialog raises an exception:

```
StreamlitAPIException: scope="fragment" can only be specified from @st.fragment-decorated functions during fragment reruns.
```

Despite dialogs inheriting fragment behavior, the scoped rerun mechanism explicitly checks for the `@st.fragment` decorator and fails for `@st.dialog`. This means you cannot trigger a dialog-only rerun to show new elements - you must use a full `st.rerun()`, which closes the dialog entirely because the condition that opened it is re-evaluated.

## Working pattern: session state with two-phase dialog

The recommended solution uses session state to track export completion, then triggers a rerun that keeps the dialog open by controlling the execution path:

```python
@st.dialog("Exporting Campaign Data", width="large")
def _export_dialog(campaign_id: str, campaign_result: dict):
    # Check if export already completed in a previous run
    if st.session_state.get("export_complete"):
        st.success("✅ Export Complete!")
        st.download_button(
            label="📥 Download Excel Report",
            data=st.session_state.get("excel_data"),
            file_name="campaign_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        if st.button("Close"):
            st.session_state.export_complete = False
            st.session_state.pop("excel_data", None)
            st.rerun()
        return  # Don't proceed to export logic
    
    # Initial state: show export button
    progress_bar = st.progress(0, "Ready to export...")
    
    if st.button("Start Export"):
        def update_progress(message: str, progress_pct: int):
            progress_bar.progress(progress_pct, f"⏳ {message}")
        
        try:
            excel_data = create_excel_export(
                campaign_id, campaign_result, 
                progress_callback=update_progress
            )
            # Store results in session state
            st.session_state.excel_data = excel_data
            st.session_state.export_complete = True
            st.rerun()  # Rerun with state that shows completion UI
        except Exception as e:
            st.error(f"Export failed: {e}")
```

This pattern works because the `st.rerun()` after export completion re-executes the dialog function, but this time the `export_complete` flag is True, so the completion UI branch renders instead of the export logic.

## Alternative pattern: pre-create placeholders

Another approach uses `st.empty()` placeholders created *before* the blocking operation, then populates them after:

```python
@st.dialog("Exporting Campaign Data", width="large")
def _export_dialog(campaign_id: str, campaign_result: dict):
    progress_placeholder = st.empty()
    result_placeholder = st.empty()
    download_placeholder = st.empty()
    close_placeholder = st.empty()
    
    progress_bar = progress_placeholder.progress(0, "Initializing export...")
    
    def update_progress(message: str, progress_pct: int):
        progress_bar.progress(progress_pct, f"⏳ {message}")
    
    try:
        excel_data = create_excel_export(
            campaign_id, campaign_result, 
            progress_callback=update_progress
        )
        progress_placeholder.empty()
        result_placeholder.success("✅ Export Complete!")
        download_placeholder.download_button(
            label="📥 Download Excel Report",
            data=excel_data,
            file_name="campaign_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        progress_placeholder.empty()
        result_placeholder.error(f"Export failed: {e}")
    
    if close_placeholder.button("Close"):
        st.rerun()
```

This approach **may work** because the placeholder elements are created during initial dialog rendering, and you're updating them in-place rather than creating new elements after the blocking code. However, some users report mixed results with this pattern inside dialogs.

## Pattern that moves download outside the dialog

If the above patterns prove unreliable, the most robust approach is to show the download button **outside the dialog** after it closes:

```python
# In your main app code
@st.dialog("Exporting Campaign Data", width="large")  
def _export_dialog(campaign_id: str, campaign_result: dict):
    progress_bar = st.progress(0, "Initializing export...")
    
    def update_progress(message: str, progress_pct: int):
        progress_bar.progress(progress_pct, f"⏳ {message}")
    
    try:
        excel_data = create_excel_export(
            campaign_id, campaign_result, 
            progress_callback=update_progress
        )
        st.session_state.export_ready = True
        st.session_state.export_data = excel_data
        st.session_state.export_filename = f"campaign_{campaign_id}.xlsx"
        st.rerun()  # Closes dialog, export UI appears in main app
    except Exception as e:
        st.error(f"Export failed: {e}")
        if st.button("Close"):
            st.rerun()

# Main app - show download when ready
if st.session_state.get("export_ready"):
    st.success("✅ Export Complete!")
    col1, col2 = st.columns([1, 4])
    with col1:
        st.download_button(
            "📥 Download",
            data=st.session_state.export_data,
            file_name=st.session_state.export_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col2:
        if st.button("Clear"):
            st.session_state.export_ready = False
            st.rerun()
```

## Why progress bars work but new elements don't

The difference between your working progress bar and failing completion UI comes down to **element creation timing**:

| Operation | Timing | Works? | Reason |
|-----------|--------|--------|--------|
| `st.progress()` | Created before blocking code | ✅ | Element exists, just being updated |
| `progress_bar.progress(n, msg)` | During blocking code | ✅ | Updating existing element in-place |
| `progress_bar.empty()` | After blocking code | ✅ | Clearing existing element |
| `st.success()` | After blocking code | ❌ | New element, no rerun to render it |
| `st.download_button()` | After blocking code | ❌ | New element, no rerun to render it |

The dialog's fragment-inherited execution completes after your blocking code runs, but the frontend never receives instructions to render the new elements because no rerun occurs. The progress bar updates work because Streamlit can update existing elements without a full rerun.

## Version-specific considerations

You're using **Streamlit 1.48.0**, which includes recent dialog improvements like non-dismissible dialogs and better dismiss handling, but **does not fix** the core blocking-operation rendering issue. GitHub Issue #9405 (the most directly related bug) remains open with **18+ upvotes** and is labeled as an enhancement request.

Upgrading to the latest Streamlit version won't solve this fundamental issue - the session state pattern described above is currently the recommended workaround across all recent versions.

## Conclusion

Your issue stems from Streamlit's batched UI rendering model combined with dialogs' fragment-inherited behavior. The key insight is that **new elements created after blocking code require a rerun to render**, but `st.rerun()` closes the dialog while `st.rerun(scope="fragment")` raises an exception inside dialogs. The solution is to use session state to track completion status, then structure your dialog function to render different UI based on that state - effectively making the "completion UI" render on a subsequent dialog execution rather than after inline blocking code.
