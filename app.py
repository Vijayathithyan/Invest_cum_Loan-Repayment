import streamlit as st
import pandas as pd
import plotly.express as px
from simulation import simulate_strategy, simulate_multiple_runs, optimize_investment_split

st.set_page_config(page_title="Investment vs Loan Repayment", layout="wide")

# Sidebar Navigation
st.sidebar.header("Navigation")
tabs = st.sidebar.radio("Go to:", [
    "🏠 Home", 
    "🏃‍♂️ Run Simulation", 
    "📈 Strategy Comparison", 
    "📊 Monte Carlo", 
    "🔍 Optimization Explorer", 
    "ℹ️ About"
])

# -------------------- CENTRALIZED USER INPUTS --------------------
st.sidebar.header("📥 Input Parameters")

st.sidebar.subheader("Simulation Settings")
years = st.sidebar.slider("Simulation Duration (Years)", 1, 30, 10)
grad_month = st.sidebar.selectbox("Expected Graduation Month", list(range(1, 13)))
moratorium = st.sidebar.slider("Moratorium Period (Months)", 0, 24, 6)

st.sidebar.subheader("Salary & Living")
salary = st.sidebar.number_input("Gross Annual Salary (USD)", min_value=0, value=90000)
tax_rate = st.sidebar.slider("US Tax Rate (%)", 0, 40, 25) / 100
expenses = st.sidebar.number_input("Monthly Expenses (USD)", min_value=0, value=2000)

st.sidebar.subheader("Loan Details")
loan_amt = st.sidebar.number_input("Loan Amount (INR)", min_value=0, value=2500000)
loan_rate = st.sidebar.number_input("Annual Loan Interest Rate (%)", min_value=0.0, value=11.0) / 100
emi = st.sidebar.number_input("Monthly EMI (INR)", min_value=0, value=27000)
loan_term = st.sidebar.slider("Loan Term (Months)", 12, 300, 120)

st.sidebar.subheader("Investment Info")
inv_rate = st.sidebar.slider("Annual Return Rate (%)", 0, 50, 12) / 100
tax_india = st.sidebar.slider("Indian Tax Rate (%)", 0, 30, 15) / 100
fx = st.sidebar.number_input("USD to INR Conversion Rate", min_value=0.0, value=83.5)

st.sidebar.subheader("Strategy Settings")
invest_pct = st.sidebar.slider("Investment % of Savings", 0, 100, 50)
threshold_pct = st.sidebar.slider("Loan Repayment Threshold % (Strategy E)", 0, 100, 50)
risk_type = st.sidebar.selectbox("Risk Driver (Strategy F)", ["Job Security", "Investment Volatility"])

st.sidebar.subheader("🧪 Scenario Engine")

enable_job_loss = st.sidebar.checkbox("📉 Simulate Job Loss", value=False)
job_loss_start = st.sidebar.slider("Month of Job Loss", 1, 60, 24) if enable_job_loss else None
job_loss_duration = st.sidebar.slider("Job Loss Duration (Months)", 1, 24, 6) if enable_job_loss else None
income_recovery_rate = st.sidebar.slider("Income Recovery After Job Loss (%)", 0, 100, 50) if enable_job_loss else None

enable_inflation = st.sidebar.checkbox("📈 Apply Inflation to Expenses", value=False)
inflation_rate = st.sidebar.slider("Annual Inflation Rate (%)", 0, 20, 6) / 100 if enable_inflation else 0

enable_fx_drift = st.sidebar.checkbox("🌍 Simulate Currency Drift (USD→INR)", value=False)
fx_drift_rate = st.sidebar.slider("Annual USD→INR Drift Rate (%)", -10, 10, -3) / 100 if enable_fx_drift else 0


params = {
    'years': years,
    'graduation_month': grad_month,
    'moratorium_months': moratorium,
    'gross_annual_salary_usd': salary,
    'us_tax_rate': tax_rate,
    'monthly_expenses_usd': expenses,
    'loan_amount_inr': loan_amt,
    'interest_rate_loan': loan_rate,
    'emi_inr': emi,
    'loan_term_months': loan_term,
    'investment_rate_annual': inv_rate,
    'indian_tax_rate': tax_india,
    'usd_to_inr_rate': fx,
    'percent_to_invest': invest_pct,
    'threshold_pct': threshold_pct,
    'risk_type': risk_type,
    'enable_job_loss': enable_job_loss,
    'job_loss_start': job_loss_start,
    'job_loss_duration': job_loss_duration,
    'income_recovery_rate': income_recovery_rate,
    'enable_inflation': enable_inflation,
    'inflation_rate': inflation_rate,
    'enable_fx_drift': enable_fx_drift,
    'fx_drift_rate': fx_drift_rate

}

# -------------------- HOME --------------------
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

    st.subheader("🧠 Strategy Selection")
    with st.expander("Click to View Strategy Descriptions"):
        st.markdown("""
- **🔴 Strategy A – Aggressive Repayment:** All savings go toward loan until it is cleared.
- **🟡 Strategy B – Balanced:** Split monthly savings between investment and repayment (default 50:50).
- **🔵 Strategy C – Invest First, Then Balanced:** Invest during moratorium, then apply Strategy B.
- **🔸 Strategy D – Invest First, Then Aggressive:** Invest during moratorium, then repay loan aggressively.
- **🟢 Strategy E – Dynamic Allocation:** Repay until X% loan cleared, then invest fully.
- **🟠 Strategy F – Risk-Aware:** Allocation varies monthly based on job security or investment volatility.
        """)

    st.subheader("🧪 Scenario Engine")
    st.markdown("""
The Scenario Engine simulates **real-world risks** like:

- 📉 **Job Loss**: Income drops temporarily during unemployment.
- 📈 **Inflation**: Monthly expenses increase gradually each year.
- 🌍 **Currency Fluctuation**: USD→INR rate drifts, impacting investment conversion.

These risks are optional but provide more realistic results. Enable them in the sidebar before running a simulation.
    """)

    if params.get("enable_job_loss") or params.get("enable_inflation") or params.get("enable_fx_drift"):
        st.warning("⚠️ Scenario Engine is active: Results may reflect job loss, inflation, or currency fluctuation risks.")

# -------------------- RUN SIMULATION --------------------
elif tabs == "🏃‍♂️ Run Simulation":
    st.header("📈 Run a Strategy Simulation")

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

    if st.button("Run Simulation"):
        df, summary = simulate_strategy(params)
        st.success("Simulation complete.")

        st.subheader("📈 Net Worth, Loan & Investment Over Time")
        fig = px.line(df, x=df.index, y=["Net Worth", "Loan Balance", "Investment Balance"])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Final Summary")
        summary_df = pd.DataFrame(summary, index=["Value"]).T
        summary_df.columns = ["Value"]
        def format_summary_value(index, value):
            if index in ['final_net_worth', 'final_loan_balance', 'final_investment_balance']:
                return f"₹{value:,.2f}"
            else:
                return f"{value:.0f}"
        st.dataframe(summary_df)


        st.subheader("📄 Detailed Monthly Table")
        st.dataframe(df)
        st.download_button("Download Results", data=df.to_csv().encode(), file_name="simulation_output.csv")
# -------------------- STRATEGY COMPARISION --------------------
elif tabs == "📈 Strategy Comparison":
    st.header("📊 Strategy Comparison")

    selected_strategies = st.multiselect(
        "Select Strategies to Compare",
        options=["A", "B", "C", "D", "E", "F"],
        default=["A", "B", "C"]
    )

    if st.button("Compare Strategies"):
        from simulation import compare_strategies
        df_compare = compare_strategies(params, selected_strategies)

        if df_compare.empty:
            st.warning("⚠️ No results could be generated. Please review your inputs or try fewer strategies.")
        else:
            st.subheader("📋 Summary Table")
            df_display = df_compare.copy()
            df_display["Final Net Worth"] = df_display["Final Net Worth"].apply(lambda x: f"₹{x:,.0f}")
            df_display["Final Investment Balance"] = df_display["Final Investment Balance"].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(df_display)

            st.subheader("📊 Net Worth by Strategy")
            fig = px.bar(df_compare, x="Strategy", y="Final Net Worth", text_auto=".2s")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📈 Loan Clearance Timeline")
            fig2 = px.bar(df_compare, x="Strategy", y="Loan Cleared In (Months)", text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)

            # ---------------- SMART RECOMMENDATION ----------------
            st.subheader("🧠 Smart Recommendation")

            try:
                df_numeric = df_compare.copy()
                df_numeric["Final Net Worth"] = pd.to_numeric(df_numeric["Final Net Worth"], errors="coerce")
                df_numeric["Final Investment Balance"] = pd.to_numeric(df_numeric["Final Investment Balance"], errors="coerce")

                # Best Net Worth Strategy
                best_net_worth_row = df_numeric.loc[df_numeric["Final Net Worth"].idxmax()]
                strategy_net = best_net_worth_row["Strategy"]
                net_value = best_net_worth_row["Final Net Worth"]

                # Fastest Loan Clearance Strategy
                loan_filtered = df_numeric[df_numeric["Loan Cleared In (Months)"] != "Not Cleared"]
                if not loan_filtered.empty:
                    loan_filtered["Loan Cleared In (Months)"] = pd.to_numeric(loan_filtered["Loan Cleared In (Months)"], errors="coerce")
                    fastest_loan_row = loan_filtered.loc[loan_filtered["Loan Cleared In (Months)"].idxmin()]
                    strategy_loan = fastest_loan_row["Strategy"]
                    loan_months = fastest_loan_row["Loan Cleared In (Months)"]
                else:
                    strategy_loan = "N/A"
                    loan_months = "No strategy cleared the loan"

                st.markdown(f"""
- 🥇 **Highest Net Worth**: Strategy **{strategy_net}** with ₹{net_value:,.0f}  
- ⏱️ **Fastest Loan Payoff**: Strategy **{strategy_loan}** in **{loan_months} months**
                """)

            except Exception as e:
                st.error(f"Smart recommendation failed: {e}")


# -------------------- STRATEGY G – MONTE CARLO --------------------
elif tabs == "📊 Monte Carlo":
    st.header("🎲 Monte Carlo Simulation")
    st.markdown("""
Run Strategy G multiple times with randomized savings allocation to analyze the range of possible financial outcomes.
""")

    num_runs = st.slider("Number of Simulations", min_value=10, max_value=500, value=100, step=10)
    params["strategy"] = "G"

    if st.button("Run Monte Carlo Simulation"):
        with st.spinner("Running simulations..."):
            df_runs = simulate_multiple_runs(params, runs=num_runs)

            st.success("Simulation complete!")

            st.subheader("📊 Net Worth Distribution")
            fig = px.histogram(df_runs, x='Final Net Worth (INR)', nbins=30)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📋 Summary Statistics")
            desc = df_runs['Final Net Worth (INR)'].describe()
            desc_formatted = desc.copy()
            desc_formatted = desc_formatted.apply(lambda x: f"₹{x:,.2f}" if isinstance(x, float) else x)
            desc_formatted['count'] = f"{int(desc['count'])}"
            st.write(desc_formatted)

            st.subheader("🧠 Interpretation")
            st.markdown(f"""
After running {num_runs} randomized simulations of Strategy G:

- 💰 **Average Net Worth:** ₹{desc['mean']:,.0f}
- 📉 **Min:** ₹{desc['min']:,.0f}, 📈 **Max:** ₹{desc['max']:,.0f}
- 📊 Most users land between ₹{desc['25%']:,.0f} and ₹{desc['75%']:,.0f}

> Even with unpredictable monthly splits, this shows your likely outcome range.
""")

# -------------------- OPTIMIZATION EXPLORER --------------------
elif tabs == "🔍 Optimization Explorer":
    st.header("🔍 Optimization Explorer")
    st.markdown("""
This tool helps you find the **optimal savings split** between loan repayment and investment for strategies like **B** or **C**.
""")

    strategy_opt = st.selectbox("Select a Strategy to Optimize", ["B - Balanced", "C - Invest First, Then Balanced"])
    granularity = st.slider("Search Step Size (in %)", min_value=1, max_value=25, value=5)
    params["strategy"] = strategy_opt[0]

    if st.button("Run Optimization"):
        with st.spinner("Running simulations..."):
            df_opt = optimize_investment_split(params, step=granularity)

            st.success("Optimization complete!")

            st.subheader("📈 Final Net Worth vs. Investment %")
            fig = px.line(df_opt, x="Investment %", y="Final Net Worth", markers=True)
            st.plotly_chart(fig, use_container_width=True)

            best_row = df_opt.loc[df_opt["Final Net Worth"].idxmax()]
            st.subheader("🏆 Best Allocation Recommendation")
            st.markdown(f"""
- 💸 **Optimal Investment %:** {int(best_row['Investment %'])}%
- 💰 **Final Net Worth:** ₹{best_row['Final Net Worth']:,.0f}
""")

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
