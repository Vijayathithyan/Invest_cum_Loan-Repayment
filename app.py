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
    "📊 Strategy G (Monte Carlo)", 
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
    'risk_type': risk_type
}

# -------------------- HOME --------------------
if tabs == "🏠 Home":
    st.title("📊 Investment-Cum-Loan Repayment Simulator")
    st.markdown("""
This tool helps you make smarter financial decisions on repaying your loan versus investing your savings. 
Choose from multiple strategies, simulate outcomes over time, and optimize based on your goals.
""")

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
        st.write(summary)

        st.subheader("📄 Detailed Monthly Table")
        st.dataframe(df)
        st.download_button("Download Results", data=df.to_csv().encode(), file_name="simulation_output.csv")

# -------------------- STRATEGY G – MONTE CARLO --------------------
elif tabs == "📊 Strategy G (Monte Carlo)":
    st.header("🎲 Monte Carlo Simulation – Strategy G")
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

# -------------------- ABOUT --------------------
elif tabs == "ℹ️ About":
    st.header("👤 About the Author")
    st.markdown("""
**Vijayathithyan B B** is a graduate student at Virginia Commonwealth University, pursuing a Master’s in Decision Analytics with a concentration in Accounting Analytics.

He combines experience in internal audit, financial analytics, and decision science to create data-driven tools that support real-life financial choices — especially for international students.

🔗 [LinkedIn Profile](https://www.linkedin.com/in/vijayathithyan-b-b-ba0b50244/)  
📂 [GitHub Repository](https://github.com/Vijayathithyan/Invest_cum_Loan-Repayment)
""")
