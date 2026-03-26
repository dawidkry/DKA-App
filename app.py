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

# --- ACTION 1: SEVERITY & ESCALATION ---
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

# --- NEW SECTION: LONG-ACTING INSULIN (Page 2) ---
st.header("2. Basal (Long-Acting) Insulin")
st.warning("⚠️ **IMPORTANT:** Regular subcutaneous long-acting insulin MUST be continued at the usual dose and time.")

with st.expander("View Protocol for Basal Insulin"):
    st.write("""
    If the patient normally takes any of the following, do NOT stop them:
    * **Lantus, Abasaglar, Toujeo, Levemir, Tresiba, Humulin I, Insulatard, Insuman Basal, Semglee.**
    * Administer at the usual dose and time even while on Fixed Rate IV Insulin.
    """)
    basal_given = st.checkbox("Confirmed: Long-acting insulin prescribed/administered?")
    if not basal_given:
        st.error("ACTION REQUIRED: Prescribe usual long-acting insulin on the chart.")

# --- ACTION 2: FLUID & POTASSIUM ---
st.header("3. Fluid & Potassium Management")

# Potassium Logic (Page 1)
st.subheader("Potassium Replacement")
if k_plus > 5.5:
    st.success("K+ > 5.5: Nil replacement.")
elif 3.5 <= k_plus <= 5.5:
    st.warning("K+ 3.5-5.5: Add 40 mmol/L KCl to IV fluid.")
else:
    st.error("K+ < 3.5: Senior review required. Higher replacement needed.")

tab1, tab2, tab3 = st.tabs(["0-6 Hours", "6-12 Hours", "Beyond 12 Hours"])

with tab1:
    st.subheader("Fluid Regime (0.9% NaCl)")
    if sbp < 90:
        st.error("SHOCK: 500mL over 10-15 mins. Repeat until BP > 90.")
    else:
        st.write("1. 1L over 1hr | 2. 1L over 2hrs | 3. 1L over 2hrs | 4. 1L over 4hrs")
    
    st.metric("Fixed Rate Insulin (0.1 unit/kg/hr)", f"{weight * 0.1:.1f} units/hr")
    if gluc < 14.0:
        st.warning("⚠️ **Glucose < 14 mmol/L:** ADD 10% Glucose at 120 mL/hr.")

with tab2:
    st.subheader("6-12 Hours")
    st.write("* 1L 0.9% NaCl + KCl over 4 hours (250ml/hr)")
    st.write("* 1L 0.9% NaCl + KCl over 6 hours (125ml/hr)")

with tab3:
    st.subheader("Beyond 12 Hours")
    st.write("Aim for resolution within 24 hours. Convert to SC insulin when eating/drinking.")

# --- ACTION 3: METABOLIC TARGETS (Page 5) ---
st.header("4. Review Metabolic Parameters")
with st.expander("Check Hourly Treatment Targets"):
    col_k1, col_k2 = st.columns(2)
    with col_k1: prev_k = st.number_input("Previous Ketones", min_value=0.0, key="pk")
    with col_k2: curr_k = st.number_input("Current Ketones", min_value=0.0, key="ck")
    
    if prev_k > 0:
        k_drop = prev_k - curr_k
        if k_drop >= 0.5: st.success(f"Target Met (Drop: {k_drop:.1f})")
        else: st.error(f"Target FAILED (Drop: {k_drop:.1f}. Required: 0.5). Check lines/pumps.")

# --- RESOLUTION CRITERIA (Page 5) ---
st.header("5. Resolution Status")
# Strict definition from bottom of Page 5
is_resolved = ket < 0.3 and v_bic > 18.0 and v_ph > 7.3

if is_resolved:
    st.balloons()
    st.success("✅ **DKA RESOLVED** (Ketones < 0.3 for 2 hours, Bicarb > 18, pH > 7.3)")
    st.info("Switch to **Subcutaneous Insulin** (if eating/drinking) or **VRII** (if NBM).")
else:
    st.warning("❌ **DKA NOT RESOLVED**")

# --- FOOTER: CAUTION GROUPS ---
st.divider()
st.subheader("⚠️ Specialist Contacts & Red Flags")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Specialist Teams:**\n- DSN: Bleep 2392\n- Registrars: 2050 / 2051\n- Referral within 24 hours.")
with c2:
    st.markdown("**Red Flags:**\n- Urine < 0.5ml/kg/hr: Catheter\n- GCS < 13: CT Head\n- SpO2 < 94%: ABG/CXR")
