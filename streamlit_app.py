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
page_4 = st.Page("pages/page_4.py", title="Diagnosis", icon="🧠")

# Set up navigation
pg = st.navigation([main_page, page_2, page_3, page_4])

# Run the selected page
pg.run()

import time
# --- DEV ONLY: boot page_2 with sample JSON ---

