import pandas as pd
import numpy as np
import random

def calculate_monthly_savings(gross_annual_salary_usd, us_tax_rate, monthly_expenses_usd):
    monthly_income_after_tax = (gross_annual_salary_usd / 12) * (1 - us_tax_rate)
    return monthly_income_after_tax - monthly_expenses_usd

def apply_tax(value, annual_tax_rate):
    return value * (1 - annual_tax_rate)

def simulate_strategy(params):
    months = params['years'] * 12
    # Job Loss Scenario Control
    job_loss_enabled = params.get("enable_job_loss", False)
    if job_loss_enabled:
        job_loss_start = params.get("job_loss_start", 0)
        job_loss_end = job_loss_start + params.get("job_loss_duration", 0)
        income_recovery = params.get("income_recovery_rate", 0) / 100
# Apply currency fluctuation
if params.get("enable_fx_drift"):
    fx_rate *= (1 + params["fx_drift_rate"] / 12)

# Apply inflation to expenses
if params.get("enable_inflation"):
    expenses *= (1 + params["inflation_rate"] / 12)

# Apply job loss
if job_loss_enabled and job_loss_start <= month <= job_loss_end:
    effective_salary = params["gross_annual_salary_usd"] * income_recovery
else:
    effective_salary = params["gross_annual_salary_usd"]

# Recalculate monthly savings
monthly_income = (effective_salary / 12) * (1 - params["us_tax_rate"])
monthly_savings_usd = monthly_income - expenses
monthly_savings_inr = monthly_savings_usd * fx_rate
    
    investment_balance = 0
    loan_balance = params['loan_amount_inr']
    emi = params['emi_inr']

    fx_rate = params["usd_to_inr_rate"]
    expenses = params["monthly_expenses_usd"]

    results = []

    for month in range(1, months + 1):
        row = {}
        invest_contrib = 0
        extra_payment = 0
        loan_payment = emi
        strategy = params['strategy']
        
        in_moratorium = month <= params['moratorium_months']

        # STRATEGY LOGIC
        if strategy == "A":  # Aggressive Repayment
            extra_payment = monthly_savings_inr
        elif strategy == "B":  # Balanced
            invest_contrib = monthly_savings_inr * (params['percent_to_invest'] / 100)
            extra_payment = monthly_savings_inr - invest_contrib
        elif strategy == "C":  # Invest first, then Balanced
            if in_moratorium:
                invest_contrib = monthly_savings_inr
            else:
                invest_contrib = monthly_savings_inr * (params['percent_to_invest'] / 100)
                extra_payment = monthly_savings_inr - invest_contrib
        elif strategy == "D":  # Invest first, then Aggressive
            if in_moratorium:
                invest_contrib = monthly_savings_inr
            else:
                extra_payment = monthly_savings_inr
        elif strategy == "E":  # Dynamic Allocation
            if loan_balance > (params['loan_amount_inr'] * (1 - params['threshold_pct'] / 100)):
                extra_payment = monthly_savings_inr
            else:
                invest_contrib = monthly_savings_inr
        elif strategy == "F":  # Risk-Aware Allocation
            risk_factor = 0.6 if params['risk_type'] == "Job Security" else 0.4
            invest_contrib = monthly_savings_inr * risk_factor
            extra_payment = monthly_savings_inr - invest_contrib
        elif strategy == "G":  # Random Split Simulation
            split = random.uniform(0, 1)
            invest_contrib = monthly_savings_inr * split
            extra_payment = monthly_savings_inr - invest_contrib

        # Apply payments
        interest_payment = loan_balance * (params['interest_rate_loan'] / 12)
        principal_payment = max(0, extra_payment + emi - interest_payment)
        loan_balance = max(0, loan_balance - principal_payment)
        investment_balance = investment_balance * (1 + params['investment_rate_annual'] / 12) + invest_contrib
        net_worth = investment_balance - loan_balance

        row['Month'] = month
        row['Loan Balance'] = loan_balance
        row['Investment Balance'] = investment_balance
        row['Net Worth'] = net_worth
        row['EMI'] = emi
        row['Invested'] = invest_contrib
        row['Extra Loan Payment'] = extra_payment

        results.append(row)

    df = pd.DataFrame(results).set_index("Month")
    summary = {
        'final_net_worth': df['Net Worth'].iloc[-1],
        'final_loan_balance': df['Loan Balance'].iloc[-1],
        'final_investment_balance': df['Investment Balance'].iloc[-1],
        'months_to_clear_loan': (df['Loan Balance'] == 0).idxmax() if (df['Loan Balance'] == 0).any() else "Not Cleared"
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
    strategy = params.get("strategy", "B")
    if strategy not in ["B", "C"]:
        return pd.DataFrame()

    results = []
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

def compare_strategies(params, strategies):
    results = []

    for strategy_code in strategies:
        try:
            test_params = params.copy()
            test_params["strategy"] = strategy_code
            df, summary = simulate_strategy(test_params)
            results.append({
                "Strategy": strategy_code,
                "Final Net Worth": summary["final_net_worth"],
                "Loan Cleared In (Months)": summary["months_to_clear_loan"],
                "Final Investment Balance": summary["final_investment_balance"]
            })
        except Exception as e:
            print(f"❌ Failed to simulate strategy {strategy_code}: {e}")
            continue

    return pd.DataFrame(results)

