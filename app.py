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

# --- ACTION 1: SEVERITY & ESCALATION (Page 1 & 5) ---
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
    st.success("Patient does not currently meet Critical Care referral criteria.")

with st.expander("View Specialist Contact Details (Page 5)"):
    st.markdown("""
    * **Diabetes Specialist Nurses (DSN):** Office 2791, 3670 | Bleep 2392
    * **Registrars:** Bleeps 2050 & 2051
    * **Consultants:** via Switchboard
    * *Refer to Specialist Team within 24 hours.*
    """)

# --- ACTION 2: FLUID & POTASSIUM (Page 1 & 3) ---
st.header("2. Fluid & Potassium Management")

# Potassium Logic from Action 3, Page 1
st.subheader("Potassium Replacement (Action 3)")
if k_plus > 5.5:
    st.success("Potassium > 5.5 mmol/L: **Nil replacement.**")
elif 3.5 <= k_plus <= 5.5:
    st.warning("Potassium 3.5 - 5.5 mmol/L: **Add 40 mmol/L KCl to IV fluid.**")
else:
    st.error("Potassium < 3.5 mmol/L: **Senior review required.** Additional potassium needed.")

st.info("**Safety Note:** Do not infuse KCl at a rate > 20mmol/hour peripherally.")

tab1, tab2, tab3 = st.tabs(["0-6 Hours", "6-12 Hours", "Beyond 12 Hours"])

with tab1:
    st.subheader("Suggested IV Fluid Regime (0.9% NaCl)")
    if sbp < 90:
        st.error("SHOCK: 500mL over 10-15 mins. Repeat until BP > 90. Critical care review if still low after 2L.")
    else:
        st.write("1. 1L over 1 hour")
        st.write("2. 1L over 2 hours (with KCl)")
        st.write("3. 1L over 2 hours (with KCl)")
        st.write("4. 1L over 4 hours (with KCl)")
    
    st.metric("Fixed Rate Insulin (0.1 unit/kg/hr)", f"{weight * 0.1:.1f} units/hr")
    
    if gluc < 14.0:
        st.warning("⚠️ **Glucose < 14 mmol/L:** ADD 10% Glucose at 120 mL/hr AND continue 0.9% NaCl for volume.")

with tab2:
    st.subheader("Management 6-12 Hours")
    st.write("* 1L 0.9% NaCl +/- KCl over 4 hours (250ml/hr)")
    st.write("* 1L 0.9% NaCl +/- KCl over 6 hours (125ml/hr)")

with tab3:
    st.subheader("Management Beyond 12 Hours")
    st.write("DKA should resolve by 24 hours. Convert to subcutaneous insulin if eating/drinking.")

# --- ACTION 3: METABOLIC TARGETS (Page 5) ---
st.header("3. Review Metabolic Parameters")
with st.expander("Check Hourly Treatment Targets"):
    st.write("If targets are NOT met: Check patency of lines and infusion pumps **BEFORE** increasing insulin by 1 unit/hour.")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        prev_k = st.number_input("Previous Ketones", min_value=0.0)
        curr_k = st.number_input("Current Ketones", min_value=0.0)
    with col_t2:
        prev_g = st.number_input("Previous Glucose", min_value=0.0)
        curr_g = st.number_input("Current Glucose", min_value=0.0)
    
    if prev_k > 0:
        k_drop = prev_k - curr_k
        g_drop = prev_g - curr_g
        if k_drop >= 0.5: st.success(f"Ketone Target Met (Drop: {k_drop:.1f})")
        else: st.error(f"Ketone Target FAILED (Drop: {k_drop:.1f}. Required: 0.5)")
        
        if g_drop >= 3.0: st.success(f"Glucose Target Met (Drop: {g_drop:.1f})")
        else: st.error(f"Glucose Target FAILED (Drop: {g_drop:.1f}. Required: 3.0)")

# --- RESOLUTION CRITERIA (Page 5) ---
st.header("4. Resolution Status")
# Combined Page 5 definition
is_resolved = ket < 0.3 and v_bic > 18.0 and v_ph > 7.3

if is_resolved:
    st.balloons()
    st.success("✅ **DKA RESOLVED** (Ketones < 0.3, Bicarb > 18, pH > 7.3)")
    st.info("Switch to **Subcutaneous Insulin** (if eating/drinking) or **VRII** (if NBM/Sepsis/MI).")
else:
    st.warning("❌ **DKA NOT RESOLVED**")

# --- CAUTION GROUPS (Page 5) ---
st.divider()
st.subheader("⚠️ High Risk Groups & Red Flags")
c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    **Cautions:**
    - Adolescents / Elderly
    - Renal/Cardiac comorbidities
    - **Pregnancy** (Check Intranet Policy)
    """)
with c2:
    st.markdown("""
    **Red Flags (Action 1):**
    - SpO2 < 94%: ABG/CXR
    - GCS < 13: Consider CT Head
    - Urine < 0.5ml/kg/hr: Catheterise
    """)
