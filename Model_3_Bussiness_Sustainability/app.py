import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
import base64
from io import BytesIO

# Import functions from backend module
# Assuming the backend code is in a file named "business_simulation.py"
from simulation_backend import generate_company_data, run_monte_carlo_simulation, visualize_simulation_results, generate_summary_charts, format_as_currency, generate_simulation_report

# Page configuration
st.set_page_config(
    page_title="Business Monte Carlo Simulator",
    page_icon="📊",
    layout="wide"
)

# CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .info-box {
        background-color: #093a60;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.3rem solid #3B82F6;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FEF2F2;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.3rem solid #EF4444;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #ECFDF5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.3rem solid #10B981;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def convert_fig_to_html(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

def create_plotly_revenue_projection(results, periods):
    time_periods = list(range(1, periods + 1))
    
    fig = go.Figure()
    
    # Average line
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=results["avg_revenue"],
            mode="lines",
            name="Average Revenue",
            line=dict(color="royalblue", width=3)
        )
    )
    
    # Add confidence intervals
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=np.percentile(results["revenue_projections"], 90, axis=0),
            mode="lines",
            name="90th Percentile",
            line=dict(color="green", width=1, dash="dash")
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=np.percentile(results["revenue_projections"], 10, axis=0),
            mode="lines",
            name="10th Percentile",
            line=dict(color="red", width=1, dash="dash"),
            fill="tonexty",
            fillcolor="rgba(65, 105, 225, 0.1)"
        )
    )
    
    fig.update_layout(
        title="Revenue Projection Over Time",
        xaxis_title="Quarters",
        yaxis_title="Revenue ($)",
        legend=dict(x=0.01, y=0.99),
        height=400
    )
    
    return fig

def create_plotly_metrics_chart(results, periods):
    time_periods = list(range(1, periods + 1))
    
    # Create subplots
    fig = make_subplots(rows=3, cols=1, 
                        subplot_titles=("Profit Projection", "Cash Flow Projection", "ROI Projection"),
                        vertical_spacing=0.15)
    
    # Add profit trace
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=results["avg_profit"],
            mode="lines",
            name="Average Profit",
            line=dict(color="green", width=3)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=np.percentile(results["profit_projections"], 90, axis=0),
            mode="lines",
            name="90th Percentile",
            line=dict(color="green", width=1, dash="dash"),
            showlegend=False
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=np.percentile(results["profit_projections"], 10, axis=0),
            mode="lines",
            name="10th Percentile",
            line=dict(color="red", width=1, dash="dash"),
            fill="tonexty",
            fillcolor="rgba(0, 128, 0, 0.1)",
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add cash flow trace
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=results["avg_cash_flow"],
            mode="lines",
            name="Average Cash Flow",
            line=dict(color="cyan", width=3),
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=np.percentile(results["cash_flow_projections"], 90, axis=0),
            mode="lines", 
            line=dict(color="green", width=1, dash="dash"),
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=np.percentile(results["cash_flow_projections"], 10, axis=0),
            mode="lines",
            line=dict(color="red", width=1, dash="dash"),
            fill="tonexty", 
            fillcolor="rgba(0, 255, 255, 0.1)",
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Add ROI trace
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=results["avg_roi"],
            mode="lines",
            name="Average ROI",
            line=dict(color="magenta", width=3),
            showlegend=False
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=np.percentile(results["roi_projections"], 90, axis=0),
            mode="lines",
            line=dict(color="green", width=1, dash="dash"),
            showlegend=False
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=time_periods,
            y=np.percentile(results["roi_projections"], 10, axis=0),
            mode="lines",
            line=dict(color="red", width=1, dash="dash"),
            fill="tonexty",
            fillcolor="rgba(255, 0, 255, 0.1)",
            showlegend=False
        ),
        row=3, col=1
    )
    
    # Break-even lines
    fig.add_hline(y=0, line=dict(color="black", width=1, dash="dash"), row=1, col=1)
    fig.add_hline(y=0, line=dict(color="black", width=1, dash="dash"), row=2, col=1)
    fig.add_hline(y=0, line=dict(color="black", width=1, dash="dash"), row=3, col=1)
    
    fig.update_xaxes(title_text="Quarters", row=3, col=1)
    fig.update_yaxes(title_text="Profit ($)", row=1, col=1)
    fig.update_yaxes(title_text="Cash Flow ($)", row=2, col=1)
    fig.update_yaxes(title_text="ROI (%)", row=3, col=1)
    
    fig.update_layout(height=900, margin=dict(t=100))
    
    return fig

def create_plotly_summary_charts(results):
    # Create 2x2 subplot
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Profitability Probability", "ROI Distribution", 
                         "ROI Probability Distribution", "Risk Assessment"),
        specs=[
            [{"type": "pie"}, {"type": "histogram"}],
            [{"type": "bar"}, {"type": "bar"}]
        ]
    )
    
    # Profitability pie chart
    profitability_data = [
        results["profitability_probability"],
        100 - results["profitability_probability"]
    ]
    labels = [f'Profitable ({profitability_data[0]:.1f}%)', 
              f'Unprofitable ({profitability_data[1]:.1f}%)']
    colors = ['#55A868', '#C44E52']
    
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=profitability_data,
            marker=dict(colors=colors),
            textinfo="label+percent",
            hole=0.4,
        ),
        row=1, col=1
    )
    
    # ROI distribution histogram
    fig.add_trace(
        go.Histogram(
            x=results["roi_projections"][:, -1],
            nbinsx=50,
            marker_color="purple",
            opacity=0.7
        ),
        row=1, col=2
    )
    
   # Add a shape instead of using add_vline
    fig.add_shape(
        type="line",
        x0=0, x1=0,
        y0=0, y1=1,
        yref="paper",
        line=dict(color="red", width=2, dash="dash"),
        row=1, col=2
    )
    
    # ROI thresholds bar chart
    roi_categories = ['Negative', '0-10%', '10-20%', '20%+']
    roi_values = [
        results["roi_thresholds"]["negative"],
        results["roi_thresholds"]["0_to_10"],
        results["roi_thresholds"]["10_to_20"],
        results["roi_thresholds"]["20_plus"]
    ]
    
    bar_colors = ['#C44E52', '#F0E442', '#55A868', '#4C72B0']
    
    fig.add_trace(
        go.Bar(
            x=roi_categories,
            y=roi_values,
            marker_color=bar_colors,
            text=[f"{v:.1f}%" for v in roi_values],
            textposition="outside"
        ),
        row=2, col=1
    )
    
    # Risk chart
    risk_categories = ['Bankruptcy', 'High Growth']
    risk_values = [
        results["bankruptcy_probability"],
        results["high_growth_probability"]
    ]
    
    risk_colors = ['#C44E52', '#55A868']
    
    fig.add_trace(
        go.Bar(
            x=risk_categories,
            y=risk_values,
            marker_color=risk_colors,
            text=[f"{v:.1f}%" for v in risk_values],
            textposition="outside"
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False
    )
    
    fig.update_xaxes(title_text="ROI Categories", row=2, col=1)
    fig.update_xaxes(title_text="Scenarios", row=2, col=2)
    fig.update_xaxes(title_text="ROI (%)", row=1, col=2)
    
    fig.update_yaxes(title_text="Probability (%)", row=2, col=1)
    fig.update_yaxes(title_text="Probability (%)", row=2, col=2)
    fig.update_yaxes(title_text="Frequency", row=1, col=2)
    
    fig.update_yaxes(range=[0, 100], row=2, col=1)
    fig.update_yaxes(range=[0, 100], row=2, col=2)
    
    return fig

# App main function
def main():
    # App header
    st.markdown('<div class="main-header">Business Monte Carlo Simulator</div>', unsafe_allow_html=True)
    
    # st.markdown("""
    # <div class="info-box">
    #     This application runs Monte Carlo simulations to predict business performance and analyze risks. 
    #     You can customize parameters, run simulations for different scenarios, 
    #     and visualize the results with interactive charts.
    # </div>
    # """, unsafe_allow_html=True)
    
    # Sidebar for input parameters
    with st.sidebar:
        st.markdown('<div class="section-header">Simulation Settings</div>', unsafe_allow_html=True)
        
        # Basic simulation settings
        periods = st.slider("Projection Periods (Quarters)", min_value=4, max_value=40, value=20, step=4)
        iterations = st.slider("Simulation Iterations", min_value=1000, max_value=20000, value=10000, step=1000)
        scenario = st.selectbox("Scenario", ["optimistic", "neutral", "pessimistic"])
        
        st.markdown('<div class="section-header">Company Parameters</div>', unsafe_allow_html=True)
        
        # Company parameter options
        param_choice = st.radio("Company Parameters", ["Generate Random Company", "Customize Parameters"])
        
        # Initialize company data
        company_data = generate_company_data()
        
        if param_choice == "Customize Parameters":
            # Financial Parameters
            st.markdown("##### Financial Parameters")
            company_data["initial_investment"] = st.number_input("Initial Investment ($)", 
                                                              min_value=100000.0, 
                                                              max_value=10000000.0, 
                                                              value=float(company_data["initial_investment"]))
            
            company_data["initial_revenue"] = st.number_input("Initial Annual Revenue ($)", 
                                                           min_value=10000.0, 
                                                           max_value=5000000.0, 
                                                           value=float(company_data["initial_revenue"]))
            
            company_data["current_cash_reserves"] = st.number_input("Cash Reserves ($)", 
                                                                min_value=0.0, 
                                                                max_value=3000000.0, 
                                                                value=float(company_data["current_cash_reserves"]))
            
            company_data["debt_level"] = st.number_input("Debt Level ($)", 
                                                      min_value=0.0, 
                                                      max_value=5000000.0, 
                                                      value=float(company_data["debt_level"]))
            
            # Growth and Cost Parameters
            st.markdown("##### Growth & Cost Parameters")
            company_data["revenue_growth_rate_mean"] = st.slider("Expected Revenue Growth Rate (%)", 
                                                              min_value=-5.0, 
                                                              max_value=25.0, 
                                                              value=float(company_data["revenue_growth_rate_mean"]))
            
            company_data["revenue_growth_volatility"] = st.slider("Revenue Growth Volatility", 
                                                              min_value=1.0, 
                                                              max_value=15.0, 
                                                              value=float(company_data["revenue_growth_volatility"]))
            
            company_data["fixed_costs"] = st.number_input("Fixed Costs (Annual $)", 
                                                       min_value=10000.0, 
                                                       max_value=2000000.0, 
                                                       value=float(company_data["fixed_costs"]))
            
            company_data["variable_costs_percentage"] = st.slider("Variable Costs (% of Revenue)", 
                                                              min_value=10.0, 
                                                              max_value=80.0, 
                                                              value=float(company_data["variable_costs_percentage"]))
            
            # Market Parameters
            st.markdown("##### Market Parameters")
            company_data["market_growth_rate_mean"] = st.slider("Market Growth Rate (%)", 
                                                             min_value=-5.0, 
                                                             max_value=20.0, 
                                                             value=float(company_data["market_growth_rate_mean"]))
            
            company_data["market_volatility"] = st.slider("Market Volatility", 
                                                       min_value=1.0, 
                                                       max_value=20.0, 
                                                       value=float(company_data["market_volatility"]))
            
            # Risk Parameters
            st.markdown("##### Risk Parameters")
            company_data["competitor_entry_probability"] = st.slider("Competitor Entry Probability (Annual)", 
                                                                 min_value=0.0, 
                                                                 max_value=0.5, 
                                                                 value=float(company_data["competitor_entry_probability"]))
            
            company_data["regulatory_change_probability"] = st.slider("Regulatory Change Probability (Annual)", 
                                                                  min_value=0.0, 
                                                                  max_value=0.5, 
                                                                  value=float(company_data["regulatory_change_probability"]))
        
        # Run simulation button
        run_simulation = st.button("Run Simulation", type="primary")
    
    # Main content area
    if "results" not in st.session_state or run_simulation:
        with st.spinner("Running Monte Carlo Simulation..."):
            # Run simulation
            results = run_monte_carlo_simulation(
                company_data,
                periods=periods,
                iterations=iterations,
                scenario=scenario
            )
            st.session_state.results = results
            st.session_state.company_data = company_data
            st.session_state.scenario = scenario
            st.session_state.periods = periods
    
    # Display results
    if "results" in st.session_state:
        results = st.session_state.results
        company_data = st.session_state.company_data
        scenario = st.session_state.scenario
        periods = st.session_state.periods
        
        # Key metrics section
        st.markdown('<div class="section-header">Key Performance Metrics</div>', unsafe_allow_html=True)
        
        final_period = periods - 1
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Final Average Revenue",
                value=format_as_currency(results["avg_revenue"][final_period]),
                delta=f"{(results['avg_revenue'][final_period]/company_data['initial_revenue']-1)*100:.1f}%"
            )
        
        with col2:
            st.metric(
                label="Profitability Probability",
                value=f"{results['profitability_probability']:.1f}%"
            )
        
        with col3:
            st.metric(
                label="Bankruptcy Risk",
                value=f"{results['bankruptcy_probability']:.1f}%",
                delta=None if results['bankruptcy_probability'] < 10 else f"{results['bankruptcy_probability']:.1f}%",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                label="Average ROI",
                value=f"{results['avg_roi'][final_period]:.2f}%",
                delta=None if results['avg_roi'][final_period] < 0 else f"{results['avg_roi'][final_period]:.2f}%"
            )
        
        # Risk assessment
        risk_level = "Low"
        if results['bankruptcy_probability'] > 20:
            risk_level = "High"
        elif results['bankruptcy_probability'] > 10:
            risk_level = "Medium"
            
        growth_potential = "Low"
        if results['high_growth_probability'] > 60:
            growth_potential = "High"
        elif results['high_growth_probability'] > 30:
            growth_potential = "Medium"
            
        col1, col2 = st.columns(2)
        
        with col1:
            risk_color = "success" if risk_level == "Low" else "warning" if risk_level == "Medium" else "error"
            st.markdown(f"""
            <div class="{risk_color}-box">
                <h3>Risk Assessment: {risk_level}</h3>
                <p>Bankruptcy Probability: {results['bankruptcy_probability']:.1f}%</p>
                <p>The business shows a {risk_level.lower()} level of risk based on the simulation.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            growth_color = "success" if growth_potential == "High" else "warning" if growth_potential == "Medium" else "error"
            st.markdown(f"""
            <div class="{growth_color}-box">
                <h3>Growth Potential: {growth_potential}</h3>
                <p>High Growth Probability: {results['high_growth_probability']:.1f}%</p>
                <p>The business shows {growth_potential.lower()} growth potential in the projected period.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["Revenue Projection", "Financial Metrics", "Summary Charts", "Report"])
        
        with tab1:
            st.plotly_chart(create_plotly_revenue_projection(results, periods), use_container_width=True)
            
            # Revenue metrics
            st.markdown("#### Revenue Metrics (End of Period)")
            rev_col1, rev_col2, rev_col3 = st.columns(3)
            
            with rev_col1:
                st.metric(
                    label="Low Estimate (10th percentile)",
                    value=format_as_currency(results['revenue_thresholds']['low_10th'])
                )
            
            with rev_col2:
                st.metric(
                    label="Median Estimate",
                    value=format_as_currency(results['revenue_thresholds']['median'])
                )
            
            with rev_col3:
                st.metric(
                    label="High Estimate (90th percentile)",
                    value=format_as_currency(results['revenue_thresholds']['high_90th'])
                )
        
        with tab2:
            st.plotly_chart(create_plotly_metrics_chart(results, periods), use_container_width=True)
            
            # Profit metrics
            st.markdown("#### Profit Metrics (End of Period)")
            profit_col1, profit_col2, profit_col3 = st.columns(3)
            
            with profit_col1:
                st.metric(
                    label="Low Estimate (10th percentile)",
                    value=format_as_currency(results['profit_thresholds']['low_10th'])
                )
            
            with profit_col2:
                st.metric(
                    label="Median Estimate",
                    value=format_as_currency(results['profit_thresholds']['median'])
                )
            
            with profit_col3:
                st.metric(
                    label="High Estimate (90th percentile)",
                    value=format_as_currency(results['profit_thresholds']['high_90th'])
                )
        
        with tab3:
            st.plotly_chart(create_plotly_summary_charts(results), use_container_width=True)
            
            # ROI distribution
            st.markdown("#### ROI Distribution")
            roi_col1, roi_col2, roi_col3, roi_col4 = st.columns(4)
            
            with roi_col1:
                st.metric(
                    label="Negative ROI",
                    value=f"{results['roi_thresholds']['negative']:.1f}%",
                    delta=None if results['roi_thresholds']['negative'] < 20 else f"{results['roi_thresholds']['negative']:.1f}%",
                    delta_color="inverse"
                )
            
            with roi_col2:
                st.metric(
                    label="0-10% ROI",
                    value=f"{results['roi_thresholds']['0_to_10']:.1f}%"
                )
            
            with roi_col3:
                st.metric(
                    label="10-20% ROI",
                    value=f"{results['roi_thresholds']['10_to_20']:.1f}%"
                )
            
            with roi_col4:
                st.metric(
                    label="20%+ ROI",
                    value=f"{results['roi_thresholds']['20_plus']:.1f}%"
                )
        
        with tab4:
            # Generate report
            report = generate_simulation_report(results, company_data, scenario, periods)
            st.markdown(report)
            
            # Download report button
            report_download = report.replace("\n", "  \n")  # Ensure proper markdown line breaks
            
            def get_report_download_link():
                # Generate a timestamp for the filename
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"business_simulation_report_{now}.md"
                
                # Create a download link
                b64 = base64.b64encode(report.encode()).decode()
                href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}">Download Report</a>'
                return href
            
            st.markdown(get_report_download_link(), unsafe_allow_html=True)
            
            # Generate matplotlib figures for download
            st.markdown("#### Download Visualization Charts")
            
            traditional_charts_col1, traditional_charts_col2 = st.columns(2)
            
            with traditional_charts_col1:
                if st.button("Generate Detailed Projections Chart"):
                    with st.spinner("Generating chart..."):
                        fig = visualize_simulation_results(results, company_data, periods)
                        st.pyplot(fig)
                        
                        # Create download link
                        buf = BytesIO()
                        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
                        buf.seek(0)
                        b64 = base64.b64encode(buf.getbuffer()).decode()
                        
                        download_filename = f"projections_chart_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        st.markdown(
                            f'<a href="data:image/png;base64,{b64}" download="{download_filename}">Download Projections Chart</a>',
                            unsafe_allow_html=True
                        )
                        plt.close(fig)
            
            with traditional_charts_col2:
                if st.button("Generate Summary Charts"):
                    with st.spinner("Generating chart..."):
                        fig = generate_summary_charts(results)
                        st.pyplot(fig)
                        
                        # Create download link
                        buf = BytesIO()
                        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
                        buf.seek(0)
                        b64 = base64.b64encode(buf.getbuffer()).decode()
                        
                        download_filename = f"summary_charts_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        st.markdown(
                            f'<a href="data:image/png;base64,{b64}" download="{download_filename}">Download Summary Charts</a>',
                            unsafe_allow_html=True
                        )
                        plt.close(fig)
    
    # Footer
    st.markdown("---")
    st.markdown("### How to Use This Tool")
    st.markdown("""
    1. **Adjust Parameters**: Use the sidebar to customize company parameters or generate random data
    2. **Run Simulation**: Click the 'Run Simulation' button to execute the Monte Carlo analysis
    3. **Explore Results**: Navigate through the tabs to view different visualizations and metrics
    4. **Download Report**: Get a detailed report of the simulation results
    """)

# Run the app
if __name__ == "__main__":
    main()