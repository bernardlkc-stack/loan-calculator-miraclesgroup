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
num_buyers = st.selectbox("Number of Buyers", [1, 2, 3, 4], index=0)

buyers_ages = []
buyers_incomes = []
for i in range(num_buyers):
    st.markdown(f"**Buyer {i+1}**")
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input(
            f"Buyer {i+1} Age",
            min_value=21, max_value=75,
            value=40 if i == 0 else 35,
            key=f"age_{i}"
        )
    with c2:
        income = st.number_input(
            f"Buyer {i+1} Monthly Income (SGD)",
            min_value=0.0, value=8000.0 if i == 0 else 5000.0,
            step=500.0, key
