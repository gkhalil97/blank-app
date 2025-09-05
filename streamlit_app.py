import streamlit as st
import numpy as np
import pandas as pd

st.title("🤖👨🏻‍⚕️ Heuris AI")
st.write(
    "Welcome to Heuris AI, your medical AI assistant and clinical decision support. Please work through the patient " \
    "journey by first inputting your patients main five demographics: Age, Gender, PC, PMHx, DHx. Please then work through the patient journey from history and examination, to investigation and then to diagnosis. "
)

import streamlit as st

# try to locate the installed package + client class
try:
    from openai import OpenAI
    st.write("OpenAI class repr:", OpenAI)
    st.write("OpenAI class module:", OpenAI.__module__)
    mod = __import__(OpenAI.__module__.split('.')[0])
    st.write("Module file:", getattr(mod, "__file__", "(no __file__)"))
except Exception as e:
    st.error(f"Import failed: {e}")

# try to read the installed distribution version
try:
    import importlib.metadata as im
    st.write("openai dist version:", im.version("openai"))
except Exception as e:
    st.write("openai dist version lookup failed:", e)


# Define the pages
main_page = st.Page("pages/main_page.py", title="Presentation", icon="🎈")
page_2 = st.Page("pages/page_2.py", title="Checklist", icon="❄️")
page_3 = st.Page("pages/page_3.py", title="Pre-test", icon="🎉")

# Set up navigation
pg = st.navigation([main_page, page_2, page_3])

# Run the selected page
pg.run()

import time

