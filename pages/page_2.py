import streamlit as st
# pages/Checklist.py
import streamlit as st
import re
import time
from openai import OpenAI

def parse_sections_by_bullets(text: str):
    BULLET_RE = re.compile(r'^\s*[-*•+]\s+(.*)$')
    items = []
    for line in text.splitlines():
        m = BULLET_RE.match(line)
        if m:
            items.append(m.group(1).strip())
    return items

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.markdown("## 📝 Checklist")

# Grab stored text (fallback if missing)
api_text = st.session_state.get("AIoutput", "- No checklist available")

items = parse_sections_by_bullets(api_text)
responses = []
infoback = []

for i, item in enumerate(items):
    sel_key = f"sel_{i}"
    cmt_key = f"cmt_{i}"

    option = st.selectbox (
        label = item, 
        options = ["Positive/Present finding", "Negative/Normal finding", "Other/comment"], 
        index=None, 
        placeholder="Please input your finding",
        key = sel_key
    )

    comment = ""
    if option in ("Positive/Present finding", "Other/comment"):
        comment = st.text_area(
            "Please comment on this finding", 
            key=cmt_key)
    st.session_state[f"chk_{i}"] = f"{item} — {option or '(no selection)'}" + (f": {comment}" if comment else "")
    responses.append((option, comment))
    infoback.append((st.session_state[f"chk_{i}"]))

# --- Validation logic ---
all_filled = all(
    option and (option not in ("Positive/Present finding", "Other/comment") or comment.strip())
    for option, comment in responses
)


# --- Action button ---
if st.button("Submit Checklist", disabled=not all_filled):

    checklist_commented = "\n".join(infoback)


    user_prompt = f"""
    Here are my checklist responses:

    {checklist_commented}

    Please calculate pre-test probabilities and recommend investigations,
    """
    with st.spinner("Generating checklist..."):
        try:
            # Responses API call (text-in, text-out)
            out = client.responses.create(
                model="gpt-5-nano",   # use a capable, cost-efficient model
                input=user_prompt,
                store=True,
                previous_response_id=st.session_state.get("checklist_id"),
                tools= [{
                        "type" : "file_search",
                        "vector_store_ids" : ["vs_68bafa7f6d3c81919a21cd7ca01c43b1"],
                    }],
            )

            # Extract the text
            st.session_state["AIoutput2"] = out.output_text
            st.session_state["checklist_id2"] = out.id
            st.success("✅ Checklist generated")
            #st.markdown (st.session_state["AIoutput2"])
            placeholder = st.empty()
            for i in range (5, 0, -1):
                placeholder.write(f"Switching to Probabilities in {i}…")
                time.sleep(1)
            st.switch_page("pages/page_3.py")
        except Exception as e:
            st.error(f"Checklist request failed: {e}")
    st.success("✅ Pre-test probabilities calculated")
