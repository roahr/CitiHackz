import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
import time
from News_Api import evaluate_company_digital_footprint

# Streamlit UI
st.set_page_config(page_title="Company Digital Footprint Dashboard", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {text-align: center; margin-bottom: 2rem;}
    .score-card {padding: 1.5rem; border-radius: 0.5rem; margin: 1rem 0;}
    .green-score {background-color: rgba(0, 128, 0, 0.1); border-left: 5px solid green;}
    .blue-score {background-color: rgba(0, 0, 255, 0.1); border-left: 5px solid blue;}
    .red-score {background-color: rgba(255, 0, 0, 0.1); border-left: 5px solid red;}
    .metrics-container {display: flex; justify-content: space-between; margin: 2rem 0;}
    .metric-box {padding: 1rem; border-radius: 0.5rem; width: 30%;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🔍 Company Digital Footprint Dashboard</h1></div>', unsafe_allow_html=True)

# Sidebar for documentation
with st.sidebar:
    st.header("📊 About The Scoring System")
    
    st.subheader("Dimension Scores")
    st.write("""
    Each article is analyzed across three key dimensions:
    
    1. **Operations Impact** (30% weight): How events affect company operations and business activities
    2. **Reputation Impact** (40% weight): How events affect public image and stakeholder trust
    3. **Financial Impact** (30% weight): How events affect financial performance or outlook
    """)
    
    st.subheader("Score Calculation")
    st.write("""
    **Sentiment Categories:**
    - 🟢 GREEN: Positive impact (base score: +0.7)
    - 🔵 BLUE: Neutral/mixed impact (base score: +0.1)
    - 🔴 RED: Negative impact (base score: -0.6)

    **Weighting Factors:**
    - Dimension weights (vary by sentiment)
    - Article recency (more recent = higher impact)
    - Final score is a weighted average across all articles and dimensions
    """)
    
    st.markdown("---")
    
    # Add detailed explanation of score calculation
    with st.expander("Detailed Score Calculation"):
        st.write("""
        **Step 1:** Each article receives a base score per dimension (operations, reputation, finance)
        - GREEN category: +0.7 base score
        - BLUE category: +0.1 base score
        - RED category: -0.6 base score
        
        **Step 2:** Apply dimension-specific weight multipliers
        - Operations weights: RED=1.2, BLUE=1.0, GREEN=1.1
        - Reputation weights: RED=1.5, BLUE=1.0, GREEN=1.2
        - Financial weights: RED=1.3, BLUE=1.0, GREEN=1.4
        
        **Step 3:** Apply recency weight
        - 0-7 days old: 1.5x weight
        - 8-30 days old: 1.2x weight
        - 31-90 days old: 1.0x weight
        - >90 days old: 0.7x weight
        
        **Step 4:** Calculate composite score
        - Weighted average of all dimensions: (Operations × 0.3) + (Reputation × 0.4) + (Finance × 0.3)
        
        **Step 5:** Determine overall rating
        - Composite score ≥ 0.3: GREEN
        - Composite score ≥ -0.1: BLUE
        - Composite score < -0.1: RED
        - Override: If any dimension score < -0.5, cap rating at BLUE
        """)

# Main UI
col1, col2 = st.columns([2, 1])

with col1:
    company_name = st.text_input("Enter Company Name", "Tesla")
    
with col2:
    max_articles = st.slider("Articles to Analyze", min_value=10, max_value=50, value=20, step=5)
    days_back = st.slider("Days to Look Back", min_value=7, max_value=45, value=24, step=7)

if st.button("📊 Analyze Company", use_container_width=True):
    with st.spinner("Fetching and analyzing news data... This may take a minute."):
        # Add a progress bar
        progress_bar = st.progress(0)
        
        # Simulated progress to give user feedback while processing
        for i in range(100):
            time.sleep(0.05)  # Adjust as needed based on expected processing time
            progress_bar.progress(i + 1)
        
        try:
            result = evaluate_company_digital_footprint(company_name, max_articles, days_back)
            
            if result["status"] == "no_data":
                st.warning("⚠️ " + result["message"])
            elif result["status"] == "error":
                st.error("❌ " + result["message"])
            else:
                # Clear progress after successful analysis
                progress_bar.empty()
                
                # Determine color class for overall rating
                rating_color = ""
                if result["overall_rating"] == "GREEN":
                    rating_color = "green-score"
                elif result["overall_rating"] == "BLUE":
                    rating_color = "blue-score"
                else:
                    rating_color = "red-score"
                
                # Display overall results
                st.markdown(f"""
                <div class="score-card {rating_color}">
                    <h2>📊 Analysis Results for {result['company']}</h2>
                    <h3>Overall Rating: {result['overall_rating']} (Score: {result['composite_score']})</h3>
                    <p>Analysis Period: {result['analysis_period']} | Articles Analyzed: {result['articles_analyzed']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display dimension scores with visualization
                st.subheader("📈 Dimension Score Breakdown")
                
                # Create columns for each dimension
                cols = st.columns(3)
                
                # Define color and icon for each dimension
                dimension_colors = {
                    "operations": "blue",
                    "reputation": "green", 
                    "finance": "orange"
                }
                
                dimension_icons = {
                    "operations": "🏭",
                    "reputation": "🌟",
                    "finance": "💰"
                }
                
                dimension_titles = {
                    "operations": "Operations Impact",
                    "reputation": "Reputation Impact",
                    "finance": "Financial Impact"
                }
                
                # Create a dictionary for the visualization
                dimension_data = {}
                
                # Display each dimension
                for i, (dim, score) in enumerate(result["dimension_scores"].items()):
                    with cols[i]:
                        # Determine score color
                        score_color = "gray"
                        if score > 0.3:
                            score_color = "green"
                        elif score > -0.2:
                            score_color = "blue"
                        else:
                            score_color = "red"
                        
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; border-radius: 0.5rem; border: 1px solid {dimension_colors[dim]};">
                            <h3>{dimension_icons[dim]} {dimension_titles[dim]}</h3>
                            <h2 style="color: {score_color};">{score}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        dimension_data[dim] = score
                
                # Create a bar chart for dimension scores
                fig, ax = plt.subplots(figsize=(10, 5))
                dims = list(dimension_data.keys())
                scores = list(dimension_data.values())
                colors = [dimension_colors[dim] for dim in dims]
                
                # Prettify dimension names for display
                dims_display = [dimension_titles[dim] for dim in dims]
                
                bars = ax.bar(dims_display, scores, color=colors, alpha=0.7)
                
                # Add a horizontal line at 0
                ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
                
                # Set the y-axis limits for better visualization
                min_score = min(scores)
                max_score = max(scores)
                buffer = 0.3  # Add some buffer
                ax.set_ylim(min(min_score - buffer, -0.8), max(max_score + buffer, 0.8))
                
                # Add the score values on top of the bars
                for bar, score in zip(bars, scores):
                    height = bar.get_height()
                    if height < 0:
                        y_pos = height - 0.1
                    else:
                        y_pos = height + 0.05
                    ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                            f'{score:.2f}', ha='center', va='bottom', fontweight='bold')
                
                ax.set_title('Dimension Score Comparison', fontsize=14)
                ax.set_ylabel('Score', fontsize=12)
                
                # Remove top and right spines
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                # Display the chart
                st.pyplot(fig)
                
                # Key Topics Section
                st.subheader("🔑 Key Topics Identified")
                
                if result["key_topics"] and len(result["key_topics"]) > 0:
                    # Create a nice display for topics
                    for i, topic in enumerate(result["key_topics"]):
                        st.markdown(f"""
                        <div style="padding: 0.8rem; margin: 0.5rem 0; background-color: #f0f2f6; border-radius: 0.5rem;">
                            <h4>Topic {i+1}: {topic}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No significant topics identified in the analyzed articles.")
                
                # Score Interpretation Section
                st.subheader("📋 Score Interpretation")
                
                composite_score = result["composite_score"]
                overall_rating = result["overall_rating"]
                
                if overall_rating == "GREEN":
                    st.markdown("""
                    <div style="background-color: rgba(0, 128, 0, 0.1); padding: 1rem; border-radius: 0.5rem; border-left: 5px solid green;">
                        <h4>🟢 Positive Digital Footprint</h4>
                        <p>The company has a predominantly positive online presence with favorable news coverage. This suggests strong performance across operations, reputation, and financial dimensions.</p>
                        <p>**Recommendation:** Maintain the positive momentum and capitalize on favorable public perception.</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif overall_rating == "BLUE":
                    st.markdown("""
                    <div style="background-color: rgba(0, 0, 255, 0.1); padding: 1rem; border-radius: 0.5rem; border-left: 5px solid blue;">
                        <h4>🔵 Neutral/Mixed Digital Footprint</h4>
                        <p>The company has a balanced online presence with mixed news coverage. There may be some concerns in specific dimensions that are offset by strengths in others.</p>
                        <p>**Recommendation:** Address any negative trends identified in specific dimensions while leveraging positive aspects.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:  # RED
                    st.markdown("""
                    <div style="background-color: rgba(255, 0, 0, 0.1); padding: 1rem; border-radius: 0.5rem; border-left: 5px solid red;">
                        <h4>🔴 Concerning Digital Footprint</h4>
                        <p>The company has a predominantly negative online presence with unfavorable news coverage. This suggests challenges across multiple dimensions that may require attention.</p>
                        <p>**Recommendation:** Develop a strategic response to address the negative aspects identified in the analysis.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Provide a download button for the complete results
                st.download_button(
                    label="📥 Download Full Analysis Report (JSON)",
                    data=json.dumps(result, indent=2),
                    file_name=f"{company_name.lower().replace(' ', '_')}_analysis.json",
                    mime="application/json"
                )
                
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.info("Please check your API keys and network connection, then try again.")

# Add explanation of the tool at the bottom
with st.expander("How This Tool Works"):
    st.write("""
    ### Methodology
    
    This dashboard analyzes a company's digital footprint by:
    
    1. **Data Collection**: Fetches recent news articles about the company using the News API
    2. **AI Analysis**: Uses Google's Gemini API to analyze each article across three dimensions:
       - Operations impact
       - Reputation impact
       - Financial impact
    3. **Score Calculation**: Applies a sophisticated weighted scoring system that considers:
       - Article sentiment (RED/BLUE/GREEN)
       - Article recency (newer articles have more impact)
       - Dimension-specific weights
    4. **Topic Identification**: Extracts key topics from the analyzed content
    
    """)