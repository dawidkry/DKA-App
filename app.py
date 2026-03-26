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
    st.subheader("Current Lab Results")
    gluc = st.number_input("Glucose (mmol/L)", min_value=0.0, step=0.1)
    ket = st.number_input("Ketones (mmol/L)", min_value=0.0, step=0.1)
    v_ph = st.number_input("Venous pH", min_value=6.8, max_value=7.6, step=0.01, value=7.35)
    v_bic = st.number_input("Bicarbonate (mmol/L)", min_value=0.0, step=0.1)
    k_plus = st.number_input("Potassium (mmol/L)", min_value=0.0, max_value=10.0, step=0.1, value=4.0)

# --- SECTION 1: EMERGENCY TRIGGERS (SBP < 90 & SEVERE DKA) ---
st.header("1. Emergency Assessment")

# Shock Logic (Page 1: Action 2)
if sbp < 90:
    st.error("🚨 **PATIENT SHOCKED (SBP < 90mmHg)**")
    st.markdown("""
    **Immediate Action:**
    * Give **500 mL Sodium Chloride 0.9%** infusion over 10-15 minutes.
    * Repeat until SBP > 90 mmHg.
    * Seek **Critical Care Review** if BP remains low after 2L of fluid.
    """)
else:
    st.success("SBP ≥ 90mmHg: Follow standard fluid resuscitation (1L over 1hr).")

# Critical Care Triggers (Page 1)
severe_criteria = []
if v_bic < 5.0 or v_ph < 7.1: severe_criteria.append("Bicarb < 5 or pH < 7.1")
if gcs < 12: severe_criteria.append("GCS < 12")
if k_plus < 3.5: severe_criteria.append("K+ < 3.5 mmol/L on admission")

if severe_criteria:
    st.warning(f"**Severe DKA Criteria Met:** {', '.join(severe_criteria)}. Call Critical Care.")

# --- SECTION 2: INSULIN & BASAL COVER ---
st.header("2. Insulin Management")
col_ins1, col_ins2 = st.columns(2)

with col_ins1:
    st.metric("Fixed Rate IV Insulin (0.1 unit/kg/hr)", f"{weight * 0.1:.1f} units/hr")
    st.caption("Prescribe 50 units Actrapid in 49.5ml 0.9% NaCl")

with col_ins2:
    st.info("**Continue Basal Insulin:**")
    st.write("Continue Lantus, Levemir, Tresiba, etc., at usual dose/time.")

# --- SECTION 3: FLUIDS & GLUCOSE SWITCH (Page 5) ---
st.header("3. IV Fluid Regime & Glucose Warning")

# Glucose < 14 Warning (Page 5: Action 2)
if gluc < 14.0:
    st.error("⚠️ **GLUCOSE < 14 mmol/L: HYPOGLYCAEMIA PREVENTION**")
    st.markdown("""
    * **ADD 10% Glucose (Dextrose) at 120 mL/hr.**
    * **CONTINUE 0.9% Sodium Chloride** as needed to restore circulating volume.
    * Do **NOT** stop the Fixed Rate Insulin infusion.
    """)
else:
    st.info("Glucose ≥ 14: Continue 0.9% Sodium Chloride regime (1L over 1hr, then 2hrs, etc.)")

# --- SECTION 4: TREATMENT TARGETS (Page 5) ---
st.header("4. Review Metabolic Targets")
st.write("Hourly monitoring required. Compare current results to 1 hour ago:")

col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    pk = st.number_input("Previous Ketones", min_value=0.0)
    k_diff = pk - ket
    if pk > 0:
        if k_diff >= 0.5: st.success(f"Target Met: Drop {k_diff:.1f}")
        else: st.error(f"FAIL: Need 0.5 mmol/L/hr drop (Current: {k_diff:.1f})")

with col_t2:
    pg = st.number_input("Previous Glucose", min_value=0.0)
    g_diff = pg - gluc
    if pg > 0:
        if g_diff >= 3.0: st.success(f"Target Met: Drop {g_diff:.1f}")
        else: st.error(f"FAIL: Need 3.0 mmol/L/hr drop (Current: {g_diff:.1f})")

with col_t3:
    pb = st.number_input("Previous Bicarb", min_value=0.0)
    b_diff = v_bic - pb
    if pb > 0:
        if b_diff >= 3.0: st.success(f"Target Met: Rise {b_diff:.1f}")
        else: st.error(f"FAIL: Need 3.0 mmol/L/hr rise (Current: {b_diff:.1f})")

# --- SECTION 5: RESOLUTION ---
st.divider()
is_resolved = ket < 0.3 and v_bic > 18.0 and v_ph > 7.3
if is_resolved:
    st.balloons()
    st.success("✅ **DKA RESOLVED** (Ketones < 0.3, Bicarb > 18, pH > 7.3)")
else:
    st.warning("DKA ongoing. Reassess hourly.")
