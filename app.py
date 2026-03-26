import streamlit as st

# 1. Page Config
st.set_page_config(
    page_title="Somerset NHS DKA Tool", 
    layout="wide"
)

# 2. Ultra-Safe CSS
# Hides only the tiny icons at the very top right. 
# No impact on the rest of the page layout.
hide_st_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            [data-testid="stDecoration"] {display:none !important;}
            .stAppDeployButton {display:none !important;}
            [data-testid="stHeader"] {height: 0rem;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- APP HEADER ---
st.title("Adult DKA Clinical Decision Support")
st.caption("Standardized Management based on NHS Somerset Foundation Trust Guidelines")

# --- SECTION 1: CURRENT PATIENT DATA ENTRY ---
# Moved from sidebar to main body for 100% visibility guarantee
st.header("📍 1. Current Patient Data")
with st.container(border=True):
    col_in1, col_in2, col_in3 = st.columns(3)
    
    with col_in1:
        st.subheader("Vitals & Weight")
        weight = st.number_input("Weight (kg)", min_value=10.0, max_value=250.0, value=70.0)
        sbp = st.number_input("Systolic BP (mmHg)", min_value=40, max_value=250, value=120)
        gcs = st.number_input("GCS Score", min_value=3, max_value=15, value=15)
        
    with col_in2:
        st.subheader("Laboratory")
        gluc = st.number_input("Glucose (mmol/L)", min_value=0.0, step=0.1)
        ket = st.number_input("Ketones (mmol/L)", min_value=0.0, step=0.1)
        k_plus = st.number_input("Potassium (mmol/L)", min_value=0.0, max_value=10.0, step=0.1, value=4.0)

    with col_in3:
        st.subheader("Acid-Base")
        v_ph = st.number_input("Venous pH", min_value=6.8, max_value=7.6, step=0.01, value=7.35)
        v_bic = st.number_input("Bicarbonate (mmol/L)", min_value=0.0, step=0.1)
        spo2 = st.slider("SpO2 on Air (%)", 70, 100, 98)

st.divider()

# --- SECTION 2: EMERGENCY TRIGGERS ---
st.header("2. Emergency Assessment")
col_em1, col_em2 = st.columns(2)

with col_em1:
    # Shock Logic (SBP < 90)
    if sbp < 90:
        st.error("🚨 **PATIENT SHOCKED (SBP < 90mmHg)**")
        st.markdown("**Action:** Give 500mL 0.9% NaCl over 10-15 mins. Repeat until BP > 90. Call Critical Care if > 2L required.")
    else:
        st.success("SBP ≥ 90mmHg: Follow standard fluid resuscitation.")

with col_em2:
    # Severe DKA Criteria
    severe_criteria = []
    if v_bic < 5.0 or v_ph < 7.1: severe_criteria.append("Bicarb < 5 or pH < 7.1")
    if gcs < 12: severe_criteria.append("GCS < 12")
    if k_plus < 3.5: severe_criteria.append("K+ < 3.5 mmol/L")

    if severe_criteria:
        st.warning(f"**Escalation Criteria Met:** {', '.join(severe_criteria)}. Call Critical Care.")
    else:
        st.info("No immediate escalation criteria met.")

# --- SECTION 3: POTASSIUM & INSULIN ---
st.header("3. Management & Prescribing")
col_med1, col_med2 = st.columns(2)

with col_med1:
    st.subheader("Potassium (K+) Replacement")
    if k_plus > 5.5:
        st.success(f"K+ {k_plus}: **NIL replacement.**")
    elif 3.5 <= k_plus <= 5.5:
        st.warning(f"K+ {k_plus}: **Add 40 mmol/L KCl to IV fluid.**")
    else:
        st.error(f"🚨 CRITICAL K+ ({k_plus}): **SENIOR REVIEW.** Additional K+ needed.")
    st.caption("Max 20mmol/hr peripherally. No K+ in 1st bag unless K+ < 3.5.")

with col_med2:
    st.subheader("Insulin")
    st.metric("Fixed Rate IV Insulin (0.1 u/kg/hr)", f"{weight * 0.1:.1f} units/hr")
    st.write("✅ **Continue usual long-acting (basal) insulin.**")

# --- SECTION 4: FLUID REGIME & GLUCOSE ---
st.header("4. IV Fluid & Glucose Warning")
if gluc < 14.0:
    st.error("⚠️ **GLUCOSE < 14: ADD 10% GLUCOSE at 120mL/hr.**")
    st.markdown("Continue 0.9% Sodium Chloride separately for volume/boluses. **Do NOT stop insulin.**")
else:
    st.info("GLUCOSE ≥ 14: Standard 0.9% NaCl regime (1L over 1hr, then 2hr, 2hr, 4hr).")

# --- SECTION 5: HOURLY TARGETS ---
st.header("5. Review Metabolic Targets (Hourly)")
st.write("Compare current data against results from **1 hour ago**:")
col_t1, col_t2, col_t3 = st.columns(3)

with col_t1:
    pk = st.number_input("Previous Ketones", min_value=0.0, key="pk_main")
    if pk > 0:
        k_diff = pk - ket
        if k_diff < 0.5: st.error(f"FAIL: Need 0.5 drop (Current: {k_diff:.1f})")
        else: st.success(f"Target Met (Drop: {k_diff:.1f})")

with col_t2:
    pg = st.number_input("Previous Glucose", min_value=0.0, key="pg_main")
    if pg > 0:
        g_diff = pg - gluc
        if g_diff < 3.0: st.error(f"FAIL: Need 3.0 drop (Current: {g_diff:.1f})")
        else: st.success(f"Target Met (Drop: {g_diff:.1f})")

with col_t3:
    pb = st.number_input("Previous Bicarb", min_value=0.0, key="pb_main")
    if pb > 0:
        b_diff = v_bic - pb
        if b_diff < 3.0: st.error(f"FAIL: Need 3.0 rise (Current: {b_diff:.1f})")
        else: st.success(f"Target Met (Rise: {b_diff:.1f})")

# --- SECTION 6: RESOLUTION ---
st.divider()
if ket < 0.3 and v_bic > 18.0 and v_ph > 7.3:
    st.balloons()
    st.success("✅ **DKA RESOLVED**: Ketones < 0.3, Bicarb > 18, pH > 7.3.")
else:
    st.warning("DKA ongoing. Reassess clinical and metabolic parameters hourly.")
