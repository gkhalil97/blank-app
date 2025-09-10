import streamlit as st
import numpy as np
import pandas as pd
import json

st.title("🤖👨🏻‍⚕️ Heuris AI")
st.write(
    "Welcome to Heuris AI, your medical AI assistant and clinical decision support. Please work through the patient " \
    "journey by first inputting your patients main five demographics: Age, Gender, PC, PMHx, DHx. Please then work through the patient journey from history and examination, to investigation and then to diagnosis. "
)

import streamlit as st

from openai import OpenAI


# try to read the installed distribution version
import importlib.metadata as im


# Define the pages
main_page = st.Page("pages/main_page.py", title="Presentation", icon="🎁")
page_2 = st.Page("pages/page_2.py", title="Checklist", icon="✅")
page_3 = st.Page("pages/page_3.py", title="Pre-test", icon="🎲")

# Set up navigation
pg = st.navigation([main_page, page_2, page_3])

# Run the selected page
pg.run()

import time
# --- DEV ONLY: boot page_2 with sample JSON ---
if st.sidebar.button("🧪 Dev: open page 2 with sample"):
    test = """{
      "presenting_complaint": "Chest pain",
      "age": 54,
      "gender": "male",
      "dhx": "Aspirin 75mg, Atorvastatin 20mg",
      "pmhx": "Hypertension, Hyperlipidaemia",
      "checklist": {
        "history_presenting_complaint": [
          {
            "id": "onset_time",
            "label": "Onset time",
            "output_style": "free_text",
            "options": null, "max_select": null,
            "true_label": null, "false_label": null,
            "minimum": null, "maximum": null, "step": null, "unit": null,
            "pattern": ".*", "minLength": 1, "maxLength": 120
          },
          {
            "id": "character_boolean",
            "label": "Is the pain crushing?",
            "output_style": "boolean",
            "options": null, "max_select": null,
            "true_label": "present", "false_label": "absent",
            "minimum": null, "maximum": null, "step": null, "unit": null,
            "pattern": null, "minLength": null, "maxLength": null
          }
        ],
        "systems_review": [],
        "past_medical_history_drug_history": [],
        "social_history": [
          {
            "id": "smoking_status",
            "label": "Smoking status",
            "output_style": "single_select_multi_option",
            "options": ["Never", "Former", "Current"],
            "max_select": null,
            "true_label": null, "false_label": null,
            "minimum": null, "maximum": null, "step": null, "unit": null,
            "pattern": null, "minLength": null, "maxLength": null
          }
        ],
        "examination": [
          {
            "id": "hr",
            "label": "Heart rate",
            "output_style": "number",
            "options": null, "max_select": null,
            "true_label": null, "false_label": null,
            "minimum": 20, "maximum": 220, "step": 1, "unit": "bpm",
            "pattern": null, "minLength": null, "maxLength": null
          }
        ],
        "red_flags": [
          {
            "id": "syncope",
            "label": "Syncope",
            "output_style": "boolean",
            "options": null, "max_select": null,
            "true_label": "yes", "false_label": "no",
            "minimum": null, "maximum": null, "step": null, "unit": null,
            "pattern": null, "minLength": null, "maxLength": null
          }
        ]
      }
    }"""
    st.session_state["AIoutput"]=json.loads(test)

    st.switch_page("pages/page_2.py")
