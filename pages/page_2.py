import streamlit as st
# pages/Checklist.py
import streamlit as st
import re
import time
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.markdown("## 📝 Checklist")
data = st.session_state.get("AIoutput", "- No checklist available")
answers = st.session_state.setdefault("answers", {})  # persist between reruns


def makenill(d):
    d.clear()

# --- DEV ONLY: boot page_2 with sample JSON ---
if st.sidebar.toggle("🧪 Dev: open with chest pain sample", key="toggle2", on_change=lambda: makenill(answers)):
    test = """{
  "presenting_complaint": "Chest Pain",
  "age": 66,
  "gender": "male",
  "dhx": "statin, apixaban, ramipril, bisoprolol",
  "pmhx": "high cholesterol, angina, high blood pressure, PAD, smoker, drinker, NAFLD, AF",
  "checklist": {
    "history_presenting_complaint": [
      {
        "id": "site_of_pain",
        "label": "Site of pain",
        "output_style": "single_select_multi_option",
        "options": [
          "retrosternal",
          "left chest",
          "right chest",
          "central/diffuse",
          "epigastric",
          "interscapular/back",
          "neck",
          "jaw"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Identify typical sites: retrosternal common in ACS/GERD; interscapular/back raises concern for aortic dissection. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "onset_timing",
        "label": "Onset/timing",
        "output_style": "single_select_multi_option",
        "options": [
          "sudden (seconds–minutes)",
          "rapid (within 1 hour)",
          "gradual (hours)",
          "insidious (days)",
          "intermittent/episodic",
          "constant since onset"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Abrupt onset increases likelihood of aortic dissection; absence lowers it. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "character_of_pain",
        "label": "Character/quality",
        "output_style": "multi_select_multi_option",
        "options": [
          "pressure/heaviness",
          "tightness",
          "sharp/stabbing",
          "tearing/ripping",
          "burning/heartburn-like",
          "pleuritic (worse on inspiration/cough)",
          "positional (worse supine)"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Tearing/ripping supports dissection; pleuritic and positional features decrease AMI likelihood (LR− ≈0.2–0.5). Burning and retrosternal symptoms can support GI/GERD. fileciteturn0file16turn2file0turn1file11",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "radiation",
        "label": "Radiation of pain",
        "output_style": "multi_select_multi_option",
        "options": [
          "no radiation",
          "left arm",
          "right arm/shoulder",
          "both arms/shoulders",
          "neck",
          "jaw",
          "back (interscapular)"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Radiation to both arms increases ACS likelihood (LR+ ~2.6); left arm radiation smaller effect. Back radiation may suggest dissection. fileciteturn1file2turn0file16",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "exertional_pain",
        "label": "Pain triggered/worsened by exertion",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "yes",
        "false_label": "no",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Associated with ACS (LR+ ~1.5–1.8 when present; lack of exertional component slightly lowers ACS probability). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "compare_with_prior_angina",
        "label": "Compared with prior angina/ischemia",
        "output_style": "single_select_multi_option",
        "options": [
          "similar to prior ischemia",
          "worse than previous angina",
          "not similar/no prior angina"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Similar to prior ischemia increases ACS likelihood (LR+ ~2.2); pain worse than prior angina modestly increases risk. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "radiation_both_arms_specific",
        "label": "Radiation to both arms",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Specific feature with LR+ ≈2.6 for ACS when present. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "diaphoresis_present",
        "label": "Diaphoresis with pain",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Increases AMI likelihood (LR+ ≈2.0). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "nausea_vomiting_present",
        "label": "Nausea or vomiting",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Increases AMI likelihood (LR+ ≈1.9). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "pleuritic_pain",
        "label": "Pleuritic (worse on inspiration/cough)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Decreases AMI likelihood (LR− ~0.2–0.6); supports pericarditis (LR+ ~3.3) or PE/pneumothorax/pneumonia. fileciteturn2file0turn2file8",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "positional_worse_supine",
        "label": "Pain worse supine / improves sitting forward",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "positional (worse supine or better leaning forward)",
        "false_label": "no positional change",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Positional pain reduces AMI likelihood (LR− ~0.3) and, if better leaning forward, supports pericarditis. fileciteturn2file0turn2file8",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "pain_reproducible_by_palpation",
        "label": "Pain reproducible by chest wall palpation",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "reproducible",
        "false_label": "not reproducible",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Strongly decreases ACS likelihood (LR− ≈0.28) and supports musculoskeletal chest pain. fileciteturn0file7turn1file18",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "sudden_tearing_quality",
        "label": "Sudden, severe tearing/ripping pain (esp. chest→back)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Increases likelihood of aortic dissection when present. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "syncope_with_pain",
        "label": "Syncope with chest pain",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "yes",
        "false_label": "no",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Raises risk of aortic dissection and also slightly increases probability of PE (LR+ ≈2.38). fileciteturn0file16turn2file17",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "hemoptysis_present",
        "label": "Hemoptysis",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Slightly increases probability of PE (LR+ ≈1.62). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "sudden_unilateral_pleuritic_pain",
        "label": "Sudden unilateral pleuritic chest pain",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Supports pneumothorax (LR+ ≈4 when present). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "sudden_or_progressive_dyspnoea",
        "label": "Sudden or progressive dyspnoea",
        "output_style": "single_select_multi_option",
        "options": [
          "none",
          "sudden onset",
          "progressive over hours–days"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Sudden dyspnoea slightly increases PE likelihood (LR+ ≈1.83). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "gi_features_reflux",
        "label": "GI features",
        "output_style": "multi_select_multi_option",
        "options": [
          "burning/heartburn",
          "pain worse with food intake",
          "retrosternal radiation of burning",
          "epigastric location",
          "episodes <1 hour"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Pain worse with food (GERD LR+ ≈10.5; GI disease LR+ ≈21), retrosternal radiation (LR+ ≈6.4), retrosternal pain (LR+ ≈5.25) support GI/GERD. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "msk_modifiers",
        "label": "MSK modifiers",
        "output_style": "multi_select_multi_option",
        "options": [
          "worse with movement",
          "worse with breathing",
          "localised muscle tension"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Features such as pain worse with movement/breathing and localized muscle tension support non-cardiac causes; movement reduces GI likelihood (LR− ~0.27–0.29) and palpation supports chest wall pain. fileciteturn1file11turn1file12",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "fever_history",
        "label": "Fever history",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present/recent",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Fever supports pneumonia (temp ≥38 °C LR+ ≈3.21) and pericarditis (fever LR+ ≈9.3). fileciteturn2file3turn2file8",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "time_course_pattern",
        "label": "Time course/progression",
        "output_style": "single_select_multi_option",
        "options": [
          "improving",
          "worsening",
          "waxing/waning",
          "constant",
          "single episode",
          "recurrent similar episodes"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Change in pain pattern over prior 24 h increases ACS likelihood (LR+ ≈2.0). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "severity_nrs",
        "label": "Severity (0–10)",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 1,
        "unit": "NRS/10",
        "explanation": "Quantify severity to track response; severity alone is not diagnostic.",
        "minLength": null,
        "maxLength": null
      }
    ],
    "systems_review": [
      {
        "id": "cv_review",
        "label": "Cardiovascular review",
        "output_style": "multi_select_multi_option",
        "options": [
          "dyspnoea on exertion",
          "orthopnoea",
          "PND",
          "palpitations",
          "reduced exercise tolerance"
        ],
        "max_select": 5,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Heart failure features (e.g., crackles on exam) may increase AMI likelihood; palpitations relevant with AF. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "resp_review",
        "label": "Respiratory review",
        "output_style": "multi_select_multi_option",
        "options": [
          "cough",
          "purulent sputum",
          "pleuritic pain",
          "wheeze",
          "recent URTI",
          "hemoptysis"
        ],
        "max_select": 5,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Cough absent lowers pneumonia probability (LR− ≈0.36); hemoptysis slightly increases PE likelihood (LR+ ≈1.62). fileciteturn2file3turn2file2",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "gi_review",
        "label": "GI review",
        "output_style": "multi_select_multi_option",
        "options": [
          "heartburn/regurgitation",
          "dysphagia",
          "odynophagia",
          "post-prandial pain",
          "nocturnal reflux"
        ],
        "max_select": 5,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Heartburn and post-prandial pain support GERD-related chest pain. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "neuro_review",
        "label": "Neurologic review (dissection context)",
        "output_style": "multi_select_multi_option",
        "options": [
          "focal weakness",
          "numbness/tingling",
          "speech disturbance",
          "visual loss",
          "new severe headache"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Subjective/observed neurologic deficits increase likelihood of aortic dissection. ",
        "minLength": null,
        "maxLength": null
      }
    ],
    "past_medical_history_drug_history": [
      {
        "id": "cv_risk_pmhx",
        "label": "Cardiovascular risk/history",
        "output_style": "multi_select_multi_option",
        "options": [
          "hypertension",
          "hyperlipidaemia",
          "diabetes",
          "known CAD/angina",
          "prior MI/PCI/CABG",
          "heart failure",
          "peripheral arterial disease",
          "known aortic aneurysm/dissection",
          "valvular disease (incl. AR/bicuspid)",
          "connective tissue disorder"
        ],
        "max_select": 8,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "PAD increases ACS likelihood (LR+ ≈2.7); known aortic disease raises dissection risk. fileciteturn0file4turn0file16",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "pe_risk_history",
        "label": "VTE/PE risk factors",
        "output_style": "multi_select_multi_option",
        "options": [
          "previous DVT/PE",
          "active cancer",
          "recent surgery (<4 weeks)",
          "recent immobilisation/long travel",
          "unilateral leg swelling/pain",
          "oestrogen therapy (if applicable)"
        ],
        "max_select": 6,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Prior VTE (LR+ ≈1.47), active cancer (≈1.74), recent surgery (≈1.63), immobilisation (≈1.41), leg swelling (≈2.11) modestly increase PE probability. fileciteturn2file2turn2file5",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "resp_pmhx",
        "label": "Respiratory history",
        "output_style": "multi_select_multi_option",
        "options": [
          "COPD/emphysema",
          "asthma",
          "prior pneumothorax",
          "recent pneumonia"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Prior pneumothorax (LR+ ≈7) and COPD (≈5) increase pneumothorax risk. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "current_medicines",
        "label": "Current regular medicines (incl. antiplatelets/anticoagulants, beta-blockers, statins)",
        "output_style": "free_text",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Record antithrombotics (e.g., apixaban) and antianginals; therapy influences testing and risk scores.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "drug_allergies",
        "label": "Drug and other allergies",
        "output_style": "free_text",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Important for analgesia/antibiotic selection.",
        "minLength": null,
        "maxLength": null
      }
    ],
    "social_history": [
      {
        "id": "smoking_status",
        "label": "Smoking status",
        "output_style": "single_select_multi_option",
        "options": [
          "never",
          "ex-smoker",
          "current"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Smoking increases pneumothorax risk (LR+ ≈5) and CAD risk. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "pack_years",
        "label": "If ex/current smoker: pack-years",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 1,
        "unit": "pack-years",
        "explanation": "Dose–response risk for cardiorespiratory disease.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "alcohol_intake",
        "label": "Alcohol intake (units/week)",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 1,
        "unit": "units/week",
        "explanation": "High intake may mimic/worsen GERD symptoms and interact with medicines.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "recreational_drugs",
        "label": "Recreational drug use",
        "output_style": "single_select_multi_option",
        "options": [
          "none",
          "cocaine/amphetamines",
          "cannabis",
          "other"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Cocaine increases risk of ACS and pneumothorax (LR+ ≈4). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "recent_travel_immobility",
        "label": "Recent long-haul travel (>4–6 h) or immobilisation",
        "output_style": "single_select_multi_option",
        "options": [
          "no",
          "yes—flight",
          "yes—car/bus/train",
          "yes—immobilised/bedrest"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Context for PE risk (immobilisation LR+ ≈1.41). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "recent_surgery_or_cancer_treatment",
        "label": "Recent surgery (≤4 weeks) or active cancer treatment",
        "output_style": "single_select_multi_option",
        "options": [
          "none",
          "recent surgery",
          "active cancer treatment"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Recent surgery (LR+ ≈1.63) and active cancer (≈1.74) increase PE likelihood. ",
        "minLength": null,
        "maxLength": null
      }
    ],
    "examination": [
      {
        "id": "heart_rate",
        "label": "Heart rate",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 1,
        "unit": "bpm",
        "explanation": "Tachycardia supports infection/PE but single sign has limited value for PE (LR+ ~1.33). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "resp_rate",
        "label": "Respiratory rate",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 1,
        "unit": "breaths/min",
        "explanation": "RR ≥20/min increases pneumonia likelihood (LR+ ≈3.47); tachypnoea slightly increases PE likelihood (LR+ ≈1.34). fileciteturn2file3turn2file14",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "oxygen_saturation",
        "label": "Oxygen saturation on air",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 1,
        "unit": "%",
        "explanation": "Hypoxia suggests PE/pneumonia/pneumothorax but is non-specific.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "temperature",
        "label": "Temperature",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 0.1,
        "unit": "°C",
        "explanation": "Fever ≥38 °C increases pneumonia likelihood (LR+ ≈3.21) and supports pericarditis. fileciteturn2file3turn2file8",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "systolic_bp_right",
        "label": "Systolic BP right arm",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 1,
        "unit": "mmHg",
        "explanation": "Measure both arms to detect differential (dissection). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "systolic_bp_left",
        "label": "Systolic BP left arm",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 1,
        "unit": "mmHg",
        "explanation": "Compare to right arm; large differential/pulse deficit increases dissection likelihood. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "bp_or_pulse_differential",
        "label": "Pulse deficit or marked systolic BP differential between limbs",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present (pulse deficit/BP differential)",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Increases aortic dissection likelihood when present. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "general_appearance",
        "label": "General appearance",
        "output_style": "multi_select_multi_option",
        "options": [
          "no distress",
          "anxious",
          "pale/clammy",
          "diaphoretic"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Diaphoresis supports AMI (LR+ ≈2.0). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "chest_wall_tenderness_exam",
        "label": "Chest wall tenderness reproducible on palpation",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Decreases ACS likelihood (LR− ≈0.28) and supports MSK. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "heart_sounds_s3",
        "label": "Third heart sound (S3)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Presence increases AMI likelihood (LR+ ≈3.2). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "murmurs",
        "label": "Murmurs/rubs",
        "output_style": "multi_select_multi_option",
        "options": [
          "none",
          "new diastolic murmur of aortic regurgitation",
          "pericardial friction rub"
        ],
        "max_select": 2,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "New AR murmur raises concern for dissection; pericardial friction rub supports pericarditis (LR+ ≈7.2). fileciteturn0file16turn2file8",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "lung_auscultation",
        "label": "Lung auscultation",
        "output_style": "multi_select_multi_option",
        "options": [
          "clear bilaterally",
          "focal crackles",
          "diffuse crackles",
          "wheeze",
          "decreased breath sounds (unilateral)"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Crackles increase pneumonia (LR+ ≈2.42) and may be seen with AMI pulmonary oedema; unilateral decreased breath sounds support pneumothorax (LR+ ≈7). fileciteturn2file3turn2file9",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "chest_percussion",
        "label": "Chest percussion",
        "output_style": "multi_select_multi_option",
        "options": [
          "normal",
          "dullness (consolidation/effusion)",
          "hyper-resonant (suggests pneumothorax)"
        ],
        "max_select": 2,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Hyper-resonance supports pneumothorax (LR+ ≈3). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "trachea_position",
        "label": "Tracheal position",
        "output_style": "single_select_multi_option",
        "options": [
          "midline",
          "deviated left",
          "deviated right",
          "unable to assess"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Deviation with hypotension/absent breath sounds suggests tension pneumothorax. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "leg_exam_for_dvt",
        "label": "Leg examination for DVT signs",
        "output_style": "multi_select_multi_option",
        "options": [
          "no swelling/tenderness",
          "unilateral calf swelling",
          "calf tenderness",
          "pitting oedema (unilateral)",
          "collateral superficial veins"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Leg swelling/thrombophlebitis increase PE likelihood (LR+ ≈2.1–2.2). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "describe_ecg",
        "label": "Describe ECG findings",
        "output_style": "free_text",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Ischaemic changes increase ACS risk but are not definitive; use in conjunction with troponin/risk scores. ",
        "minLength": null,
        "maxLength": null
      }
    ],
    "red_flags": [
      {
        "id": "hemodynamic_instability",
        "label": "Hemodynamic instability (shock, SBP very low, altered consciousness)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Shock markedly increases risk of PE (LR+ ≈4.07) and may occur with MI, dissection, tension pneumothorax. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "sudden_tearing_pain_redflag",
        "label": "Sudden severe tearing/ripping chest or back pain",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Classic for aortic dissection. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "pulse_or_bp_differential_redflag",
        "label": "Pulse deficit or marked inter-arm BP differential",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Increases dissection likelihood. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "new_neuro_deficit_redflag",
        "label": "New focal neurologic deficit with chest pain",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Neurologic involvement increases aortic dissection likelihood. ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "syncope_with_chest_pain",
        "label": "Syncope with chest pain",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "yes",
        "false_label": "no",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Concerning for dissection and slightly increases probability of PE (LR+ ≈2.38). fileciteturn0file16turn2file17",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "severe_hypoxia_redflag",
        "label": "Severe hypoxia or acute respiratory distress",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Consider PE, pneumothorax, pneumonia, ACS-related pulmonary oedema.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "tension_pneumothorax_signs",
        "label": "Signs of tension pneumothorax (tracheal deviation, hypotension, unilateral absent breath sounds)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Life-threatening; unilateral absent breath sounds has high LR+ for pneumothorax (~7). ",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "massive_hemoptysis",
        "label": "Massive hemoptysis",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Emergency; consider PE and other causes. ",
        "minLength": null,
        "maxLength": null
      }
    ]
  }
}
"""
    data=json.loads(test)
if st.sidebar.toggle("🧪 Dev: open with abdominal pain sample", key="toggle1", on_change=lambda: makenill(answers)):
  test = """{
  "presenting_complaint": "Abdominal Pain",
  "age": 67,
  "gender": "female",
  "dhx": "Apixaban",
  "pmhx": "Previous stroke, AF, IBS, fibromyalgia",
  "checklist": {
    "history_presenting_complaint": [
      {
        "id": "site_of_pain",
        "label": "SOCRATES – Site of maximal pain",
        "output_style": "single_select_multi_option",
        "options": [
          "right upper quadrant (RUQ)",
          "epigastric",
          "left upper quadrant (LUQ)",
          "right lower quadrant (RLQ)",
          "periumbilical",
          "suprapubic",
          "left iliac fossa (LIF)",
          "diffuse/generalised",
          "right flank",
          "left flank"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Localisation narrows differential: RUQ (biliary), epigastric (peptic/pancreas), RLQ (appendix/caecum), LIF (diverticulitis), flanks (renal/ureter). Diffuse pain raises peritonitis/ischemia/obstruction.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "onset_timing",
        "label": "SOCRATES – Onset and timing",
        "output_style": "single_select_multi_option",
        "options": [
          "sudden (seconds–minutes)",
          "rapid (minutes–hours)",
          "gradual (hours–days)",
          "insidious (days–weeks)",
          "intermittent/colicky",
          "constant since onset"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Sudden severe onset suggests AAA rupture, mesenteric ischemia, or perforation; gradual/intermittent fits biliary/renal colic or bowel obstruction.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "character_quality",
        "label": "SOCRATES – Character/quality of pain",
        "output_style": "multi_select_multi_option",
        "options": [
          "colicky/cramping",
          "sharp/stabbing",
          "aching/dull",
          "burning",
          "tearing/ripping",
          "pressure/fullness"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Colic suggests luminal obstruction (biliary/renal/bowel). Burning epigastric pain suggests acid/ulcer. Tearing pain radiating to back raises concern for AAA.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "radiation",
        "label": "SOCRATES – Radiation",
        "output_style": "multi_select_multi_option",
        "options": [
          "none",
          "to right shoulder/scapula",
          "to back (thoracolumbar)",
          "loin-to-groin",
          "to pelvis",
          "to chest"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Right shoulder suggests diaphragmatic irritation (cholecystitis). Back radiation suggests pancreatitis/AAA. Loin-to-groin suggests ureteric colic.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "alleviating_aggravating",
        "label": "SOCRATES – Aggravating/relieving factors",
        "output_style": "multi_select_multi_option",
        "options": [
          "movement/coughing",
          "palpation",
          "eating (any)",
          "fatty meals",
          "alcohol",
          "bowel movement",
          "passing flatus",
          "antacids/PPIs help",
          "leaning forward helps",
          "nothing helps"
        ],
        "max_select": 5,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Pain worse on movement/palpation suggests peritonism (LR+ ≈3 for peritoneal signs). Relief with leaning forward supports pancreatitis; fatty meal trigger suggests biliary colic/cholecystitis.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "severity_nrs",
        "label": "SOCRATES – Severity (0–10)",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 1,
        "unit": "NRS/10",
        "explanation": "Quantifies pain for analgesia and reassessment; not diagnostic alone.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "progression_course",
        "label": "SOCRATES – Time course/progression",
        "output_style": "single_select_multi_option",
        "options": [
          "improving",
          "unchanged",
          "worsening",
          "waxing/waning",
          "single episode",
          "recurrent similar episodes"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Worsening constant pain suggests inflammation/ischemia; recurrent episodes fit biliary/renal colic or IBS (diagnosis of exclusion when red flags absent).",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "gi_associated_symptoms",
        "label": "Associated GI symptoms",
        "output_style": "multi_select_multi_option",
        "options": [
          "anorexia",
          "nausea",
          "vomiting",
          "coffee-ground/haematemesis",
          "bloating",
          "heartburn/epigastric burning",
          "diarrhoea",
          "constipation",
          "obstipation (no stool or flatus)",
          "bright red blood per rectum",
          "melaena",
          "early satiety"
        ],
        "max_select": 8,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Obstipation + distension suggests mechanical obstruction. Haematemesis/melaena suggests upper GI bleed (risk increased on apixaban). Early satiety can indicate gastric outlet obstruction/mass.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "vomit_character",
        "label": "If vomiting: character",
        "output_style": "single_select_multi_option",
        "options": [
          "non-bilious",
          "bilious",
          "feculent",
          "coffee-ground/bloody"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Bilious suggests distal to pylorus; feculent suggests distal small/large bowel obstruction; coffee-ground/bloody indicates bleeding.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "bowel_habit_change",
        "label": "Change in bowel habit from baseline",
        "output_style": "single_select_multi_option",
        "options": [
          "no change",
          "new constipation",
          "new diarrhoea",
          "alternating diarrhoea/constipation",
          "new nocturnal symptoms"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "In older adults, new-onset change (esp. with weight loss/bleeding) is a red flag for colorectal pathology rather than IBS.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "jaundice_cholestasis_symptoms",
        "label": "Jaundice or cholestatic symptoms",
        "output_style": "multi_select_multi_option",
        "options": [
          "jaundice",
          "pale (acholic) stools",
          "dark urine",
          "pruritus",
          "no cholestatic symptoms"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Triad of RUQ pain + fever + jaundice suggests ascending cholangitis (emergency). Pale stools/dark urine point to obstructive jaundice.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "urinary_symptoms",
        "label": "Urinary symptoms",
        "output_style": "multi_select_multi_option",
        "options": [
          "dysuria/urgency",
          "visible haematuria",
          "flank pain colic",
          "urinary retention",
          "fever/rigors with urinary symptoms",
          "no urinary symptoms"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Colicky flank pain with haematuria supports ureteric stone (LR+ ≈3 for haematuria in renal colic). Fever + obstruction suggests pyonephrosis (urologic emergency).",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "systemic_symptoms",
        "label": "Systemic symptoms",
        "output_style": "multi_select_multi_option",
        "options": [
          "fever/rigors",
          "unintentional weight loss",
          "night sweats",
          "syncope/presyncope",
          "generalised myalgia/fatigue",
          "none"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Weight loss and night sweats raise concern for malignancy/infection. Syncope with tearing abdominal/back pain suggests AAA rupture.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "ibd_vs_ibs_screen",
        "label": "IBS vs organic disease screen (given IBS history)",
        "output_style": "multi_select_multi_option",
        "options": [
          "nocturnal pain/diarrhoea",
          "GI bleeding",
          "age >50 at symptom change",
          "unexplained weight loss",
          "iron-deficiency anaemia",
          "family history colorectal cancer/IBD",
          "none of these"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Presence of these features argues against IBS and for organic pathology; absence supports functional disorder.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "anticoag_red_flags_hpc",
        "label": "Features concerning for bleeding on anticoagulation",
        "output_style": "multi_select_multi_option",
        "options": [
          "new abdominal wall bruise/lump after cough/strain (rectus sheath haematoma)",
          "syncope/dizziness",
          "black or bloody stools",
          "haematemesis",
          "back/flank pain with hypotension"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "DOAC use (apixaban) increases risk of GI and retroperitoneal bleeding; abdominal wall pain with ecchymosis suggests rectus sheath haematoma.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "biliary_food_trigger",
        "label": "RUQ/epigastric pain after fatty meal",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "yes",
        "false_label": "no",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Post-prandial, fatty-food–triggered pain supports biliary colic/cholecystitis.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "pancreatitis_pattern",
        "label": "Epigastric pain persistent, radiating to back and eased by leaning forward",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Typical for pancreatitis; back radiation increases likelihood (reported LR+ ≈2–3). Alcohol/biliary risk factors relevant.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "appendicitis_features",
        "label": "Periumbilical pain migrating to RLQ",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Migration to RLQ is a useful predictor of appendicitis (LR+ ≈3). Less typical in older adults but still possible.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "obstruction_features",
        "label": "Triad: colicky pain + distension + obstipation",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "triad present",
        "false_label": "not present",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Suggests mechanical bowel obstruction; prior surgery/hernia increase risk.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "mesenteric_ischaemia_symptom",
        "label": "Pain out of proportion to abdominal findings (esp. with AF)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "yes",
        "false_label": "no",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Embolic mesenteric ischaemia risk increased with atrial fibrillation; disproportionate pain is a classic feature (moderate LR+, high stakes).",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "infective_risks",
        "label": "Infective and exposure risks",
        "output_style": "multi_select_multi_option",
        "options": [
          "sick contacts",
          "recent antibiotics (C. difficile risk)",
          "recent foreign travel/camping",
          "undercooked/seafood ingestion",
          "immunosuppression",
          "none"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Helps assess gastroenteritis/C. difficile/parasites; immunosuppression blunts signs.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "gynae_screen_postmenopausal",
        "label": "Gynaecologic screen (post-menopausal)",
        "output_style": "multi_select_multi_option",
        "options": [
          "new vaginal bleeding",
          "pelvic pain/pressure",
          "vaginal discharge",
          "dyspareunia",
          "no gynaecologic symptoms"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Post-menopausal bleeding is abnormal and may relate to pelvic pathology causing lower abdominal pain.",
        "minLength": null,
        "maxLength": null
      }
    ],
    "systems_review": [
      {
        "id": "cardiorespiratory_review",
        "label": "Cardiorespiratory review",
        "output_style": "multi_select_multi_option",
        "options": [
          "pleuritic chest pain",
          "shortness of breath",
          "cough/sputum",
          "orthopnoea/PND",
          "palpitations",
          "none"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Pneumonia/inferior MI can present as upper abdominal pain; dyspnoea and pleuritic pain suggest extra-abdominal causes.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "gi_review_extra",
        "label": "Additional GI review",
        "output_style": "multi_select_multi_option",
        "options": [
          "dysphagia/odynophagia",
          "early satiety",
          "heartburn/regurgitation",
          "anal pain/pruritus",
          "change in stool calibre",
          "none"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Targets upper GI pathology and distal obstruction/malignancy clues.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "neuro_review",
        "label": "Neurological review (baseline vs new)",
        "output_style": "multi_select_multi_option",
        "options": [
          "new confusion/delirium",
          "new focal deficit",
          "headache",
          "no neurological symptoms"
        ],
        "max_select": 2,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Older adults may present with delirium in sepsis/ischemia; prior stroke noted for baseline comparison.",
        "minLength": null,
        "maxLength": null
      }
    ],
    "past_medical_history_drug_history": [
      {
        "id": "abdominal_surgical_history",
        "label": "Prior abdominal/pelvic surgery or hernia",
        "output_style": "multi_select_multi_option",
        "options": [
          "no prior surgery",
          "appendectomy",
          "cholecystectomy",
          "bowel surgery/adhesions",
          "AAA/vascular surgery",
          "known hernia (ventral/inguinal/femoral)"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Adhesions and hernias are leading causes of small bowel obstruction in older adults.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "gi_and_biliary_history",
        "label": "Known GI/biliary/renal conditions",
        "output_style": "multi_select_multi_option",
        "options": [
          "peptic ulcer disease",
          "gallstones/biliary colic",
          "pancreatitis",
          "diverticular disease",
          "inflammatory bowel disease",
          "kidney stones",
          "no known GI disease"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Pre-existing disease shifts pre-test probabilities toward recurrence/complications.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "vascular_risk_history",
        "label": "Vascular risk/aneurysm history",
        "output_style": "multi_select_multi_option",
        "options": [
          "known AAA/aortic disease",
          "peripheral vascular disease",
          "ischaemic heart disease",
          "hypertension",
          "diabetes",
          "none"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Vascular disease increases risk of mesenteric ischaemia and AAA pathology; AF already present raises embolic risk.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "anticoagulant_details",
        "label": "Anticoagulation details (apixaban)",
        "output_style": "multi_select_multi_option",
        "options": [
          "last dose within 12 h",
          "missed doses",
          "concomitant antiplatelet/NSAID use",
          "prior GI bleed",
          "renal impairment"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Timing, interactions, and renal function affect bleeding risk and reversal planning.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "other_medicines",
        "label": "Other current/recent medicines",
        "output_style": "multi_select_multi_option",
        "options": [
          "NSAIDs",
          "steroids",
          "PPIs/H2 blockers",
          "opioids",
          "recent antibiotics (last 8 weeks)",
          "no other relevant meds"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "NSAIDs/steroids ↑ risk of ulcer/perforation; recent antibiotics raise C. difficile risk; PPIs may mask ulcer symptoms.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "allergies",
        "label": "Drug/food allergies",
        "output_style": "free_text",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Important for analgesia/antibiotic choices.",
        "minLength": null,
        "maxLength": null
      }
    ],
    "social_history": [
      {
        "id": "smoking_status_packyears",
        "label": "Smoking status (pack-years)",
        "output_style": "single_select_multi_option",
        "options": [
          "never",
          "ex-smoker (<10 pack-years)",
          "ex-smoker (≥10 pack-years)",
          "current (<10/day)",
          "current (10–20/day)",
          "current (>20/day)"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Smoking is a key risk for AAA and peptic disease; quantification assists risk stratification.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "alcohol_intake",
        "label": "Alcohol intake (units/week and recent heavy use)",
        "output_style": "single_select_multi_option",
        "options": [
          "none",
          "low/moderate",
          "binge in last 72 h",
          "chronic heavy use"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Alcohol is a major risk factor for pancreatitis and gastritis.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "dietary_triggers_exposures",
        "label": "Dietary triggers and exposures",
        "output_style": "multi_select_multi_option",
        "options": [
          "recent large/fatty meal",
          "seafood/shellfish",
          "unpasteurised/undercooked foods",
          "suspect food poisoning",
          "no relevant exposures"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Links to biliary colic and infectious gastroenteritis workup.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "recent_travel_or_hospital",
        "label": "Recent travel or hospital/antibiotic exposure",
        "output_style": "multi_select_multi_option",
        "options": [
          "recent foreign travel",
          "recent hospitalisation",
          "antibiotics in last 8 weeks",
          "none"
        ],
        "max_select": 2,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Travel-related pathogens and C. difficile risk assessment.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "baseline_function_frailty",
        "label": "Baseline function/frailty and supports",
        "output_style": "single_select_multi_option",
        "options": [
          "independent",
          "some assistance",
          "dependent/care home"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Guides disposition and tolerance of illness/interventions in older adults.",
        "minLength": null,
        "maxLength": null
      }
    ],
    "examination": [
      {
        "id": "general_abdo_inspection",
        "label": "Abdominal inspection",
        "output_style": "multi_select_multi_option",
        "options": [
          "distension",
          "surgical scars",
          "visible peristalsis",
          "caput medusae",
          "pulsatile epigastric mass",
          "Cullen sign (periumbilical ecchymosis)",
          "Grey–Turner sign (flank ecchymosis)",
          "abdominal wall ecchymosis/lump"
        ],
        "max_select": 5,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Distension suggests obstruction/ascites; pulsatile mass suggests AAA; ecchymoses imply intra-abdominal/retroperitoneal bleeding or rectus sheath haematoma (anticoagulated).",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "bowel_sounds",
        "label": "Auscultation – bowel sounds",
        "output_style": "single_select_multi_option",
        "options": [
          "normal",
          "high-pitched/tinkling",
          "hypoactive",
          "absent"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "High-pitched/tinkling suggests obstruction; absent/hypoactive may indicate peritonitis/ileus.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "palpation_quadrant_tenderness",
        "label": "Palpation – quadrant of maximal tenderness",
        "output_style": "single_select_multi_option",
        "options": [
          "RUQ",
          "epigastric",
          "LUQ",
          "RLQ",
          "periumbilical",
          "suprapubic",
          "LIF",
          "generalised"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Local tenderness helps localise source and track progression (e.g., periumbilical to RLQ in appendicitis).",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "peritonism_signs",
        "label": "Peritonism – guarding/rigidity/rebound",
        "output_style": "multi_select_multi_option",
        "options": [
          "no guarding",
          "voluntary guarding",
          "involuntary guarding/rigidity",
          "rebound tenderness"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Peritoneal irritation increases likelihood of surgical pathology (overall LR+ ≈3–5 depending on sign combination).",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "murphy_sign",
        "label": "Murphy sign (arrest of inspiration on RUQ palpation)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "positive",
        "false_label": "negative",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Suggestive of acute cholecystitis (LR+ ≈2–3; LR− ≈0.4).",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "rovsing_psoas_obturator",
        "label": "Appendicitis manoeuvres",
        "output_style": "multi_select_multi_option",
        "options": [
          "McBurney point tenderness",
          "Rovsing sign (RLQ pain on LLQ palpation)",
          "Psoas sign",
          "Obturator sign"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "These increase likelihood of appendicitis when positive (typical LR+ ≈2–3 each); utility lower in older adults but still informative.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "cva_tenderness",
        "label": "Costovertebral angle (CVA) tenderness",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Supports pyelonephritis/renal colic in the right context.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "carnett_sign",
        "label": "Carnett sign (pain worse with tensing abdominal wall)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "positive",
        "false_label": "negative",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Positive sign suggests abdominal wall source (e.g., rectus sheath haematoma) rather than intra-abdominal pathology.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "hernia_orifices_examined",
        "label": "Hernia orifices (inguinal/femoral/umbilical)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "examined",
        "false_label": "not examined",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Strangulated/obstructed hernia is a reversible surgical cause of pain/obstruction in older adults.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "aortic_exam",
        "label": "Aortic palpation and bedside aortic POCUS if concern",
        "output_style": "multi_select_multi_option",
        "options": [
          "no expansile mass felt",
          "expansile pulsatile mass",
          "tender aorta",
          "POCUS aorta performed"
        ],
        "max_select": 2,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "In patients >65 with sudden severe pain/collapse, assessing for AAA is critical; palpation plus POCUS rapidly risk-stratifies.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "rectal_exam",
        "label": "Digital rectal exam (if indicated): stool colour, masses, tenderness",
        "output_style": "free_text",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Melaena/bright red blood guides source; masses/tenesmus suggest distal pathology.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "pv_exam_if_indicated",
        "label": "Pelvic (speculum/bimanual) exam if gynae symptoms",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "done",
        "false_label": "not indicated/not done",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Lower abdominal pain with bleeding/discharge requires pelvic assessment even post-menopause.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "postural_bp",
        "label": "Lying and standing blood pressure (orthostatic drop)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "orthostatic drop present",
        "false_label": "no orthostatic drop",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Advanced observation: supports volume depletion or occult GI bleed; avoid if unstable.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "ambulatory_spo2",
        "label": "Mobile/ambulatory oxygen saturation",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": 1,
        "unit": "% on air/with exertion",
        "explanation": "Advanced observation: unexplained desaturation may point to extra-abdominal pathology (e.g., pneumonia/PE) mimicking abdominal pain.",
        "minLength": null,
        "maxLength": null
      }
    ],
    "red_flags": [
      {
        "id": "hemodynamic_instability",
        "label": "Shock/hemodynamic instability or syncope",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Suggests life-threatening causes such as AAA rupture, massive GI bleed, sepsis, or mesenteric ischaemia; immediate resuscitation and senior review.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "peritonitis_redflag",
        "label": "Generalised peritonitis (rigidity/rebound)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Indicates intra-abdominal catastrophe requiring urgent surgical evaluation.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "gi_bleed_redflag",
        "label": "Haematemesis or melaena/BRBPR (on apixaban)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "yes",
        "false_label": "no",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Anticoagulation increases bleed severity; consider reversal pathways and urgent endoscopic/surgical input.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "biliary_sepsis_redflag",
        "label": "Charcot triad (fever, RUQ pain, jaundice) or hypotension/confusion (Reynolds pentad)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "meets triad/pentad",
        "false_label": "not met",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Ascending cholangitis requires urgent antibiotics and biliary decompression.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "mesenteric_ischaemia_redflag",
        "label": "Severe pain out of proportion to exam in AF/vascular patient",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "High mortality time-critical diagnosis; early CT angiography and surgical review.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "bowel_obstruction_redflag",
        "label": "Persistent vomiting + distension + obstipation",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Classic for high-grade obstruction; risk of strangulation if pain becomes continuous with peritonism.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "aaa_redflag",
        "label": "Sudden tearing abdominal/back pain with collapse or pulsatile mass",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "AAA rupture/dissection is immediately life-threatening; palpation/POCUS expedite diagnosis.",
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "obstructed_infected_kidney_redflag",
        "label": "Fever/rigors with flank pain and urinary obstruction",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "explanation": "Suggests obstructed infected system (pyonephrosis); requires urgent decompression.",
        "minLength": null,
        "maxLength": null
      }
    ]
  }}
  """
  data=json.loads(test)

# Grab stored text (fallback if missing)
if data == "- No checklist available":
    st.warning("Please generate a checklist")
    st.stop()



#if isinstance(data, (str, bytes, bytearray)):
   # try:
   #     data = json.loads(data)
   # except Exception as e:
   #     st.error(f"Could not parse JSON string: {e}")
   #     st.stop()
   # st.session_state["AIoutput"] = data  # store back as dict

# from here on, `data` is a dict  # debug

#just presenting the data inputted back to the user
meta_cols = st.columns(3)
meta_cols[0].metric("Presenting complaint", data.get("presenting_complaint", "—"))
meta_cols[1].metric("Age", data.get("age", "—"))
meta_cols[2].metric("Gender", data.get("gender", "—"))
st.metric("Past Medical History", data.get("pmhx", "—"))
st.metric("Drug History", data.get("dhx", "—"))

#getting the checklist stuff
checklist = data["checklist"]
answers = st.session_state.setdefault("answers", {})  # persist between reruns

#Giving nicer headings
SECTION_TITLES = {
    "history_presenting_complaint": "History of Presenting Complaint",
    "systems_review": "Systems Review",
    "past_medical_history_drug_history": "PMHx / DHx",
    "social_history": "Social History",
    "examination": "Examination",
    "red_flags": "Red Flags",
}

#worth taking obs from everyone
st.markdown("**Vitals**")
vitals_cols=st.columns(4)
bp_cols=st.columns(2)
sats = vitals_cols[0].number_input('O2 Sats (%)', min_value=0, max_value=100)
hr = vitals_cols[1].number_input('HR/min', min_value=20, max_value=220)
temp = vitals_cols[2].number_input('temp (C)', min_value=30.0, max_value=45.0, step=0.1)
rr = vitals_cols[3].number_input('RR/min', min_value=1, max_value=40)
dbp = bp_cols[1].number_input('dBP', min_value=0, max_value=140)
sbp = bp_cols[0].number_input('sBP', min_value=20, max_value=240)

answers["presenting_complaint"] = data.get("presenting_complaint", "—")
answers["age"]= data.get("age", "—")
answers["gender"] = data.get("gender", "—")
answers["past_medical_history"] = data.get("pmhx", "—")
answers["drug_history"] = data.get("dhx", "—")
answers["obs_hr"] = hr
answers["obs_temp"] = temp
answers["obs_sats"] = sats
answers["obs_rr"] = rr
answers["obs_dbp"] = dbp
answers["obs_sbp"] = sbp

def render_item(item):
    """
    Renders one item according to output_style.
    Stores the value in st.session_state['answers'][item['id']].
    """
    oid = item["id"]
    label = item["label"]
    style = item["output_style"]
    opts = item["options"]  # may be None
    max_select = item["max_select"]
    true_label = item["true_label"]
    false_label = item["false_label"]
    minimum = item["minimum"]
    maximum = item["maximum"]
    step = item["step"]
    unit = item["unit"]
    explanation = item["explanation"]
    min_len = item["minLength"]
    max_len = item["maxLength"]

    help_text = None
    key = f"ans_{oid}"

    if style == "boolean":
        # Show true/false labels as help if provided
        tf_help = []
        if true_label: tf_help.append(f"True = {true_label}")
        if false_label: tf_help.append(f"False = {false_label}")
        help_text = " | ".join(tf_help) if tf_help else None
        val = st.toggle(label, value=answers.get(oid, False), help=help_text, key=key)

    elif style == "number":
        unit_txt = f" ({unit})" if unit else ""

        # Pull any saved answer
        default = answers.get(oid)

        # If no answer yet, pick something safe inside the allowed range
        if default is None:
            if minimum is not None:
                default = minimum
            else:
                default = 0

        # --- Ensure type consistency ---
        all_ints = all(
            isinstance(v, int) or v is None
            for v in (minimum, maximum, step, default)
        )

        if all_ints:
            val = st.number_input(
                f"{label}{unit_txt}",
                min_value=minimum if minimum is not None else None,
                max_value=maximum if maximum is not None else None,
                step=step if step is not None else 1,
                value=int(default),
                key=key,
            )
        else:
            val = st.number_input(
                f"{label}{unit_txt}",
                min_value=float(minimum) if minimum is not None else None,
                max_value=float(maximum) if maximum is not None else None,
                step=float(step) if step is not None else 1.0,
                value=float(default),
                format="%.2f",
                key=key,
            )

    elif style == "single_select_multi_option":
        if not opts:
            st.warning(f"{label}: no options provided")
            return
        val = st.selectbox(label, options=opts, index=opts.index(answers.get(oid)) if answers.get(oid) in opts else 0, key=key)

    elif style == "multi_select_multi_option":
        if not opts:
            st.warning(f"{label}: no options provided")
            return
        help_text = f"Select up to {max_select}" if max_select else None
        default = answers.get(oid, [])
        val = st.multiselect(label, options=opts, default=default, help=help_text, key=key)
        if max_select and len(val) > max_select:
            st.error(f"Please select at most {max_select} option(s).")

    elif style == "free_text":
        ph = ""
        val = st.text_input(label, value=answers.get(oid, ""), placeholder=ph, key=key)
        # Basic validation pass
        errs = []
        if min_len is not None and len(val) < min_len:
            errs.append(f"Min length {min_len}")
        if max_len is not None and len(val) > max_len:
            errs.append(f"Max length {max_len}")
        if errs:
            st.warning(" ; ".join(errs))

    else:
        st.warning(f"Unknown output_style: {style}")
        return
    
    colA, colB = st.columns([1,4])

    if explanation:
        if colA.checkbox("More info", key=f"exp_{oid}"):
            st.markdown(explanation)
   
    answers[oid] = val

    if style != "free_text":
      if colB.checkbox("Comment", key=f"comm_{oid}"):
          comment = st.text_area("Comment", value=answers.get(f"{oid}_comment", ""), key=f"comm_text_{oid}")
          answers[f"{oid}_comment"] = comment
    # Persist
    


# Render each section in schema order
for section_key in [
    "history_presenting_complaint",
    "systems_review",
    "past_medical_history_drug_history",
    "social_history",
    "examination",
    "red_flags",
]:
    items = checklist.get(section_key, [])
    if not items:
        continue
    with st.expander(SECTION_TITLES.get(section_key, section_key).title(), expanded=True):
        for it in items:
            render_item(it)


# Save/export
col_a, col_b = st.columns([1,1])
if col_a.button("Save current answers"):
    st.success("Answers saved in session.")

import json
if col_b.download_button(
    "Download JSON (answers + template)",
    data=json.dumps({"template": data, "answers": answers}, indent=2),
    file_name="ed_checklist.json",
    mime="application/json"
):
    st.toast("Downloaded.")
    
# --- Action button ---
if st.button("Submit Checklist"):
    with st.spinner("Uploading checklist..."):
        try:
            # Responses API call (text-in, text-out)
            out = client.responses.create (
                prompt = {
                    "id": "pmpt_68c18bb506ec819685c867061bbce13802152266a9918ce2",
                    "version": "26",
                    "variables": {
                        "answer": json.dumps(answers),
                        "template": json.dumps(data)
                        }},
                store= True,
                previous_response_id=st.session_state.get("checklist_id")  
            )

            # Extract the text
            if "AIoutput2" not in st.session_state:
                st.session_state.AIoutput2 = {}
            if "checklist_id2" not in st.session_state:
                st.session_state.checklist_id2= {}

            st.session_state["AIoutput2"] = json.loads(out.output_text)
            st.session_state["checklist_id2"] = out.id
            #st.markdown (st.session_state["AIoutput2"])
        except Exception as e:
            st.error(f"Checklist request failed: {e}")
    st.success("✅ Pre-test probabilities calculated")
    placeholder = st.empty()
    for i in range (5, 0, -1):
        placeholder.write(f"Switching to Probabilities in {i}…")
        time.sleep(1)
    st.switch_page("pages/page_3.py")
