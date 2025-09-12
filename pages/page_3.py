import streamlit as st
from openai import OpenAI
st.markdown("# Pre-test Probabilities 🎲")
st.sidebar.markdown("# Pre-test Probabilities 🎲")
import json
import streamlit as st

# ---- Replace with your model output (or load from request) ----
raw = r'''{"case_id":"case-AD-44M-CP-001","applied_features":[{"condition":"Aortic dissection","feature":"Connective tissue disease","value":"present","likelihood_ratio":14.0,"direction":"increase","evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"condition":"Aortic dissection","feature":"Hypertension","value":"present","likelihood_ratio":1.46,"direction":"increase","evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"condition":"Aortic dissection","feature":"Abrupt-onset pain","value":"present","likelihood_ratio":2.48,"direction":"increase","evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"condition":"Aortic dissection","feature":"Back","value":"present","likelihood_ratio":2.32,"direction":"increase","evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"condition":"Aortic dissection","feature":"Tearing/ripping","value":"present","likelihood_ratio":42.07,"direction":"increase","evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"condition":"Aortic dissection","feature":"Pulse deficit","value":"present","likelihood_ratio":31.14,"direction":"increase","evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"condition":"Aortic dissection","feature":"Hypotension","value":"present","likelihood_ratio":17.2,"direction":"increase","evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"condition":"Aortic dissection","feature":"New murmur","value":"present","likelihood_ratio":9.41,"direction":"increase","evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"condition":"Aortic dissection","feature":"Pleuritic","value":"absent","likelihood_ratio":0.9,"direction":"decrease","evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"condition":"Acute coronary syndrome","feature":"Dyspnoea","value":"present","likelihood_ratio":1.2,"direction":"increase","evidence_ids":["file-1Wm3yC3Djoz7CTc64pKVsW-ACS_Likelihood_Ratios.csv"]},{"condition":"Acute coronary syndrome","feature":"Diaphoresis","value":"present","likelihood_ratio":1.3,"direction":"increase","evidence_ids":["file-1Wm3yC3Djoz7CTc64pKVsW-ACS_Likelihood_Ratios.csv"]},{"condition":"Acute coronary syndrome","feature":"Worse with exertion","value":"absent","likelihood_ratio":0.75,"direction":"decrease","evidence_ids":["file-1Wm3yC3Djoz7CTc64pKVsW-ACS_Likelihood_Ratios.csv"]},{"condition":"Pulmonary embolism","feature":"Shock","value":"present","likelihood_ratio":4.07,"direction":"increase","evidence_ids":["file-TTRXCDCYMmP9ivmf1Xz5Xq-pulmonary_embolism_LRs.csv"]},{"condition":"Pulmonary embolism","feature":"Tachypnoea","value":"present","likelihood_ratio":1.34,"direction":"increase","evidence_ids":["file-TTRXCDCYMmP9ivmf1Xz5Xq-pulmonary_embolism_LRs.csv"]},{"condition":"Pulmonary embolism","feature":"Dyspnoea","value":"present","likelihood_ratio":1.42,"direction":"increase","evidence_ids":["file-TTRXCDCYMmP9ivmf1Xz5Xq-pulmonary_embolism_LRs.csv"]},{"condition":"Pulmonary embolism","feature":"Current DVT","value":"absent","likelihood_ratio":0.787,"direction":"decrease","evidence_ids":["file-TTRXCDCYMmP9ivmf1Xz5Xq-pulmonary_embolism_LRs.csv"]},{"condition":"Pulmonary embolism","feature":"Immobilization","value":"absent","likelihood_ratio":0.893,"direction":"decrease","evidence_ids":["file-TTRXCDCYMmP9ivmf1Xz5Xq-pulmonary_embolism_LRs.csv"]},{"condition":"Pulmonary embolism","feature":"Surgery","value":"absent","likelihood_ratio":0.897,"direction":"decrease","evidence_ids":["file-TTRXCDCYMmP9ivmf1Xz5Xq-pulmonary_embolism_LRs.csv"]},{"condition":"Pulmonary embolism","feature":"Active cancer","value":"absent","likelihood_ratio":0.925,"direction":"decrease","evidence_ids":["file-TTRXCDCYMmP9ivmf1Xz5Xq-pulmonary_embolism_LRs.csv"]},{"condition":"Pulmonary embolism","feature":"Past history of VTE","value":"absent","likelihood_ratio":0.94,"direction":"decrease","evidence_ids":["file-TTRXCDCYMmP9ivmf1Xz5Xq-pulmonary_embolism_LRs.csv"]},{"condition":"Pneumonia","feature":"Fever ≥38 °C","value":"present","likelihood_ratio":3.21,"direction":"increase","evidence_ids":["file-MfRbjD1XHSCrMv8DZDqRMa-pneumonia_LRs.csv"]},{"condition":"Pneumonia","feature":"Respiratory rate ≥20/min","value":"present","likelihood_ratio":3.47,"direction":"increase","evidence_ids":["file-MfRbjD1XHSCrMv8DZDqRMa-pneumonia_LRs.csv"]},{"condition":"Pneumonia","feature":"Pulse >100/min","value":"present","likelihood_ratio":2.79,"direction":"increase","evidence_ids":["file-MfRbjD1XHSCrMv8DZDqRMa-pneumonia_LRs.csv"]},{"condition":"Pneumonia","feature":"Chest pain","value":"present","likelihood_ratio":1.37,"direction":"increase","evidence_ids":["file-MfRbjD1XHSCrMv8DZDqRMa-pneumonia_LRs.csv"]},{"condition":"Pneumonia","feature":"Crackles","value":"absent","likelihood_ratio":0.75,"direction":"decrease","evidence_ids":["file-MfRbjD1XHSCrMv8DZDqRMa-pneumonia_LRs.csv"]},{"condition":"Musculoskeletal chest pain","feature":"Anterior chest wall tenderness","value":"absent","likelihood_ratio":0.0606,"direction":"decrease","evidence_ids":["file-Gf2FDPRYjpJ81vLJrDTrDt-MSK_LRs_chest_pain.csv"]},{"condition":"COPD (new diagnosis)","feature":"Never smoked","value":"absent (never smoker)","likelihood_ratio":0.2,"direction":"decrease","evidence_ids":["file-3qmWpvyCB5KuaKFiDePsoc-COPD_Likelihood_Ratios.csv"]},{"condition":"COPD (new diagnosis)","feature":"Age <45","value":"present (age 44)","likelihood_ratio":0.2,"direction":"decrease","evidence_ids":["file-3qmWpvyCB5KuaKFiDePsoc-COPD_Likelihood_Ratios.csv"]},{"condition":"COPD (new diagnosis)","feature":"Male gender","value":"male","likelihood_ratio":1.6,"direction":"increase","evidence_ids":["file-3qmWpvyCB5KuaKFiDePsoc-COPD_Likelihood_Ratios.csv"]},{"condition":"Pericarditis","feature":"Male sex (modifier)","value":"male","likelihood_ratio":1.85,"direction":"increase","evidence_ids":["CONTEXT_PERICARDITIS_SEX_MOD"]}],"differentials":[{"rank":1,"diagnosis":"Aortic dissection","probability":0.999955,"feature_notes":"Sudden tearing retrosternal pain radiating to back; hypotension; pulse deficits; diastolic AR-type murmur; connective tissue disorder; hypertension.","evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"],"confidence":"high"},{"rank":2,"diagnosis":"Pneumonia","probability":0.39455,"feature_notes":"Fever 38.0°C, tachypnoea 30/min, tachycardia 120/min, chest pain; clear lungs reduce probability.","evidence_ids":["file-MfRbjD1XHSCrMv8DZDqRMa-pneumonia_LRs.csv"],"confidence":"medium"},{"rank":3,"diagnosis":"Gastro-oesophageal/upper GI cause of chest pain","probability":0.3,"feature_notes":"Retrosternal pain without palpation reproducibility; no exertional component. No validated LRs applied.","evidence_ids":["CONTEXT_BASELINES"],"confidence":"low"},{"rank":4,"diagnosis":"Pulmonary embolism","probability":0.242146,"feature_notes":"Shock with tachypnoea and dyspnoea increases probability; absence of DVT signs, immobilization, surgery, active cancer, and prior VTE reduces it.","evidence_ids":["file-TTRXCDCYMmP9ivmf1Xz5Xq-pulmonary_embolism_LRs.csv"],"confidence":"medium"},{"rank":5,"diagnosis":"Mental-health related chest pain (e.g., panic)","probability":0.23,"feature_notes":"Baseline risk for chest pain presentations; not adjusted due to confounding by shock/fever.","evidence_ids":["CONTEXT_BASELINES"],"confidence":"low"},{"rank":6,"diagnosis":"Acute coronary syndrome","probability":0.103713,"feature_notes":"Dyspnoea and diaphoresis increase while non-exertional pain decreases probability; pleuritic pain absent (no effect).","evidence_ids":["file-UoejGy5BUAJgrT9NKEuCv2-ACS_prevalence_baseline_rates.csv","file-1Wm3yC3Djoz7CTc64pKVsW-ACS_Likelihood_Ratios.csv"],"confidence":"medium"},{"rank":7,"diagnosis":"Pericarditis","probability":0.078465,"feature_notes":"Male sex increases baseline; no classic pericarditis features documented (positional/pleuritic/ECG).","evidence_ids":["CONTEXT_PERICARDITIS_SEX_MOD"],"confidence":"low"},{"rank":8,"diagnosis":"Musculoskeletal chest pain","probability":0.023019,"feature_notes":"Absence of anterior chest wall tenderness markedly lowers probability.","evidence_ids":["file-Gf2FDPRYjpJ81vLJrDTrDt-MSK_LRs_chest_pain.csv"],"confidence":"medium"},{"rank":9,"diagnosis":"Pneumothorax","probability":0.004,"feature_notes":"Baseline only; no unilateral signs, normal percussion and midline trachea.","evidence_ids":["CONTEXT_BASELINES"],"confidence":"low"},{"rank":10,"diagnosis":"COPD (new diagnosis)","probability":0.000646,"feature_notes":"Never smoked and age <45 reduce probability; male sex increases slightly.","evidence_ids":["file-3qmWpvyCB5KuaKFiDePsoc-COPD_Likelihood_Ratios.csv"],"confidence":"medium"}],"recommended_investigations":{"bloods":[{"test":"Group and save / crossmatch","priority":1,"rationale":"Prepare for potential urgent aortic surgery; high-risk dissection.","targets":["Aortic dissection"],"safety_priority":true,"evidence_ids":[]},{"test":"Urea & electrolytes, creatinine","priority":2,"rationale":"Assess renal function before contrast CTA; monitor shock.","targets":["Aortic dissection","Pulmonary embolism","Pneumonia"],"safety_priority":true,"evidence_ids":[]},{"test":"Full blood count","priority":3,"rationale":"Assess anaemia/leukocytosis.","targets":["Aortic dissection","Pneumonia"],"safety_priority":false,"evidence_ids":[]},{"test":"Coagulation screen (PT/INR, aPTT)","priority":4,"rationale":"Baseline before potential anticoagulation/surgery.","targets":["Aortic dissection","Pulmonary embolism"],"safety_priority":true,"evidence_ids":[]},{"test":"High-sensitivity troponin","priority":5,"rationale":"Identify myocardial injury/ACS or dissection-related coronary involvement.","targets":["Acute coronary syndrome","Aortic dissection"],"safety_priority":true,"evidence_ids":["file-1Wm3yC3Djoz7CTc64pKVsW-ACS_Likelihood_Ratios.csv"]},{"test":"CRP +/- Procalcitonin","priority":6,"rationale":"Support pneumonia diagnosis and severity assessment.","targets":["Pneumonia"],"safety_priority":false,"evidence_ids":["file-MfRbjD1XHSCrMv8DZDqRMa-pneumonia_LRs.csv"]},{"test":"Arterial/Venous blood gas with lactate","priority":7,"rationale":"Assess hypoxia and shock; guide resuscitation.","targets":["Aortic dissection","Pulmonary embolism","Pneumonia"],"safety_priority":true,"evidence_ids":[]},{"test":"Blood cultures","priority":8,"rationale":"Sepsis work-up with fever before antibiotics if safe to delay briefly.","targets":["Pneumonia"],"safety_priority":false,"evidence_ids":[]}],"bedside":[{"test":"12-lead ECG","priority":1,"rationale":"Immediate safety test for ischaemia and to detect complications of dissection.","targets":["Acute coronary syndrome","Aortic dissection","Pulmonary embolism"],"safety_priority":true,"evidence_ids":["file-1Wm3yC3Djoz7CTc64pKVsW-ACS_Likelihood_Ratios.csv"]},{"test":"POCUS transthoracic echocardiography","priority":2,"rationale":"Look for aortic regurgitation, pericardial effusion/tamponade, aortic root dilation, RV strain.","targets":["Aortic dissection","Pericarditis","Pulmonary embolism"],"safety_priority":true,"evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"test":"Continuous pulse oximetry and cardiac monitoring","priority":3,"rationale":"Monitor for hypoxia/arrhythmia while evaluating high-risk causes.","targets":["Pulmonary embolism","Aortic dissection","Pneumonia"],"safety_priority":true,"evidence_ids":[]}],"radiology":[{"test":"CTA aorta (arch to iliac bifurcation)","priority":1,"rationale":"Definitive imaging for suspected aortic dissection in unstable patient as soon as feasible.","targets":["Aortic dissection"],"safety_priority":true,"evidence_ids":["file-P6Kub4VWvzcpohDyEU6aEF-aortic_dissection_LRs.csv"]},{"test":"Portable chest X-ray","priority":2,"rationale":"Rapid assessment for mediastinal widening, alternate pathology, and pneumonia.","targets":["Aortic dissection","Pneumonia","Pneumothorax"],"safety_priority":true,"evidence_ids":[]},{"test":"CT pulmonary angiography (if CTA aorta negative and PE suspicion persists)","priority":3,"rationale":"Definitive imaging for PE.","targets":["Pulmonary embolism"],"safety_priority":true,"evidence_ids":[]}]},"missing_fields":["ECG findings not yet available","No chest X-ray reported","Laboratory results (troponin, CRP/PCT, D-dimer) not available","No bedside echocardiography findings"]}'''
data = json.loads(raw)
# ---------------------------------------------------------------

def show_applied_features(applied_features):
    import streamlit as st

    with st.expander("Show applied clinical features & likelihood ratios"):
        if not applied_features:
            st.info("No clinical features applied.")
            return

        # Group features by condition/diagnosis
        grouped = {}
        for f in applied_features:
            cond = f.get("condition", "Unspecified")
            grouped.setdefault(cond, []).append(f)

        # Render each condition section as sub-expanders
        for cond, feats in grouped.items():
            with st.expander(f"{cond} ({len(feats)} features)"):
                for f in feats:
                    feat_name = f.get("feature", "Unknown feature")
                    val = f.get("value", "")
                    lr = f.get("likelihood_ratio", "")
                    direction = f.get("direction", "")
                    ev = ", ".join(f.get("evidence_ids", []))
                    st.markdown(
                        f"- **{feat_name}**: {val} "
                        f"(LR = `{lr}`, {direction})  "
                        f"{'📖 ' + ev if ev else ''}"
                    )
# --- Differentials with sliders ---
st.subheader("Differentials:") 
"Please find the estimated likelihood of considered differentials below. Adjust probabilities as required (%). Please note they are all independent probabilities. "
"On submission, these likelihoods will be used as pre-test probabilities for the investigations below."
adjusted_dx = []
show_applied_features(data["applied_features"])

for d in sorted(data["differentials"], key=lambda x: x["rank"]):
    label = d["diagnosis"]
    p0 = float(d["probability"])
    p_pct = int(round(p0 * 100))
    # Slider 0..100% with 1% step
    p_new_pct = st.slider(f"{d['rank']}. {label}", 0, 100, p_pct, 1)
    p_new = max(0.0, min(1.0, p_new_pct / 100.0))
      # Rationale/description under the slider
    notes = d.get("feature_notes", "")
    if notes:
        st.caption(f"**Why:** {notes}")

    adjusted_dx.append({
        "rank": d["rank"],
        "diagnosis": label,
        "probability": p_new
    })

st.divider()

# --- Investigations by category with inputs for results ---
st.subheader("Enter investigation results")

ix_results = {"bloods": {}, "bedside": {}, "radiology": {}}

def investigation_section(title, items, category_key):
    if not items:
        return
    st.markdown(f"### {title}")
    for item in sorted(items, key=lambda x: x.get("priority", 999)):
        test = item["test"]
        prio = item.get("priority", "-")
        rationale = item.get("rationale", "")
        # Clean, no "bloods:"/"bedside:" prefix — just the test name
        st.markdown(f"**{test}**  ·  Priority **{prio}**")
        if rationale:
            st.caption(f"**Why:** {rationale}")

        # Click-to-add textbox for result
        with st.container():
            add_box = st.checkbox("Add result", key=f"chk_{category_key}_{test}")
            if add_box:
                val = st.text_input(
                    "Result",
                    key=f"in_{category_key}_{test}",
                    placeholder="Enter result (e.g., 45 ng/L, 'ST depression', 'mediastinal widening')"
                )
                if val != "":
                    ix_results[category_key][test] = val
        st.write("")  # small spacer

investigation_section("Bloods",   data["recommended_investigations"]["bloods"],   "bloods")
investigation_section("Bedside",  data["recommended_investigations"]["bedside"],  "bedside")
investigation_section("Radiology",data["recommended_investigations"]["radiology"],"radiology")

st.divider()

# ================================ Submit ================================
# --- Submit payload (adjusted probs + entered results) ---
if st.button("Send results"):
    payload = {
        "case_id": data["case_id"],
        "adjusted_differentials": adjusted_dx,
        "investigation_results": ix_results
    }
    st.success("Prepared payload to send:")
    st.code(json.dumps(payload, indent=2))
    # Here you would POST to your backend, e.g.:
    # import requests
    # r = requests.post("https://your-backend/cases/submit", json=payload, timeout=30)
    # st.write(r.status_code, r.text)
