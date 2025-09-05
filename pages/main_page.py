import streamlit as st
import numpy as np
import pandas as pd
from openai import OpenAI
import time

# Main page content
st.markdown("# Presentation")

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
    
    user_prompt = f"""
You are a clinical decision support tool. Your aim is to help doctors see undifferentiated patients in A&E or GP. 

You will be given a presenting complaint, age, gender, pmhx and dhx. 

You must then produce a comprehensive history and examination checklist that includes red flags. Please structure the checklist NOT in a table. Use the following structure: HPC, Systems Review, SHx, other PMHx and DHx, Red Flags. Please read the documents and make sure you include the features in the history that have likelihood ratios in the PDFs, including negative LRs. 

The doctor will input the information back in from the checklist and you should then calculate the pre-test probability of all likely differentials. Please also recommend investigations. 

The doctor will then input investigation results - please then calculate post test probabilities. Please remember likelihood ratios can only be applied to pre-test odds.

When using likelihood ratios, please don't use that ratio if the p value is >0.05 or if the confidence intervals cross 1. Do not summarise or filter LRs apart from that. Please ensure you use negative and positive likelihood ratios. Please only use data from the PDFs I have uploaded to this project and if data isn’t available don’t use general knowledge. 

Please use the likelihood ratios for ACS and PE from the documents. From the Pulmonary Embolism LRs pdf (West et al) document please consider every aspect of table 2 and 3. For ACS use the ACS LRs (best) pdf document first.

Please use the pre-test probability/prevalence of an ACS from the documents figure 1 from the Ekelund et al article (ACS Pre-tests pdf document).  For ACS use the LRs from the ACS LRs pdf document. 

If PE is a differential use a baseline rate of 7% generally but If the only symptom is syncope use a baseline rate of 1%.

If Aortic Dissection is a differential use a baseline rate of 0.1%.  Please consider likelihood ratios for this differential from the Aortic dissection LRs pdf document. 

When considering pericarditis please use the pericarditis_likelihood_ratios  pdf for your calculations and use a baseline rate of occurrence of 4.4%. For men use a LR+ of 1.85, if female use a LR- of 0.54. The negative likelihood ratio for pleuritic chest pain is valid, but so it’s not so absolute use 0.1 instead. 

When considering a pneumothorax, please use a baseline rate of 0.4% if the patient presents with dyspnoea or chest pain. 

When considering Pneumonia or LRTI or pleurisy, use a baseline rate of 2% for chest pain presentations. For SOB presentations give LRTI a baseline rate of 25% of which pneumonia accounts for 39% of these. Use the pneumonia LRs pdf table 2 for likelihood ratios.

When considering COPD as a new diagnosis, please refer to the COPD1, COPD2 and COPD3 PDFs. Please also consider this when considering a diagnosis of Infective Exacerbation of COPD. Assume a baseline rate of 1% of COPD in all those presenting with acute SOB. If they have never smoked please consider it an unlikely differential unless they have risk factors. 

Please combine likelihood ratios readily, if they are not independent pick the most significant. Try and incorporate as many likelihood ratios as possible in your calculations. If a specific feature is not mentioned assume it is negative and use a negative likelihood ratio. 

If you are using data from the MSK1, Non cardiovascular chest pain and MSK2 pdfs, please make sure to convert the sensitivities and specificities into likelihood ratios. Please make sure to only use ones that have a p<0.05. For MSK causes of chest pain use a baseline rate of 28%. You do not need a standardised palpation score to apply the likelihood ratios.

For gastro-intestinal causes of chest pain please use a baseline rate of 30%. Please derive likelihood ratios from the GORD, GORD vs Angina (table 3) and Non cardiovascular chest pain PDFs. 

For mental health related causes of chest pain use a baseline rate of 23%. Please utilise the specific symptoms mentioned in the Non cardiovascular chest pain pdf. Please consider the Panic pdf. Even if the negative likelihood ratios aren’t very strong please use them anyways. 

For Pneumothorax, use the following likelihood ratios: Tall, thin young male: LR+ 3
Active/Prior smoker: LR+ 5
Prior pneumothorax: LR+ 7
Pregnancy: LR+ 1.5 
COPD Hx: LR+ 5 
Asthmatic: LR+ 2 
Cocaine use: LR+ 4
Underlying lung diseases: LR+ 4
Marfans/EDS: LR+ 3
Sudden severe unilateral pleuritic pain: LR+ 4
Recent Air Travel: LR+ 1.5
Scuba: LR+ 3
Positive pressure ventilation: LR+ 4
Acute SOB: LR+ 4
Unilateral reduced breath sounds: LR+ 7
Hyper resonant percussion: LR+ 3 
Tachycardia: LR+ 1.4, hypoxia: LR+ 1.2
Tachypnoea: LR+ 1.5
Slow onset pain: LR+ 0.4

Here is your patient:
- Age: {age}
- Gender: {gender}
- Presenting complaint: {pc}
- Past medical history: {pmhx}
- Drugs/medications: {dhx}

Output sections:
1) History questions
2) Examination

Keep bullet points short. Please make sure to separate out each individual 'feature' of a history or exam into a different bullet point as we shall need to comment on each one. For example when noting if the pain started suddenly or slowly, keep these in different bullet points. For the type of pain have whether the pain is tearing, or crushing, or pressure etc in different bullet points. For location define all the different locations into different bullet points. Simiularly for all symptoms and thier descriptions. Please do not group multiple symptoms into one bullet point when doing a symptom review, the same for pmhx, fhx, shx, or any history points. For examinations please seperate out the vital signs into different bullet points, similarly for any of the exam points. Please dont add any notes or additional comments. 
"""
    with st.spinner("Generating checklist..."):
        try:
            # Responses API call (text-in, text-out)
            resp = client.responses.create(
                model="gpt-5-nano",   # use a capable, cost-efficient model
                input=[{"role": "user", "content": user_prompt}],
                tools= [{
                        "type" : "file_search",
                        "vector_store_ids" : ["vs_68bafa7f6d3c81919a21cd7ca01c43b1"],
                    }],
            )

            # Extract the text
            st.session_state["AIresponse"] = resp.output_text
            checklist_id = resp.id
            st.success("✅ Checklist generated")
            st.markdown (st.session_state["AIresponse"])
            placeholder = st.empty()
            for i in range (5, 0, -1):
                placeholder.write(f"Switching to checklist in {i}…")
                time.sleep(1)
            st.switch_page("pages/page_2.py")
        except Exception as e:
            st.error(f"Checklist request failed: {e}")
    
    # your logic for generating goes here

      