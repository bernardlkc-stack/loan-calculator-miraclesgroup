import streamlit as st
import math

# ---------------------------
# APP CONFIGURATION
# ---------------------------
st.set_page_config(page_title="Resale Private Property Loan Calculator | MiraclesGroup", layout="centered")

st.title("🏠 Resale Private Property Loan Calculator (Singapore)")
st.caption("Built by MiraclesGroup | Powered by Streamlit")

st.divider()

# ---------------------------
# USER INPUTS
# ---------------------------
st.header("Enter Your Property Details")

purchase_price = st.number_input("Property Purchase Price (SGD)", min_value=100000.0, value=1500000.0, step=10000.0)
downpayment_percent = st.slider("Downpayment (%)", min_value=5, max_value=75, value=25)
interest_rate = st.number_input("Loan Interest Rate (per annum %)", min_value=0.1, value=3.5, step=0.1)
loan_tenure = st.slider("Loan Tenure (Years)", min_value=5, max_value=30, value=25)
buyer_age = st.number_input("Buyer’s Age", min_value=21, max_value=75, value=40)
monthly_income = st.number_input("Monthly Income (SGD, optional)", min_value=0.0, value=8000.0, step=500.0)
existing_loans = st.number_input("Monthly Loan Commitments (SGD, optional)", min_value=0.0, value=0.0, step=100.0)
num_existing_properties = st.selectbox("Number of Outstanding Housing Loans", [0, 1, 2], index=0)

st.divider()

# ---------------------------
# LOAN & LTV LOGIC
# ---------------------------
if num_existing_properties == 0:
    ltv_limit = 0.75
elif num_existing_properties == 1:
    ltv_limit = 0.45
else:
    ltv_limit = 0.35

max_loan_allowed = purchase_price * ltv_limit
chosen_loan_amount = purchase_price * (1 - downpayment_percent / 100)

if chosen_loan_amount > max_loan_allowed:
    chosen_loan_amount = max_loan_allowed

max_tenure_allowed = max(75 - buyer_age, 0)
if loan_tenure > max_tenure_allowed:
    st.warning(f"⚠️ Based on your age, the maximum loan tenure allowed is {int(max_tenure_allowed)} years.")
    loan_tenure = max_tenure_allowed

monthly_interest_rate = interest_rate / 100 / 12
months = int(loan_tenure * 12)

if monthly_interest_rate > 0:
    monthly_instalment = chosen_loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** months) / ((1 + monthly_interest_rate) ** months - 1)
else:
    monthly_instalment = chosen_loan_amount / months

total_payment = monthly_instalment * months
total_interest = total_payment - chosen_loan_amount

if monthly_income > 0:
    tdsr_limit = 0.55 * monthly_income
    total_monthly_commitment = monthly_instalment + existing_loans
    if total_monthly_commitment > tdsr_limit:
        tdsr_status = "❌ Exceeds TDSR limit"
        tdsr_color = "red"
    else:
        tdsr_status = "✅ Within TDSR limit"
        tdsr_color = "green"
else:
    tdsr_status = "N/A"
    tdsr_color = "gray"

# ---------------------------
# DISPLAY RESULTS
# ---------------------------
st.header("💡 Loan Summary")

col1, col2 = st.columns(2)
with col1:
    st.metric("Loan Amount (SGD)", f"${chosen_loan_amount:,.0f}")
    st.metric("Monthly Instalment", f"${monthly_instalment:,.0f}")
with col2:
    st.metric("Total Interest Payable", f"${total_interest:,.0f}")
    st.metric("Total Payment", f"${total_payment:,.0f}")

st.markdown(f"**TDSR Status:** <span style='color:{tdsr_color}'>{tdsr_status}</span>", unsafe_allow_html=True)

st.divider()

st.header("📊 Notes & Disclaimers")
st.markdown("""
- **LTV Limits:** 75% (no outstanding loan), 45% (1 loan), 35% (2+ loans).  
- **TDSR Cap:** Total Debt Servicing Ratio capped at 55% of gross monthly income (MAS rule).  
- **Age Limit:** Combined age and loan tenure capped at 75 years.  
- This calculator provides an **illustrative estimate**. Always verify figures with your banker or mortgage advisor.
""")
