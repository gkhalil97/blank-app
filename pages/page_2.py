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

# --- DEV ONLY: boot page_2 with sample JSON ---
if st.sidebar.toggle("🧪 Dev: open with sample"):
    test = """{
  "presenting_complaint": "chest pain",
  "age": 44,
  "gender": "male",
  "dhx": "none",
  "pmhx": "none",
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
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "onset_timing",
        "label": "Onset/timing of pain (abrupt onset is important for aortic dissection )",
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
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "character_of_pain",
        "label": "Character/quality of pain (pleuritic, sharp, positional, or palpation-reproducible features reduce AMI likelihood )",
        "output_style": "multi_select_multi_option",
        "options": [
          "pressure/heaviness",
          "tightness",
          "squeezing/crushing",
          "sharp/stabbing",
          "tearing/ripping",
          "burning/indigestion-like",
          "pleuritic (worse on inspiration/cough)",
          "positional (worse lying supine)"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "radiation",
        "label": "Radiation (arm/jaw/back radiation is informative for AMI risk  )",
        "output_style": "multi_select_multi_option",
        "options": [
          "no radiation",
          "left arm",
          "right arm/shoulder",
          "both arms/shoulders",
          "neck",
          "jaw",
          "back (interscapular)",
          "epigastrium"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "exertional_pain",
        "label": "Pain triggered/worsened by exertion (associated with AMI/ACS  )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "yes",
        "false_label": "no",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "pleuritic_pain",
        "label": "Pleuritic chest pain (decreases AMI likelihood )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "positional_worse_supine",
        "label": "Pain worse when lying flat (positional pain decreases AMI likelihood; consider pericarditis if improved leaning forward )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "yes (worse supine)",
        "false_label": "no",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "pain_reproducible_by_palpation",
        "label": "Pain reproducible by chest wall palpation (decreases AMI likelihood )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "reproducible",
        "false_label": "not reproducible",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "improves_leaning_forward",
        "label": "Pain improves when leaning forward (supports pericarditis differential)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "improves",
        "false_label": "no change/worse",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "diaphoresis_present",
        "label": "Diaphoresis with chest pain (increases AMI likelihood )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "nausea_vomiting_present",
        "label": "Nausea or vomiting with chest pain (increases AMI likelihood )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "associated_symptoms_other",
        "label": "Other associated symptoms",
        "output_style": "multi_select_multi_option",
        "options": [
          "dyspnoea",
          "palpitations",
          "presyncope/syncope",
          "fever/rigors",
          "cough",
          "hemoptysis",
          "heartburn/regurgitation",
          "dysphagia/odynophagia",
          "recent viral illness",
          "anxiety/panic",
          "unilateral leg swelling/pain"
        ],
        "max_select": 6,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
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
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "duration_of_pain",
        "label": "Duration of current episode (minutes/hours)",
        "output_style": "free_text",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": 1,
        "maxLength": 20
      },
      {
        "id": "severity_nrs",
        "label": "Severity (0–10)",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": 0,
        "maximum": 10,
        "step": 1,
        "unit": "NRS/10",
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "sudden_severe_tearing_quality",
        "label": "Sudden severe “tearing/ripping” pain (suggestive of aortic dissection; absence lowers probability )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
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
          "peripheral oedema",
          "palpitations",
          "known heart murmur",
          "exercise tolerance reduced"
        ],
        "max_select": 5,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "resp_review",
        "label": "Respiratory review",
        "output_style": "multi_select_multi_option",
        "options": [
          "pleuritic chest pain",
          "wheeze",
          "productive cough (green/yellow)",
          "rusty sputum",
          "hemoptysis",
          "recent URTI",
          "pleuritic shoulder tip pain"
        ],
        "max_select": 5,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "gi_review",
        "label": "Gastrointestinal review",
        "output_style": "multi_select_multi_option",
        "options": [
          "heartburn/regurgitation",
          "dysphagia",
          "odynophagia",
          "epigastric pain",
          "nausea/vomiting",
          "bloating",
          "pain after meals",
          "pain lying after meals"
        ],
        "max_select": 6,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "neuro_review",
        "label": "Neurologic review (sudden focal deficit can suggest aortic dissection )",
        "output_style": "multi_select_multi_option",
        "options": [
          "weakness (unilateral)",
          "numbness/tingling (unilateral)",
          "speech disturbance",
          "visual loss",
          "new severe headache",
          "syncope"
        ],
        "max_select": 4,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      }
    ],
    "past_medical_history_drug_history": [
      {
        "id": "cardiovascular_risk_factors",
        "label": "Cardiovascular risk factors/past history (history of hypertension raises AD likelihood; prior MI/CAD relevant to ACS  )",
        "output_style": "multi_select_multi_option",
        "options": [
          "none",
          "hypertension",
          "hyperlipidaemia",
          "diabetes",
          "known CAD/angina",
          "prior MI/PCI/CABG",
          "heart failure",
          "known aortic disease/aneurysm",
          "valvular disease (incl. bicuspid aortic valve)",
          "connective tissue disorder (Marfan/Ehlers-Danlos)",
          "family history premature CAD (<55 male/<65 female)"
        ],
        "max_select": 8,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "thromboembolism_history",
        "label": "VTE risk/history (supports PE assessment)",
        "output_style": "multi_select_multi_option",
        "options": [
          "none",
          "previous DVT/PE",
          "active cancer or treatment",
          "recent surgery (<4 weeks)",
          "recent immobilisation/bedrest",
          "oestrogen therapy",
          "pregnancy/postpartum (if applicable)",
          "unilateral leg swelling/pain"
        ],
        "max_select": 6,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "substance_use_risk",
        "label": "Substances that may trigger ACS/AD or mimic chest pain",
        "output_style": "multi_select_multi_option",
        "options": [
          "none",
          "cocaine/amphetamines",
          "excess alcohol",
          "NSAIDs (pericarditis/GI)",
          "PDE-5 inhibitors (if nitrates considered)"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
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
        "pattern": "null",
        "minLength": 0,
        "maxLength": 200
      },
      {
        "id": "allergies",
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
        "pattern": "null",
        "minLength": 0,
        "maxLength": 160
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
        "pattern": null,
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
        "minimum": 0,
        "maximum": 200,
        "step": 1,
        "unit": "pack-years",
        "pattern": null,
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
        "minimum": 0,
        "maximum": 200,
        "step": 1,
        "unit": "units/week",
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "recreational_drugs",
        "label": "Recreational drug use (cocaine/amphetamines increase AD/ACS risk )",
        "output_style": "single_select_multi_option",
        "options": [
          "none",
          "cocaine",
          "amphetamines",
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
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "recent_travel_immobility",
        "label": "Recent long-haul travel (>4–6 h) or immobilisation (PE risk context )",
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
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "baseline_function",
        "label": "Baseline activity/exercise tolerance",
        "output_style": "single_select_multi_option",
        "options": [
          "normal",
          "mildly limited",
          "moderately limited",
          "severely limited"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      }
    ],
    "examination": [
      {
        "id": "avpu_gcs",
        "label": "Conscious level",
        "output_style": "single_select_multi_option",
        "options": [
          "alert",
          "voice responsive",
          "pain responsive",
          "unresponsive"
        ],
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "heart_rate",
        "label": "Heart rate (bpm)",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": 20,
        "maximum": 250,
        "step": 1,
        "unit": "bpm",
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "resp_rate",
        "label": "Respiratory rate (breaths/min)",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": 4,
        "maximum": 80,
        "step": 1,
        "unit": "breaths/min",
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "systolic_bp_right",
        "label": "Systolic BP right arm (mmHg)",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": 50,
        "maximum": 260,
        "step": 1,
        "unit": "mmHg",
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "systolic_bp_left",
        "label": "Systolic BP left arm (mmHg)",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": 50,
        "maximum": 260,
        "step": 1,
        "unit": "mmHg",
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "bp_difference_ge20",
        "label": "Systolic BP difference ≥20 mmHg between arms (increases likelihood of aortic dissection )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "≥20 mmHg",
        "false_label": "<20 mmHg/none",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "oxygen_saturation",
        "label": "Oxygen saturation (%) on air",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": 50,
        "maximum": 100,
        "step": 1,
        "unit": "%",
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "temperature",
        "label": "Temperature (°C)",
        "output_style": "number",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": 30,
        "maximum": 43,
        "step": 0.1,
        "unit": "°C",
        "pattern": null,
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
          "diaphoretic (supports AMI risk )",
          "in respiratory distress"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "jvp_assessment",
        "label": "JVP elevated >3 cm above sternal angle",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "elevated",
        "false_label": "not elevated",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "chest_wall_tenderness_exam",
        "label": "Chest wall tenderness reproducible on palpation (decreases AMI likelihood )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "heart_sounds_s3",
        "label": "Third heart sound (S3) present (increases AMI likelihood )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "murmurs",
        "label": "Murmurs",
        "output_style": "multi_select_multi_option",
        "options": [
          "none",
          "systolic murmur",
          "diastolic murmur of aortic regurgitation (consider AD )",
          "pericardial friction rub (pericarditis)"
        ],
        "max_select": 2,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "pulse_deficits",
        "label": "Pulse deficits between limbs (increases likelihood of aortic dissection )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "lung_auscultation",
        "label": "Lung auscultation",
        "output_style": "multi_select_multi_option",
        "options": [
          "clear bilaterally",
          "focal crackles (supports AMI/pulmonary oedema/pneumonia context )",
          "diffuse crackles",
          "wheeze",
          "reduced breath sounds (unilateral)",
          "bronchial breathing"
        ],
        "max_select": 3,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "chest_percussion",
        "label": "Chest percussion",
        "output_style": "multi_select_multi_option",
        "options": [
          "normal resonance",
          "dullness (consolidation/effusion)",
          "hyper-resonance (consider pneumothorax)"
        ],
        "max_select": 2,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "trachea_position",
        "label": "Tracheal position (deviation suggests tension pneumothorax)",
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
        "pattern": null,
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
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "neuro_focal_deficit",
        "label": "Focal neurologic deficit on exam (increases likelihood of aortic dissection )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "describe_ecg",
        "label": "Describe ECG findings (new ischemic changes raise AMI risk context)",
        "output_style": "free_text",
        "options": null,
        "max_select": null,
        "true_label": null,
        "false_label": null,
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": ".*",
        "minLength": 0,
        "maxLength": 240
      }
    ],
    "red_flags": [
      {
        "id": "hemodynamic_instability",
        "label": "Hemodynamic instability (SBP <90 mmHg, HR >120, altered consciousness)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "sudden_tearing_pain_redflag",
        "label": "Sudden severe tearing/ripping chest or back pain (aortic dissection risk )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "bp_or_pulse_differential_redflag",
        "label": "Pulse or systolic BP differential between limbs (aortic dissection risk )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "new_neuro_deficit_redflag",
        "label": "New focal neurologic deficit with chest pain (aortic dissection risk )",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
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
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "severe_hypoxia",
        "label": "Severe hypoxia (SpO2 <90% on air) or acute respiratory distress",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
        "minLength": null,
        "maxLength": null
      },
      {
        "id": "tension_pneumothorax_signs",
        "label": "Signs of tension pneumothorax (tracheal deviation, hypotension, distended neck veins, unilateral absent breath sounds)",
        "output_style": "boolean",
        "options": null,
        "max_select": null,
        "true_label": "present",
        "false_label": "absent",
        "minimum": null,
        "maximum": null,
        "step": null,
        "unit": null,
        "pattern": null,
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
        "pattern": null,
        "minLength": null,
        "maxLength": null
      }
    ]
  }
}
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
    pattern = item["pattern"]
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

    # Persist
    answers[oid] = val


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
                    "version": "22",
                    "variables": {
                        "answer": json.dumps(answers)
                        }},
                #store=True,
                #previous_response_id=st.session_state.get("checklist_id")  
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
