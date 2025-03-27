import streamlit as st

st.title("🧪 Debugging the App Form Step-by-Step")

with st.form("debug_form"):
    st.subheader("💼 Salary & Expense Info")

    gross_salary = st.number_input("Gross Annual Salary (USD)", value=90000)
    us_tax = st.slider("US Tax Rate (%)", 10, 40, 25)
    expenses = st.number_input("Monthly Living Expenses (USD)", value=2000.0)
    fx_rate = st.number_input("USD to INR Conversion Rate", value=83.5)

    submitted = st.form_submit_button("Run Test")
    if submitted:
        st.success("✅ Form submitted successfully!")
