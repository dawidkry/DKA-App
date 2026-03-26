import streamlit as st

# 1. Page Config
st.set_page_config(
    page_title="Somerset NHS DKA Tool", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- HEADER ---
st.title("Adult DKA Clinical Decision Support")
st.caption("Standardized Management based on NHS Somerset Foundation Trust Guidelines")

# --- INPUT SECTION (Main Body to ensure visibility) ---
st.header("📍 Step 1: Input Patient Data")
with st.container(border=True):
    col_v1, col_v2, col_v3 = st.columns(3)
    
    with col_v1:
        st.subheader("Basic Info")
        weight = st.number_input("Weight (kg)", min_value=10.0, max_value=250.0, value=70.0)
        sbp = st.number_input("Systolic BP (mmHg)", min_value=40, max_value=250, value=120)
        gcs = st.number_input("GCS Score", min_value=3, max_value=15, value=15)
        
    with col_v2:
        st.subheader("Lab Results")
        gluc = st.number_input("Glucose (mmol/L)", min_value=0.0, step=0.1)
        ket = st.number_input("Ketones (mmol/L)", min_value=0.0, step=0.1)
        k_plus = st.number_input("Potassium (mmol/L)", min_value=0.0, max_value=10.0, step=0.1, value=4.0)

    with col_v3:
        st.subheader("Acid/Base")
        v_ph = st.number_input("Venous pH", min_value=6.8, max_value=7.6, step=0.01, value=7.35)
        v_bic = st.number_input("Bicarbonate (mmol/L)", min_value=0.0, step=0.1)
        spo2 = st.slider("SpO2 on Air (%)", 70, 100, 98)

st.divider()

# --- SECTION 2: EMERGENCY TRIGGERS ---
st.header("2. Emergency Assessment")

# Shock Logic
if sbp < 90:
    st.error("🚨 **PATIENT SHOCKED (SBP < 90mmHg)**: Give 500mL 0.9% NaCl over 10-15 mins. Repeat until BP > 90. Seek senior review.")
else:
    st.success("SBP ≥ 90mmHg: Follow standard fluid resuscitation.")

# Critical Care Triggers
severe_criteria = []
if v_bic < 5.0 or v_ph < 7.1: severe_criteria.append("Bicarb < 5 or pH < 7.1")
if gcs < 12: severe_criteria.append("GCS < 12")
if k_plus < 3.5: severe_criteria.append("K+ < 3.5 mmol/L")

if severe_criteria:
    st.warning(f"**Severe DKA Criteria:** {', '.join(severe_criteria)}. Call Critical Care.")

# --- SECTION 3: POTASSIUM (K+) & INSULIN ---
st.header("3. Electrolyte & Insulin Management")
col_med1, col_med2 = st.columns(2)

with col_med1:
    st.subheader("Potassium (K+)")
    if k_plus > 5.5:
        st.success("K+ > 5.5: **Nil replacement.**")
    elif 3.5 <= k_plus <= 5.5:
        st.warning("K+ 3.5-5.5: **Add 40 mmol/L KCl to IV fluid.**")
    else:
        st.error("🚨 CRITICAL K+: **SENIOR REVIEW REQUIRED.**")
    st.caption("Safety: Max 20mmol/hr peripherally. No K+ in 1st bag unless K+ < 3.5.")

with col_med2:
    st.subheader("Insulin")
    st.metric("Fixed Rate Insulin (0.1 u/kg/hr)", f"{weight * 0.1:.1f} units/hr")
    st.info("**Important:** Continue usual long-acting (basal) insulin.")

# --- SECTION 4: FLUIDS & GLUCOSE ---
st.header("4. IV Fluid Regime")
if gluc < 14.0:
    st.error("⚠️ **GLUCOSE < 14: ADD 10% GLUCOSE at 120mL/hr.**")
    st.write("Continue 0.9% NaCl as needed for volume. Do NOT stop insulin.")
else:
    st.info("GLUCOSE ≥ 14: Continue 0.9% NaCl regime (1L over 1hr, then 2hrs, etc.)")

# --- SECTION 5: HOURLY TARGETS ---
st.header("5. Review Metabolic Targets (Hourly)")
st.write("Input results from 1 hour ago to check progress:")
col_t1, col_t2, col_t3 = st.columns(3)

with col_t1:
    pk = st.number_input("Previous Ketones", min_value=0.0, key="pk")
    if pk > 0 and (pk - ket) < 0.5: st.error(f"FAIL: Need 0.5 drop (Current: {pk-ket:.1f})")
    elif pk > 0: st.success("Target Met")

with col_t2:
    pg = st.number_input("Previous Glucose", min_value=0.0, key="pg")
    if pg > 0 and (pg - gluc) < 3.0: st.error(f"FAIL: Need 3.0 drop (Current: {pg-gluc:.1f})")
    elif pg > 0: st.success("Target Met")

with col_t3:
    pb = st.number_input("Previous Bicarb", min_value=0.0, key="pb")
    if pb > 0 and (v_bic - pb) < 3.0: st.error(f"FAIL: Need 3.0 rise (Current: {v_bic-pb:.1f})")
    elif pb > 0: st.success("Target Met")

# --- SECTION 6: RESOLUTION ---
st.divider()
if ket < 0.3 and v_bic > 18.0 and v_ph > 7.3:
    st.balloons()
    st.success("✅ **DKA RESOLVED**: Ketones < 0.3, Bicarb > 18, pH > 7.3.")
else:
    st.warning("DKA ongoing. Reassess parameters hourly.")
