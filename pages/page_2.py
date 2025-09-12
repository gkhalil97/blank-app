import streamlit as st
# pages/Checklist.py
import streamlit as st
import re
import time
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.markdown("## 📝 Checklist")

# Grab stored text (fallback if missing)
data = st.session_state.get("AIoutput", "- No checklist available")
if data == "- No checklist available":
    "Please generate a checklist"
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
            out = client.responses.create(
                model="gpt-5-nano",   # use a capable, cost-efficient model
                input=json.dumps(answers),
                store=True,
                previous_response_id=st.session_state.get("checklist_id"),
                tools= [{
                        "type" : "file_search",
                        "vector_store_ids" : ["vs_68bafa7f6d3c81919a21cd7ca01c43b1"],
                    }],
            )

            # Extract the text
            st.session_state["AIoutput2"] = out.output_text
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
