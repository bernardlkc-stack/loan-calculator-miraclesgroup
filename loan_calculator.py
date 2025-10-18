import streamlit as st
import math
from babel.numbers import format_decimal

# ---------------------------
# CONFIGURATION
# ---------------------------
st.set_page_config(
    page_title="Resale Private Property Loan Calculator | MiraclesGroup",
    layout="centered"
)

st.title("🏠 Resale Private Property Loan Calculator (Singapore)")
st.caption("Built by MiraclesGroup | Powered by Streamlit")
st.divider()

# ---------------------------
# HELPERS
# ---------------------------
def format_number(num):
    """Format integer with commas."""
    try:
        return format_decimal(num, locale='en_SG')
    except:
        return f"{num:,.0f}"

def int_input(label, default="", step=1, min_val=0, max_val=None, key=None, help=None, placeholder=None):
    """Integer input box with auto-comma formatting and placeholder text."""
    raw_str = st.text_input(label, value=default, key=key, help=help, placeholder=placeholder)
    clean = raw_str.replace(",", "").strip()
    if clean == "":
        clean = "0"
    try:
        value = int(float(clean))
    except ValueError:
        value = 0
    value = max(min_val, value)
    if max_val is not None:
        value = min(max_val, value)
    return value

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
        age = int_input(f"Age of Buyer {i+1}", default="40", key=f"age_{i}")
    with c2:
        income = int_input(
            f"Monthly Income (SGD)",
            default="",
            key=f"inc_{i}",
            placeholder="Enter monthly income per buyer"
        )
    ages.append(age)
    incomes.append(income)

total_income = sum(incomes)

# Compute IWAA (Income Weighted Average Age)
if total_income > 0:
    iw_age = sum(a * i for a, i in zip(ages, incomes)) / total_income
else:
    iw_age = min(ages)

# ---------------------------
# MAS MAX TENURE (65 - IWAA)
# ---------------------------
mas_max_tenure = min(30.0, 65.0 - float(iw_age))
mas_max_tenure = round(max(5.0, mas_max_tenure), 1)

st.info(
    f"💡 **Income-Weighted Average Age (IWAA):** {iw_age:.1f} years\n"
    f"🏦 **Maximum Loan Tenure allowed by MAS:** {mas_max_tenure:.0f} years "
    f"(Rule: min(30, 65 − IWAA))"
)

st.divider()

# ---------------------------
# EXISTING LOANS
# ---------------------------
existing_loans = int_input("Other Monthly Loan Commitments (SGD)", default="0")
num_outstanding = st.selectbox("Outstanding Housing Loans (for LTV limit)", [0, 1, 2], index=0)

# ---------------------------
# PROPERTY & LOAN DETAILS
# ---------------------------
st.subheader("🏡 Property & Loan Details")

ltv_ratio = {0: 0.75, 1: 0.45, 2: 0.35}[num_outstanding]

# Added placeholder text below 👇
price = int_input(
    "Property Purchase Price (SGD)",
    default="",
    placeholder="Enter Property Purchase Price"
)
downpayment = st.slider("Downpayment (%)", 5, 75, 25)

loan_amount = price * (1 - downpayment / 100.0)
ltv_max = price * ltv_ratio
if loan_amount > ltv_max:
    loan_amount = ltv_max
    st.warning(f"LTV capped at {int(ltv_ratio*100)}% ⇒ maximum loan ${format_number(ltv_max)}")

interest = st.number_input(
    "Loan Interest Rate (per annum %)",
    min_value=0.1, value=3.5, step=0.1, format="%.2f"
)

# ---------------------------
# TENURE SLIDER (IWAA RULE)
# ---------------------------
chosen_tenure = st.slider(
    "Select Loan Tenure (Years)",
    min_value=5.0,
    max_value=float(mas_max_tenure),
    value=float(mas_max_tenure),
    step=0.5,
    help="Maximum tenure is capped by the IWAA rule. You may choose a shorter tenure."
)

st.success(
    f"🕒 Tenure selected for calculation: **{chosen_tenure:.0f} years** "
    f"(MAS max from IWAA {iw_age:.1f} → {mas_max_tenure:.0f} years)"
)

st.divider()

# ---------------------------
# REPAYMENT CALCULATIONS
# ---------------------------
r = interest / 100.0 / 12.0
n = int(chosen_tenure * 12)
monthly = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1) if r > 0 else loan_amount / n
total_interest = monthly * n - loan_amount
total_payment = loan_amount + total_interest

# ---------------------------
# TDSR
# ---------------------------
tdsr_cap = 0.55 * total_income
total_commitment = monthly + existing_loans
tdsr_ok = total_commitment <= tdsr_cap
tdsr_status = "✅ Within TDSR" if tdsr_ok else "❌ Exceeds TDSR"
tdsr_color = "green" if tdsr_ok else "red"

# ---------------------------
# RESULTS
# ---------------------------
st.header("💡 Loan Summary")

c1, c2 = st.columns(2)
with c1:
    st.metric("Loan Amount", f"${format_number(loan_amount)}")
    st.metric("Monthly Instalment", f"${format_number(round(monthly))}")
with c2:
    st.metric("Total Interest Payable", f"${format_number(round(total_interest))}")
    st.metric("Total Payment", f"${format_number(round(total_payment))}")

st.markdown(
    f"**TDSR Status:** <span style='color:{tdsr_color}'>{tdsr_status}</span>",
    unsafe_allow_html=True
)
st.caption(f"Tenure used: **{chosen_tenure:.0f} years** (MAS max via IWAA = {iw_age:.1f})")

st.divider()

# ---------------------------
# BUYER SUMMARY
# ---------------------------
st.subheader("👨‍👩‍👧‍👦 Buyer Summary")
for i in range(num_buyers):
    st.markdown(f"- Buyer {i+1}: Age {ages[i]}, Income ${format_number(incomes[i])}")
st.markdown(f"**Total Household Income:** ${format_number(total_income)}")

st.divider()

# ---------------------------
# NOTES
# ---------------------------
st.header("📊 Notes")
st.markdown("""
- **IWAA (Income-Weighted Average Age):** (Σ Age×Income / Σ Income)  
- **MAS Tenure Cap:** **min(30 years, 65 − IWAA)**  
- **LTV limits:** 75%, 45%, 35% depending on number of outstanding home loans  
- **TDSR cap:** monthly debt ≤ 55% of gross income  
- Buyers can always choose a shorter tenure for faster repayment  
- Figures are illustrative — confirm with your banker
""")
