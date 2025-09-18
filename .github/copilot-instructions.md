# Copilot Instructions for AI Coding Agents

## Project Overview
- This is a Streamlit-based medical AI assistant app (Heuris AI) for clinical decision support.
- The app guides users through a patient journey: demographics → history/exam → investigations → diagnosis.
- Main entry point: `streamlit_app.py` (handles navigation and page selection).
- Pages are modularized in `pages/`:
  - `main_page.py`: Patient demographics and presenting complaint input
  - `page_2.py`: Checklist generation and display
  - `page_3.py`: Pre-test probability and differential diagnosis

## Key Patterns & Conventions
- **Navigation**: Uses `st.Page` and `st.navigation` to switch between pages.
- **Session State**: Relies heavily on `st.session_state` for cross-page data persistence (e.g., patient info, AI outputs).
- **OpenAI Integration**: Each page initializes an `OpenAI` client using `st.secrets["OPENAI_API_KEY"]`.
- **Checklist Data**: Checklist structure is JSON-based and passed between pages via session state.
- **Dev/Test Shortcuts**: The sidebar in `streamlit_app.py` includes a dev button to preload sample data for testing.

## Developer Workflows
- **Run locally**:
  1. `pip install -r requirements.txt`
  2. `streamlit run streamlit_app.py`
- **No explicit test suite**: Testing is manual via the UI and dev/test buttons.
- **Secrets**: Requires an OpenAI API key in Streamlit secrets (see Streamlit docs for setup).

## Project-Specific Advice
- When adding new pages, register them in `streamlit_app.py` using `st.Page` and add to the navigation list.
- Use `st.session_state` for any data that must persist across navigation.
- Follow the JSON structure for checklist and model outputs as seen in `page_2.py` and `page_3.py`.
- For new AI features, use the existing OpenAI client pattern and store results in session state.
- UI layout uses `st.columns` for form grouping and metrics display.

## Integration Points
- **External APIs**: OpenAI API (via `openai` Python package)
- **Streamlit Secrets**: All API keys and sensitive config must be stored in `.streamlit/secrets.toml`

## Example: Adding a New Page
```python
# In streamlit_app.py
new_page = st.Page("pages/new_page.py", title="New Feature", icon="🆕")
pages = [main_page, page_2, page_3, new_page]
pg = st.navigation(pages)
pg.run()
```

## References
- Main app: `streamlit_app.py`
- Page modules: `pages/`
- Requirements: `requirements.txt`
- Project README: `README.md`

---
If any section is unclear or missing, please provide feedback for further refinement.
