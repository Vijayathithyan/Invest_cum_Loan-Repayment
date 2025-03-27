import streamlit as st

st.title("🧪 Debug Step 4: Investment + Strategy Inputs")

with st.form("debug_form_4"):
    st.subheader("💼 Salary & Expense Info")

    gross_salary = st.number_input("Gross Annual Salary (USD)", value=90000)
    us_tax = st.slider("US Tax Rate (%)", 10, 40, 25)
    expenses = st.number_input("Monthly Living Expenses (USD)", value=2000.0)
    fx_rate = st.number_input("USD to INR Conversion Rate", value=83.5)

    monthly_salary_usd = gross_salary / 12
    after_tax_usd = monthly_salary_usd * (1 - us_tax / 100)
    monthly_savings_usd = after_tax_usd - expenses
    monthly_savings_inr = monthly_savings_usd * fx_rate

    st.markdown(f"**💰 Estimated Monthly Savings (INR): ₹{monthly_savings_inr:,.2f}**")

    st.subheader("🏦 Loan Details")
    loan_amt = st.number_input("Education Loan Amount (INR)", value=2500000)
    interest_rate = st.number_input("Loan Interest Rate (%)", value=10.85, step=0.01, format="%.2f")
    emi = st.number_input("Monthly EMI (INR)", value=27000)
    moratorium = st.slider("Moratorium Period (Months)", 0, 24, 6)
    loan_term = st.selectbox("Loan Duration (Months)", [60, 84, 120, 180, 240])

    st.subheader("📈 Investment Details")
    invest_rate = st.number_input("Investment Return Rate (%)", value=12.0, step=0.1, format="%.2f")
    tax_rate = st.slider("Indian Tax Rate (%)", 0, 30, 15)

    st.subheader("🧪 Strategy")
    strategy = st.selectbox("Select Strategy", ['A', 'B', 'C', 'D'])
    invest_percent = st.slider("Percent of Savings to Invest (%)", 0, 100, 60)

    st.subheader("⚙️ Simulation Settings")
    sim_years = st.slider("Number of Years to Simulate", 1, 30, 10)

    submitted = st.form_submit_button("Run Test")
    if submitted:
        st.success("✅ All input sections are working!")
