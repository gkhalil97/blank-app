# streamlit_app.py
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Diagnosis Inference", page_icon="🧠", layout="wide")

# ---------------------------------------------
# 1) Wire this to AI output (a Python dict)
# ---------------------------------------------

# Optional: quick demo payload (toggle in sidebar)
SAMPLE_JSON = r"""{
"differentials": [
{
"condition": "Aortic dissection",
"pre_test_probability": 1,
"likelihood_ratios": [
{
"test_name": "Portable chest X-ray (CXR)",
"test_value": "Normal study; no mediastinal widening (\"NAD\")",
"units": "N/A",
"lr_positive": 3.4,
"lr_negative": 0.3,
"reference": "Rational Clinical Examination: normal mediastinum on CXR reduces odds of dissection (LR−≈0.3). Widened mediastinum increases odds (LR+ reported ~3–10 across studies). JAMA. 2002;287:2262-72; later reviews show LR− range 0.14–0.60. citeturn6search2turn13search0"
}
],
"post_test_probability": 1,
"reasoning": "Search/lookup and classification:\n- Chest X-ray and aortic dissection: JAMA Rational Clinical Examination reports that a normal mediastinum/aorta on CXR decreases the probability of acute thoracic aortic dissection with LR−≈0.3; subsequent meta-analyses show LR− ranging ~0.14–0.60. We use LR−=0.30. citeturn6search2turn13search0\nCalculations (Bayes):\n- Given pre-test probability p=1.00 (odds=∞), any finite LR (including LR−=0.30) leaves odds=∞ → post-test probability remains 1.00. This indicates the provided pre-test (100%) is not updateable by testing; if your intended pre-test was lower (e.g., 0.20), then with LR−=0.30: odds 0.20/(0.80)=0.25 → 0.25×0.30=0.075 → post-test p=0.075/(1+0.075)=0.0698 (≈7.0%).\nNotes/limitations:\n- CXR cannot exclude dissection; if suspicion is material, definitive imaging (CTA/TEE/MRA) is required. The pre-test probability of 100% is likely a placeholder—please confirm an intended value to enable meaningful updating. citeturn6search5"
},
{
"condition": "Pneumonia",
"pre_test_probability": 0.39,
"likelihood_ratios": [
{
"test_name": "C-reactive protein (CRP)",
"test_value": "30 mg/L (interpreted as mg/L; input listed mmol/L). Using threshold ≥20 mg/L → classified Positive.",
"units": "mg/L",
"lr_positive": 2.08,
"lr_negative": 0.32,
"reference": "Meta-analysis of adult CAP biomarkers: CRP LR+ 2.08 and LR− 0.32 at 20 mg/L; LR+ 3.64 and LR− 0.36 at 50 mg/L; LR+ 5.89 and LR− 0.47 at 100 mg/L. We used the 20 mg/L cut for classification (patient value 30 mg/L). citeturn7search0"
},
{
"test_name": "Portable chest X-ray (CXR) vs CT for CAP",
"test_value": "Normal CXR (no infiltrate) → classified Negative",
"units": "N/A",
"lr_positive": 3.98,
"lr_negative": 0.36,
"reference": "Updated systematic review (studies using CT reference): CXR sensitivity 72.6%, specificity 82.0% → LR+ 3.98, LR− 0.36. We used LR− for a normal film. citeturn9search0"
}
],
"post_test_probability": 0.32374904659701653,
"reasoning": "Search/lookup and classification:\n- CRP: For CAP diagnosis in adults, CRP has cutoffs with reported LRs; at 20 mg/L, LR+≈2.08 and LR−≈0.32; at 50 mg/L, LR+≈3.64 and LR−≈0.36. Patient CRP reported as 30 “mmol/L”; standard CRP units are mg/L—assumed 30 mg/L. Classified positive at the 20 mg/L threshold. citeturn7search0\n- Chest radiograph: Using CT as reference, pooled CXR LR−≈0.36 for a normal film. Classified negative (no infiltrate). citeturn9search0\nCalculations (Bayes):\n- Start p=0.39 → odds=0.39/0.61=0.6393.\n- Apply CRP positive (LR+=2.08): odds→0.6393×2.08=1.3298 → p=1.3298/(1+1.3298)=0.5708.\n- Apply CXR negative (LR−=0.36): odds→1.3298×0.36=0.4787 → p=0.4787/(1+0.4787)=0.3237 (≈32.4%).\nNotes/limitations:\n- Different CRP thresholds give different LRs. If you instead treat 50 mg/L as the decision threshold, the CRP would be negative (LR−≈0.36) and the post-test would be lower (≈15–20%) when combined with a negative CXR."
},
{
"condition": "Gastro-oesophageal/upper GI cause of chest pain",
"pre_test_probability": 0.3,
"likelihood_ratios": [],
"post_test_probability": 0.3,
"reasoning": "No provided test has validated diagnostic LRs for this differential in the acute chest-pain setting; we therefore applied no update (LR assumed 1), leaving p unchanged at 0.30."
},
{
"condition": "Pulmonary embolism",
"pre_test_probability": 0.24,
"likelihood_ratios": [],
"post_test_probability": 0.24,
"reasoning": "From the supplied studies, none provide validated diagnostic LRs applicable to the actual observed results for PE (e.g., 'saddle ST-elevation' on ECG is not a typical PE sign with validated LR; normal CXR is non-diagnostic for PE). Without a D-dimer, V/Q, or CTPA result, no Bayesian update was applied (LR=1). For reference, typical ECG signs like S1Q3T3 have only modest LR+ (~2–4) and are prognostic rather than diagnostic; a normal CXR does not exclude PE. citeturn11search4turn11search1"
},
{
"condition": "Mental-health related chest pain (e.g., panic)",
"pre_test_probability": 0.23,
"likelihood_ratios": [],
"post_test_probability": 0.23,
"reasoning": "No validated diagnostic tests among the provided results specifically update this diagnosis; LR assumed 1 → p unchanged at 0.23."
},
{
"condition": "Acute coronary syndrome",
"pre_test_probability": 0.1,
"likelihood_ratios": [
{
"test_name": "12‑lead ECG",
"test_value": "ST‑segment elevation reported ('saddle' morphology) → treated as 'any ST elevation' for diagnostic LR",
"units": "N/A",
"lr_positive": 11.2,
"lr_negative": 0.3,
"reference": "Rational Clinical Examination: 'any ST elevation' LR+≈11.2 for MI; range for new ST elevation ≥1 mm LR+≈5.7–53.9 across heterogeneous studies. Morphology matters (concave elevation can reflect pericarditis). We used LR+=11.2 for calculation. citeturn3search4turn1search0"
},
{
"test_name": "High‑sensitivity cardiac troponin I (hs‑cTnI) at presentation",
"test_value": "50 ng/L (male). Positivity depends on assay-specific 99th percentile: Abbott (male 35 ng/L) → positive; Siemens Atellica/Centaur (male ~53.5–58 ng/L) → negative. Classification is therefore assay‑dependent.",
"units": "ng/L",
"lr_positive": 6.3,
"lr_negative": 0.135,
"reference": "Assay 99th percentiles: Abbott male 35 ng/L; Siemens Atellica male 53.5 ng/L (2021–22 guideline table). Diagnostic meta‑analysis (sensitive/hs‑cTnI at 99th percentile) shows LR+≈6.3 and LR−≈0.135 for MI at presentation. We did NOT use this in the primary calculation due to assay ambiguity, but we provide a sensitivity analysis below. citeturn12search4turn12search0turn0search2"
}
],
"post_test_probability": 0.5544554455445545,
"reasoning": "Search/lookup and classification:\n- ECG: The RCE series reports substantial diagnostic value of ST elevation for MI (LR+ ~11; range wider in heterogeneous studies). Our ECG descriptor ('saddle ST elevation') can be seen in pericarditis and may lower the effective LR for MI vs pericarditis; we nevertheless apply the established 'any ST elevation' LR for ACS recognition, noting this caveat. citeturn3search4turn1search0\n- hs‑cTnI cutoff: The 99th percentile is assay- and sex-specific. Abbott (male 35 ng/L) would classify 50 ng/L as positive; Siemens Atellica/Centaur male URLs ~53–58 ng/L would classify 50 ng/L as negative. Because the assay is not specified, we did not include troponin in the primary update. We list validated LRs for hs‑cTnI at the 99th percentile (LR+≈6.3; LR−≈0.135) for sensitivity analysis. citeturn12search4turn12search0turn0search2\nPrimary calculation (ECG only):\n- Pre‑test p=0.10 → odds=0.10/0.90=0.1111.\n- Apply ECG ST‑elevation LR+=11.2: odds→0.1111×11.2=1.2444 → p=1.2444/(1+1.2444)=0.5545 (≈55.5%).\nSensitivity analysis (not used for the primary post‑test because the assay is unknown):\n- If hs‑cTnI is positive at the 99th percentile (e.g., Abbott/Beckman assays): odds after ECG=1.2444 → ×6.3=7.84 → p≈0.8869 (88.7%).\n- If hs‑cTnI is negative at the 99th percentile (e.g., Siemens male URL ~53.5–58 ng/L): odds after ECG=1.2444 → ×0.135=0.168 → p≈0.1438 (14.4%).\nActionable next step: confirm the hs‑cTnI assay/platform and repeat per a validated 0/1–3 h algorithm to refine the probability. citeturn0search5turn0search3"
},
{
"condition": "Pericarditis",
"pre_test_probability": 0.08,
"likelihood_ratios": [
{
"test_name": "12‑lead ECG (pattern recognition)",
"test_value": "Reported 'saddle' (concave) ST elevation; pericarditis typically shows diffuse concave ST elevation with PR depression and reciprocal changes in aVR/V1.",
"units": "N/A",
"lr_positive": 1,
"lr_negative": 1,
"reference": "Guidance describes typical ECG patterns but robust, generalizable LRs for pericarditis-specific ECG features are lacking; thus we did not apply a quantitative LR. citeturn2search4turn3search3"
}
],
"post_test_probability": 0.08,
"reasoning": "Search/lookup and classification:\n- ECG features consistent with pericarditis (diffuse, concave ST elevation; PR depression) are described in guidelines and reviews, but we did not find validated, widely generalizable LRs for these specific features to quantify an update. Therefore, no Bayesian change was applied (LR=1). citeturn2search4turn3search3\nNotes:\n- The ECG morphology reported could support pericarditis; echocardiography and inflammatory markers (plus serial ECGs) can strengthen/clarify this diagnosis."
},
{
"condition": "Musculoskeletal chest pain",
"pre_test_probability": 0.02,
"likelihood_ratios": [],
"post_test_probability": 0.02,
"reasoning": "No validated diagnostic LRs among the provided tests for this diagnosis; no update (LR=1)."
},
{
"condition": "Pneumothorax",
"pre_test_probability": 0,
"likelihood_ratios": [
{
"test_name": "Portable AP chest X‑ray",
"test_value": "Normal (no pneumothorax) → Negative",
"units": "N/A",
"lr_positive": 1000000,
"lr_negative": 0.54,
"reference": "Systematic review/meta-analysis vs CT: supine/AP CXR pooled sensitivity ≈0.46 and specificity ≈1.00; thus LR−≈0.54. Positive LR is very large with near-100% specificity, but we used LR− for a negative film. citeturn10search2"
}
],
"post_test_probability": 0,
"reasoning": "Calculations:\n- Pre‑test p=0 → odds=0. Even with LR−=0.54, post‑test odds remain 0 → p=0. The provided pre‑test of 0% makes the test update moot; if a nonzero pre‑test were intended, a normal supine/AP CXR only modestly lowers probability (LR−≈0.54). citeturn10search2"
},
{
"condition": "COPD (new diagnosis)",
"pre_test_probability": 0,
"likelihood_ratios": [],
"post_test_probability": 0,
"reasoning": "No targeted diagnostic tests provided; LR=1, p unchanged at 0%."
}
]
}
"""
# --------------- RENDER ----------------
def render_diagnosis(ddx: dict):
    st.title("🧠 Diagnosis Inference")
    for d in ddx.get("differentials", []):
        condition = d.get("condition")
        pre = float(d.get("pre_test_probability"))*100
        post = float(d.get("post_test_probability"))*100
        lr_items = d.get("likelihood_ratios") # tolerate any upstream typo
        reasoning = d.get("reasoning", "")

        st.markdown(f"### Condition: **{condition}**")

        # Metrics
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.metric("Pre-test probability", f"{pre:.2f} %")
            st.progress(int(round(max(0, min(100, pre)))))
        with c2:
            delta = post - pre
            st.metric("Post-test probability", f"{post:.2f} %", delta=f"{delta:+.2f} pp")
            st.progress(int(round(max(0, min(100, post)))))
        with c3:
            def p_to_odds(pct: float) -> float:
                p = pct / 100.0
                if p <= 0: return 0.0
                if p >= 1: return float("inf")
                return p / (1 - p)
            st.caption("Odds (info)")
            st.write(f"Pre-test odds: **{p_to_odds(pre):.3f}**")
            st.write(f"Post-test odds: **{p_to_odds(post):.3f}**")

        st.divider()

        # LR table
        def fmt(v):
            if v is None: return ""
            if isinstance(v, float): return f"{v:.3g}"
            return str(v)

        rows = [{
            "Test": fmt(x["test_name"]),
            "Value": fmt(x["test_value"]),
            "Units": fmt(x.get("units")),
            "LR+": float(x["lr_positive"]),
            "LR−": float(x["lr_negative"]),
            "Reference": fmt(x["reference"]),
        } for x in lr_items]

        df = pd.DataFrame(rows, columns=["Test", "Value", "Units", "LR+", "LR−", "Reference"])

        st.subheader("Likelihood ratios")
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "LR+": st.column_config.NumberColumn(format="%.3f"),
                "LR−": st.column_config.NumberColumn(format="%.3f"),
            },
        )

        st.subheader("Reasoning")
        st.markdown(reasoning if reasoning else "_No reasoning provided._")

        with st.expander("Raw JSON"):
            st.code(json.dumps(d, indent=2))

# ----------------- DEV INPUT (optional) -----------------
if st.sidebar.toggle("🧪 Dev: open with sample", value=False):
    ai_payload = json.loads(SAMPLE_JSON)
elif 'AIoutput3' in st.session_state:
    ai_payload = st.session_state['AIoutput3']
else:
    ai_payload = None

# Render
if ai_payload is None:
    st.info("Assign your AI dict to `ai_payload` (above). Or use the sidebar dev input to test.")
else:
    render_diagnosis(ai_payload)