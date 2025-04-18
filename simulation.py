# simulation.py

import pandas as pd
import numpy as np
import random

def calculate_monthly_savings(gross_annual_salary_usd, us_tax_rate, monthly_expenses_usd):
    monthly_income_after_tax = (gross_annual_salary_usd / 12) * (1 - us_tax_rate)
    return monthly_income_after_tax - monthly_expenses_usd

def apply_tax(value, annual_tax_rate):
    return value * (1 - annual_tax_rate)

def simulate_strategy(params):
    months = params['years_to_simulate'] * 12
    results = []

    loan_balance = params['loan_amount_inr']
    investment_balance = 0
    emi = params['emi_inr']
    moratorium = params['moratorium_months']
    total_loan = params['loan_amount_inr']
    monthly_loan_rate = params['interest_rate_loan'] / 12
    monthly_invest_rate = params['investment_rate_annual'] / 12
    monthly_savings_usd = calculate_monthly_savings(
        params['gross_annual_salary_usd'], params['us_tax_rate'], params['monthly_expenses_usd']
    )
    monthly_savings_inr = monthly_savings_usd * params['usd_to_inr_rate']

    break_even_month = None
    emi_covered_month = None
    loan_repaid = False

    for month in range(1, months + 1):
        row = {}
        invest_contrib = 0
        extra_payment = 0
        loan_payment = 0
        is_moratorium = month <= moratorium

        if is_moratorium:
            loan_balance *= (1 + monthly_loan_rate)
            emi_payment = 0
        else:
            loan_balance *= (1 + monthly_loan_rate)
            emi_payment = min(loan_balance, emi)

            strategy = params['strategy']

            if strategy == 'A':
                extra_payment = min(loan_balance - emi_payment, monthly_savings_inr)

            elif strategy == 'B':
                invest_ratio = params.get('invest_ratio', 0.5)
                invest_contrib = monthly_savings_inr * invest_ratio
                extra_payment = min(loan_balance - emi_payment, monthly_savings_inr - invest_contrib)

            elif strategy == 'C':
                if is_moratorium:
                    invest_contrib = monthly_savings_inr
                else:
                    invest_ratio = params.get('invest_ratio', 0.5)
                    invest_contrib = monthly_savings_inr * invest_ratio
                    extra_payment = min(loan_balance - emi_payment, monthly_savings_inr - invest_contrib)

            elif strategy == 'D':
                if is_moratorium:
                    invest_contrib = monthly_savings_inr
                elif loan_balance > 0:
                    extra_payment = min(loan_balance - emi_payment, monthly_savings_inr)
                else:
                    invest_contrib = monthly_savings_inr

            elif strategy == 'E':
                repay_threshold = params.get('repay_threshold', 0.5)
                repaid_ratio = (total_loan - loan_balance) / total_loan
                if repaid_ratio < repay_threshold:
                    extra_payment = min(loan_balance - emi_payment, monthly_savings_inr)
                else:
                    invest_contrib = monthly_savings_inr

            elif strategy == 'F':
                risk_type = params.get('risk_type', 'job')
                if risk_type == 'job':
                    invest_ratio = params.get('job_security_prob', 1.0)
                else:
                    volatility = params.get('investment_volatility', 0.2)
                    invest_ratio = max(0.0, 1.0 - volatility)
                invest_contrib = monthly_savings_inr * invest_ratio
                extra_payment = min(loan_balance - emi_payment, monthly_savings_inr - invest_contrib)

            elif strategy == 'G':
                invest_ratio = random.uniform(0.0, 1.0)
                invest_contrib = monthly_savings_inr * invest_ratio
                extra_payment = min(loan_balance - emi_payment, monthly_savings_inr - invest_contrib)

            else:
                invest_contrib = monthly_savings_inr / 2
                extra_payment = monthly_savings_inr / 2

            loan_payment = emi_payment + extra_payment
            loan_balance -= loan_payment

        investment_balance *= (1 + monthly_invest_rate)
        investment_balance += invest_contrib

        investment_income = investment_balance * monthly_invest_rate
        investment_income_after_tax = apply_tax(investment_income, params['indian_tax_rate'])

        net_worth = investment_balance - loan_balance
        if break_even_month is None and net_worth >= 0:
            break_even_month = month
        if emi_covered_month is None and investment_income_after_tax >= emi:
            emi_covered_month = month
        if not loan_repaid and loan_balance <= 0:
            loan_repaid = True

        row['Month'] = month
        row['Opening Loan Balance'] = loan_balance + loan_payment
        row['Loan Payment (INR)'] = loan_payment if not is_moratorium else 0
        row['Remaining Loan Balance'] = loan_balance
        row['Investment Contribution (INR)'] = invest_contrib
        row['Investment Income (INR)'] = investment_income
        row['Investment Income after Tax (INR)'] = investment_income_after_tax
        row['Total Investment (INR)'] = investment_balance
        row['Loan Payment (USD)'] = loan_payment / params['usd_to_inr_rate'] if loan_payment > 0 else 0
        row['Total Investment (USD)'] = investment_balance / params['usd_to_inr_rate']
        row['Net Worth (INR)'] = net_worth

        results.append(row)

        if loan_balance <= 0:
            loan_balance = 0

    df = pd.DataFrame(results).set_index('Month')
    summary = {
        'final_net_worth': net_worth,
        'loan_cleared_month': break_even_month,
        'investment_covers_emi_month': emi_covered_month,
        'loan_repaid': loan_repaid
    }

    return df, summary

def simulate_multiple_runs(params, runs=100):
    results = []
    for i in range(runs):
        run_params = params.copy()
        run_params['strategy'] = 'G'  # force strategy G for all runs
        df, summary = simulate_strategy(run_params)
        results.append({
            'Run': i + 1,
            'Final Net Worth (INR)': summary['final_net_worth']
        })
    return pd.DataFrame(results)
def optimize_investment_split(params, step=5):
    """
    Simulate strategies B or C over different investment % splits (0% to 100%) 
    to find the allocation that maximizes final net worth.
    """
    results = []
    strategy = params.get("strategy", "B")

    if strategy not in ["B", "C"]:
        return pd.DataFrame()  # Only optimize for B or C

    for invest_pct in range(0, 101, step):
        test_params = params.copy()
        test_params["percent_to_invest"] = invest_pct
        test_params["strategy"] = strategy
        df, summary = simulate_strategy(test_params)
        results.append({
            "Investment %": invest_pct,
            "Final Net Worth": summary["final_net_worth"]
        })

    return pd.DataFrame(results)

