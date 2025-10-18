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

num_buyers = st.selectbox("Number of Buyers", [1, 2, 3, 4]_
