# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from simulation import simulate_strategy

st.set_page_config(page_title="Investment vs Loan Repayment", layout="wide")
st.title("📊 Investment-Cum-Loan Repayment Simulator")

# Sidebar navigation
st.sidebar.header("Navigation")
tabs = st.sidebar.radio("Go to:", ["🏠 Run Simulation", "📈 Strategy Comparison", "🔍 Optimization Explorer", "ℹ️ About"])

# Common Input Section (used in all tabs)
def user_inputs():
    st.subheader("User Profile & Simulation Horizon")
    years_to_simulate = st.number_input("Simulation Duration (Years)", min_value=1, max_value=30, value=10)
    moratorium_months = st.slider("Moratorium Period (Months)", 0, 36, 6)

    st.subheader("💼 Salary & Expense Info")
    gross_annual_salary_usd = st.number_input("Gross Annual Salary (USD)", value=90000.0)
    us_tax_rate = st.slider("US Income Tax Rate (%)", 10, 40, 25) / 100
    monthly_expenses_usd = st.number_input("Monthly Living Expenses (USD)", value=2000.0)

    st.subheader("💰 Loan Details")
    loan_amount_inr = st.number_input("Education Loan Amount (INR)", value=2500000.0)
    interest_rate_loan = st.slider("Loan Interest Rate (%)", 1, 25, 11) / 100
    emi_inr = st.number_input("Monthly EMI (INR)", value=27000.0)
    loan_term_months = st.slider("Loan Term (Months)", 12, 300, 120)

    st.subheader("📈 Investment Details")
    investment_rate_annual = st.slider("Investment Return Rate (%)", 0, 40, 12) / 100
    indian_tax_rate = st.slider("Indian Tax on Investment (%)", 0, 30, 15) / 100
    usd_to_inr_rate = st.number_input("USD to INR Rate", value=83.5)

    return {
        'years_to_simulate': years_to_simulate,
        'moratorium_months': moratorium_months,
        'gross_annual_salary_usd': gross_annual_salary_usd,
        'us_tax_rate': us_tax_rate,
        'monthly_expenses_usd': monthly_expenses_usd,
        'loan_amount_inr': loan_amount_inr,
        'interest_rate_loan': interest_rate_loan,
        'emi_inr': emi_inr,
        'loan_term_months': loan_term_months,
        'investment_rate_annual': investment_rate_annual,
        'indian_tax_rate': indian_tax_rate,
        'usd_to_inr_rate': usd_to_inr_rate
    }

# Tab 1: Run Simulation
if tabs == "🏠 Run Simulation":
    st.header("Run a Strategy Simulation")
    params = user_inputs()

    st.subheader("🧠 Strategy Selection")
    strategy = st.radio("Choose a Strategy", [
        "A - Aggressive Repayment",
        "B - Balanced",
        "C - Invest First, Then Balanced",
        "D - Invest First, Then Aggressive",
        "E - Dynamic Allocation",
        "F - Risk-Aware Allocation"
    ])

    strategy_code = strategy[0]
    params['strategy'] = strategy_code

    if strategy_code in ['B', 'C']:
        params['invest_ratio'] = st.slider("% of Savings to Invest", 0, 100, 50) / 100

    if strategy_code == 'E':
        params['repay_threshold'] = st.slider("Switch to Investing After Reaching (% of Loan Repaid)", 10, 100, 50) / 100

    if strategy_code == 'F':
        risk_type = st.radio("Risk Driver", ['Job Security', 'Investment Volatility'])
        params['risk_type'] = 'job' if risk_type == 'Job Security' else 'investment'
        if params['risk_type'] == 'job':
            params['job_security_prob'] = st.slider("Job Security Probability", 0.0, 1.0, 0.9)
        else:
            params['investment_volatility'] = st.slider("Investment Volatility (0 = low, 1 = high)", 0.0, 1.0, 0.2)

    if st.button("Run Simulation"):
        with st.spinner("Simulating..."):
            df, summary = simulate_strategy(params)
            st.success("Simulation Complete!")

            st.subheader("📊 Summary Results")
            st.write(f"**Final Net Worth (INR):** ₹{summary['final_net_worth']:,.0f}")
            st.write(f"**Loan Cleared In Month:** {summary['loan_cleared_month']}")
            st.write(f"**Investment Income Covers EMI In Month:** {summary['investment_covers_emi_month']}")
            st.write(f"**Loan Fully Repaid?** {'✅ Yes' if summary['loan_repaid'] else '❌ No'}")

            st.subheader("📉 Net Worth and Balances Over Time")
            fig = px.line(df, y=['Net Worth (INR)', 'Remaining Loan Balance', 'Total Investment (INR)'], title="Monthly Financial Progress")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📄 Detailed Monthly Report")
            st.dataframe(df.round(2))
            csv = df.to_csv(index=True).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="simulation_output.csv", mime="text/csv")

# Tab 2: Strategy Comparison (Placeholder)
elif tabs == "📈 Strategy Comparison":
    st.header("Compare Multiple Strategies")
    st.info("🛠 This module will allow running multiple strategies side-by-side. Coming next!")

# Tab 3: Optimization Explorer (Placeholder)
elif tabs == "🔍 Optimization Explorer":
    st.header("Optimize Savings Split")
    st.info("🛠 This module will optimize % allocation to investment vs repayment. Coming next!")

# Tab 4: About
elif tabs == "ℹ️ About":
    st.header("About This Project")
    st.markdown("""
    This app helps international students or professionals simulate different strategies for handling
    their loan repayments and investments after graduation. It supports:

    - Aggressive repayment
    - Balanced investment and repayment
    - Invest-first hybrid strategies
    - Dynamic and risk-based strategies

    Built using **Python**, **Pandas**, **Streamlit**, and **Plotly**.
    
    GitHub: [Invest-Cum-Loan-Repayment](https://github.com/Vijayathithyan/Invest_cum_Loan-Repayment)
    """)
