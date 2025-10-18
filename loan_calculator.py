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
# BUYER & INCOME DETAILS
# ---------------------------
st.subheader("👥 Buyer Details")
