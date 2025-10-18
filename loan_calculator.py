import streamlit as st
import math

# ---------------------------
# APP CONFIGURATION
# ---------------------------
st.set_page_config(
    page_title="Resale Private Property Loan Calculator | MiraclesGroup",
    layout="centered"
)

st.title("🏠 Resale Private Property Loan Calculator (Singapore)")
st.caption("Built by MiraclesGroup | Powered by Streamlit")
st.divider()

# ---------------------------
# BUYER DETAILS
# ---------------------------
st.subheader("👥 Buyer Details")

num_buyers = st.selectbox("Number of Buyers", [1, 2, 3, 4], index=0)

ages, incomes = [], []

for i in range(num_buyers):
    st.markdown(f"**Buyer {i+1}**")
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input(f"Age of Buyer {i+1}", min_value=21, max_value=75, value=40, key=f"age_{i}")
    with c2:
        income = st.number_input(f"Monthly Income (SGD)", min_value=0.0, value=8000.0, step=500.0, key=f"inc_{i}")
    ages.append(age)
    incomes.append(income)

total_income = sum(incomes)
iw_age = sum(a * i for a, i in zip(ages, incomes)) / total_income if total_income > 0 else min(ages)
max_tenure = max(5, min(30, 75 - iw_age))

existing_loans = st.number_input("Other Monthly Loan Commitments (SGD, optional)", min_value=0.0, value=0.0, step=100.0)
num_outstanding = st.selectbox("Outstanding Housing Loans (for LTV limit)", [0, 1, 2], index=0)

st.divider()

# ---------------------------
# PROPERTY & LOAN DETAILS
# ---------------------------
st.subheader("🏡 Property & Loan Details")

calc_mode = st.radio("How would you like to calculate?", ["By Property Price", "By Loan Amount (IWAA)"], index=0)

# LTV ratio
ltv_ratio = {0: 0.75, 1: 0.45, 2: 0.35}[num_outstanding]

if calc_mode == "By Property Price":
    price = st.number_input("Property Purchase Price (SGD)", min_value=100000.0, value=1500000.0, step=10000.0)
    downpayment = st.slider("Downpayment (%)", 5, 75, 25)
    loan_amount = price * (1 - downpayment / 100)
    max_loan = price * ltv_ratio
    if loan_amount > max_loan:
        loan_amount = max_loan
        st.warning(f"LTV capped at {int(ltv_ratio*100)}% ⇒ max loan ${max_loan:,.0f}")

else:
    loan_amount = st.number_input("I want to borrow (SGD)", min_value=50000.0, value=1000000.0, step=50000.0)
    price_check = st.number_input("Property Price (optional, for LTV check)", min_value=0.0, value=0.0, step=10000.0)
    if price_check > 0 and loan_amount > price_check * ltv_ratio:
        st.error(f"❗ IWAA ${loan_amount:,.0f} exceeds {int(ltv_ratio*100)}% LTV limit of ${price_check:,.0f} (max ${price_check*ltv_ratio:,.0f}).")

interest = st.number_input("Loan Interest Rate (per annum %)", min_value=0.1, value=3.5, step=0.1)

# Automatic IWAA tenure display
st.info(f"💡 IWAA = **{iw_age:.1f} years**  →  Max tenure = **{max_tenure:.1f} years** (MAS cap: min(30, 75 − IWAA))")

st.divider()

# ---------------------------
# CALCULATE REPAYMENT
# ---------------------------
r = interest / 100 / 12
n = int(max_tenure * 12)
monthly = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1) if r > 0 else loan_amount / n
total_interest = monthly * n - loan_amount
total_payment = loan_amount + total_interest

# TDSR
tdsr_cap = 0.55 * total_income
tdsr_ok = monthly + existing_loans <= tdsr_cap
tdsr_status = "✅ Within TDSR" if tdsr_ok else "❌ Exceeds TDSR"
tdsr_color = "green" if tdsr_ok else "red"

# ---------------------------
# RESULTS
# ---------------------------
st.header("💡 Loan Summary")

c1, c2 = st.columns(2)
with c1:
    st.metric("Loan Amount", f"${loan_amount:,.0f}")
    st.metric("Monthly Instalment", f"${monthly:,.0f}")
with c2:
    st.metric("Total Interest Payable", f"${total_interest:,.0f}")
    st.metric("Total Payment", f"${total_payment:,.0f}")

st.markdown(f"**TDSR Status:** <span style='color:{tdsr_color}'>{tdsr_status}</span>", unsafe_allow_html=True)
st.caption(f"Tenure used: **{max_tenure:.1f} years** (based on IWAA = {iw_age:.1f})")

st.divider()
st.subheader("👨‍👩‍👧‍👦 Buyer Summary")
for i in range(num_buyers):
    st.markdown(f"- Buyer {i+1}: Age {ages[i]}, Income ${incomes[i]:,.0f}")
st.markdown(f"**Total Income:** ${total_income:,.0f}")

st.divider()
st.header("📊 Notes")
st.markdown("""
- **IWAA (Income-Weighted Average Age):** (Σ Age×Income / Σ Income)  
- **Tenure cap:** min(30 years, 75 − IWAA).  
- **LTV limits:** 75%, 45%, 35% (depending on outstanding loans).  
- **TDSR cap:** monthly debt ≤ 55% of gross income.  
- Illustrative purposes only — confirm with banker.
""")
