import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from simulation_backend import (
    generate_random_business_data, 
    monte_carlo_simulation, 
    visualize_results
)

# Set page configuration
st.set_page_config(
    page_title="Business Sustainability Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .info-text {
        color: #555;
        font-size: 0.9rem;
    }
    .success-text {
        color: #2E7D32;
        font-weight: bold;
    }
    .warning-text {
        color: #FF6F00;
        font-weight: bold;
    }
    .danger-text {
        color: #C62828;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown("<h1 class='main-header'>Business Sustainability & Profitability Analyzer</h1>", unsafe_allow_html=True)
st.markdown("""
This advanced tool helps you analyze business data, run Monte Carlo simulations, and 
forecast future profitability with confidence intervals. Generate random business data 
or upload your own to get started.
""")

# Sidebar for controls and settings
with st.sidebar:
    st.title("Simulation Controls")
    
    # Simulation parameters
    iterations = st.slider("Monte Carlo Iterations", 1000, 20000, 10000, 1000, 
                          help="Higher values provide more accurate results but take longer to compute")
    
    years = st.slider("Projection Years", 1, 10, 5, 1,
                    help="Number of years to project into the future")
    
    # Data generation settings
    if st.checkbox("Show Advanced Generation Settings", False):
        num_businesses = st.slider("Number of Businesses", 5, 50, 10, 
                                 help="Number of businesses to include in random generation")
        st.info("These settings only apply to randomly generated data.")
    else:
        num_businesses = 10
    
    # Export options
    st.subheader("Export Options")
    export_format = st.selectbox("Export Format", ["CSV", "Excel", "JSON"])
    
    if "business_data" in st.session_state:
        if st.button("Export Data"):
            # This would be implemented to provide downloadable data
            st.success(f"Data prepared for export in {export_format} format!")

# Main content area - using tabs for organization
tab1, tab2, tab3 = st.tabs(["Data Management", "Simulation Results", "Insights & Recommendations"])

with tab1:
    st.markdown("<h2 class='sub-header'>Business Data</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Generate Random Business Data", key="gen_data"):
            with st.spinner("Generating realistic business data..."):
                # Add slight delay to show the spinner
                time.sleep(0.5)
                business_data = generate_random_business_data(n=num_businesses)
                st.session_state["business_data"] = business_data
                st.session_state["data_source"] = "random"
                st.success(f"Successfully generated data for {num_businesses} businesses!")
    
    with col2:
        uploaded_file = st.file_uploader("Or upload your own data (CSV)", type=['csv'])
        if uploaded_file is not None:
            try:
                business_data = pd.read_csv(uploaded_file)
                required_columns = [
                    "Business ID", "Initial Investment", "Revenue Growth (%)", 
                    "Fixed Costs", "Variable Costs", "Market Volatility", 
                    "Risk Factors"
                ]
                
                missing_columns = [col for col in required_columns if col not in business_data.columns]
                
                if missing_columns:
                    st.error(f"Uploaded file is missing required columns: {', '.join(missing_columns)}")
                else:
                    st.session_state["business_data"] = business_data
                    st.session_state["data_source"] = "uploaded"
                    st.success("Data successfully uploaded and validated!")
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
    
    # Display the data if it exists
    if "business_data" in st.session_state:
        business_data = st.session_state["business_data"]
        
        # Show data summary statistics
        st.markdown("<h3>Data Overview</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("Number of Businesses", len(business_data))
        with col2:
            st.metric("Avg. Initial Investment", f"${business_data['Initial Investment'].mean():,.2f}")
        with col3:
            st.metric("Avg. Growth Rate", f"{business_data['Revenue Growth (%)'].mean():.2f}%")
        
        # Show data table with expanded features
        st.markdown("<h3>Business Data</h3>", unsafe_allow_html=True)
        
        # Format the dataframe for better display
        display_df = business_data.copy()
        for col in ['Initial Investment', 'Fixed Costs', 'Variable Costs']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")
        
        if 'Revenue Growth (%)' in display_df.columns:
            display_df['Revenue Growth (%)'] = display_df['Revenue Growth (%)'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(display_df, use_container_width=True)
        
        # Run simulation when data is available
        if st.button("Run Monte Carlo Simulation", type="primary"):
            st.session_state["run_simulation"] = True

with tab2:
    if "business_data" in st.session_state and st.session_state.get("run_simulation", False):
        st.markdown("<h2 class='sub-header'>Monte Carlo Simulation Results</h2>", unsafe_allow_html=True)
        
        business_data = st.session_state["business_data"]
        
        with st.spinner(f"Running {iterations} Monte Carlo simulations... This may take a moment."):
            # Run the enhanced simulation
            future_profits, metrics = monte_carlo_simulation(
                business_data, 
                iterations=iterations,
                years_projected=years
            )
            
            # Store results in session state
            st.session_state["simulation_results"] = {
                "profits": future_profits,
                "metrics": metrics
            }
        
        # Show key metrics
        st.markdown("<h3>Simulation Metrics</h3>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Mean Projected Profit", f"${metrics['mean_profit']:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Median Projected Profit", f"${metrics['median_profit']:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            profit_status = "success-text" if metrics['probability_profitable'] > 75 else "warning-text" if metrics['probability_profitable'] > 50 else "danger-text"
            st.markdown(f"<div class='metric-card'><h3>Probability of Profit</h3><p class='{profit_status}'>{metrics['probability_profitable']:.1f}%</p></div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Standard Deviation", f"${metrics['std_dev']:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display year-by-year projections
        st.markdown("<h3>Year-by-Year Projections</h3>", unsafe_allow_html=True)
        
        yearly_data = list(metrics['yearly_projections'].items())
        years = [item[0] for item in yearly_data]
        values = [item[1] for item in yearly_data]
        
        # Create a simple bar chart
        yearly_fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(years, values, color='#1f77b4')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            label_text = f"${height:,.0f}"
            ax.annotate(label_text,
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom',
                        rotation=0,
                        fontsize=8)
        
        ax.set_ylabel("Average Profit ($)")
        ax.set_title("Projected Average Profit by Year")
        plt.tight_layout()
        
        st.pyplot(yearly_fig)
        
        # Visualization of the probability distribution
        st.markdown("<h3>Profit Distribution</h3>", unsafe_allow_html=True)
        fig = visualize_results(future_profits, metrics)
        st.pyplot(fig)
        
        # Percentile table
        st.markdown("<h3>Profit Percentiles</h3>", unsafe_allow_html=True)
        
        percentile_df = pd.DataFrame({
            "Percentile": ["10th", "25th", "50th (Median)", "75th", "90th"],
            "Value": [
                f"${metrics['percentiles']['p10']:,.2f}",
                f"${metrics['percentiles']['p25']:,.2f}",
                f"${metrics['percentiles']['p50']:,.2f}",
                f"${metrics['percentiles']['p75']:,.2f}",
                f"${metrics['percentiles']['p90']:,.2f}"
            ],
            "Interpretation": [
                "Worst case scenario (10% chance of being below this value)",
                "Lower quartile",
                "Median outcome",
                "Upper quartile",
                "Best case scenario (10% chance of exceeding this value)"
            ]
        })
        
        st.table(percentile_df)
    else:
        st.info("Please generate or upload business data and run the simulation in the 'Data Management' tab to see results here.")

with tab3:
    if "simulation_results" in st.session_state:
        st.markdown("<h2 class='sub-header'>Business Insights & Recommendations</h2>", unsafe_allow_html=True)
        
        metrics = st.session_state["simulation_results"]["metrics"]
        
        # Overall assessment
        probability = metrics['probability_profitable']
        if probability > 75:
            risk_level = "Low Risk"
            risk_color = "success-text"
            recommendation = "The business model shows strong probability of success. Consider scaling operations and potentially seeking investment for expansion."
        elif probability > 50:
            risk_level = "Moderate Risk"
            risk_color = "warning-text"
            recommendation = "The business model shows reasonable probability of success, but with significant uncertainty. Consider optimizing costs and improving growth strategies before major expansion."
        else:
            risk_level = "High Risk"
            risk_color = "danger-text"
            recommendation = "The business model shows concerning risk levels. Consider restructuring costs, revisiting growth assumptions, or pivoting the business model."
        
        st.markdown(f"<h3>Overall Risk Assessment: <span class='{risk_color}'>{risk_level}</span></h3>", unsafe_allow_html=True)
        
        # Key insights
        st.markdown("<h3>Key Insights</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("<h4>Probability Analysis</h4>", unsafe_allow_html=True)
            st.markdown(f"• **Probability of profitability:** {probability:.1f}%")
            st.markdown(f"• **Mean projected profit:** ${metrics['mean_profit']:,.2f}")
            st.markdown(f"• **Profit range (10th to 90th percentile):** ${metrics['percentiles']['p10']:,.2f} to ${metrics['percentiles']['p90']:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("<h4>Growth Projection</h4>", unsafe_allow_html=True)
            
            yearly_projections = metrics['yearly_projections']
            first_year = list(yearly_projections.keys())[0]
            last_year = list(yearly_projections.keys())[-1]
            # Replace the problematic growth_rate calculation (around line 315) with this safer version:

            first_year_value = yearly_projections.get(first_year, 0)
            last_year_value = yearly_projections.get(last_year, 0)

            # Handle potential division by zero or negative values
            if first_year_value <= 0 or last_year_value <= 0:
                growth_rate = 0
            else:
                try:
                    # Calculate compound annual growth rate
                    growth_rate = ((last_year_value / first_year_value) ** (1/years) - 1) * 100
                    # In case of any calculation errors, default to 0
                    if not np.isfinite(growth_rate):
                        growth_rate = 0
                except Exception:
                    growth_rate = 0

            st.markdown(f"• **Compound annual growth rate:** {growth_rate:.2f}%")
            st.markdown(f"• **First year projection:** ${yearly_projections[first_year]:,.2f}")
            st.markdown(f"• **Final year projection:** ${yearly_projections[last_year]:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("<h3>Strategic Recommendations</h3>", unsafe_allow_html=True)
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(recommendation)
        
        # Add specific actionable recommendations
        st.markdown("<h4>Actionable Steps</h4>", unsafe_allow_html=True)
        
        if probability > 75:
            st.markdown("""
            1. **Expansion Strategy**: Consider geographical or product line expansion
            2. **Investment**: Prepare for additional funding rounds with this favorable projection data
            3. **Talent Acquisition**: Invest in hiring key talent to support growth
            4. **Risk Management**: Develop contingency plans for the 10% worst-case scenarios
            """)
        elif probability > 50:
            st.markdown("""
            1. **Cost Optimization**: Identify and reduce variable costs where possible
            2. **Growth Focus**: Target specific growth initiatives with highest ROI potential
            3. **Revenue Streams**: Diversify revenue streams to reduce volatility
            4. **Milestone Planning**: Set clear profitability milestones before major expansion
            """)
        else:
            st.markdown("""
            1. **Business Model Review**: Conduct comprehensive review of business model viability
            2. **Cost Restructuring**: Implement significant cost-cutting measures
            3. **Pivot Consideration**: Explore alternative business models or market segments
            4. **Funding Strategy**: Secure additional capital buffer to weather high uncertainty
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Please complete the simulation in previous tabs to see insights and recommendations here.")

