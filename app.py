import streamlit as st

st.set_page_config(page_title="Somerset NHS DKA Tool", layout="wide")

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
    st.subheader("Lab Results")
    gluc = st.number_input("Glucose (mmol/L)", min_value=0.0, step=0.1)
    ket = st.number_input("Ketones (mmol/L)", min_value=0.0, step=0.1)
    v_ph = st.number_input("Venous pH", min_value=6.8, max_value=7.6, step=0.01, value=7.35)
    v_bic = st.number_input("Bicarbonate (mmol/L)", min_value=0.0, step=0.1)
    k_plus = st.number_input("Potassium (mmol/L)", min_value=0.0, max_value=10.0, step=0.1, value=4.0)

# --- CRITICAL CARE CHECK (Page 1: Severe DKA) ---
st.header("1. Severity & Escalation")
severe_criteria = []
if v_bic < 5.0 or v_ph < 7.1: severe_criteria.append("Bicarb < 5 or pH < 7.1")
if gcs < 12: severe_criteria.append("GCS < 12")
if spo2 < 92: severe_criteria.append("Saturations < 92% on air")
if k_plus < 3.5: severe_criteria.append("Hypokalaemia (< 3.5 mmol/L) on admission")
if sbp < 90: severe_criteria.append("Persistent hypotension despite 2L fluid")

if severe_criteria:
    st.error(f"🚨 **SEVERE DKA - CALL CRITICAL CARE:** {', '.join(severe_criteria)}")
else:
    st.success("Patient does not currently meet Critical Care referral criteria based on provided vitals.")

# --- ACTION 1: REASSESS (Page 5) ---
with st.expander("Action 1: Immediate Clinical Red Flags"):
    cols = st.columns(3)
    with cols[0]:
        st.warning("**Poor Urine Output**")
        st.write("If < 0.5ml/kg/hour: **Catheterise**")
    with cols[1]:
        st.warning("**Vomiting/Reduced GCS**")
        st.write("Consider **NG Tube**")
    with cols[2]:
        st.warning("**Persistent Acidosis**")
        st.write("Consider other causes or CT Head (if GCS < 13)")

# --- ACTION 2: FLUID REGIME (Page 5) ---
st.header("2. Fluid & Insulin Management")
tab1, tab2, tab3 = st.tabs(["0-6 Hours", "6-12 Hours", "Beyond 12 Hours"])

with tab1:
    st.subheader("Suggested IV Fluid Regime")
    if sbp < 90:
        st.error("SHOCK: 500mL 0.9% NaCl over 10-15 mins. Repeat until SBP > 90.")
    else:
        st.info("1. 1L 0.9% NaCl over 1 hour\n2. 1L 0.9% NaCl + KCl over 2 hours\n3. 1L 0.9% NaCl + KCl over 2 hours\n4. 1L 0.9% NaCl + KCl over 4 hours")
    
    st.metric("Fixed Rate Insulin (0.1 unit/kg/hr)", f"{weight * 0.1:.1f} units/hr")
    
    if gluc < 14.0:
        st.warning("⚠️ **Glucose < 14 mmol/L:** ADD 10% Glucose at 120 mL/hr. Continue 0.9% NaCl to restore volume.")

with tab2:
    st.subheader("Management 6-12 Hours")
    st.write("* 1L 0.9% NaCl +/- Potassium over 4 hours (250ml/hr)")
    st.write("* 1L 0.9% NaCl +/- Potassium over 6 hours (125ml/hr)")
    if k_plus < 3.5 or k_plus > 5.5:
        st.error("Monitor K+ 2 hourly (level is outside 3.5-5.5 range)")

with tab3:
    st.subheader("Resolution & Transition")
    resolved = ket < 0.3 and v_bic > 18.0 and v_ph > 7.3
    if resolved:
        st.balloons()
        st.success("DKA RESOLVED: Convert to subcutaneous insulin if eating/drinking.")
        st.info("If unable to eat/drink (sepsis/MI), switch to **Variable Rate Insulin Infusion (VRII)**.")
    else:
        st.warning("DKA NOT RESOLVED: Continue FRII and check for precipitating factors.")

# --- CAUTION GROUPS (Page 5) ---
st.divider()
st.subheader("⚠️ Caution: High Risk Groups")
st.markdown("- Adolescents / Elderly\n- Renal or Cardiac comorbidities\n- **Pregnancy**: See specific DKA policy on Intranet")
