import streamlit as st
import pandas as pd
import plotly.express as px
from simulation import simulate_strategy, simulate_multiple_runs
from input_utils import user_inputs  # Assume you moved input form logic here

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

# 🌐 Collect all inputs once — globally reused
params = user_inputs()

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

# -------------------- STRATEGY G: MONTE CARLO --------------------
elif tabs == "📊 Strategy G (Monte Carlo)":
    st.header("🎲 Monte Carlo Simulation – Strategy G")
    st.markdown("""
Run Strategy G multiple times with randomized savings allocation to analyze the range of possible financial outcomes.
""")

    num_runs = st.slider("Number of Simulations", min_value=10, max_value=500, value=100, step=10)

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
- 📊 Majority outcomes fall between ₹{desc['25%']:,.0f} and ₹{desc['75%']:,.0f}

> Even with unpredictable monthly splits, this shows your likely outcome range.
""")

# -------------------- OPTIMIZATION --------------------
elif tabs == "🔍 Optimization Explorer":
    st.header("🔍 Optimization Explorer")
    st.markdown("""
This tool helps you find the **optimal savings split** between loan repayment and investment for strategies like **B** or **C**.
The goal is to **maximize your final net worth** at the end of the chosen simulation period.
""")
    st.info("🚧 Optimization logic coming soon!")

# -------------------- ABOUT --------------------
elif tabs == "ℹ️ About":
    st.header("👤 About the Author")
    st.markdown("""
**Vijayathithyan B B** is a graduate student at Virginia Commonwealth University, pursuing a Master’s in Decision Analytics with a concentration in Accounting Analytics. 

He combines experience in internal audit, financial analytics, and decision science to create data-driven tools that support real-life financial choices — especially for international students.

🔗 [LinkedIn Profile](https://www.linkedin.com/in/vijayathithyan-b-b-ba0b50244/)  
📂 [GitHub Repository](https://github.com/Vijayathithyan/Invest_cum_Loan-Repayment)
""")
