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
# EXISTING LOANS & CPF OPTION
# ---------------------------
st.subheader("💰 Existing Loans & CPF Option")
existing_loans = int_input(
    "Other Monthly Loan Commitments (SGD)",
    default="0",
    placeholder="Enter total monthly loan obligations"
)
num_outstanding = st.selectbox("Outstanding Housing Loans (for LTV limit)", [0, 1, 2], index=0)

pledge_option = st.selectbox(
    "CPF Retirement Account Option",
    ["Unpledge (Standard 55%)", "Pledge (Up to 60%)"],
    index=0,
    help="Pledging CPF can improve your LTV slightly depending on bank assessment."
)

# Adjust LTV based on pledge/unpledge
ltv_ratio = {0: 0.75, 1: 0.45, 2: 0.35}[num_outstanding]
if pledge_option == "Pledge (Up to 60%)":
    ltv_ratio = min(ltv_ratio + 0.05, 0.80)

# ---------------------------
# PROPERTY & LOAN DETAILS
# ---------------------------
st.subheader("🏡 Property & Loan Details")

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

# Loan interest rate input
interest_str = st.text_input(
    "Loan Interest Rate (per annum %)",
    value="",
    placeholder="Enter loan interest rate (e.g. 3.5)"
)
try:
    interest = float(interest_str)
except ValueError:
    interest = 0.0

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
r = interest / 100.0 / 12.0 if interest > 0 else 0
n = int(chosen_tenure * 12)
if r > 0:
    monthly = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
else:
    monthly = loan_amount / n if n > 0 else 0
total_interest = monthly * n - loan_amount
total_payment = loan_amount + total_interest

# ---------------------------
# TDSR + MAX LOAN LOGIC
# ---------------------------
tdsr_cap = 0.55 * total_income
total_commitment = monthly + existing_loans
tdsr_ok = total_commitment <= tdsr_cap
tdsr_status = "✅ Within TDSR" if tdsr_ok else "❌ Exceeds TDSR"
tdsr_color = "green" if tdsr_ok else "red"

# Compute max loan based on TDSR limit
if r > 0:
    max_loan_tdsr = (tdsr_cap - existing_loans) * ((1 + r) ** n - 1) / (r * (1 + r) ** n)
else:
    max_loan_tdsr = (tdsr_cap - existing_loans) * n

# Shortfall (if any)
shortfall = loan_amount - max_loan_tdsr if loan_amount > max_loan_tdsr else 0

# ---------------------------
# RESULTS
# ---------------------------
st.header("💡 Loan Summary")

c1, c2 = st.columns(2)
with c1:
    st.metric("Loan Amount", f"${format_number(loan_amount)}")
    st.metric("Monthly Instalment", f"${format_number(round(monthly))}")
    st.metric("TDSR Limit (55%)", f"${format_number(round(tdsr_cap))}")
with c2:
    st.metric("Max Loan (Based on TDSR)", f"${format_number(round(max_loan_tdsr))}")
    st.metric("Total Interest Payable", f"${format_number(round(total_interest))}")
    st.metric("Total Payment", f"${format_number(round(total_payment))}")

if shortfall > 0:
    st.error(
        f"⚠️ Loan exceeds TDSR limit.\n\n"
        f"💸 Shortfall: **${format_number(round(shortfall))}** "
        f"(to be paid by cash/CPF)."
    )
else:
    st.success("✅ Loan amount is within TDSR and LTV limits.")

st.markdown(
    f"**TDSR Status:** <span style='color:{tdsr_color}'>{tdsr_status}</span>",
    unsafe_allow_html=True
)
st.caption(f"Tenure used: **{chosen_tenure:.0f} years** (MAS max via IWAA = {iw_age:.1f})")

# ---------------------------
# ASSET SIMULATION
# ---------------------------
if shortfall > 0:
    st.divider()
    st.subheader("💎 Asset Simulation — How Much You’d Need")

    asset_needed_pledge = shortfall * 48
    asset_needed_unpledge = shortfall * 48 / 0.3

    st.info(
        f"To cover your shortfall of ${format_number(round(shortfall))} via assets:\n\n"
        f"🔹 **If Pledged:** You’ll need approximately **${format_number(round(asset_needed_pledge))}** in fixed deposit locked for 48 months.\n"
        f"🔸 **If Unpledged:** You’ll need approximately **${format_number(round(asset_needed_unpledge))}** in liquid assets (30% recognition)."
    )

st.divider()

# ---------------------------
# NOTES
# ---------------------------
st.header("📊 Notes")
st.markdown("""
- **Pledging:** Monthly income contribution = Asset Value ÷ 48  
- **Unpledging:** Monthly income contribution = (Asset Value × 0.3) ÷ 48  
- **MAS Tenure Cap:** min(30 years, 65 − IWAA)  
- **TDSR limit:** 55% of gross monthly income  
- **LTV limits:** depend on outstanding loans (75%, 45%, 35%)  
- **CPF Pledge Option:** may raise LTV up to 80% depending on bank policy  
- **Shortfall:** amount exceeding TDSR-based maximum must be covered by cash/CPF or additional recognized assets  
- Figures are estimates — confirm with your banker for exact eligibility
""")
