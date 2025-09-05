import streamlit as st
# pages/Checklist.py
import streamlit as st
import re
from openai import OpenAI

def parse_sections_by_bullets(text: str):
    BULLET_RE = re.compile(r'^\s*[-*•+]\s+(.*)$')
    items = []
    for line in text.splitlines():
        m = BULLET_RE.match(line)
        if m:
            items.append(m.group(1).strip())
    return items

st.markdown("## 📝 Checklist")

# Grab stored text (fallback if missing)
api_text = st.session_state.get("AIresponse", "- No checklist available")

items = parse_sections_by_bullets(api_text)

for i, item in enumerate(items):
    st.checkbox(item, key=f"chk_{i}")


