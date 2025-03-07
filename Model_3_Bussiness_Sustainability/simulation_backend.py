import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import datetime
from scipy.stats import multivariate_normal

def generate_company_data(industry_type="SaaS", size="startup", market_condition="normal"):
    """
    Generates realistic parameters based on industry benchmarks.
    
    Args:
        industry_type: Industry vertical ("SaaS", "Manufacturing", "Retail", "Biotech")
        size: Company size ("startup", "growth", "established")
        market_condition: Economic conditions ("boom", "normal", "recession")
        
    Returns:
        Dictionary with realistic company parameters
    """
    # Base parameters by industry
    industry_params = {
        "SaaS": {
            "revenue_growth_rate_mean": 25,  # 25% annual growth is typical
            "revenue_growth_volatility": 10,
            "variable_costs_percentage": 30,  # Typical gross margin of 70%
            "fixed_costs_base": 800000,  # Higher fixed costs (engineering, etc)
            "r_and_d_percentage": 15,
            "marketing_percentage": 15,
            "customer_retention_rate": 85,
            "market_growth_rate_mean": 20,
            "industry_cyclicality": 2,  # Less cyclical
            "market_volatility": 8,
        },
        "Manufacturing": {
            "revenue_growth_rate_mean": 8,
            "revenue_growth_volatility": 5,
            "variable_costs_percentage": 60,
            "fixed_costs_base": 2000000,
            "r_and_d_percentage": 5,
            "marketing_percentage": 8,
            "customer_retention_rate": 90,
            "market_growth_rate_mean": 6,
            "industry_cyclicality": 4,  # More cyclical
            "market_volatility": 6,
        },
        "Retail": {
            "revenue_growth_rate_mean": 10,
            "revenue_growth_volatility": 8,
            "variable_costs_percentage": 70,
            "fixed_costs_base": 1500000,
            "r_and_d_percentage": 2,
            "marketing_percentage": 12,
            "customer_retention_rate": 70,
            "market_growth_rate_mean": 5,
            "industry_cyclicality": 5,  # Highly cyclical
            "market_volatility": 9,
            "seasonality_factor": 0.25,  # High seasonality
        },
        "Biotech": {
            "revenue_growth_rate_mean": 15,
            "revenue_growth_volatility": 20,
            "variable_costs_percentage": 40,
            "fixed_costs_base": 4000000,
            "r_and_d_percentage": 25,
            "marketing_percentage": 10,
            "customer_retention_rate": 95,
            "market_growth_rate_mean": 12,
            "industry_cyclicality": 1,  # Less cyclical
            "market_volatility": 15,
            "seasonality_factor": 0.05,  # Low seasonality
        }
    }
    
    # Size-based adjustments
    size_adjustments = {
        "startup": {
            "initial_investment": (500000, 3000000),
            "initial_revenue": (100000, 2000000),
            "current_cash_reserves": (200000, 1000000),
            "debt_level": (0, 500000),
            "revenue_growth_rate_mean": 1.5,  # Higher growth
            "revenue_growth_volatility": 1.3,  # Higher volatility
            "market_share": (0.1, 2),
            "employee_count": (5, 50),
            "funding_rounds": (1, 4),
            "funding_probability": (0.3, 0.7),
            "funding_amount_mean": (500000, 3000000),
            "competitor_entry_probability": 1.3,  # Higher risk
            "supply_chain_disruption_probability": 1.2,
            "credit_score": (650, 750)
        },
        "growth": {
            "initial_investment": (2000000, 10000000),
            "initial_revenue": (1000000, 10000000),
            "current_cash_reserves": (500000, 3000000),
            "debt_level": (500000, 3000000),
            "revenue_growth_rate_mean": 1.0,  # Baseline growth
            "revenue_growth_volatility": 1.0,
            "market_share": (2, 8),
            "employee_count": (50, 200),
            "funding_rounds": (0, 2),
            "funding_probability": (0.2, 0.5),
            "funding_amount_mean": (2000000, 10000000),
            "competitor_entry_probability": 1.0,
            "supply_chain_disruption_probability": 1.0,
            "credit_score": (680, 780)
        },
        "established": {
            "initial_investment": (5000000, 50000000),
            "initial_revenue": (10000000, 100000000),
            "current_cash_reserves": (2000000, 20000000),
            "debt_level": (2000000, 20000000),
            "revenue_growth_rate_mean": 0.6,  # Lower growth
            "revenue_growth_volatility": 0.7,  # Lower volatility
            "market_share": (5, 25),
            "employee_count": (200, 1000),
            "funding_rounds": (0, 1),
            "funding_probability": (0.1, 0.3),
            "funding_amount_mean": (5000000, 30000000),
            "competitor_entry_probability": 0.8,  # Lower risk
            "supply_chain_disruption_probability": 0.9,
            "credit_score": (700, 820)
        }
    }
    
    # Market condition adjustments
    market_adjustments = {
        "boom": {
            "revenue_growth_rate_mean": 1.3,
            "market_growth_rate_mean": 1.4,
            "funding_probability": 1.3,
            "competitor_entry_probability": 1.2,  # More competitors in boom
            "cost_inflation_rate": 1.1
        },
        "normal": {
            "revenue_growth_rate_mean": 1.0,
            "market_growth_rate_mean": 1.0,
            "funding_probability": 1.0,
            "competitor_entry_probability": 1.0,
            "cost_inflation_rate": 1.0
        },
        "recession": {
            "revenue_growth_rate_mean": 0.6,
            "market_growth_rate_mean": 0.4,
            "funding_probability": 0.5,
            "competitor_entry_probability": 0.7,  # Fewer new competitors in recession
            "cost_inflation_rate": 0.8
        }
    }
    
    # Start with industry parameters
    if industry_type not in industry_params:
        industry_type = "SaaS"  # Default to SaaS if invalid industry
    
    company_data = industry_params[industry_type].copy()
    
    # Apply size-based parameter ranges
    size_params = size_adjustments[size]
    for key, value_range in size_params.items():
        if isinstance(value_range, tuple) and len(value_range) == 2:
            # Set random value within the range
            company_data[key] = np.random.uniform(value_range[0], value_range[1])
        elif isinstance(value_range, (int, float)):
            # Apply multiplier to existing parameter
            if key in company_data:
                company_data[key] = company_data[key] * value_range
    
    # Apply market condition adjustments
    market_params = market_adjustments[market_condition]
    for key, multiplier in market_params.items():
        if key in company_data:
            company_data[key] = company_data[key] * multiplier
    
    # Set fixed costs based on the base rate and company size
    employee_salary = 100000  # Average annual salary
    if "employee_count" in company_data and "fixed_costs_base" in company_data:
        company_data["fixed_costs"] = (company_data["fixed_costs_base"] + 
                                      (company_data["employee_count"] * employee_salary)) / 4  # Quarterly
    
    # Set risk factors based on industry and size
    if "competitor_entry_probability" not in company_data:
        company_data["competitor_entry_probability"] = 0.15
    if "competitor_impact" not in company_data:
        company_data["competitor_impact"] = np.random.uniform(5, 20)
    
    if "regulatory_change_probability" not in company_data:
        # Biotech has higher regulatory risk
        company_data["regulatory_change_probability"] = 0.25 if industry_type == "Biotech" else 0.1
    if "regulatory_impact" not in company_data:
        company_data["regulatory_impact"] = np.random.uniform(10, 30) if industry_type == "Biotech" else np.random.uniform(5, 15)
    
    if "supply_chain_disruption_probability" not in company_data:
        # Manufacturing and Retail have higher supply chain risk
        company_data["supply_chain_disruption_probability"] = 0.2 if industry_type in ["Manufacturing", "Retail"] else 0.1
    if "supply_chain_impact" not in company_data:
        company_data["supply_chain_impact"] = np.random.uniform(10, 25)
    
    # Ensure seasonality factor is set
    if "seasonality_factor" not in company_data:
        company_data["seasonality_factor"] = 0.1  # Default moderate seasonality
    
    # Set cost inflation rate if not already set
    if "cost_inflation_rate" not in company_data:
        company_data["cost_inflation_rate"] = np.random.uniform(1.5, 3.5)  # 1.5-3.5% annual inflation
        
    # Set market share growth based on company size and growth rate
    if "market_share_growth" not in company_data:
        if size == "startup":
            company_data["market_share_growth"] = company_data["revenue_growth_rate_mean"] / 5  # Aggressive share growth
        elif size == "growth":
            company_data["market_share_growth"] = company_data["revenue_growth_rate_mean"] / 8  # Moderate share growth
        else:
            company_data["market_share_growth"] = company_data["revenue_growth_rate_mean"] / 15  # Slow share growth
    
    # Ensure employee productivity is set
    if "employee_productivity" not in company_data:
        company_data["employee_productivity"] = np.random.uniform(0.8, 1.2)
    
    # Convert annual growth rates to quarterly
    for key in ["revenue_growth_rate_mean", "market_growth_rate_mean", "cost_inflation_rate"]:
        if key in company_data:
            # Convert annual rate to quarterly: (1+annual)^0.25 - 1
            company_data[key] = ((1 + company_data[key]/100) ** 0.25 - 1) * 100
    
    return company_data

def run_monte_carlo_simulation(company_data, periods=20, iterations=10000, scenario="neutral"):
    """
    Performs enhanced Monte Carlo Simulation with realistic business dynamics.
    
    Args:
        company_data: Dictionary with company parameters
        periods: Number of time periods to simulate (quarters)
        iterations: Number of simulation iterations
        scenario: "optimistic", "neutral", or "pessimistic"
        
    Returns:
        Dictionary with simulation results
    """
    # Adjust parameters based on scenario
    scenario_adjustments = {
        "optimistic": {
            "revenue_growth_rate_mean": 1.3,
            "market_growth_rate_mean": 1.2,
            "cost_inflation_rate": 0.8,
            "competitor_entry_probability": 0.7,
            "regulatory_change_probability": 0.7,
            "supply_chain_disruption_probability": 0.7,
            "customer_retention_rate": 1.1,
            "funding_probability": 1.3
        },
        "neutral": {
            "revenue_growth_rate_mean": 1.0,
            "market_growth_rate_mean": 1.0,
            "cost_inflation_rate": 1.0,
            "competitor_entry_probability": 1.0,
            "regulatory_change_probability": 1.0,
            "supply_chain_disruption_probability": 1.0,
            "customer_retention_rate": 1.0,
            "funding_probability": 1.0
        },
        "pessimistic": {
            "revenue_growth_rate_mean": 0.7,
            "market_growth_rate_mean": 0.7,
            "cost_inflation_rate": 1.2,
            "competitor_entry_probability": 1.3,
            "regulatory_change_probability": 1.3,
            "supply_chain_disruption_probability": 1.3,
            "customer_retention_rate": 0.9,
            "funding_probability": 0.6
        }
    }
    
    adj = scenario_adjustments[scenario]
    
    # Apply scenario adjustments
    adjusted_data = company_data.copy()
    for key in adj:
        if key in adjusted_data:
            adjusted_data[key] = adjusted_data[key] * adj[key]
    
    # Initialize arrays to store results
    revenue_projections = np.zeros((iterations, periods))
    profit_projections = np.zeros((iterations, periods))
    cash_flow_projections = np.zeros((iterations, periods))
    roi_projections = np.zeros((iterations, periods))
    market_share_projections = np.zeros((iterations, periods))
    bankruptcy_count = 0
    high_growth_count = 0
    
    # Calculate maximum market size based on initial parameters
    initial_market_size = adjusted_data["initial_revenue"] / (adjusted_data["market_share"] / 100)
    
    # Run simulations
    for i in range(iterations):
        # Initialize starting values
        revenue = adjusted_data["initial_revenue"]
        cash = adjusted_data["current_cash_reserves"]
        debt = adjusted_data["debt_level"]
        market_share = adjusted_data["market_share"]
        market_size = initial_market_size
        
        # Initialize S-curve parameters for revenue growth
        # Uses logistic growth curve that slows as market share increases
        max_market_share = min(80, market_share * 5)  # Cap at 80% or 5x current
        growth_midpoint = periods / 2  # Middle of the simulation period
        growth_steepness = 0.5  # Controls steepness of S-curve
        
        # Seasonality pattern (more realistic with industry-specific amplitude)
        seasonality = np.sin(np.linspace(0, 2*np.pi*periods/4, periods)) * adjusted_data["seasonality_factor"]
        
        # Risk event trackers
        competitor_entered = False
        competitor_entry_periods = []
        regulatory_change = False
        regulatory_change_periods = []
        supply_chain_disruptions = []
        
        # Initialize funding rounds
        funding_rounds_remaining = adjusted_data.get("funding_rounds", 0)
        last_funding_period = -4  # Ensure first funding round doesn't happen immediately
        
        # Economic cycle modeling - uses sine wave with random starting point
        econ_cycle_length = 16  # 4 years cycle (16 quarters)
        econ_cycle_start = np.random.uniform(0, econ_cycle_length)
        econ_cycle_amplitude = 0.2  # Economic cycle impact magnitude
        
        # Track customer metrics for realistic growth modeling
        customer_count = revenue / (1000 if "SaaS" in str(company_data) else 100)  # Average revenue per customer
        customer_acquisition_rate = 0.1  # Initial acquisition rate
        
        for t in range(periods):
            # Economic cycle effect (global factor affecting multiple parameters)
            econ_cycle_phase = (t + econ_cycle_start) % econ_cycle_length
            econ_cycle_factor = 1 + econ_cycle_amplitude * np.sin(2 * np.pi * econ_cycle_phase / econ_cycle_length)
            
            # Market growth with cyclicality and economic cycle
            market_cycle_factor = 1 + 0.2 * np.sin(t / (6 + adjusted_data["industry_cyclicality"]))
            market_growth = np.random.normal(
                adjusted_data["market_growth_rate_mean"] * market_cycle_factor * econ_cycle_factor / 100,
                adjusted_data["market_volatility"] / 100
            )
            
            # Update market size
            market_size = market_size * (1 + market_growth)
            
            # Risk Events - with persistent and correlated effects
            
            # Competitor entry (persistent effect)
            if np.random.random() < adjusted_data["competitor_entry_probability"] / periods and not competitor_entered:
                competitor_entered = True
                competitor_entry_periods.append(t)
                market_share *= (1 - adjusted_data["competitor_impact"] / 100)
                
                # A new competitor also increases marketing costs temporarily
                adjusted_data["marketing_percentage"] *= 1.2
            
            # Competitor effect decays slowly over time if company responds
            if competitor_entered and len(competitor_entry_periods) > 0:
                for entry_period in competitor_entry_periods:
                    periods_since_entry = t - entry_period
                    if periods_since_entry > 0 and periods_since_entry <= 4:  # Effect lasts 4 quarters
                        # Gradual recovery (stronger if better marketing)
                        recovery_factor = adjusted_data["marketing_percentage"] / 10 * (periods_since_entry / 4)
                        market_share *= (1 + recovery_factor / 100)
            
            # Regulatory change (persistent effect)
            if np.random.random() < adjusted_data["regulatory_change_probability"] / periods and not regulatory_change:
                regulatory_change = True
                regulatory_change_periods.append(t)
                revenue_impact = adjusted_data["regulatory_impact"] / 100
                revenue *= (1 - revenue_impact)
                
                # Regulatory changes often increase fixed costs
                adjusted_data["fixed_costs"] *= (1 + revenue_impact / 2)
            
            # Supply chain disruption (temporary effect)
            if np.random.random() < adjusted_data["supply_chain_disruption_probability"] / periods:
                supply_chain_disruptions.append(t)
                revenue *= (1 - adjusted_data["supply_chain_impact"] / 100)
                
                # Supply issues affect customer retention too
                adjusted_data["customer_retention_rate"] *= 0.95  # Temporary 5% drop
            
            # Supply chain effects recover over time
            if len(supply_chain_disruptions) > 0:
                for disruption_period in supply_chain_disruptions.copy():
                    if t - disruption_period >= 2:  # Effect lasts 2 quarters
                        supply_chain_disruptions.remove(disruption_period)
                        adjusted_data["customer_retention_rate"] /= 0.95  # Restore retention rate
            
            # S-curve growth modeling (logistic function)
            market_share_factor = market_share / max_market_share
            s_curve_dampening = 1 / (1 + np.exp(-growth_steepness * (t - growth_midpoint)))
            
            # Calculate growth rate with S-curve dynamics and market conditions
            base_growth_rate = adjusted_data["revenue_growth_rate_mean"] / 100
            market_saturation_factor = 1 - market_share_factor  # Slows growth as market share increases
            
            # Customer-based growth model
            retention_rate = adjusted_data["customer_retention_rate"] / 100
            existing_customers = customer_count * retention_rate
            
            # New customer acquisition slows as market saturates
            acquisition_rate = customer_acquisition_rate * market_saturation_factor * (1 + market_growth)
            new_customers = customer_count * acquisition_rate
            
            # Update customer count
            customer_count = existing_customers + new_customers
            
            # Convert to revenue growth
            customer_value_growth = np.random.normal(0.005, 0.002)  # Small increase in customer value over time
            growth_from_customers = (customer_count / (revenue / (1000 if "SaaS" in str(company_data) else 100)) - 1)
            
            # Combine factors for final growth rate
            growth_rate = (growth_from_customers + customer_value_growth) * econ_cycle_factor
            
            # Apply seasonality
            growth_rate = growth_rate + seasonality[t]
            
            # Update market share - constrained by realistic growth
            market_share_growth = adjusted_data["market_share_growth"] / 100 * market_saturation_factor
            market_share = min(max_market_share, market_share * (1 + market_share_growth))
            
            # Limit market share based on company size and performance
            if market_share > 50 and np.random.random() < 0.2:  # Anti-trust risk
                market_share *= 0.9  # Forced divestiture or increased competition
            
            # Update revenue - based on market size, market share, and growth factors
            revenue = revenue * (1 + growth_rate)
            
            # Calculate costs with realistic scaling
            
            # Fixed costs with step functions
            employee_growth = max(0, growth_rate * 0.7)  # Hire at 70% of revenue growth rate
            step_threshold = 3_000_000  # Revenue threshold for facility expansion
            if revenue > step_threshold and revenue / step_threshold > (t+1):
                facility_expansion = True
                fixed_costs = adjusted_data["fixed_costs"] * (1.2 + t * 0.01)  # 20% jump plus small increase per period
            else:
                facility_expansion = False
                fixed_costs = adjusted_data["fixed_costs"] * (1 + adjusted_data["cost_inflation_rate"] / 100) ** t
                fixed_costs *= (1 + employee_growth)  # Fixed costs grow with team size
            
            # Variable costs with economies of scale
            base_variable_rate = adjusted_data["variable_costs_percentage"] / 100
            scale_factor = max(0.8, 1 - (revenue / adjusted_data["initial_revenue"] - 1) * 0.05)  # Max 20% reduction
            variable_costs = revenue * base_variable_rate * scale_factor
            
            # Calculate R&D and marketing expenses
            r_and_d = revenue * (adjusted_data["r_and_d_percentage"] / 100)
            marketing = revenue * (adjusted_data["marketing_percentage"] / 100)
            
            # Calculate profit
            profit = revenue - fixed_costs - variable_costs - r_and_d - marketing
            
            # Check for funding round - more likely if growing fast or running out of cash
            funding = 0
            cash_runway = cash / abs(min(0, profit)) if profit < 0 else 8  # Quarters of runway remaining
            
            funding_trigger = (cash_runway < 3 or (growth_rate > 0.1 and market_share_factor < 0.5))
            if (funding_rounds_remaining > 0 and 
                t - last_funding_period >= 4 and  # At least 4 quarters since last round
                funding_trigger and
                np.random.random() < adjusted_data["funding_probability"] / periods):
                
                # Funding amount depends on company metrics
                valuation_multiple = 4 + growth_rate * 100  # Higher multiple for faster growth
                valuation = revenue * 4 * valuation_multiple
                
                # Funding amount is percentage of valuation
                funding_percent = np.random.uniform(0.1, 0.3)  # 10-30% of company
                funding = valuation * funding_percent
                
                funding_rounds_remaining -= 1
                last_funding_period = t
            
            # Update cash and debt with realistic debt management
            debt_interest = debt * 0.015  # 6% annual interest (1.5% quarterly)
            
            if profit > 0:
                # Pay more debt when profitable
                debt_payment = min(debt, max(debt * 0.05, profit * 0.2))  # Pay 5% of debt or 20% of profit
            else:
                # Minimum debt payment when unprofitable
                debt_payment = debt * 0.02  # 2% minimum payment
            
            debt = max(0, debt - debt_payment + debt_interest)
            
            cash_flow = profit - debt_payment + funding
            cash = cash + cash_flow
            
            # Realistic debt financing when cash is low
            if cash < 0:
                credit_score = adjusted_data.get("credit_score", 700)
                credit_score_factor = min(1.0, credit_score / 750)  # Better terms for higher credit
                
                if debt < revenue * 2 and credit_score > 650:  # Debt limit and minimum score
                    # Can get debt financing
                    interest_premium = (1.1 - credit_score_factor) + (debt / revenue) * 0.5  # Higher premium for more debt
                    new_debt = abs(cash) * (1.1 + interest_premium)  # Premium based on credit and debt load
                    debt += new_debt
                    cash = cash + new_debt * 0.9  # Only 90% of debt is usable cash (fees, etc.)
                else:
                    # Forced cost cutting
                    adjusted_data["marketing_percentage"] *= 0.8
                    adjusted_data["r_and_d_percentage"] *= 0.7
                    fixed_costs *= 0.9  # Layoffs and cost reduction
                    cash = 0  # Still barely at zero
            
            # Calculate ROI
            initial_investment = adjusted_data["initial_investment"]
            roi = (profit / (initial_investment / 4)) * 100 if initial_investment > 0 else 0  # Quarterly ROI
            
            # Store projections
            revenue_projections[i, t] = revenue
            profit_projections[i, t] = profit
            cash_flow_projections[i, t] = cash_flow
            roi_projections[i, t] = roi
            market_share_projections[i, t] = market_share
            
        # Count special cases
        if cash <= 0 and debt > adjusted_data["initial_investment"] * 1.5:
            bankruptcy_count += 1
        
        if revenue > adjusted_data["initial_revenue"] * 3:
            high_growth_count += 1
    
    # Calculate probability thresholds
    revenue_thresholds = {
        "low_10th": np.percentile(revenue_projections[:, -1], 10),
        "median": np.percentile(revenue_projections[:, -1], 50),
        "high_90th": np.percentile(revenue_projections[:, -1], 90)
    }
    
    profit_thresholds = {
        "low_10th": np.percentile(profit_projections[:, -1], 10),
        "median": np.percentile(profit_projections[:, -1], 50),
        "high_90th": np.percentile(profit_projections[:, -1], 90)
    }
    
    # Calculate average trajectories
    avg_revenue = np.mean(revenue_projections, axis=0)
    avg_profit = np.mean(profit_projections, axis=0)
    avg_cash_flow = np.mean(cash_flow_projections, axis=0)
    avg_roi = np.mean(roi_projections, axis=0)
    avg_market_share = np.mean(market_share_projections, axis=0)
    
    # Calculate standard deviations
    std_revenue = np.std(revenue_projections, axis=0)
    std_profit = np.std(profit_projections, axis=0)
    std_cash_flow = np.std(cash_flow_projections, axis=0)
    std_roi = np.std(roi_projections, axis=0)
    std_market_share = np.std(market_share_projections, axis=0)
    
    # Calculate profitability probability
    profitable_count = np.sum(profit_projections[:, -1] > 0)
    profitability_probability = profitable_count / iterations * 100
    
    # Calculate ROI thresholds
    roi_thresholds = {
        "negative": np.sum(roi_projections[:, -1] < 0) / iterations * 100,
        "0_to_10": np.sum((roi_projections[:, -1] >= 0) & (roi_projections[:, -1] < 10)) / iterations * 100,
        "10_to_20": np.sum((roi_projections[:, -1] >= 10) & (roi_projections[:, -1] < 20)) / iterations * 100,
        "20_plus": np.sum(roi_projections[:, -1] >= 20) / iterations * 100
    }
    
    return {
        "revenue_projections": revenue_projections,
        "profit_projections": profit_projections,
        "cash_flow_projections": cash_flow_projections,
        "roi_projections": roi_projections,
        "market_share_projections": market_share_projections,
        "avg_revenue": avg_revenue,
        "avg_profit": avg_profit,
        "avg_cash_flow": avg_cash_flow,
        "avg_roi": avg_roi,
        "avg_market_share": avg_market_share,
        "std_revenue": std_revenue,
        "std_profit": std_profit,
        "std_cash_flow": std_cash_flow,
        "std_roi": std_roi,
        "std_market_share": std_market_share,
        "revenue_thresholds": revenue_thresholds,
        "profit_thresholds": profit_thresholds,
        "bankruptcy_probability": bankruptcy_count / iterations * 100,
        "high_growth_probability": high_growth_count / iterations * 100,
        "profitability_probability": profitability_probability,
        "roi_thresholds": roi_thresholds
    }

def visualize_simulation_results(results, company_data, periods=20, show_confidence=True):
    """Creates visualization plots for the Monte Carlo simulation results"""
    # Time periods for x-axis
    time_periods = list(range(1, periods + 1))
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(15, 20))
    
    # Revenue projection plot
    ax1 = fig.add_subplot(411)
    ax1.plot(time_periods, results["avg_revenue"], 'b-', linewidth=2, label='Average Revenue')
    
    if show_confidence:
        ax1.fill_between(
            time_periods,
            results["avg_revenue"] - results["std_revenue"],
            results["avg_revenue"] + results["std_revenue"],
            color='blue', alpha=0.1
        )
        ax1.fill_between(
            time_periods,
            np.percentile(results["revenue_projections"], 10, axis=0),
            np.percentile(results["revenue_projections"], 90, axis=0),
            color='blue', alpha=0.2, label='10-90% Confidence'
        )
    
    # Plot threshold lines
    ax1.axhline(y=results["revenue_thresholds"]["low_10th"], color='r', linestyle='--', label='Low (10th percentile)')
    ax1.axhline(y=results["revenue_thresholds"]["high_90th"], color='g', linestyle='--', label='High (90th percentile)')
    
    ax1.set_title('Revenue Projection Over Time')
    ax1.set_xlabel('Quarters')
    ax1.set_ylabel('Revenue ($)')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # Profit projection plot
    ax2 = fig.add_subplot(412)
    ax2.plot(time_periods, results["avg_profit"], 'g-', linewidth=2, label='Average Profit')
    
    if show_confidence:
        ax2.fill_between(
            time_periods,
            results["avg_profit"] - results["std_profit"],
            results["avg_profit"] + results["std_profit"],
            color='green', alpha=0.1
        )
        ax2.fill_between(
            time_periods,
            np.percentile(results["profit_projections"], 10, axis=0),
            np.percentile(results["profit_projections"], 90, axis=0),
            color='green', alpha=0.2, label='10-90% Confidence'
        )
    
    # Plot threshold lines
    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3, label='Break Even')
    ax2.axhline(y=results["profit_thresholds"]["low_10th"], color='r', linestyle='--', label='Low (10th percentile)')
    ax2.axhline(y=results["profit_thresholds"]["high_90th"], color='g', linestyle='--', label='High (90th percentile)')
    
    ax2.set_title('Profit Projection Over Time')
    ax2.set_xlabel('Quarters')
    ax2.set_ylabel('Profit ($)')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # Cash Flow projection plot
    ax3 = fig.add_subplot(413)
    ax3.plot(time_periods, results["avg_cash_flow"], 'c-', linewidth=2, label='Average Cash Flow')
    
    if show_confidence:
        ax3.fill_between(
            time_periods,
            results["avg_cash_flow"] - results["std_cash_flow"],
            results["avg_cash_flow"] + results["std_cash_flow"],
            color='cyan', alpha=0.1
        )
        ax3.fill_between(
            time_periods,
            np.percentile(results["cash_flow_projections"], 10, axis=0),
            np.percentile(results["cash_flow_projections"], 90, axis=0),
            color='cyan', alpha=0.2, label='10-90% Confidence'
        )
    
    ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3, label='Break Even')
    ax3.set_title('Cash Flow Projection Over Time')
    ax3.set_xlabel('Quarters')
    ax3.set_ylabel('Cash Flow ($)')
    ax3.legend()
    ax3.grid(True, linestyle='--', alpha=0.7)
    
    # ROI projection plot
    ax4 = fig.add_subplot(414)
    ax4.plot(time_periods, results["avg_roi"], 'm-', linewidth=2, label='Average ROI')
    
    if show_confidence:
        ax4.fill_between(
            time_periods,
            results["avg_roi"] - results["std_roi"],
            results["avg_roi"] + results["std_roi"],
            color='magenta', alpha=0.1
        )
        ax4.fill_between(
            time_periods,
            np.percentile(results["roi_projections"], 10, axis=0),
            np.percentile(results["roi_projections"], 90, axis=0),
            color='magenta', alpha=0.2, label='10-90% Confidence'
        )
    
    ax4.axhline(y=0, color='k', linestyle='-', alpha=0.3, label='Break Even')
    ax4.set_title('ROI Projection Over Time')
    ax4.set_xlabel('Quarters')
    ax4.set_ylabel('ROI (%)')
    ax4.legend()
    ax4.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    return fig

def generate_summary_charts(results):
    """Creates summary charts for Monte Carlo simulation results"""
    
    # Create a figure with 2x2 subplots
    fig = plt.figure(figsize=(15, 12))
    
    # Profitability probability pie chart
    ax1 = fig.add_subplot(221)
    profitability_data = [
        results["profitability_probability"],
        100 - results["profitability_probability"]
    ]
    labels = [f'Profitable ({profitability_data[0]:.1f}%)', f'Unprofitable ({profitability_data[1]:.1f}%)']
    colors = ['#55A868', '#C44E52']
    ax1.pie(profitability_data, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Probability of Profitability')
    
    # ROI distribution histogram
    ax2 = fig.add_subplot(222)
    sns.histplot(results["roi_projections"][:, -1], bins=50, kde=True, ax=ax2, color='purple')
    ax2.axvline(x=0, color='r', linestyle='--')
    ax2.set_title('ROI Distribution (End of Period)')
    ax2.set_xlabel('ROI (%)')
    ax2.set_ylabel('Frequency')
    
    # ROI thresholds bar chart
    ax3 = fig.add_subplot(223)
    roi_categories = ['Negative', '0-10%', '10-20%', '20%+']
    roi_values = [
        results["roi_thresholds"]["negative"],
        results["roi_thresholds"]["0_to_10"],
        results["roi_thresholds"]["10_to_20"],
        results["roi_thresholds"]["20_plus"]
    ]
    
    bar_colors = ['#C44E52', '#F0E442', '#55A868', '#4C72B0']
    bars = ax3.bar(roi_categories, roi_values, color=bar_colors)
    
    # Add percentage labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom')
    
    ax3.set_title('ROI Probability Distribution')
    ax3.set_xlabel('ROI Categories')
    ax3.set_ylabel('Probability (%)')
    ax3.set_ylim(0, 100)
    
    # Risk chart
    ax4 = fig.add_subplot(224)
    risk_categories = ['Bankruptcy', 'High Growth']
    risk_values = [
        results["bankruptcy_probability"],
        results["high_growth_probability"]
    ]
    
    bar_colors = ['#C44E52', '#55A868']
    bars = ax4.bar(risk_categories, risk_values, color=bar_colors)
    
    # Add percentage labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom')
    
    ax4.set_title('Risk and Opportunity Assessment')
    ax4.set_xlabel('Scenarios')
    ax4.set_ylabel('Probability (%)')
    ax4.set_ylim(0, 100)
    
    plt.tight_layout()
    return fig

def format_as_currency(value):
    """Formats a number as currency"""
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:.2f}"

def generate_simulation_report(results, company_data, scenario="neutral", periods=20):
    """Generates a text report summarizing the Monte Carlo simulation results"""
    
    report = []
    report.append(f"# Business Performance Simulation Report\n")
    report.append(f"**Scenario:** {scenario.capitalize()}")
    report.append(f"**Simulation Date:** {datetime.datetime.now().strftime('%Y-%m-%d')}")
    report.append(f"**Projection Period:** {periods} quarters ({periods/4:.1f} years)\n")
    
    report.append("## Company Initial Parameters")
    report.append(f"- Initial Investment: {format_as_currency(company_data['initial_investment'])}")
    report.append(f"- Initial Revenue: {format_as_currency(company_data['initial_revenue'])}")
    report.append(f"- Cash Reserves: {format_as_currency(company_data['current_cash_reserves'])}")
    report.append(f"- Debt Level: {format_as_currency(company_data['debt_level'])}")
    report.append(f"- Revenue Growth Rate (Expected): {company_data['revenue_growth_rate_mean']:.1f}%")
    report.append(f"- Market Growth Rate (Expected): {company_data['market_growth_rate_mean']:.1f}%")
    report.append(f"- Fixed Costs: {format_as_currency(company_data['fixed_costs'])}")
    report.append(f"- Variable Costs: {company_data['variable_costs_percentage']:.1f}% of revenue\n")
    
    report.append("## Performance Projections")
    final_period = periods - 1
    report.append(f"### Revenue Projections (End of Period)")
    report.append(f"- Low estimate (10th percentile): {format_as_currency(results['revenue_thresholds']['low_10th'])}")
    report.append(f"- Median estimate (50th percentile): {format_as_currency(results['revenue_thresholds']['median'])}")
    report.append(f"- High estimate (90th percentile): {format_as_currency(results['revenue_thresholds']['high_90th'])}")
    report.append(f"- Growth multiple from initial: {results['avg_revenue'][final_period]/company_data['initial_revenue']:.2f}x\n")
    
    report.append(f"### Profit Projections (End of Period)")
    report.append(f"- Low estimate (10th percentile): {format_as_currency(results['profit_thresholds']['low_10th'])}")
    report.append(f"- Median estimate (50th percentile): {format_as_currency(results['profit_thresholds']['median'])}")
    report.append(f"- High estimate (90th percentile): {format_as_currency(results['profit_thresholds']['high_90th'])}")
    report.append(f"- Probability of being profitable: {results['profitability_probability']:.1f}%\n")
    
    report.append(f"### ROI Projections")
    report.append(f"- Average ROI (End of Period): {results['avg_roi'][final_period]:.2f}%")
    report.append(f"- ROI Distribution:")
    report.append(f"  - Negative ROI: {results['roi_thresholds']['negative']:.1f}%")
    report.append(f"  - 0-10% ROI: {results['roi_thresholds']['0_to_10']:.1f}%")
    report.append(f"  - 10-20% ROI: {results['roi_thresholds']['10_to_20']:.1f}%")
    report.append(f"  - 20%+ ROI: {results['roi_thresholds']['20_plus']:.1f}%\n")
    
    report.append("## Risk Assessment")
    report.append(f"- Bankruptcy Probability: {results['bankruptcy_probability']:.1f}%")
    report.append(f"- High Growth Probability: {results['high_growth_probability']:.1f}%")
    
    report.append("\n## Key Insights")
    
    # Generate dynamic insights based on results
    if results['profitability_probability'] >= 75:
        report.append("- The business shows strong probability of profitability across most scenarios.")
    elif results['profitability_probability'] >= 50:
        report.append("- The business shows moderate probability of profitability, but has significant risk.")
    else:
        report.append("- The business shows limited probability of profitability in its current configuration.")
    
    if results['bankruptcy_probability'] >= 25:
        report.append("- There is a significant risk of bankruptcy. Risk mitigation strategies are recommended.")
    elif results['bankruptcy_probability'] >= 10:
        report.append("- There is a moderate risk of bankruptcy. Conservative financial management is advised.")
    else:
        report.append("- The risk of bankruptcy is relatively low across most simulated scenarios.")
    
    if results['roi_thresholds']['20_plus'] >= 40:
        report.append("- The potential for high ROI (20%+) is strong, indicating good investment potential.")
    elif results['roi_thresholds']['negative'] >= 40:
        report.append("- The risk of negative ROI is high, suggesting reconsideration of the business model.")
    
    if results['avg_revenue'][final_period] >= company_data['initial_revenue'] * 2:
        report.append(f"- The business is projected to more than double in size over the analysis period.")
    
    return "\n".join(report)