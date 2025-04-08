import pandas as pd
import streamlit as st
import altair as alt

class UserInput:
    def __init__(self, gross_annual_salary_usd, us_tax_rate, monthly_expenses_usd, 
                 loan_amount_inr, interest_rate_loan, emi_inr, moratorium_months,
                 loan_term_months, investment_rate_annual, indian_tax_rate,
                 usd_to_inr_rate, percent_to_invest, years_to_simulate, strategy_type):

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
    loan_fully_repaid = False

    for month in range(1, months + 1):
        loan_balance *= (1 + monthly_loan_interest)

        if month > user_input.moratorium_months and not loan_fully_repaid:
            loan_balance -= user_input.emi_inr

        investment_contrib = 0
        repay_extra = 0

        if user_input.strategy_type == 'A':
            if not loan_fully_repaid:
                repay_extra = monthly_savings_inr
            else:
                investment_contrib = monthly_savings_inr
        elif user_input.strategy_type == 'B':
            investment_contrib = monthly_savings_inr * invest_ratio
            repay_extra = monthly_savings_inr * repay_ratio
        elif user_input.strategy_type == 'C':
            if month <= user_input.moratorium_months:
                investment_contrib = monthly_savings_inr
            else:
                investment_contrib = monthly_savings_inr * invest_ratio
                repay_extra = monthly_savings_inr * repay_ratio
        elif user_input.strategy_type == 'D':
            if month <= user_input.moratorium_months:
                investment_contrib = monthly_savings_inr
            else:
                repay_extra = monthly_savings_inr

        if not loan_fully_repaid:
            loan_balance -= repay_extra
            if loan_balance <= 0:
                loan_balance = 0
                loan_fully_repaid = True

        investment_balance += investment_contrib
        returns = investment_balance * monthly_investment_return * (1 - user_input.indian_tax_rate / 100)
        investment_balance += returns
        net_worth = investment_balance - loan_balance

        df.loc[month - 1] = [month, loan_balance, investment_balance, net_worth, returns]

    return df

def run_simulation_with_jobloss(user_input, jobloss_prob_annual):
    import random
    months = user_input.years_to_simulate * 12
    df = pd.DataFrame(columns=["Month", "Loan Balance", "Investment Balance", "Net Worth", "Investment Return", "Job Loss"])

    loan_balance = user_input.loan_amount_inr
    investment_balance = 0
    monthly_loan_interest = user_input.interest_rate_loan / 12 / 100
    monthly_investment_return = user_input.investment_rate_annual / 12 / 100
    monthly_savings_usd = (user_input.gross_annual_salary_usd / 12) * (1 - user_input.us_tax_rate) - user_input.monthly_expenses_usd
    monthly_savings_inr = monthly_savings_usd * user_input.usd_to_inr_rate
    invest_ratio = user_input.percent_to_invest / 100
    repay_ratio = 1 - invest_ratio
    loan_fully_repaid = False
    job_lost = False
    monthly_jobloss_prob = jobloss_prob_annual / 12 / 100

    for month in range(1, months + 1):
        if not job_lost and random.random() < monthly_jobloss_prob:
            job_lost = True

        loan_balance *= (1 + monthly_loan_interest)

        if month > user_input.moratorium_months and not loan_fully_repaid and not job_lost:
            loan_balance -= user_input.emi_inr

        investment_contrib = 0
        repay_extra = 0

        if not job_lost:
            if user_input.strategy_type == 'A':
                if not loan_fully_repaid:
                    repay_extra = monthly_savings_inr
                else:
                    investment_contrib = monthly_savings_inr
            elif user_input.strategy_type == 'B':
                investment_contrib = monthly_savings_inr * invest_ratio
                repay_extra = monthly_savings_inr * repay_ratio
            elif user_input.strategy_type == 'C':
                if month <= user_input.moratorium_months:
                    investment_contrib = monthly_savings_inr
                else:
                    investment_contrib = monthly_savings_inr * invest_ratio
                    repay_extra = monthly_savings_inr * repay_ratio
            elif user_input.strategy_type == 'D':
                if month <= user_input.moratorium_months:
                    investment_contrib = monthly_savings_inr
                else:
                    repay_extra = monthly_savings_inr

        if not loan_fully_repaid:
            loan_balance -= repay_extra
            if loan_balance <= 0:
                loan_balance = 0
                loan_fully_repaid = True

        investment_balance += investment_contrib
        returns = investment_balance * monthly_investment_return * (1 - user_input.indian_tax_rate / 100)
        investment_balance += returns
        net_worth = investment_balance - loan_balance

        df.loc[month - 1] = [month, loan_balance, investment_balance, net_worth, returns, job_lost]

    return df

def plot_simulation_results(df, emi):
    df_long = df.melt(id_vars='Month', value_vars=['Loan Balance', 'Investment Balance', 'Net Worth'],
                      var_name='Metric', value_name='Amount')

    chart = alt.Chart(df_long).mark_line().encode(
        x=alt.X('Month', title='Month'),
        y=alt.Y('Amount', title='Amount (INR)'),
        color='Metric',
        tooltip=['Month', 'Metric', 'Amount']
    ).properties(
        title='📊 Loan, Investment & Net Worth Over Time',
        width=700,
        height=400
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

def generate_summary(df, user_input):
    final_row = df.iloc[-1]
    st.write(f"📍 Final Net Worth: ₹{final_row['Net Worth']:,.0f}")
    st.write(f"📈 Investment Balance: ₹{final_row['Investment Balance']:,.0f}")
    st.write(f"💸 Remaining Loan Balance: ₹{final_row['Loan Balance']:,.0f}")
