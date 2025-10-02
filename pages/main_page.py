import streamlit as st
import numpy as np
import pandas as pd
from openai import OpenAI
import time
import json

# Main page content
st.markdown("# 🎁 Presentation")

import importlib.metadata as im

st.sidebar.markdown("# Presentation")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

left, right = st.columns(2)

left.number_input ("🕰️ Age", value=None, key="age")
right.selectbox ("👩🏻👨🏻 Gender", ("Male", "Female"), key="gender")

centre, = st.columns(1)
with centre:
    new_PC = st.selectbox("🤢 Presenting Complaint", ("Chest Pain", "Abdominal Pain", "Other"))
    if new_PC == "Other":
            new_PC = st.text_input ("", label_visibility="collapsed", placeholder = "Enter new presenting complaint")

st.session_state["PC"] = new_PC

left1, right1 = st.columns (2)
left1.text_area ("🔄 PMHx", placeholder = "Please enter every element of their past medical history separated by a comma, if none please type 'none'.", key="PMHx")
right1.text_area ("💊 DHx", placeholder = "Please enter all medications separated by a comma, if none please type 'none'. ", key="DHx")

# Collect required fields
age = st.session_state.get("age")
gender = st.session_state.get("gender")
pc = st.session_state.get("PC")
pmhx = st.session_state.get("PMHx")
dhx = st.session_state.get("DHx")

# Validation: all fields must be filled
all_fields_filled = (
    age is not None and
    gender is not None and
    pc and
    pmhx and pmhx.strip() != "" and
    dhx and dhx.strip() != ""
)

# Button is disabled until all_fields_filled is True
if st.button("Generate Checklist", disabled=not all_fields_filled):

    with st.spinner("Generating checklist..."):
        try:
            # Responses API call (text-in, text-out)
            if pc == "Chest Pain":
                out = client.responses.create(
                    prompt= {
                        "id": "pmpt_68bf7334017481948669f4b41306f6240d2d9e134aedefe3",
                        "version": "22",
                        "variables": {
                            "pc": pc,
                            "age": str(age),
                            "gender": gender,
                            "pmhx": pmhx,
                            "dhx":dhx
                            }
                    } # type: ignore
                    )
            else: 
                out = client.responses.create(
                    prompt= {
                        "id": "pmpt_68d154bc037c8196bca817fb873d0fca076e02cfb8566420",
                        "version": "3", 
                        "variables": {
                            "pc": pc,
                            "age": str(age),
                            "gender": gender,
                            "pmhx": pmhx,
                            "dhx":dhx
                            }
                    } # type: ignore
                    store=True
                    )
            try:
                data = out.output[0].content[0].json # type: ignore
            except Exception:
                data = json.loads(out.output_text)

            # Extract the text
            st.session_state["AIoutput"] = data
            st.session_state["AIoutput_raw"] = out.output_text
            st.session_state["checklist_id"] = out.id

            st.success("✅ Checklist generated")
            #st.markdown (st.session_state["AIoutput"])
            placeholder = st.empty()
            for i in range (5, 0, -1):
                placeholder.write(f"Switching to checklist in {i}…")
                time.sleep(1)
            st.switch_page("pages/page_2.py")
        except Exception as e:
            st.error(f"Checklist request failed: {e}")
    
   
      