import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

class UserInput:
    def __init__(self, initial_investment, monthly_contribution, loan_amount, loan_interest_rate, loan_term_years):
        self.initial_investment = initial_investment
        self.monthly_contribution = monthly_contribution
        self.loan_amount = loan_amount
        self.loan_interest_rate = loan_interest_rate / 100  # Convert percentage to decimal
        self.loan_term_years = loan_term_years

def run_simulation(user_input):
    months = user_input.loan_term_years * 12
    monthly_rate = user_input.loan_interest_rate / 12

    # Calculate monthly loan payment
    if monthly_rate > 0:
        monthly_payment = user_input.loan_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    else:
        monthly_payment = user_input.loan_amount / months if months > 0 else 0

    # Initialize DataFrame to store results
    df = pd.DataFrame(index=range(1, months + 1), columns=['Month', 'Investment Balance', 'Loan Balance', 'Net Worth'])
    df['Month'] = df.index

    investment_balance = user_input.initial_investment
    loan_balance = user_input.loan_amount

    for month in range(1, months + 1):
        # Update loan balance
        interest_payment = loan_balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        loan_balance -= principal_payment

        # Update investment balance
        investment_balance += user_input.monthly_contribution
        investment_balance *= (1 + monthly_rate)  # Assuming investment grows at the same rate as loan interest

        # Calculate net worth
        net_worth = investment_balance - loan_balance

        # Store results
        df.at[month, 'Investment Balance'] = investment_balance
        df.at[month, 'Loan Balance'] = loan_balance
        df.at[month, 'Net Worth'] = net_worth

    return df

def plot_simulation_results(df):
    plt.figure(figsize=(10, 6))
    plt.plot(df['Month'], df['Investment Balance'], label='Investment Balance', color='blue')
    plt.plot(df['Month'], df['Loan Balance'], label='Loan Balance', color='red')
    plt.plot(df['Month'], df['Net Worth'], label='Net Worth', color='green')
    plt.xlabel('Month')
    plt.ylabel('Amount ($)')
    plt.title('Investment and Loan Repayment Simulation')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

def generate_summary(df):
    final_month = df.iloc[-1]
    summary = {
        'Final Investment Balance': final_month['Investment Balance'],
        'Final Loan Balance': final_month['Loan Balance'],
        'Final Net Worth': final_month['Net Worth']
    }
    return summary
