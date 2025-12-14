# Styling Streamlit Expander Headers

## Approach 1: Markdown Formatting in Label (Recommended)

Most markdown formatting works directly in the expander label - colors, bold, italics, emojis:

```python
import streamlit as st

# Simple colored text
with st.expander(":red[Warning] - Click to expand"):
    st.write("Content here")

# Multiple formatting options
text = r":pencil: **Bold title** _with italics_ and :violet[color]"
with st.expander(text, expanded=False):
    st.write("Content here")
```

Available color options: `:red[text]`, `:blue[text]`, `:green[text]`, `:orange[text]`, `:violet[text]`

**Important:** Watch indentation in triple-quoted strings - it affects rendering.

---

## Approach 2: CSS Injection (More Control, Less Stable)

Use `data-testid` selectors as they're more stable than `st-emotion-cache-*` classes:

```python
import streamlit as st

st.markdown("""
<style>
div[data-testid="stExpander"] details summary p {
    color: red !important;
    font-size: 20px !important;
}
</style>
""", unsafe_allow_html=True)

with st.expander("Styled expander"):
    st.write("Content")
```

Or using `st.html()`:

```python
st.html("""
<style>
div[data-testid="stExpander"] summary p {
    color: blue !important;
    font-weight: bold !important;
}
</style>
""")
```

---

## Finding Selectors for Your Version

CSS class names change between Streamlit versions. To find the correct selectors:

1. Run your Streamlit app
2. Right-click the expander header in browser
3. Select "Inspect" / "Inspect Element"
4. Look for `data-testid` attributes (more stable) or class names
5. Test selectors in browser DevTools before adding to code

---

## Notes

- Approach 1 is cleaner and version-stable
- Approach 2 gives more control but may break on Streamlit updates
- The `!important` flag helps override Streamlit's default styles
- Inject CSS after creating the element, or at the end of your script