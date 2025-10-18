# ---------------------------
# PROPERTY & LOAN DETAILS
# ---------------------------
st.subheader("🏡 Property & Loan Details")

loan_mode = st.radio("How would you like to calculate your loan?", ["By Property Price", "By Loan Amount"], index=0)

if loan_mode == "By Property Price":
    purchase_price = st.number_input("Property Purchase Price (SGD)", min_value=100000.0, value=1500000.0, step=10000.0)
    downpayment_percent = st.slider("Downpayment (%)", min_value=5, max_value=75, value=25)
    chosen_loan_amount = purchase_price * (1 - downpayment_percent / 100)
else:
    chosen_loan_amount = st.number_input("I want to borrow (SGD)", min_value=50000.0, value=1000000.0, step=50000.0)
    purchase_price = None
    downpayment_percent = None

interest_rate = st.number_input("Loan Interest Rate (per annum %)", min_value=0.1, value=3.5, step=0.1)

# ----- dynamic max tenure based on loan amount & MAS rule -----
# basic MAS limit based on youngest buyer
mas_limit = max(75 - youngest_age, 5)    # ensures at least 5 years

# optional soft logic – smaller loans may deserve shorter tenures
if chosen_loan_amount <= 500000:
    practical_limit = 20
elif chosen_loan_amount <= 1000000:
    practical_limit = 25
else:
    practical_limit = 30

max_tenure_limit = min(mas_limit, practical_limit)

loan_tenure = st.slider(
    "Loan Tenure (Years)",
    min_value=5,
    max_value=int(max_tenure_limit),
    value=min(25, int(max_tenure_limit))
)

st.caption(f"🔹 Maximum tenure allowed: {int(max_tenure_limit)} years (based on youngest buyer & loan size)")
