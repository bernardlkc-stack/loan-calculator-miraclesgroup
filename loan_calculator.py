import streamlit as st

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
# BUYER & INCOME DETAILS
# ---------------------------
st.subheader("👥 Buyer Details")

# 👇 make sure this whole line is on ONE line
num_buyers = st.selectbox("Number of Buyers", [1, 2, 3, 4], index=0)

buyers_ages = []
buyers_incomes = []

for i in range(num_buyers):
    st.markdown(f"**Buyer {i+1} Details**")
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            f"Buyer {i+1} Age",
            min_value=21,
            max_value=75,
            value=40 if i == 0 else 35,
            key=f"age_{i}"
        )

    with col2:
        income = st.number_input(
            f"Buyer {i+1} Monthly Income (SGD)",
            min_value=0.0,
            value=8000.0 if i == 0 else 5000.0,
            step=500.0,
            key=f"income_{i}"
        )

    buyers_ages.append(age)
    buyers_incomes.append(income)

youngest_age = min(buyers_ages)
total_income = sum(buyers_incomes)

existing_loans_monthly = st.number_input(
    "Total Monthly Loan Commitments (SGD, optional)",
    min_value=0.0,
    value=0.0,
    step=100.0
)

num_outstanding_home_loans = st.selectbox(
    "Number of Outstanding Housing Loans (to determine LTV limit)",
    [0, 1, 2],
    index=0
)

st.divider()

# ---------------------------
# LOAN ENTRY: PRICE vs IWAA
# ---------------------------
st.subheader("🏡 Property & Loan Details")

calc_mode = st.radio(
    "How would you like to calculate?",
    ["By Property Price", "By Loan Amount (IWAA)"],
    index=0
)

# LTV limits by outstanding loans (MAS)
if num_outstanding_home_loans == 0:
    ltv_limit_ratio = 0.75
elif num_outstanding_home_loans == 1:
    ltv_limit_ratio = 0.45
else:
    ltv_limit_ratio = 0.35

# Tenure cap (MAS): min(30 years, 75 - youngest_age)
mas_tenure_cap = max(0, 75 - youngest_age)
tenure_cap_years = min(30, mas_tenure_cap)
if tenure_cap_years < 5:
    tenure_cap_years = 5

if calc_mode == "By Property Price":
    price = st.number_input(
        "Property Purchase Price (SGD)",
        min_value=100000.0,
        value=1500000.0,
        step=10000.0
    )
    down_pct = st.slider("Downpayment (%)", 5, 75, 25)
    loan_amount = price * (1 - down_pct / 100.0)
    ltv_max_loan = price * ltv_limit_ratio

    if loan_amount > ltv_max_loan:
        st.warning(
            f"⚠️ LTV capped at {int(ltv_limit_ratio*100)}% ⇒ "
            f"maximum allowable loan is ${ltv_max_loan:,.0f}. "
            "Loan amount has been limited accordingly."
        )
        loan_amount = ltv_max_loan

    price_for_ltv_check = price

else:
    loan_amount = st.number_input(
        "I want to borrow (SGD)",
        min_value=50000.0,
        value=1000000.0,
        step=50000.0
    )
    price_for_ltv_check = st.number_input(
        "Property Price (optional, for LTV check)",
        min_value=0.0,
        value=0.0,
        step=10000.0,
        help="Enter property price if you'd like to check LTV limit."
    )

    if price_for_ltv_check > 0 and loan_amount > price_for_ltv_check * ltv_limit_ratio:
        st.error(
            f"❗ IWAA ${loan_amount:,.0f} exceeds LTV {int(ltv_limit_ratio*100)}% "
            f"of price ${price_for_ltv_check:,.0f} "
            f"(max ${price_for_ltv_check*ltv_limit_ratio:,.0f})."
        )

interest_pa = st.number_input(
    "Loan Interest Rate (per annum %)",
    min_value=0.1,
    value=3.5,
    step=0.1
)

loan_tenure_years = st.slider(
    "Loan Tenure (Years)",
    min_value=5,
    max_value=int(tenure_cap_years),
    value=min(25, int(tenure_cap_years))
)
st.caption(f"🔹 Tenure capped by MAS at min(30, 75 − youngest age) ⇒ **{int(tenure_cap_years)} years**.")

st.divider()

# ---------------------------
# CALCULATIONS
# ---------------------------
r = interest_pa / 100 / 12
n = int(loan_tenure_years * 12)

if r > 0:
    monthly_instalment = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
else:
    monthly_instalment = loan_amount / n

total_payment = monthly_instalment * n
total_interest = total_payment - loan_amount

if total_income > 0:
    tdsr_cap = 0.55 * total_income
    total_commitment = monthly_instalment + existing_loans_monthly
    tdsr_status = "✅ Within TDSR limit" if total_commitment <= tdsr_cap else "❌ Exceeds TDSR limit"
    tdsr_color = "green" if total_commitment <= tdsr_cap else "red"
else:
    tdsr_status = "N/A"
    tdsr_color = "gray"

# ---------------------------
# DISPLAY RESULTS
# ---------------------------
st.header("💡 Loan Summary")

c1, c2 = st.columns(2)
with c1:
    st.metric("Loan Amount (SGD)", f"${loan_amount:,.0f}")
    st.metric("Monthly Instalment", f"${monthly_instalment:,.0f}")
with c2:
    st.metric("Total Interest Payable", f"${total_interest:,.0f}")
    st.metric("Total Payment", f"${total_payment:,.0f}")

st.markdown(f"**TDSR Status:** <span style='color:{tdsr_color}'>{tdsr_status}</span>", unsafe_allow_html=True)

if calc_mode == "By Property Price":
    st.markdown(f"**Price Entered:** ${price_for_ltv_check:,.0f}  \n**LTV Limit:** {int(ltv_limit_ratio*100)}%")
elif price_for_ltv_check:
    st.markdown(f"**LTV Check Price:** ${price_for_ltv_check:,.0f}  \n**Limit:** {int(ltv_limit_ratio*100)}%")

st.divider()

st.subheader("👨‍👩‍👧‍👦 Buyer Summary")
for i in range(num_buyers):
    st.markdown(f"- **Buyer {i+1}:** Age {buyers_ages[i]}, Income ${buyers_incomes[i]:,.0f}")
st.markdown(f"**Total Combined Income:** ${total_income:,.0f}")
st.markdown(f"**Youngest Buyer’s Age:** {youngest_age} years")

st.divider()

st.header("📊 Notes & Disclaimers")
st.markdown("""
- **Tenure cap (MAS):** min(30 years, 75 − youngest buyer’s age).  
- **LTV limits:** 75% (no outstanding loan), 45% (1 loan), 35% (2+ loans).  
- **TDSR cap:** Monthly debt ≤ 55% of gross income.  
- IWAA mode computes instalments from loan amount.  
- Illustrative use only — confirm with your banker.
""")
