# streamlit_app.py
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Diagnosis Inference", page_icon="🧠", layout="wide")

# ---------------------------------------------
# 1) Wire this to AI output (a Python dict)
# ---------------------------------------------

# Optional: quick demo payload (toggle in sidebar)
SAMPLE_JSON = {
    "condition": "Pulmonary embolism",
    "pre_test_probability": 18.0,
    "likelihood_ratios": [
        {
            "test_name": "D-dimer (high-sensitivity)",
            "test_value": "negative",
            "units": None,
            "lr_positive": 1.6,
            "lr_negative": 0.06,
            "reference": "R/O PE study 2023"
        },
        {
            "test_name": "CTPA",
            "test_value": "no filling defect",
            "units": None,
            "lr_positive": 30.0,
            "lr_negative": 0.08,
            "reference": "Imaging meta-analysis 2022"
        }
    ],
    "post_test_probability": 1.2,
    "reasoning": "Pre-test from Wells/gestalt; negative D-dimer and normal CTPA drive risk down."
}

# --------------- RENDER ----------------
def render_diagnosis(d: dict):
    st.title("🧠 Diagnosis Inference")

    condition = d["condition"]
    pre = float(d["pre_test_probability"])*100
    post = float(d["post_test_probability"])*100
    lr_items = d["likelihood_ratros"] if "likelihood_ratros" in d else d["likelihood_ratios"]  # tolerate any upstream typo
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
    ai_payload = SAMPLE_JSON
elif 'AIoutput3' in st.session_state:
    ai_payload = st.session_state['AIoutput3']
else:
    ai_payload = None

# Render
if ai_payload is None:
    st.info("Assign your AI dict to `ai_payload` (above). Or use the sidebar dev input to test.")
else:
    render_diagnosis(ai_payload)