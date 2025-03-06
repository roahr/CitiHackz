import numpy as np
import pandas as pd
import random
from scipy.stats import norm
import matplotlib.pyplot as plt
import seaborn as sns
from functools import lru_cache
from typing import List, Dict, Any, Tuple, Optional

def generate_random_business_data(n: int = 10) -> pd.DataFrame:
    """
    Generates random dataset for businesses with improved type hinting and performance.
    
    Args:
        n: Number of businesses to generate data for
        
    Returns:
        DataFrame containing random business data
    """
    # Use numpy vectorization for better performance
    business_ids = np.arange(1, n + 1)
    initial_investments = np.random.randint(500_000, 5_000_000, size=n)
    revenue_growth_rates = np.round(np.random.uniform(5, 20, size=n), 2)
    fixed_costs = np.random.randint(100_000, 1_000_000, size=n)
    variable_costs = np.random.randint(50_000, 500_000, size=n)
    
    # Generate categorical data
    volatility_options = ["Low", "Moderate", "High"]
    risk_options = ["Low", "Medium", "High"]
    expansion_options = ["Yes", "No"]
    
    market_volatility = np.random.choice(volatility_options, size=n)
    risk_factors = np.random.choice(risk_options, size=n)
    funding_rounds = np.random.randint(0, 5, size=n)
    expansion_plans = np.random.choice(expansion_options, size=n)
    credit_scores = np.random.randint(600, 850, size=n)
    
    # Create DataFrame directly from dict for better performance
    data = {
        "Business ID": business_ids,
        "Initial Investment": initial_investments,
        "Revenue Growth (%)": revenue_growth_rates,
        "Fixed Costs": fixed_costs,
        "Variable Costs": variable_costs,
        "Market Volatility": market_volatility,
        "Risk Factors": risk_factors, 
        "Funding Rounds": funding_rounds,
        "Expansion Plans": expansion_plans,
        "Credit Score": credit_scores
    }
    
    return pd.DataFrame(data)

@lru_cache(maxsize=32)
def get_risk_modifier(risk_level: str) -> float:
    """
    Returns a risk modifier based on the risk level.
    Uses caching for repeated calls with the same risk level.
    
    Args:
        risk_level: Risk level (Low, Medium, High)
        
    Returns:
        Risk modifier as a float
    """
    risk_modifiers = {
        "Low": 0.8,
        "Medium": 1.0,
        "High": 1.2
    }
    return risk_modifiers.get(risk_level, 1.0)

@lru_cache(maxsize=32)
def get_volatility_scale(volatility: str) -> float:
    """
    Returns a scale factor based on market volatility.
    Uses caching for repeated calls with the same volatility.
    
    Args:
        volatility: Market volatility level (Low, Moderate, High)
        
    Returns:
        Volatility scale factor as a float
    """
    volatility_scales = {
        "Low": 3.0,
        "Moderate": 5.0,
        "High": 8.0
    }
    return volatility_scales.get(volatility, 5.0)

def monte_carlo_simulation(
    business_data: pd.DataFrame, 
    iterations: int = 10000,
    years_projected: int = 5
) -> Tuple[List[float], Dict[str, Any]]:
    """
    Performs Monte Carlo Simulation on business revenue with improved modeling.
    
    Args:
        business_data: DataFrame containing business data
        iterations: Number of Monte Carlo iterations
        years_projected: Number of years to project into the future
        
    Returns:
        Tuple containing:
            - List of projected profits across all iterations
            - Dictionary with additional simulation metrics
    """
    # Pre-allocate arrays for better performance
    num_businesses = len(business_data)
    all_profits = np.zeros(iterations)
    yearly_profits = {f"Year {y+1}": np.zeros(iterations) for y in range(years_projected)}
    profitable_iterations = 0
    
    # Prepare business data for vectorized operations
    initial_investments = business_data["Initial Investment"].values
    base_growth_rates = business_data["Revenue Growth (%)"].values / 100
    fixed_costs = business_data["Fixed Costs"].values
    variable_costs = business_data["Variable Costs"].values
    
    # Get risk and volatility modifiers
    risk_modifiers = np.array([get_risk_modifier(r) for r in business_data["Risk Factors"]])
    volatility_scales = np.array([get_volatility_scale(v) for v in business_data["Market Volatility"]])
    
    for i in range(iterations):
        # Initialize year 0 revenue
        revenue = initial_investments.copy()
        total_profit = 0
        
        for year in range(years_projected):
            # Generate random growth rates based on risk and volatility
            growth_variations = norm.rvs(
                loc=base_growth_rates * risk_modifiers,
                scale=volatility_scales / 100,
                size=num_businesses
            )
            
            # Calculate new revenue based on growth
            revenue = revenue * (1 + growth_variations)
            
            # Calculate costs with some random variation
            cost_variation = np.random.uniform(0.95, 1.05, size=num_businesses)
            current_costs = (fixed_costs + variable_costs * cost_variation)
            
            # Calculate profits
            year_profits = revenue - current_costs
            yearly_profit = np.sum(year_profits)
            yearly_profits[f"Year {year+1}"][i] = yearly_profit
            
            # Add to total profit (weighted less for later years to account for time value)
            discount_factor = 1 / (1.05 ** year)  # Simple discount factor
            total_profit += yearly_profit * discount_factor
        
        all_profits[i] = total_profit
        if total_profit > 0:
            profitable_iterations += 1
    
    # Calculate additional metrics
    metrics = {
        "mean_profit": np.mean(all_profits),
        "median_profit": np.median(all_profits),
        "std_dev": np.std(all_profits),
        "probability_profitable": profitable_iterations / iterations * 100,
        "yearly_projections": {year: np.mean(profits) for year, profits in yearly_profits.items()},
        "percentiles": {
            "p10": np.percentile(all_profits, 10),
            "p25": np.percentile(all_profits, 25),
            "p50": np.percentile(all_profits, 50),
            "p75": np.percentile(all_profits, 75),
            "p90": np.percentile(all_profits, 90)
        }
    }
    
    return all_profits.tolist(), metrics

def visualize_results(profit_predictions: List[float], metrics: Optional[Dict] = None) -> plt.Figure:
    """
    Plots enhanced probability distribution of future profits.
    
    Args:
        profit_predictions: List of profit predictions from Monte Carlo simulation
        metrics: Optional dictionary of additional metrics to display
        
    Returns:
        Matplotlib figure object
    """
    # Set a more professional style
    sns.set_style("whitegrid")
    
    # Create figure with subplots
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot histogram with KDE
    sns.histplot(
        profit_predictions, 
        bins=50, 
        kde=True, 
        color='#1f77b4',
        alpha=0.7,
        ax=ax
    )
    
    # Add mean line
    mean_profit = np.mean(profit_predictions)
    ax.axvline(
        x=mean_profit, 
        color='red', 
        linestyle='--', 
        linewidth=2,
        label=f'Mean: ${mean_profit:,.2f}'
    )
    
    # Add percentile lines if metrics provided
    if metrics and 'percentiles' in metrics:
        ax.axvline(
            x=metrics['percentiles']['p10'], 
            color='orange', 
            linestyle=':', 
            linewidth=1.5,
            label=f'10th percentile: ${metrics["percentiles"]["p10"]:,.2f}'
        )
        ax.axvline(
            x=metrics['percentiles']['p90'], 
            color='green', 
            linestyle=':', 
            linewidth=1.5,
            label=f'90th percentile: ${metrics["percentiles"]["p90"]:,.2f}'
        )
    
    # Format axes
    ax.set_xlabel("Projected Profit ($)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title("Monte Carlo Simulation - Profit Distribution", fontsize=14, fontweight='bold')
    
    # Format ticks for better readability
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'${x:,.0f}'))
    
    # Add legend
    ax.legend(loc='upper right')
    
    # Tight layout
    plt.tight_layout()
    
    return fig