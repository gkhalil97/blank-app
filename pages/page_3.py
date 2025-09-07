import streamlit as st
from openai import OpenAI
st.markdown("# Pre-test Probabilities 🎲")
st.sidebar.markdown("# Pre-test Probabilities 🎲")
api_text = st.session_state.get("AIoutput2", "- No probabilities available")
api_text