import streamlit as st

# 1. Page Config & CSS Injection to hide Streamlit header/footer/icons
st.set_page_config(page_title="Somerset NHS DKA Tool", layout="wide")

# This hides the 'hamburger' menu, the 'Deploy' button, and the GitHub icon
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            #stDecoration {display:none;}
            </style>
            """
# FIXED: Changed unsafe_text_area to unsafe_allow_html
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- APP HEADER ---
st.title("Adult DKA Clinical Decision Support")
st.caption("Standardized Management based on NHS Somerset Foundation Trust Guidelines")

# --- SIDEBAR: CLINICAL PARAMETERS ---
with st.sidebar:
    st.header("Patient Data")
    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=250.0, value=70.0)
    
    st.divider()
    st.subheader("Current Vitals")
    sbp = st.number_input("Systolic BP (mmHg)", min_value=40, max_value=250, value=120)
    gcs = st.number_input("GCS Score", min_value=3, max_value=15, value=15)
    spo2 = st.slider("SpO2 on Air (%)", 70, 100, 98)
    
    st.divider()
    st.subheader("Current Lab Results")
    gluc = st.number_input("Glucose (mmol/L)", min_value=0.0, step=0.1)
    ket = st.number_input("Ketones (mmol/L)", min_value=0.0, step=0.1)
    v_ph = st.number_input("Venous pH", min_value=6.8, max_value=7.6, step=0.01, value=7.35)
    v_bic = st.number_input("Bicarbonate (mmol/L)", min_value=0.0, step=0.1)
    k_plus = st.number_input("Potassium (mmol/L)", min_value=0.0, max_value=10.0, step=0.1, value=4.0)

# --- SECTION 1: EMERGENCY TRIGGERS ---
st.header("1. Emergency Assessment")

# Shock Logic (Page 1)
if sbp < 90:
    st.error("🚨 **PATIENT SHOCKED (SBP < 90mmHg)**: Give 500mL 0.9% NaCl over 10-15 mins. Repeat until BP > 90.")
else:
    st.success("SBP ≥ 90mmHg: Follow standard fluid resuscitation.")

# Critical Care Triggers (Page 1)
severe_criteria = []
if v_bic < 5.0 or v_ph < 7.1: severe_criteria.append("Bicarb < 5 or pH < 7.1")
if gcs < 12: severe_criteria.append("GCS < 12")
if k_plus < 3.5: severe_criteria.append("K+ < 3.5 mmol/L (Admission Risk)")

if severe_criteria:
    st.warning(f"**Severe DKA / Escalation Criteria Met:** {', '.join(severe_criteria)}. Call Critical Care.")

# --- SECTION 2: POTASSIUM (K+) REPLACEMENT ---
st.header("2. Potassium (K+) Replacement")
if k_plus > 5.5:
    st.success(f"K+ is {k_plus}: **NIL replacement.**")
elif 3.5 <= k_plus <= 5.5:
    st.warning(f"K+ is {k_plus}: **Add 40 mmol/L KCl to IV fluid.**")
else:
    st.error(f"🚨 CRITICAL K+ ({k_plus}): **SENIOR REVIEW REQUIRED.** Additional potassium needed.")

st.info("**Safety:** Aim for K+ 4.0-5.0. No K+ in 1st bag (unless K+ < 3.5). Max 20mmol/hr peripherally.")

# --- SECTION 3: INFUSION MANAGEMENT ---
st.header("3. Infusion Management")
col_f1, col_f2 = st.columns(2)

with col_f1:
    st.subheader("IV Fluid & Glucose")
    if gluc < 14.0:
        st.error("⚠️ GLUCOSE < 14: **ADD 10% GLUCOSE at 120mL/hr.** Continue 0.9% NaCl for volume.")
    else:
        st.info("GLUCOSE ≥ 14: Standard 0.9% NaCl regime (1hr, 2hr, 2hr, 4hr).")

with col_f2:
    st.subheader("Insulin")
    st.metric("Fixed Rate Insulin (0.1 u/kg/hr)", f"{weight * 0.1:.1f} units/hr")
    st.write("✅ **Continue usual long-acting (basal) insulin.**")

# --- SECTION 4: HOURLY METABOLIC TARGETS ---
st.header("4. Review Metabolic Targets (Hourly)")
col_t1, col_t2, col_t3 = st.columns(3)

with col_t1:
    pk = st.number_input("Previous Ketones", min_value=0.0)
    if pk > 0:
        k_diff = pk - ket
        if k_diff < 0.5: st.error(f"FAIL: Need 0.5 mmol/L drop (Current: {k_diff:.1f})")
        else: st.success("Ketone Target Met")

with col_t2:
    pg = st.number_input("Previous Glucose", min_value=0.0)
    if pg > 0:
        g_diff = pg - gluc
        if g_diff < 3.0: st.error(f"FAIL: Need 3.0 mmol/L drop (Current: {g_diff:.1f})")
        else: st.success("Glucose Target Met")

with col_t3:
    pb = st.number_input("Previous Bicarb", min_value=0.0)
    if pb > 0:
        b_diff = v_bic - pb
        if b_diff < 3.0: st.error(f"FAIL: Need 3.0 mmol/L rise (Current: {b_diff:.1f})")
        else: st.success("Bicarb Target Met")

# --- SECTION 5: RESOLUTION ---
st.divider()
if ket < 0.3 and v_bic > 18.0 and v_ph > 7.3:
    st.balloons()
    st.success("✅ **DKA RESOLVED**: Ketones < 0.3, Bicarb > 18, pH > 7.3.")
else:
    st.warning("DKA ongoing. Reassess clinical and metabolic parameters hourly.")
