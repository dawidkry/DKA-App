import streamlit as st

st.set_page_config(page_title="Adult DKA Management Tool", layout="wide")

st.title("Adult Diabetic Ketoacidosis (DKA) Management Tool")
st.caption("Based on NHS Somerset Foundation Trust Guidelines")

# --- SIDEBAR: PATIENT BASICS ---
with st.sidebar:
    st.header("Patient Data")
    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=250.0, value=70.0)
    glucose = st.number_input("Capillary Blood Glucose (mmol/L)", min_value=0.0, step=0.1)
    ketones = st.number_input("Ketonaemia (mmol/L)", min_value=0.0, step=0.1)
    bicarb = st.number_input("Bicarbonate (mmol/L)", min_value=0.0, step=0.1)
    ph = st.number_input("Venous pH", min_value=6.0, max_value=8.0, step=0.01, value=7.3)

# --- STEP 1: DIAGNOSIS ---
st.header("1. Diagnosis Check")
is_dka = (glucose > 11.0 or False) and (ketones >= 3.0) and (bicarb < 15.0 or ph < 7.3)

if is_dka:
    st.success("DIAGNOSIS CONFIRMED: All 3 criteria met.")
else:
    st.warning("DIAGNOSIS NOT MET: Ensure all criteria (Glucose/Known Diabetes, Ketones, and Acidosis) are present.")

# --- STEP 2: IMMEDIATE MANAGEMENT (0-60 MINS) ---
st.header("2. Immediate Management (0-60 Minutes)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Fluid Replacement")
    sbp_low = st.checkbox("Is Patient Shocked? (SBP < 90mmHg)")
    
    if sbp_low:
        st.error("ACTION: Give 500mL Sodium Chloride 0.9% over 10-15 mins. Repeat until BP > 90mmHg.")
    else:
        st.info("ACTION: Give 1L 0.9% Sodium Chloride over 1 hour.")

with col2:
    st.subheader("Fixed Rate Insulin Infusion")
    insulin_rate = weight * 0.1
    st.metric("Insulin Rate", f"{insulin_rate:.1f} units/hr")
    st.write(f"Prescribe 50 units Actrapid in 49.5ml 0.9% NaCl (1 unit/ml).")

# --- STEP 3: POTASSIUM REPLACEMENT ---
st.header("3. Potassium Replacement")
k_level = st.number_input("Current Serum Potassium (mmol/L)", min_value=0.0, max_value=10.0, step=0.1, value=4.0)

if k_level > 5.5:
    st.write("✅ **Potassium Replacement:** Nil")
elif 3.5 <= k_level <= 5.5:
    st.write("⚠️ **Potassium Replacement:** Add 40 mmol/L to IV fluid")
else:
    st.error("🚨 **CRITICAL:** Potassium < 3.5 mmol/L. Senior review required; additional potassium needed.")

# --- STEP 4: MONITORING & TARGETS ---
st.header("4. Treatment Targets & Monitoring")

st.info("""
**Targets for Resolution:**
* Blood Ketones to fall by at least **0.5 mmol/L / hour**
* Blood Glucose to fall by at least **3 mmol/L / hour**
* Venous Bicarbonate to rise by **3 mmol/L / hour**
""")

# Metabolic Reassessment Logic
st.subheader("Metabolic Review (60 mins - 6 hours)")
current_ketones = st.number_input("Current Ketones (after 1hr)", min_value=0.0, step=0.1)
previous_ketones = st.number_input("Previous Ketones", min_value=0.0, step=0.1)

if previous_ketones > 0:
    reduction = previous_ketones - current_ketones
    if reduction < 0.5:
        st.error(f"Target NOT met (Reduction: {reduction:.1f}). Increase insulin rate by 1 unit/hour and check lines.")
    else:
        st.success(f"Target met (Reduction: {reduction:.1f}). Continue current rate.")

# Glucose management
if glucose < 14.0:
    st.warning("Glucose < 14 mmol/L: Start 10% Glucose at 120 mL/hr alongside 0.9% NaCl.")

# --- STEP 5: RESOLUTION ---
st.header("5. DKA Resolution")
res_ketones = st.number_input("Final Ketones", min_value=0.0, step=0.1, key="res_k")
res_bicarb = st.number_input("Final Bicarbonate", min_value=0.0, step=0.1, key="res_bi")
res_ph = st.number_input("Final pH", min_value=6.0, step=0.01, value=7.4, key="res_ph")

if res_ketones < 0.3 and res_bicarb > 18.0 and res_ph > 7.3:
    st.balloons()
    st.success("DKA RESOLVED: Convert to subcutaneous insulin if patient is eating/drinking.")
else:
    st.write("DKA not yet resolved. Continue IV infusion and monitoring.")
