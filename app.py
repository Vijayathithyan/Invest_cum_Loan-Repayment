import streamlit as st

st.title("🧪 Debug Step 2: Monthly Savings Preview")

with st.form("debug_form_2"):
    st.subheader("💼 Salary & Expense Info")

    gross_salary = st.number_input("Gross Annual Salary (USD)", value=90000)
    us_tax = st.slider("US Tax Rate (%)", 10, 40, 25)
    expenses = st.number_input("Monthly Living Expenses (USD)", value=2000.0)
    fx_rate = st.number_input("USD to INR Conversion Rate", value=83.5)

    # 💰 Monthly Savings Preview
    monthly_salary_usd = gross_salary / 12
    after_tax_usd = monthly_salary_usd * (1 - us_tax / 100)
    monthly_savings_usd = after_tax_usd - expenses
    monthly_savings_inr = monthly_savings_usd * fx_rate

    st.markdown(f"**💰 Estimated Monthly Savings (INR): ₹{monthly_savings_inr:,.2f}**")

    submitted = st.form_submit_button("Run Test")
    if submitted:
        st.success("✅ Calculation ran successfully!")
