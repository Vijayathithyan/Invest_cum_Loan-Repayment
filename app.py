# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from simulation import simulate_strategy

st.set_page_config(page_title="Investment vs Loan Repayment", layout="wide")

# Sidebar navigation
st.sidebar.header("Navigation")
tabs = st.sidebar.radio("Go to:", ["🏠 Home", "🏃‍♂️ Run Simulation", "📈 Strategy Comparison", "🔍 Optimization Explorer", "ℹ️ About"])

# Common Input Section

def user_inputs():
    col1, col2 = st.columns(2)
    with col1:
        years_to_simulate = st.number_input("Simulation Duration (Years)", min_value=1, max_value=30, value=10)
        gross_annual_salary_usd = st.number_input("Gross Annual Salary (USD)", value=90000.0)
        monthly_expenses_usd = st.number_input("Monthly Living Expenses (USD)", value=2000.0)
        loan_amount_inr = st.number_input("Education Loan Amount (INR)", value=2500000.0)
        emi_inr = st.number_input("Monthly EMI (INR)", value=27000.0)
        investment_rate_annual = st.slider("Investment Return Rate (%)", 0.0, 40.0, 12.0) / 100
        usd_to_inr_rate = st.number_input("USD to INR Rate", value=83.5)
    with col2:
        moratorium_months = st.slider("Moratorium Period (Months)", 0, 36, 6)
        us_tax_rate = st.slider("US Income Tax Rate (%)", 10, 40, 25) / 100
        interest_rate_loan = st.number_input("Loan Interest Rate (%)", value=11.0)
        loan_term_months = st.slider("Loan Term (Months)", 12, 300, 120)
        indian_tax_rate = st.slider("Indian Tax on Investment (%)", 0, 30, 15) / 100

    return {
        'years_to_simulate': years_to_simulate,
        'moratorium_months': moratorium_months,
        'gross_annual_salary_usd': gross_annual_salary_usd,
        'us_tax_rate': us_tax_rate,
        'monthly_expenses_usd': monthly_expenses_usd,
        'loan_amount_inr': loan_amount_inr,
        'interest_rate_loan': interest_rate_loan / 100,
        'emi_inr': emi_inr,
        'loan_term_months': loan_term_months,
        'investment_rate_annual': investment_rate_annual,
        'indian_tax_rate': indian_tax_rate,
        'usd_to_inr_rate': usd_to_inr_rate
    }

# Home tab content
if tabs == "🏠 Home":
    st.title("📊 Investment-Cum-Loan Repayment Simulator")
    st.markdown("""
Welcome to the **Investment-Cum-Loan Repayment Simulator**! This tool is designed to help you
make informed decisions about how to allocate your monthly savings between repaying a student loan
and investing in Indian financial instruments.

### How It Works:
- Enter your income, loan, and investment details.
- Choose a strategy: from aggressive repayment to balanced investing.
- Run a month-by-month simulation for up to 30 years.
- Get insights on your final net worth, break-even point, and investment coverage.

### Benefits:
- See how different strategies affect your net worth.
- Compare strategies side-by-side.
- Use optimization to find the best savings split.

Use the navigation sidebar to begin your simulation.
""")

# Run Simulation tab content
elif tabs == "🏃‍♂️ Run Simulation":
    st.header("Run a Strategy Simulation")
    params = user_inputs()

    st.subheader("🧠 Strategy Selection")
    with st.expander("Click to View Strategy Descriptions"):
        st.markdown("""
- **🔴 Strategy A – Aggressive Repayment:** All savings go toward loan until it is cleared.
- **🟡 Strategy B – Balanced:** Split monthly savings between investment and repayment (default 50:50).
- **🔵 Strategy C – Invest First, Then Balanced:** Invest during moratorium, then apply Strategy B.
- **🔸 Strategy D – Invest First, Then Aggressive:** Invest during moratorium, then repay loan aggressively.
- **🟢 Strategy E – Dynamic Allocation:** Repay until X% loan cleared, then invest fully.
- **🟠 Strategy F – Risk-Aware:** Allocation varies monthly based on job security or investment volatility.
- **🟣 Strategy G – Random Split Simulation:** Each month, the savings split between investment and repayment is randomized. This allows users to explore how unpredictable behavior might impact final outcomes.
        """)

    strategy = st.radio("Choose a Strategy", [
        "A - Aggressive Repayment",
        "B - Balanced",
        "C - Invest First, Then Balanced",
        "D - Invest First, Then Aggressive",
        "E - Dynamic Allocation",
        "F - Risk-Aware Allocation",
        "G - Random Split Simulation"
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

# Strategy Comparison
elif tabs == "📈 Strategy Comparison":
    st.header("Compare Multiple Strategies")
    st.info("🛠 This module will allow running multiple strategies side-by-side. Coming next!")

# Optimization
elif tabs == "🔍 Optimization Explorer":
    st.header("🔍 Strategy G – Monte Carlo Simulation")
    st.markdown("""
This tool runs Strategy G (Random Split Simulation) multiple times to analyze variability in final outcomes.
You can explore the distribution of net worth based on unpredictable saving behavior.
""")

    params = user_inputs()
    num_runs = st.slider("Number of Simulations", min_value=10, max_value=500, value=100, step=10)

    if st.button("Run Monte Carlo Simulation"):
        with st.spinner("Running multiple Strategy G simulations..."):
            from simulation import simulate_multiple_runs
            df_runs = simulate_multiple_runs(params, runs=num_runs)

            st.success("Simulation complete!")
            
            st.subheader("📊 Net Worth Distribution")
            import plotly.express as px
            fig = px.histogram(df_runs, x='Final Net Worth (INR)', nbins=30, title="Distribution of Final Net Worth")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🧠 Interpretation")
            st.markdown(f"""
            After running {num_runs} randomized simulations of Strategy G:
            
            - 💰 On average, your net worth at the end of the simulation was **₹{desc['mean']:,.0f}**.
            - 📉 The lowest outcome observed was **₹{desc['min']:,.0f}**, and the highest was **₹{desc['max']:,.0f}**.
            - 📊 This spread shows how unpredictable monthly decisions can impact your long-term wealth.
            
            👉 In simple terms: Even if you don't follow a fixed savings plan, you'll likely end up between ₹{desc['25%']:,.0f} and ₹{desc['75%']:,.0f}, assuming similar income and loan conditions.
            """)

            st.subheader("📋 Summary Statistics")
            desc = df_runs['Final Net Worth (INR)'].describe()
            desc_formatted = desc.apply(lambda x: f"₹{x:,.2f}" if desc.name != 'count' else f"{x:,.0f}")
            desc_formatted['count'] = f"{int(desc['count'])}"  # Ensure count is integer and no ₹
            st.write(desc_formatted)

# About
elif tabs == "ℹ️ About":
    st.header("👤 About the Author")
    st.markdown("""
**Vijayathithyan B B** is a graduate student at **Virginia Commonwealth University**, pursuing a Master’s in Decision Analytics with a concentration in Accounting Analytics. With a background in auditing and financial risk assessment, Vijay brings together technical expertise in **Python, SQL, and data analytics** with real-world experience in **SOX compliance, internal controls, and forensic accounting**.

Before transitioning into analytics, he served as a Senior Auditor in India, where he led business development, built audit automation tools, and managed regulatory compliance for growing firms. He is also a **CPA-eligible** professional with multiple postgraduate degrees in **Accounting and Finance**.

Vijay is passionate about applying decision science to real-world financial dilemmas — especially those faced by international students like himself. This app was created from personal experience, aiming to simplify complex investment and repayment decisions through interactive simulation and data-driven strategy.

When not crunching numbers or designing tools, Vijay is actively involved in mentoring youth initiatives, co-founding creative workshops, and volunteering for economic development projects in his hometown.

📫 [LinkedIn](https://www.linkedin.com/in/vijayathithyan-b-b-ba0b50244/)  
🔗 [GitHub](https://github.com/Vijayathithyan/Invest_cum_Loan-Repayment)
    """)
