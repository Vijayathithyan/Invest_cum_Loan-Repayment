import streamlit as st
import pandas as pd
from simulation import UserInput, run_simulation, plot_simulation_results, generate_summary

st.set_page_config(page_title="Investment & Loan Strategy Simulator", layout="centered")
st.title("💸 Investment-Cum-Loan Repayment Simulator")

# Initialize session state for form submission
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Define the form
with st.form("input_form"):
    with st.expander("💼 Salary & Expense Info", expanded=True):
        gross_salary = st.number_input("Gross Annual Salary (USD)", value=90000, help="Your pre-tax yearly salary expected from your job in the US.")
        us_tax = st.slider("US Tax Rate (%)", 10, 40, 25, help="Estimated total tax rate (federal + state) applied to your US salary.")
        expenses = st.number_input("Monthly Living Expenses (USD)", value=2000.0, help="Your monthly personal expenses while living in the US (excluding taxes).")
        fx_rate = st.number_input("USD to INR Conversion Rate", value=83.5, help="Assumed currency conversion rate from USD to INR.")

    with st.expander("🏦 Loan Details", expanded=True):
        loan_amt = st.number_input("Education Loan Amount (INR)", value=2500000, help="Total loan amount you borrowed in India, in INR.")
        interest_rate = st.number_input("Loan Interest Rate (%)", value=10.85, step=0.01, format="%.2f", help="Annual interest rate charged by the bank on your loan.")
        emi = st.number_input("Monthly EMI (INR)", value=27000, help="Minimum monthly loan payment (EMI) as per the bank schedule.")
        moratorium = st.slider("Moratorium Period (Months)", 0, 24, 6, help="Months after graduation during which you're not required to repay the loan.")
        loan_term = st.selectbox("Loan Duration (Months)", [60, 84, 120, 180, 240], help="Total repayment period as per your loan agreement.")

    with st.expander("📈 Investment Details", expanded=True):
        invest_rate = st.number_input("Investment Return Rate (%)", value=12.0, step=0.1, format="%.2f", help="Estimated annual return percentage on your investments.")
        tax_rate = st.slider("Indian Tax Rate (%)", 0, 30, 15, help="Tax rate in India applied to gains from your investments.")

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
        strategy = st.selectbox("Choose a Strategy", ['A', 'B', 'C', 'D'], index=1)
        invest_percent = st.slider("Percent of Savings to Invest (%)", 0, 100, 60, help="Out of your monthly savings, how much (%) you want to allocate to investments.")

    with st.expander("⚙️ Simulation Settings", expanded=True):
        sim_years = st.slider("Number of Years to Simulate", 1, 30, 10, help="Time horizon for the simulation in years after graduation.")

    # Form submission
    submitted = st.form_submit_button("Review Your Inputs")
    if submitted:
        st.session_state.form_submitted = True
        # Store inputs in session state
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

# After form submission, provide download option and simulation
if st.session_state.form_submitted:
    st.subheader("📥 Download Your Input Data")
    input_data = pd.DataFrame([st.session_state.user_inputs])
    csv_data = input_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Input Data as CSV",
        data=csv_data,
        file_name='user_input_data.csv',
        mime='text/csv'
    )

    # Start Simulation
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

        df = run_simulation(user_input)

        st.markdown("## 📈 Simulation Summary")
        generate_summary(df, user_input)

        st.markdown("## 📊 Visualization")
        plot_simulation_results(df, user_input.emi_inr)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Simulation Output (CSV)", csv, "simulation_output.csv")

        df.to_excel("simulation_output.xlsx", index=False)
        with open("simulation_output.xlsx", "rb") as f:
            st.download_button("Download Simulation Output (Excel)", f, "simulation_output.xlsx")
        

st.markdown("---")
st.header("🧠 Optimize Your Investment Strategy")

if st.button("🔍 Optimize % to Invest"):
    optimize_results = []

    for pct in range(0, 105, 5):  # 0 to 100 by 5%
        test_input = UserInput(
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
            percent_to_invest=pct,
            years_to_simulate=st.session_state.user_inputs["Number of Years to Simulate"],
            strategy_type=st.session_state.user_inputs["Chosen Strategy"]
        )

        df_opt = run_simulation(test_input)
        final_net_worth = df_opt.iloc[-1]["Net Worth"]
        optimize_results.append({"% Invest": pct, "Net Worth": final_net_worth})

    opt_df = pd.DataFrame(optimize_results)

    best_row = opt_df.loc[opt_df["Net Worth"].idxmax()]
    best_pct = best_row["% Invest"]
    best_value = best_row["Net Worth"]

    st.success(f"💡 Best % to Invest: **{best_pct}%** — Final Net Worth: ₹{best_value:,.0f}")
    st.line_chart(opt_df.set_index("% Invest"))

    csv = opt_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Optimization Results (CSV)", csv, "optimization_output.csv")
