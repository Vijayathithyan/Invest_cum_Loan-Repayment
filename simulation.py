import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

class UserInput:
    def __init__(
        self, gross_annual_salary_usd, us_tax_rate, monthly_expenses_usd,
        loan_amount_inr, interest_rate_loan, emi_inr, moratorium_months,
        loan_term_months, investment_rate_annual, indian_tax_rate,
        usd_to_inr_rate, percent_to_invest, years_to_simulate, strategy_type
    ):
        self.gross_annual_salary_usd = gross_annual_salary_usd
        self.us_tax_rate = us_tax_rate
        self.monthly_expenses_usd = monthly_expenses_usd
        self.loan_amount_inr = loan_amount_inr
        self.interest_rate_loan = interest_rate_loan
        self.emi_inr = emi_inr
        self.moratorium_months = moratorium_months
        self.loan_term_months = loan_term_months
        self.investment_rate_annual = investment_rate_annual
        self.indian_tax_rate = indian_tax_rate
        self.usd_to_inr_rate = usd_to_inr_rate
        self.percent_to_invest = percent_to_invest
        self.years_to_simulate = years_to_simulate
        self.strategy_type = strategy_type

def run_simulation(user_input):
    months = user_input.years_to_simulate * 12
    df = pd.DataFrame(columns=["Month", "Loan Balance", "Investment Balance", "Net Worth", "Investment Return"])

    loan_balance = user_input.loan_amount_inr
    investment_balance = 0
    monthly_loan_interest = user_input.interest_rate_loan / 12 / 100
    monthly_investment_return = user_input.investment_rate_annual / 12 / 100
    monthly_savings_usd = (user_input.gross_annual_salary_usd / 12) * (1 - user_input.us_tax_rate) - user_input.monthly_expenses_usd
    monthly_savings_inr = monthly_savings_usd * user_input.usd_to_inr_rate
    invest_ratio = user_input.percent_to_invest / 100
    repay_ratio = 1 - invest_ratio

    for month in range(1, months + 1):
        loan_interest = loan_balance * monthly_loan_interest
        loan_balance += loan_interest

        if month > user_input.moratorium_months:
            loan_balance -= user_input.emi_inr

        if user_input.strategy_type == 'A':
            investment_contrib = 0
            repay_extra = monthly_savings_inr
        elif user_input.strategy_type == 'B':
            investment_contrib = monthly_savings_inr * invest_ratio
            repay_extra = monthly_savings_inr * repay_ratio
        elif user_input.strategy_type == 'C':
            if month <= user_input.moratorium_months:
                investment_contrib = monthly_savings_inr
                repay_extra = 0
            else:
                investment_contrib = monthly_savings_inr * invest_ratio
                repay_extra = monthly_savings_inr * repay_ratio
        elif user_input.strategy_type == 'D':
            if month <= user_input.moratorium_months:
                investment_contrib = monthly_savings_inr
                repay_extra = 0
            else:
                investment_contrib = 0
                repay_extra = monthly_savings_inr
        else:
            investment_contrib = 0
            repay_extra = 0

        loan_balance -= repay_extra
        investment_balance += investment_contrib
        returns = investment_balance * monthly_investment_return * (1 - user_input.indian_tax_rate / 100)
        investment_balance += returns

        df.loc[month] = [
            month,
            max(loan_balance, 0),
            investment_balance,
            investment_balance - max(loan_balance, 0),
            returns
        ]

    return df

def generate_summary(df, user_input):
    final = df.iloc[-1]
    breakeven_month = df[df["Net Worth"] > 0].first_valid_index()
    roi_month = df[df["Investment Return"] >= user_input.emi_inr].first_valid_index()

    st.write(f"📆 **Final Net Worth:** ₹{final['Net Worth']:,.0f}")
    st.write(f"📉 **Final Loan Balance:** ₹{final['Loan Balance']:,.0f}")
    st.write(f"📈 **Final Investment Balance:** ₹{final['Investment Balance']:,.0f}")
    if breakeven_month:
        st.write(f"✅ **Net worth turns positive in month {int(breakeven_month)}**")
    if roi_month:
        st.write(f"💸 **Investment returns start covering EMI from month {int(roi_month)}**")

def plot_simulation_results(df, emi):
    st.line_chart(df[["Loan Balance", "Investment Balance", "Net Worth"]])
