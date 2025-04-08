import pandas as pd
import streamlit as st
import altair as alt
from simulation import UserInput, run_simulation, optimize_investment, SIM_HISTORY

# ... (your main app logic before this remains unchanged)

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
