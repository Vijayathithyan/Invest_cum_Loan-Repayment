import streamlit as st
import pandas as pd
from simulation import UserInput, run_simulation, run_simulation_with_jobloss, plot_simulation_results, generate_summary
import random

st.set_page_config(page_title="Investment & Loan Strategy Simulator", layout="centered")

# --- Sidebar Setup ---
with st.sidebar:
    st.title("📊 Investment & Loan Strategy Simulator")
    st.markdown("""
    This tool helps international students simulate and compare strategies for:
    - Repaying student loans 💸
    - Investing monthly savings 📈
    - Maximizing net worth 💰

    Choose a strategy, enter your assumptions, and simulate outcomes over time.
    """)
    st.markdown("👤 **Built by:** Vijayathithyan B B")
    st.markdown("[🌐 GitHub](https://github.com/Vijayathithyan/Invest_cum_Loan-Repayment)")
    st.markdown("[🌐 LinkedIn](https://www.linkedin.com/in/vijayathithyan-b-b-ba0b50244?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BpoVLoxgLQr6rGli3yJJ3aA%3D%3D)")
    
    st.markdown("### 🎲 Try Advanced Scenario")
    st.markdown("**Job Loss Probability Simulation**")
    st.markdown("""
    Simulate what happens if you unexpectedly lose your job during the simulation window.

    - You define a job loss probability (% per year)
    - Each month, there's a small chance you'll lose your income
    - After job loss: no savings, no repayments, no new investments
    - Investments continue to grow. Loan accrues interest.
    """)
    enable_jobloss_sim = st.checkbox("Enable Job Loss Simulation")
    jobloss_prob = st.slider("Job Loss Probability (% per year)", 0, 100, 10)

st.title("💸 Investment-Cum-Loan Repayment Simulator")

# --- Input Form ---
with st.form("input_form"):
    with st.expander("💼 Salary & Expense Info", expanded=True):
        gross_salary = st.number_input("Gross Annual Salary (USD)", value=90000,
            help="Your annual pre-tax salary in the United States.")
        us_tax = st.slider("US Tax Rate (%)", 10, 40, 25,
            help="Estimated combined federal and state income tax rate.")
        expenses = st.number_input("Monthly Living Expenses (USD)", value=2000.0,
            help="Your estimated monthly spending on rent, food, transport, etc.")
        fx_rate = st.number_input("USD to INR Conversion Rate", value=83.5,
            help="The current exchange rate used for USD to INR conversion.")

    with st.expander("🏦 Loan Details", expanded=True):
        loan_amt = st.number_input("Education Loan Amount (INR)", value=2500000,
            help="The total loan amount borrowed in India in INR.")
        interest_rate = st.number_input("Loan Interest Rate (%)", value=10.85, step=0.01, format="%.2f",
            help="Annual interest rate applied to the education loan.")
        emi = st.number_input("Monthly EMI (INR)", value=27000,
            help="Your fixed monthly repayment amount as agreed with the bank.")
        moratorium = st.slider("Moratorium Period (Months)", 0, 24, 6,
            help="Months after graduation during which no EMI is required.")
        loan_term = st.selectbox("Loan Duration (Months)", [60, 84, 120, 180, 240],
            help="Total loan repayment period as per agreement.")

    with st.expander("📈 Investment Details", expanded=True):
        invest_rate = st.number_input("Investment Return Rate (%)", value=12.0, step=0.1, format="%.2f",
            help="Expected average annual return on your investments.")
        tax_rate = st.slider("Indian Tax Rate (%)", 0, 30, 15,
            help="Tax rate in India on returns from your investment income.")

    with st.expander("🧪 Strategy Options", expanded=True):
        st.markdown("### 📘 Strategy Overview")
        st.markdown("""
        **🔴 Strategy A – Aggressive Repayment**  
        Use 100% of savings to aggressively repay the loan. No investments until the loan is cleared.

        **🟡 Strategy B – Balanced**  
        Split your monthly savings between investments and loan repayment based on your chosen percentage.

        **🔵 Strategy C – Invest First, Then Balanced**  
        During the moratorium period, invest all your savings. After that, split your savings between investments and repayment.

        **🟣 Strategy D – Invest First, Then Aggressive**  
        Invest all savings during the moratorium, then use 100% of savings for aggressive loan repayment.
        """)
        strategy = st.selectbox("Choose a Strategy", ['A', 'B', 'C', 'D'], index=1,
            help="Select a repayment-investment strategy from the four available options.")
        invest_percent = st.slider("Percent of Savings to Invest (%)", 0, 100, 60,
            help="What percentage of your monthly savings you'd like to invest.")

    with st.expander("⚙️ Simulation Settings", expanded=True):
        sim_years = st.slider("Number of Years to Simulate", 1, 30, 10,
            help="Time horizon in years to project the loan and investment simulation.")

    submitted = st.form_submit_button("Review Your Inputs")

# Save inputs immediately to session_state for use in simulation
st.session_state.user_inputs = {
    "Gross Annual Salary (USD)": gross_salary,
    "US Tax Rate (%)": us_tax,
    "Monthly Living Expenses (USD)": expenses,
    "USD to INR Conversion Rate": fx_rate,
    "Education Loan Amount (INR)": loan_amt,
    "Loan Interest Rate (%)": interest_rate,
    "Monthly EMI (INR)": emi,
    "Moratorium Period (Months)": moratorium,
    "Loan Duration (Months)": loan_term,
    "Investment Return Rate (%)": invest_rate,
    "Indian Tax Rate (%)": tax_rate,
    "Chosen Strategy": strategy,
    "Percent of Savings to Invest (%)": invest_percent,
    "Number of Years to Simulate": sim_years
}

# Show Start Simulation Button
if st.button("🚀 Start Simulation"):
    user_input = UserInput(
        gross_annual_salary_usd=st.session_state.user_inputs["Gross Annual Salary (USD)"],
        us_tax_rate=st.session_state.user_inputs["US Tax Rate (%)"] / 100,
        monthly_expenses_usd=st.session_state.user_inputs["Monthly Living Expenses (USD)"],
        loan_amount_inr=st.session_state.user_inputs["Education Loan Amount (INR)"],
        interest_rate_loan=st.session_state.user_inputs["Loan Interest Rate (%)"],
        emi_inr=st.session_state.user_inputs["Monthly EMI (INR)"],
        moratorium_months=st.session_state.user_inputs["Moratorium Period (Months)"],
        loan_term_months=st.session_state.user_inputs["Loan Duration (Months)"],
        investment_rate_annual=st.session_state.user_inputs["Investment Return Rate (%)"],
        indian_tax_rate=st.session_state.user_inputs["Indian Tax Rate (%)"],
        usd_to_inr_rate=st.session_state.user_inputs["USD to INR Conversion Rate"],
        percent_to_invest=st.session_state.user_inputs["Percent of Savings to Invest (%)"],
        years_to_simulate=st.session_state.user_inputs["Number of Years to Simulate"],
        strategy_type=st.session_state.user_inputs["Chosen Strategy"]
    )

    if enable_jobloss_sim:
        df = run_simulation_with_jobloss(user_input, jobloss_prob)
    else:
        df = run_simulation(user_input)

    st.markdown("## 📈 Simulation Summary")
    generate_summary(df, user_input)

    st.markdown("## 📊 Visualization")
    plot_simulation_results(df, user_input.emi_inr)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Simulation Output (CSV)", csv, "simulation_output.csv")

    df.to_excel("simulation_output.xlsx", index=False)
    with open("simulation_output.xlsx", "rb") as f:
        st.download_button("Download Simulation Output (Excel)", f, "simulation_output.xlsx")
