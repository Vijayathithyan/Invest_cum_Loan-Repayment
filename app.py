import pandas as pd
import streamlit as st
import altair as alt
from io import BytesIO
from simulation import UserInput, run_simulation, optimize_investment, SIM_HISTORY, store_simulation_run, plot_simulation_results, generate_summary

st.set_page_config(page_title="Investment + Loan Repayment Decision", layout="wide")
st.title("💼 Investment-Cum-Loan Repayment Simulator")

st.markdown("""
This tool helps international students simulate different strategies to repay education loans and invest savings after graduation.
You can compare strategies, optimize your savings allocation, and simulate real-life uncertainty like job loss.
""")

with st.expander("📘 Strategy Descriptions", expanded=True):
    st.markdown("""
    - **Strategy A**: Aggressive loan repayment. 100% of savings go to loan until fully repaid, then switch to investment.
    - **Strategy B**: Balanced approach. A fixed % of savings is invested, the rest goes toward early loan repayment.
    - **Strategy C**: Investment-first. During moratorium, invest all savings. After that, split between loan and investment.
    - **Strategy D**: Delayed aggressive repayment. Invest all savings during moratorium, then aggressively repay loan.
    """)

with st.form("user_inputs"):
    st.markdown("### 📥 Enter Your Inputs")
    col1, col2 = st.columns(2)
    with col1:
        gross_salary = st.number_input("Gross Annual Salary (USD)", value=90000, help="Your pre-tax yearly salary expected from your job in the US.")
        us_tax_rate = st.slider("US Tax Rate (%)", 0, 50, 25, help="Federal, state, and other applicable taxes as a percentage of gross income.")
        monthly_expenses = st.number_input("Monthly Living Expenses (USD)", value=2000, help="Expected monthly spending excluding loan and investment.")
        loan_amount = st.number_input("Loan Amount (INR)", value=2000000, help="Total education loan taken in Indian Rupees.")
        interest_rate = st.number_input("Loan Interest Rate (%)", value=10.85, step=0.01, help="Annual interest rate on your education loan.")
        emi = st.number_input("Monthly EMI (INR)", value=25000, help="Fixed monthly repayment amount once moratorium ends.")
        moratorium = st.number_input("Moratorium Period (Months)", value=6, help="Months after graduation when EMI is not required.")
    with col2:
        loan_term = st.number_input("Total Loan Term (Months)", value=84, help="Full duration of loan repayment as per agreement.")
        invest_rate = st.number_input("Investment Return Rate (%)", value=12, help="Expected annual return on your investments.")
        indian_tax_rate = st.slider("Indian Tax Rate (%)", 0, 30, 10, help="Tax applicable on investment returns in India.")
        usd_inr = st.number_input("USD to INR Conversion Rate", value=83.0, help="Estimated exchange rate for converting salary to INR.")
        pct_invest = st.slider("% of Savings to Invest", 0, 100, 50, help="Portion of post-expense, post-tax savings to invest.")
        years = st.slider("Years to Simulate", 1, 20, 7, help="Number of years to project into the future.")
        strategy = st.selectbox("Select Strategy", ["A", "B", "C", "D"], help="Choose a strategy to simulate.")

    submitted = st.form_submit_button("Review Your Inputs")
    if submitted:
        user_inputs = {
            "Gross Annual Salary (USD)": gross_salary,
            "US Tax Rate (%)": us_tax_rate,
            "Monthly Living Expenses (USD)": monthly_expenses,
            "Loan Amount (INR)": loan_amount,
            "Loan Interest Rate (%)": interest_rate,
            "Monthly EMI (INR)": emi,
            "Moratorium Period (Months)": moratorium,
            "Total Loan Term (Months)": loan_term,
            "Investment Return Rate (%)": invest_rate,
            "Indian Tax Rate (%)": indian_tax_rate,
            "USD to INR Conversion Rate": usd_inr,
            "% of Savings to Invest": pct_invest,
            "Years to Simulate": years,
            "Strategy": strategy
        }
        st.session_state["user_inputs"] = user_inputs
        st.success("Inputs recorded. Now start the simulation below!")

# --- MAIN SIMULATION ---
if "user_inputs" in st.session_state:
    st.markdown("## 🚀 Run Strategy Simulation")
    if st.button("Start Simulation"):
        u = st.session_state.user_inputs
        user_input = UserInput(
            gross_annual_salary_usd=u["Gross Annual Salary (USD)"],
            us_tax_rate=u["US Tax Rate (%)"] / 100,
            monthly_expenses_usd=u["Monthly Living Expenses (USD)"],
            loan_amount_inr=u["Loan Amount (INR)"],
            interest_rate_loan=u["Loan Interest Rate (%)"],
            emi_inr=u["Monthly EMI (INR)"],
            moratorium_months=u["Moratorium Period (Months)"],
            loan_term_months=u["Total Loan Term (Months)"],
            investment_rate_annual=u["Investment Return Rate (%)"],
            indian_tax_rate=u["Indian Tax Rate (%)"],
            usd_to_inr_rate=u["USD to INR Conversion Rate"],
            percent_to_invest=u["% of Savings to Invest"],
            years_to_simulate=u["Years to Simulate"],
            strategy_type=u["Strategy"]
        )
        df = run_simulation(user_input)
        st.success("Simulation complete!")

        generate_summary(df, user_input)
        plot_simulation_results(df, user_input.emi_inr)

        with BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Simulation")
            st.download_button("Download Simulation Output (Excel)", buffer.getvalue(), "simulation_output.xlsx")

        store_simulation_run(user_input, df)

# --- OPTIMIZATION MODULE ---
if st.sidebar.button("📈 Optimize % to Invest"):
    st.subheader("💡 Optimization Results")
    if "user_inputs" in st.session_state:
        raw = st.session_state.user_inputs
        test_input = UserInput(
            gross_annual_salary_usd=raw["Gross Annual Salary (USD)"],
            us_tax_rate=raw["US Tax Rate (%)"] / 100,
            monthly_expenses_usd=raw["Monthly Living Expenses (USD)"],
            loan_amount_inr=raw["Loan Amount (INR)"],
            interest_rate_loan=raw["Loan Interest Rate (%)"],
            emi_inr=raw["Monthly EMI (INR)"],
            moratorium_months=raw["Moratorium Period (Months)"],
            loan_term_months=raw["Total Loan Term (Months)"],
            investment_rate_annual=raw["Investment Return Rate (%)"],
            indian_tax_rate=raw["Indian Tax Rate (%)"],
            usd_to_inr_rate=raw["USD to INR Conversion Rate"],
            percent_to_invest=raw["% of Savings to Invest"],
            years_to_simulate=raw["Years to Simulate"],
            strategy_type=raw["Strategy"]
        )

        opt_df = optimize_investment(test_input)
        chart = alt.Chart(opt_df).mark_line(point=True).encode(
            x=alt.X('% Invest'),
            y=alt.Y('Final Net Worth'),
            tooltip=['% Invest', 'Final Net Worth']
        ).properties(
            title='Final Net Worth vs % of Savings Invested',
            width=700, height=400
        ).interactive()
        st.altair_chart(chart, use_container_width=True)
        st.download_button("Download Optimization Results (CSV)", opt_df.to_csv(index=False), "optimization_output.csv")
    else:
        st.warning("Please enter your input data first by starting a simulation.")

# --- SIMULATION HISTORY ---
if len(SIM_HISTORY) > 0:
    st.subheader("📜 Simulation History")
    st.dataframe(pd.DataFrame(SIM_HISTORY))
