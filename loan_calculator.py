import streamlit as st
import math
from babel.numbers import format_decimal

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Resale Private Property Loan Calculator | MiraclesGroup",
    layout="centered"
)

# ---------------------------
# STYLE – COMPACT CSS
# ---------------------------
st.markdown("""
<style>
    h1, h2, h3, h4, h5, h6 { margin-bottom: 0.2rem !important; }
    .stMetric { font-size: 0.9rem !important; }
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .stSlider { margin-top: 0.2rem !important; margin-bottom: 0.8rem !important; }
    .stSelectbox, .stTextInput { margin-bottom: 0.5rem !important; }
    .stMarkdown { line-height: 1.3 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🏠 Resale Private Property Loan Calculator")
st.caption("MiraclesGroup | Compact Edition")
st.divider()

# ---------------------------
# HELPERS
# ---------------------------
def format_number(num):
    try:
        return format_decimal(num, locale='en_SG')
    except:
        return f"{num:,.0f}"

def int_input(label, default="", step=1, min_val=0, max_val=None, key=None, placeholder=None):
    raw_str = st.text_input(label, value=default, key=key, placeholder=placeholder)
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

def pmt(rate, nper, pv):
    if nper <= 0: return 0.0
    if rate <= 0: return pv / nper
    return pv * (rate * (1 + rate) ** nper) / ((1 + rate) ** nper - 1)

# ---------------------------
# BUYER DETAILS
# ---------------------------
st.subheader("👥 Buyer Details")

num_buyers = st.selectbox("No. of Buyers", [1, 2, 3, 4], index=0)
ages, incomes = [], []

cols = st.columns(2)
for i in range(num_buyers):
    with cols[i % 2]:
        st.markdown(f"**Buyer {i+1}**")
        age = int_input(f"Age {i+1}", "40", key=f"age_{i}")
        income = int_input("Monthly Income (SGD)", "", key=f"inc_{i}", placeholder="e.g. 6000")
        ages.append(age)
        incomes.append(income)

total_income = sum(incomes)
iw_age = sum(a * i for a, i in zip(ages, incomes)) / total_income if total_income > 0 else min(ages)

mas_max_tenure = min(30.0, 65.0 - float(iw_age))
mas_max_tenure = round(max(5.0, mas_max_tenure), 1)

st.caption(f"💡 IWAA: {iw_age:.1f} yrs | Max Tenure: {mas_max_tenure:.0f} yrs (Rule: min(30, 65 − IWAA))")
st.divider()

# ---------------------------
# EXISTING LOANS (SIDE BY SIDE)
# ---------------------------
st.subheader("💰 Existing Loan Commitments")

col1, col2 = st.columns(2)
with col1:
    existing_loans = int_input(
        "Other Monthly Loans (SGD)",
        "0",
        placeholder="e.g. 1000",
        key="existing_loans"
    )
with col2:
    num_outstanding = st.selectbox(
        "Outstanding Home Loans",
        ["0 - None", "1 - One Property", "2 - Two or More"],
        index=0,
        key="outstanding_loans"
    )

num_outstanding_int = int(num_outstanding[0])  # extract first character as number
ltv_ratio = {0: 0.75, 1: 0.45, 2: 0.35}[num_outstanding_int]

# ---------------------------
# PROPERTY & LOAN DETAILS
# ---------------------------
st.subheader("🏡 Property & Loan Details")

price = int_input("Property Price (SGD)", "", placeholder="Enter purchase price")
downpayment = st.slider("Downpayment (%)", 5, 75, 25)
loan_amount = price * (1 - downpayment / 100)
ltv_max = price * ltv_ratio
if loan_amount > ltv_max:
    loan_amount = ltv_max
    st.warning(f"LTV capped at {int(ltv_ratio*100)}% → Max loan ${format_number(ltv_max)}")

interest_str = st.text_input("Interest Rate (%)", "", placeholder="e.g. 3.5")
try: interest = float(interest_str)
except ValueError: interest = 0.0

chosen_tenure = st.slider("Loan Tenure (yrs)", 5.0, float(mas_max_tenure), float(mas_max_tenure), 0.5)
st.caption(f"Selected: {chosen_tenure:.0f} yrs (MAS max via IWAA {iw_age:.1f})")
st.divider()

# ---------------------------
# CALCULATIONS
# ---------------------------
r = interest / 100 / 12
n = int(chosen_tenure * 12)
monthly = pmt(r, n, loan_amount)
total_interest = monthly * n - loan_amount
total_payment = loan_amount + total_interest

tdsr_cap = 0.55 * total_income
max_loan_tdsr = (tdsr_cap - existing_loans) * ((1 + r) ** n - 1) / (r * (1 + r) ** n) if r > 0 else (tdsr_cap - existing_loans) * n
shortfall = max(loan_amount - max_loan_tdsr, 0)

tdsr_ok = shortfall == 0
tdsr_color = "green" if tdsr_ok else "red"
max_property_price = max_loan_tdsr / ltv_ratio if ltv_ratio > 0 else 0

# ---------------------------
# RESULTS
# ---------------------------
st.subheader("💡 Loan Summary (Compact View)")

# Row 1: Actual Plan
c1, c2, c3 = st.columns(3)
with c1: st.metric("Property Price", f"${format_number(price)}")
with c2: st.metric("Loan Required", f"${format_number(loan_amount)}")
with c3: st.metric("Monthly", f"${format_number(round(monthly))}")

# Row 2: Max Affordable Plan
c4, c5, c6 = st.columns(3)
with c4: st.metric("Max Property Price", f"${format_number(round(max_property_price))}")
with c5: st.metric("Max Loan Eligible", f"${format_number(round(max_loan_tdsr))}")
with c6:
    max_monthly = pmt(r, n, max_loan_tdsr)
    st.metric("Monthly (Max)", f"${format_number(round(max_monthly))}")

if shortfall > 0:
    st.markdown(
        f"<div style='color:#b30000;font-size:0.95rem;margin-top:0.5rem;'>⚠️ Loan exceeds TDSR by "
        f"<b>${format_number(round(shortfall))}</b> (to be paid by cash/CPF).</div>",
        unsafe_allow_html=True)
else:
    st.markdown("<div style='color:#007700;font-size:0.95rem;'>✅ Within TDSR & LTV limits.</div>", unsafe_allow_html=True)

st.caption(f"TDSR Limit (55%): ${format_number(round(tdsr_cap))} | Status: "
           f"<span style='color:{tdsr_color};font-weight:600;'>{'Within' if tdsr_ok else 'Exceeds'}</span>", unsafe_allow_html=True)
st.divider()

# ---------------------------
# ASSET SIMULATION
# ---------------------------
if shortfall > 0:
    st.markdown("#### 💎 Asset Simulation")
    extra_monthly_needed = pmt(r, n, shortfall)
    recognized_income_needed = extra_monthly_needed / 0.55
    asset_needed_pledge = recognized_income_needed * 48
    asset_needed_unpledge = recognized_income_needed * 48 / 0.30

    c1, c2 = st.columns(2)
    with c1: st.metric("If Pledged (Locked 48m)", f"${format_number(round(asset_needed_pledge))}")
    with c2: st.metric("If Unpledged (Showfund)", f"${format_number(round(asset_needed_unpledge))}")

    st.markdown("""
    <div style='font-size:0.85rem;line-height:1.3;margin-top:0.3rem;color:#555;'>
    <b>Showfund Timelines:</b><br>
    1️⃣ At loan application — show proof (bank statement) for LO.<br>
    2️⃣ Before disbursement — reconfirm funds are available.<br>
    <i>Showfunds aren’t locked but must remain accessible.</i>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# FOOTNOTE
# ---------------------------
st.caption("Figures are estimates for planning only. Please confirm final eligibility with your banker.")
