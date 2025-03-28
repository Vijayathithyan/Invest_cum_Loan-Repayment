import streamlit as st
import pandas as pd
from simulation import UserInput, run_simulation, plot_simulation_results, generate_summary

st.set_page_config(page_title="Investment & Loan Strategy Simulator", layout="centered")
st.title("📊 Investment-Cum-Loan Repayment Simulator")

with st.form("input_form"):
    st.subheader("💼 Salary & Expense Info")

    gross_salary = st.number_input("Gross Annual Salary (USD)", value=90000, help="Your pre-tax yearly salary expected from your job in the US.")
    us_tax = st.slider("US Tax Rate (%)", 10, 40, 25,  help="Estimated total tax rate (federal + state) applied to your US salary.")
    expenses = st.number_input("Monthly Living Expenses (USD)", value=2000.0, help="Your monthly personal expenses while living in the US (excluding taxes).")
    fx_rate = st.number_input("USD to INR Conversion Rate", value=83.5, help="Assumed currency conversion rate from USD to INR.")

    monthly_salary_usd = gross_salary / 12
    after_tax_usd = monthly_salary_usd * (1 - us_tax / 100)
    monthly_savings_usd = after_tax_usd - expenses
    monthly_savings_inr = monthly_savings_usd * fx_rate

    st.markdown(f"**💰 Estimated Monthly Savings (INR): ₹{monthly_savings_inr:,.2f}**")

    st.subheader("🏦 Loan Details")
    loan_amt = st.number_input("Education Loan Amount (INR)", value=2500000, help="Total loan amount you borrowed, in INR (or Home Currency).")
    interest_rate = st.number_input("Loan Interest Rate (%)", value=10.85, step=0.01, format="%.2f",  help="Annual interest rate charged by the bank on your loan.")
    emi = st.number_input("Monthly EMI (INR)", value=27000, help="Minimum monthly loan payment (EMI) as per the bank schedule.")
    moratorium = st.slider("Moratorium Period (Months)", 0, 24, 6, help="Months after graduation during which you're not required to repay the loan.")
    loan_term = st.selectbox("Loan Duration (Months)", [60, 84, 120, 180, 240, 300], help="Total repayment period as per your loan agreement.")

    st.subheader("📈 Investment Details")
    invest_rate = st.number_input("Investment Return Rate (%)", value=12.0, step=0.1, format="%.2f", help="Estimated annual return percentage on your investments.")
    tax_rate = st.slider("Indian Tax Rate (%)", 0, 30, 15,  help="Tax rate in India applied to gains from your investments.")

    st.subheader("🧪 Strategy Options")
   
    st.markdown("""
    ### 📘 Strategy Overview
    
    **🔴 Strategy A – Aggressive Repayment**  
    Use 100% of savings to aggressively repay the loan. No investments until the loan is cleared.
    
    **🟡 Strategy B – Balanced**  
    Split your monthly savings between investments and loan repayment based on your chosen percentage.
    
    **🔵 Strategy C – Invest First, Then Balanced**  
    During the moratorium period, invest all your savings. After that, split your savings between investments and repayment.
    
    **🟣 Strategy D – Invest First, Then Aggressive**  
    Invest all savings during the moratorium, then use 100% of savings for aggressive loan repayment.
    """)
    
    strategy = st.selectbox("Select Strategy", ['A', 'B', 'C', 'D'])

    # 📝 Strategy description box
    strategy_descriptions = {
        'A': "🔴 **Aggressive Repayment** – Use 100% of savings to repay the loan. No investment until full repayment.",
        'B': "🟡 **Balanced** – Split monthly savings between investments and repayment based on your input ratio.",
        'C': "🔵 **Invest First, Then Balanced** – Invest during the moratorium, then follow a split approach.",
        'D': "🟣 **Invest First, Then Aggressive** – Invest during the moratorium, then aggressively repay the loan."
    }

    st.info(strategy_descriptions[strategy])
    invest_percent = st.slider("Percent of Savings to Invest (%)", 0, 100, 60, help="Out of your monthly savings, how much (%) you want to allocate to investments.")

    st.subheader("⚙️ Simulation Settings")
    sim_years = st.slider("Number of Years to Simulate", 1, 30, 10, help="Time horizon for the simulation in years after graduation.")

    submitted = st.form_submit_button("Review and Simulate")

    if submitted:
        with st.expander("📋 Review Your Inputs Before Running Simulation", expanded=True):
            st.markdown("### Salary & Expenses")
            st.write(f"**Gross Annual Salary (USD):** ${gross_salary:,.0f}")
            st.write(f"**US Tax Rate:** {us_tax}%")
            st.write(f"**Monthly Expenses (USD):** ${expenses:,.0f}")
            st.write(f"**USD to INR Rate:** ₹{fx_rate:.2f}")
            st.markdown("---")
    
            st.markdown("### Loan Details")
            st.write(f"**Loan Amount (INR):** ₹{loan_amt:,.0f}")
            st.write(f"**Loan Interest Rate:** {interest_rate:.2f}%")
            st.write(f"**Monthly EMI:** ₹{emi:,.0f}")
            st.write(f"**Moratorium Period:** {moratorium} months")
            st.write(f"**Loan Duration:** {loan_term} months")
            st.markdown("---")
    
            st.markdown("### Investment Plan")
            st.write(f"**Investment Return Rate:** {invest_rate:.2f}%")
            st.write(f"**Indian Tax Rate on Returns:** {tax_rate}%")
            st.write(f"**% of Savings to Invest:** {invest_percent}%")
            st.markdown("---")
    
            st.markdown("### Strategy & Simulation")
            st.write(f"**Selected Strategy:** {strategy}")
            st.write(f"**Years to Simulate:** {sim_years}")
            st.success("✅ All inputs loaded. Click below to start the simulation.")
    
            if st.button("Start Simulation"):
                # Proceed to run simulation (your existing logic goes here)
                user_input = UserInput(
                    gross_annual_salary_usd=gross_salary,
                    us_tax_rate=us_tax / 100,
                    monthly_expenses_usd=expenses,
                    loan_amount_inr=loan_amt,
                    interest_rate_loan=interest_rate,
                    emi_inr=emi,
                    moratorium_months=moratorium,
                    loan_term_months=loan_term,
                    investment_rate_annual=invest_rate,
                    indian_tax_rate=tax_rate,
                    usd_to_inr_rate=fx_rate,
                    percent_to_invest=invest_percent,
                    years_to_simulate=sim_years,
                    strategy_type=strategy
                )
    
                df = run_simulation(user_input)
                st.markdown("## 📈 Simulation Summary")
                generate_summary(df, user_input)
                st.markdown("## 📊 Visualization")
                plot_simulation_results(df, user_input.emi_inr)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, "simulation_output.csv")
                df.to_excel("simulation_output.xlsx", index=False)
                with open("simulation_output.xlsx", "rb") as f:
                    st.download_button("Download Excel", f, "simulation_output.xlsx")


if submitted:
    # Create input object
    user_input = UserInput(
        gross_annual_salary_usd=gross_salary,
        us_tax_rate=us_tax / 100,
        monthly_expenses_usd=expenses,
        loan_amount_inr=loan_amt,
        interest_rate_loan=interest_rate,
        emi_inr=emi,
        moratorium_months=moratorium,
        loan_term_months=loan_term,
        investment_rate_annual=invest_rate,
        indian_tax_rate=tax_rate,
        usd_to_inr_rate=fx_rate,
        percent_to_invest=invest_percent,
        years_to_simulate=sim_years,
        strategy_type=strategy
    )

    # Run simulation
    df = run_simulation(user_input)

    st.markdown("## 📈 Simulation Summary")
    generate_summary(df, user_input)

    st.markdown("## 📊 Visualization")
    plot_simulation_results(df, user_input.emi_inr)

    st.markdown("## 📥 Download Results")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "simulation_output.csv")

    df.to_excel("simulation_output.xlsx", index=False)
    with open("simulation_output.xlsx", "rb") as f:
        st.download_button("Download Excel", f, "simulation_output.xlsx")
