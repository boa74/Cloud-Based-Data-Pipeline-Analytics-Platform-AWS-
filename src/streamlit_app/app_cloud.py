"""
Cloud-Based Streamlit Dashboard: RDS Integration
Comprehensive analysis using data from PostgreSQL RDS
Optimized for EC2 deployment
"""

# Auto-install required packages if not available
import subprocess
import sys

def install_package(package):
    """Install package if not available"""
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required packages
required_packages = [
    'streamlit', 'pandas', 'plotly', 'sqlalchemy', 
    'psycopg2-binary', 'numpy', 'scipy', 'statsmodels'
]

for package in required_packages:
    install_package(package)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from sqlalchemy import create_engine, text
import psycopg2
import os
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Cloud Computing Project Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for refined design
st.markdown("""
<style>
    /* Main title styling */
    h1 {
        color: #1f77b4;
        font-weight: 600;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.3em;
        margin-bottom: 0.5em;
    }
    
    /* Subheader styling */
    h2 {
        color: #2c3e50;
        font-weight: 500;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
    }
    
    h3 {
        color: #34495e;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 500;
        color: #6c757d;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        font-weight: 500;
        border-radius: 0.3rem;
        padding: 0.5rem 1.5rem;
        border: none;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1565a0;
    }
    
    /* Selectbox and multiselect */
    [data-baseweb="select"] {
        border-radius: 0.3rem;
    }
    
    /* Success/Error/Info boxes */
    .stSuccess {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    
    .stError {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    
    .stInfo {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
    
    .stWarning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 0.3rem;
        overflow: hidden;
    }
    
    /* Footer styling */
    footer {
        visibility: hidden;
    }
    
    /* Horizontal rule */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Database Connection Configuration
# ============================================================================

# RDS Configuration - Update these for your deployment
DB_CONFIG = {
    'host': 'apan5450-boa.clkygjbv9yeo.us-east-1.rds.amazonaws.com',
    'port': 5432,
    'database': 'postgres',
    'user': 'apan54502',  # Updated username
    'password': 'apan54502'
}

@st.cache_resource
def get_db_connection():
    """Create database connection with error handling"""
    try:
        connection_string = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(
            connection_string, 
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 30}
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        st.stop()

@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_data_from_rds(query, description="data"):
    """Load data from RDS with caching and error handling"""
    try:
        engine = get_db_connection()
        with st.spinner(f"Loading {description}..."):
            df = pd.read_sql(query, engine)
            
        # Convert date columns
        date_columns = ['date', 'trade_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        return df
    except Exception as e:
        st.error(f"Error loading {description}: {str(e)}")
        return pd.DataFrame()

# ============================================================================
# Data Loading Functions
# ============================================================================

@st.cache_data(ttl=600)
def load_ultimate_dataset(limit=None, date_filter=None):
    """Load ultimate stock analysis dataset"""
    query = """
    SELECT date, ticker, company_name, sector, industry,
           open, high, low, close, volume, num_stocks,
           "Close_^GSPC", "Return", volatility_7,
           depression_word_count, total_articles, depression_index,
           avg_national_rainfall, price_range, price_change_pct,
           depression_index_category, year, month, quarter, day_of_week
    FROM ultimate_stock_analysis
    """
    
    conditions = []
    if date_filter and len(date_filter) == 2:
        start_date, end_date = date_filter
        conditions.append(f"date >= '{start_date}' AND date <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY date DESC, ticker"
    
    if limit:
        query += f" LIMIT {limit}"
    
    return load_data_from_rds(query, "ultimate dataset")

@st.cache_data(ttl=600)
def load_sector_analysis():
    """Load sector daily analysis"""
    query = """
    SELECT date, sector, open, high, low, close, volume, daily_return, 
           price_range, price_change_pct, num_stocks_in_sector,
           sp500_close, sp500_return, sp500_volatility_7d, avg_rainfall,
           depression_index, depression_word_count, total_articles,
           avg_depression_per_article, year, month, quarter, 
           day_of_week, day_of_year, depression_index_category
    FROM sector_daily_analysis 
    ORDER BY date DESC, sector
    """
    return load_data_from_rds(query, "sector analysis")

@st.cache_data(ttl=600)
def load_industry_analysis():
    """Load industry daily analysis"""
    query = """
    SELECT date, industry, open, high, low, close, volume, daily_return,
           price_range, price_change_pct, num_stocks_in_industry,
           sp500_close, sp500_return, sp500_volatility_7d, avg_rainfall,
           depression_index, depression_word_count, total_articles,
           avg_depression_per_article, year, month, quarter,
           day_of_week, day_of_year, depression_index_category
    FROM industry_daily_analysis 
    ORDER BY date DESC, industry
    LIMIT 50000
    """
    return load_data_from_rds(query, "industry analysis")

@st.cache_data(ttl=600)
def load_sector_statistics():
    """Load sector summary statistics"""
    # Note: sector_summary_statistics table actually contains industry data
    query = """
    SELECT industry as sector, daily_return_mean, daily_return_std, daily_return_min, daily_return_max,
           close_mean, close_min, close_max, volume_mean, price_change_pct_mean, price_change_pct_std,
           depression_index_mean, num_stocks_in_industry_first as num_stocks_in_sector_first
    FROM sector_summary_statistics 
    ORDER BY daily_return_mean DESC
    """
    return load_data_from_rds(query, "sector statistics")

@st.cache_data(ttl=600)
def load_industry_statistics():
    """Load industry summary statistics"""
    query = """
    SELECT industry, daily_return_mean, daily_return_std, daily_return_min, daily_return_max,
           close_mean, close_min, close_max, volume_mean, price_change_pct_mean, price_change_pct_std,
           depression_index_mean, num_stocks_in_industry_first
    FROM industry_summary_statistics 
    ORDER BY daily_return_mean DESC
    """
    return load_data_from_rds(query, "industry statistics")

@st.cache_data(ttl=600)
def load_time_series_data():
    """Load merged time series data"""
    query = """
    SELECT date, open, high, low, close, volume, num_stocks,
           "Close_^GSPC", "Return", volatility_7, depression_word_count,
           total_articles, depression_index, avg_national_rainfall,
           price_range, price_change_pct, depression_index_category
    FROM merged_time_series_data 
    ORDER BY date DESC
    """
    return load_data_from_rds(query, "time series data")

# ============================================================================
# Main Application
# ============================================================================

st.title("Cloud Computing Project Dashboard")
st.markdown("*Real-time analysis from PostgreSQL RDS | Deployed on AWS EC2*")
st.markdown("---")

# Sidebar - Connection Status
with st.sidebar:
    st.header("System Status")
    
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM ultimate_stock_analysis LIMIT 1"))
            total_records = result.fetchone()[0]
        st.success(f"Connected to RDS")
        st.info(f"{total_records:,} records available")
    except Exception as e:
        st.error(f"RDS Connection Failed: {str(e)[:100]}...")

# Navigation
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Select Analysis Page",
    ["Overview", "S&P 500 Indicators Analysis", "Sector Analysis", "Industry Analysis", 
     "Stock Analysis", "Correlation Analysis", "Depression Analysis",
     "Industry Volatility Analysis", "Real-time Query"]
)

# ============================================================================
# Overview Page
# ============================================================================

if page == "Overview":
    st.header("Data Overview & Summary")
    
    # Load summary statistics
    sector_stats = load_sector_statistics()
    industry_stats = load_industry_statistics()
    
    if not sector_stats.empty and not industry_stats.empty:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Sectors Analyzed", len(sector_stats))
        with col2:
            st.metric("Industries Analyzed", len(industry_stats))
        with col3:
            avg_return = sector_stats['daily_return_mean'].mean()
            st.metric("Avg Daily Return", f"{avg_return:.6f}")
        with col4:
            total_stocks = sector_stats['num_stocks_in_sector_first'].sum()
            st.metric("Total Stocks", f"{total_stocks:,}")
        
        st.markdown("---")
        
        # Top performing sectors
        st.subheader("Top Performing Sectors")
        top_sectors = sector_stats.head(10)
        
        fig_sectors = px.bar(
            top_sectors,
            x='sector',
            y='daily_return_mean',
            color='daily_return_std',
            title="Average Daily Returns by Sector",
            color_continuous_scale='Viridis'
        )
        fig_sectors.update_xaxes(tickangle=45)
        st.plotly_chart(fig_sectors, use_container_width=True)
        
        # Risk-Return Analysis
        st.subheader("Sector Risk-Return Profile")
        
        fig_risk = px.scatter(
            sector_stats,
            x='daily_return_std',
            y='daily_return_mean',
            size='num_stocks_in_sector_first',
            hover_name='sector',
            title="Risk vs Return by Sector",
            labels={'daily_return_std': 'Risk (Std Dev)', 'daily_return_mean': 'Average Return'}
        )
        st.plotly_chart(fig_risk, use_container_width=True)

# ============================================================================
# S&P 500 Indicators Analysis Page
# ============================================================================

elif page == "S&P 500 Indicators Analysis":
    st.header("S&P 500 Index and Market Indicators Analysis")
    st.markdown("*Analyzing correlations between S&P 500 Index and key market indicators*")
    
    # Load time series data
    time_series = load_time_series_data()
    
    if not time_series.empty:
        # Get latest S&P 500 index value
        latest_data = time_series.iloc[0]  # Most recent (ordered DESC)
        latest_date = latest_data['date']
        latest_sp500 = latest_data.get('Close_^GSPC', latest_data.get('close', 'N/A'))
        
        # Current Index Display
        st.subheader("Current S&P 500 Index")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if isinstance(latest_sp500, (int, float)):
                st.metric("S&P 500 Index", f"{latest_sp500:,.2f}")
            else:
                st.metric("S&P 500 Index", str(latest_sp500))
        with col2:
            if 'volatility_7' in latest_data:
                st.metric("7-Day Volatility", f"{latest_data['volatility_7']:.6f}")
        with col3:
            if 'depression_index' in latest_data:
                st.metric("Depression Index", f"{latest_data['depression_index']:.4f}")
        
        st.markdown("---")
        
        # Prepare data for correlation analysis
        analysis_data = time_series.copy().sort_values('date')
        
        # Select key variables
        key_vars = {
            'S&P 500 Close': 'Close_^GSPC' if 'Close_^GSPC' in analysis_data.columns else 'close',
            'Volatility (7-day)': 'volatility_7',
            'Rainfall': 'avg_national_rainfall',
            'Depression Index': 'depression_index',
            'Depression Word Count': 'depression_word_count'
        }
        
        # Filter to available columns
        available_vars = {k: v for k, v in key_vars.items() if v in analysis_data.columns}
        
        if len(available_vars) >= 2:
            # Correlation Matrix
            st.subheader("Correlation Matrix")
            
            # Create correlation data
            corr_data = analysis_data[list(available_vars.values())].dropna()
            corr_data.columns = list(available_vars.keys())  # Rename columns for display
            
            if not corr_data.empty and len(corr_data) > 1:
                corr_matrix = corr_data.corr()
                
                # Interactive correlation heatmap
                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    title="Correlation Matrix: S&P 500 Index vs Market Indicators",
                    color_continuous_scale='RdBu_r',
                    zmin=-1,
                    zmax=1,
                    labels=dict(x="Indicator", y="Indicator", color="Correlation")
                )
                fig_corr.update_layout(height=500)
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Detailed Correlation Table
                st.subheader("Detailed Correlation Statistics")
                
                # Calculate correlations with S&P 500
                sp500_col = list(available_vars.keys())[0]  # First is S&P 500
                corr_results = []
                
                for var in list(available_vars.keys())[1:]:  # Skip S&P 500 itself
                    if var in corr_data.columns:
                        corr_coef = corr_data[sp500_col].corr(corr_data[var])
                        if not np.isnan(corr_coef):
                            # Calculate p-value using scipy
                            valid_data = corr_data[[sp500_col, var]].dropna()
                            if len(valid_data) > 2:
                                _, p_value = pearsonr(valid_data[sp500_col], valid_data[var])
                                significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
                                
                                corr_results.append({
                                    'Indicator': var,
                                    'Correlation with S&P 500': f"{corr_coef:.4f}",
                                    'P-value': f"{p_value:.4f}",
                                    'Significance': significance,
                                    'Strength': 'Very Strong' if abs(corr_coef) > 0.8 else 
                                               'Strong' if abs(corr_coef) > 0.6 else
                                               'Moderate' if abs(corr_coef) > 0.4 else
                                               'Weak' if abs(corr_coef) > 0.2 else 'Very Weak',
                                    'Direction': 'Positive' if corr_coef > 0 else 'Negative'
                                })
                
                if corr_results:
                    corr_df = pd.DataFrame(corr_results)
                    st.dataframe(corr_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # Time Series Visualization
                st.subheader("Time Series: All Indicators Over Time")
                
                # Create multi-axis plot
                fig_ts = go.Figure()
                
                # S&P 500 (left axis)
                sp500_col_name = available_vars['S&P 500 Close']
                if sp500_col_name in analysis_data.columns:
                    fig_ts.add_trace(go.Scatter(
                        x=analysis_data['date'],
                        y=analysis_data[sp500_col_name],
                        name='S&P 500 Index',
                        yaxis='y',
                        line=dict(color='#1f77b4', width=2)
                    ))
                
                # Volatility (right axis)
                if 'volatility_7' in analysis_data.columns:
                    fig_ts.add_trace(go.Scatter(
                        x=analysis_data['date'],
                        y=analysis_data['volatility_7'] * 1000,  # Scale for visibility
                        name='Volatility (7-day) × 1000',
                        yaxis='y2',
                        line=dict(color='#ff7f0e', width=2)
                    ))
                
                # Depression Index (right axis)
                if 'depression_index' in analysis_data.columns:
                    fig_ts.add_trace(go.Scatter(
                        x=analysis_data['date'],
                        y=analysis_data['depression_index'],
                        name='Depression Index',
                        yaxis='y3',
                        line=dict(color='#d62728', width=2)
                    ))
                
                # Rainfall (right axis)
                if 'avg_national_rainfall' in analysis_data.columns:
                    fig_ts.add_trace(go.Scatter(
                        x=analysis_data['date'],
                        y=analysis_data['avg_national_rainfall'],
                        name='Rainfall',
                        yaxis='y4',
                        line=dict(color='#2ca02c', width=2)
                    ))
                
                # Depression Word Count (right axis)
                if 'depression_word_count' in analysis_data.columns:
                    fig_ts.add_trace(go.Scatter(
                        x=analysis_data['date'],
                        y=analysis_data['depression_word_count'],
                        name='Depression Word Count',
                        yaxis='y5',
                        line=dict(color='#9467bd', width=2)
                    ))
                
                fig_ts.update_layout(
                    title="S&P 500 Index and Market Indicators Over Time",
                    xaxis_title="Date",
                    yaxis=dict(title="S&P 500 Index", side="left", position=0),
                    yaxis2=dict(title="Volatility (×1000)", side="right", overlaying="y", position=0.95),
                    yaxis3=dict(title="Depression Index", side="right", overlaying="y", position=0.85),
                    yaxis4=dict(title="Rainfall", side="right", overlaying="y", position=0.75),
                    yaxis5=dict(title="Word Count", side="right", overlaying="y", position=0.65),
                    height=600,
                    hovermode='x unified'
                )
                st.plotly_chart(fig_ts, use_container_width=True)
                
                st.markdown("---")
                
                # Scatter Plots: S&P 500 vs Each Indicator
                st.subheader("Scatter Analysis: S&P 500 vs Individual Indicators")
                
                indicators_to_plot = [k for k in list(available_vars.keys())[1:] if available_vars[k] in analysis_data.columns]
                
                if indicators_to_plot:
                    # Create tabs for each indicator
                    tabs = st.tabs(indicators_to_plot)
                    
                    for idx, indicator in enumerate(indicators_to_plot):
                        with tabs[idx]:
                            indicator_col = available_vars[indicator]
                            
                            # Prepare data
                            plot_data = analysis_data[[sp500_col_name, indicator_col, 'date']].dropna()
                            
                            if not plot_data.empty and len(plot_data) > 1:
                                # Scatter plot
                                fig_scatter = px.scatter(
                                    plot_data,
                                    x=sp500_col_name,
                                    y=indicator_col,
                                    hover_data=['date'],
                                    title=f"S&P 500 Index vs {indicator}",
                                    labels={
                                        sp500_col_name: 'S&P 500 Index',
                                        indicator_col: indicator
                                    },
                                    trendline="ols"
                                )
                                
                                # Calculate correlation
                                corr_val = plot_data[sp500_col_name].corr(plot_data[indicator_col])
                                
                                # Add correlation info to title
                                if not np.isnan(corr_val):
                                    fig_scatter.update_layout(
                                        title=f"S&P 500 Index vs {indicator} (Correlation: {corr_val:.4f})"
                                    )
                                
                                st.plotly_chart(fig_scatter, use_container_width=True)
                                
                                # Statistics
                                col1, col2 = st.columns(2)
                                with col1:
                                    if not np.isnan(corr_val):
                                        st.metric("Correlation Coefficient", f"{corr_val:.4f}")
                                with col2:
                                    st.metric("Data Points", len(plot_data))
                                
                                # Statistical summary
                                with st.expander("View Statistical Summary"):
                                    summary_stats = plot_data[[sp500_col_name, indicator_col]].describe()
                                    st.dataframe(summary_stats, use_container_width=True)
                            else:
                                st.warning(f"Insufficient data for {indicator} analysis.")
                
                st.markdown("---")
                
                # Rolling Correlation Analysis
                st.subheader("Rolling Correlation Analysis")
                
                rolling_window = st.slider("Rolling Window (days)", 30, 365, 90, 30)
                
                # Calculate rolling correlations
                rolling_corrs = {}
                for indicator in indicators_to_plot:
                    indicator_col = available_vars[indicator]
                    if indicator_col in analysis_data.columns:
                        rolling_corr = analysis_data[sp500_col_name].rolling(window=rolling_window).corr(
                            analysis_data[indicator_col]
                        )
                        rolling_corrs[indicator] = rolling_corr
                
                if rolling_corrs:
                    fig_rolling = go.Figure()
                    
                    colors = ['#ff7f0e', '#d62728', '#2ca02c', '#9467bd', '#8c564b']
                    for idx, (indicator, rolling_corr) in enumerate(rolling_corrs.items()):
                        fig_rolling.add_trace(go.Scatter(
                            x=analysis_data['date'],
                            y=rolling_corr,
                            name=indicator,
                            line=dict(color=colors[idx % len(colors)], width=2)
                        ))
                    
                    fig_rolling.add_hline(y=0, line_dash="dash", line_color="gray", 
                                        annotation_text="No Correlation")
                    fig_rolling.update_layout(
                        title=f"{rolling_window}-Day Rolling Correlation: S&P 500 vs Indicators",
                        xaxis_title="Date",
                        yaxis_title="Correlation Coefficient",
                        height=500,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_rolling, use_container_width=True)
                    
                    # Summary of rolling correlations
                    st.markdown("**Rolling Correlation Summary**")
                    rolling_summary = []
                    for indicator, rolling_corr in rolling_corrs.items():
                        valid_corr = rolling_corr.dropna()
                        if len(valid_corr) > 0:
                            rolling_summary.append({
                                'Indicator': indicator,
                                'Mean Correlation': f"{valid_corr.mean():.4f}",
                                'Std Correlation': f"{valid_corr.std():.4f}",
                                'Min Correlation': f"{valid_corr.min():.4f}",
                                'Max Correlation': f"{valid_corr.max():.4f}"
                            })
                    
                    if rolling_summary:
                        rolling_summary_df = pd.DataFrame(rolling_summary)
                        st.dataframe(rolling_summary_df, use_container_width=True, hide_index=True)
            else:
                st.warning("Insufficient data for correlation analysis. Need at least 2 data points.")
        else:
            st.error("Required columns not found in the dataset.")
    else:
        st.error("No time series data available.")

# ============================================================================
# Sector Analysis Page
# ============================================================================

elif page == "Sector Analysis":
    st.header("Sector-Level Analysis")
    
    sector_data = load_sector_analysis()
    
    if not sector_data.empty:
        # Date range selector
        min_date = sector_data['date'].min().date()
        max_date = sector_data['date'].max().date()
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=max_date - timedelta(days=365), min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
        
        # Filter data
        filtered_data = sector_data[
            (sector_data['date'].dt.date >= start_date) & 
            (sector_data['date'].dt.date <= end_date)
        ]
        
        # Sector selector
        sectors = st.multiselect(
            "Select Sectors",
            options=sorted(filtered_data['sector'].unique()),
            default=sorted(filtered_data['sector'].unique())[:5]
        )
        
        if sectors:
            sector_subset = filtered_data[filtered_data['sector'].isin(sectors)]
            
            # Performance metrics
            metric = st.selectbox(
                "Select Metric",
                ['close', 'daily_return', 'volume', 'price_change_pct']
            )
            
            fig_performance = px.line(
                sector_subset,
                x='date',
                y=metric,
                color='sector',
                title=f"{metric.replace('_', ' ').title()} Over Time"
            )
            st.plotly_chart(fig_performance, use_container_width=True)
            
            # Summary statistics
            st.subheader("Summary Statistics")
            summary = sector_subset.groupby('sector').agg({
                'daily_return': ['mean', 'std'],
                'close': ['mean', 'min', 'max'],
                'volume': 'mean'
            }).round(6)
            
            summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
            st.dataframe(summary, use_container_width=True)

# ============================================================================
# Industry Analysis Page
# ============================================================================

elif page == "Industry Analysis":
    st.header("Industry-Level Analysis")
    
    industry_stats = load_industry_statistics()
    
    if not industry_stats.empty:
        # Top industries
        st.subheader("Top Performing Industries")
        
        top_n = st.slider("Number of top industries to show", 5, 50, 20)
        top_industries = industry_stats.head(top_n)
        
        fig_top = px.bar(
            top_industries,
            x='daily_return_mean',
            y='industry',
            orientation='h',
            title=f"Top {top_n} Industries by Average Daily Return",
            height=max(400, top_n * 25)
        )
        st.plotly_chart(fig_top, use_container_width=True)
        
        # Industry search and details
        st.subheader("Industry Search")
        selected_industry = st.selectbox(
            "Select Industry for Details",
            options=industry_stats['industry'].tolist()
        )
        
        if selected_industry:
            industry_row = industry_stats[industry_stats['industry'] == selected_industry].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Daily Return", f"{industry_row['daily_return_mean']:.6f}")
            with col2:
                st.metric("Return Std Dev", f"{industry_row['daily_return_std']:.6f}")
            with col3:
                st.metric("Avg Close Price", f"${industry_row['close_mean']:.2f}")
            with col4:
                st.metric("Number of Stocks", f"{industry_row['num_stocks_in_industry_first']}")

# ============================================================================
# Stock Analysis Page
# ============================================================================

elif page == "Stock Analysis":
    st.header("Individual Stock Analysis")
    
    # Load sample of ultimate dataset for stock picker
    sample_stocks = load_ultimate_dataset(limit=10000)
    
    if not sample_stocks.empty:
        # Stock selector
        stocks = sorted(sample_stocks['ticker'].unique())
        selected_stock = st.selectbox("Select Stock", options=stocks)
        
        if selected_stock:
            # Get stock data
            stock_data = sample_stocks[sample_stocks['ticker'] == selected_stock].copy()
            stock_data = stock_data.sort_values('date')
            
            # Stock info
            if not stock_data.empty:
                latest = stock_data.iloc[-1]
                
                st.subheader(f"{latest['company_name']} ({selected_stock})")
                st.write(f"**Sector:** {latest['sector']} | **Industry:** {latest['industry']}")
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Latest Close", f"${latest['close']:.2f}")
                with col2:
                    avg_return = stock_data['Return'].mean() if 'Return' in stock_data.columns else 0
                    st.metric("Avg Daily Return", f"{avg_return:.6f}")
                with col3:
                    volatility = stock_data['volatility_7'].iloc[-1] if 'volatility_7' in stock_data.columns else 0
                    st.metric("Current Volatility", f"{volatility:.6f}")
                with col4:
                    st.metric("Data Points", len(stock_data))
                
                # Price chart
                fig_price = px.line(
                    stock_data,
                    x='date',
                    y='close',
                    title=f"{selected_stock} Stock Price Over Time"
                )
                st.plotly_chart(fig_price, use_container_width=True)
                
                # Returns chart
                if 'Return' in stock_data.columns:
                    fig_returns = px.line(
                        stock_data,
                        x='date',
                        y='Return',
                        title=f"{selected_stock} Daily Returns"
                    )
                    st.plotly_chart(fig_returns, use_container_width=True)

# ============================================================================
# Correlation Analysis Page
# ============================================================================

elif page == "Correlation Analysis":
    st.header("Comprehensive Correlation Analysis")
    
    time_series = load_time_series_data()
    ultimate_data = load_ultimate_dataset(limit=50000)
    
    if not time_series.empty:
        # Calculate correlation matrix for all numerical variables
        numeric_cols = time_series.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['date', 'year', 'month', 'quarter', 'day_of_week']
        numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        if len(numeric_cols) >= 2:
            # Full correlation matrix
            corr_matrix = time_series[numeric_cols].corr()
            
            st.subheader("Complete Correlation Matrix")
            
            # Interactive correlation heatmap
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title="Full Variable Correlation Matrix",
                color_continuous_scale='RdBu_r',
                zmin=-1,
                zmax=1
            )
            fig_corr.update_layout(height=600)
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Top 5 Correlations Table
            st.subheader("Top 5 Strongest Correlations")
            
            # Get upper triangle of correlation matrix to avoid duplicates
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    var1 = corr_matrix.columns[i]
                    var2 = corr_matrix.columns[j]
                    corr_value = corr_matrix.iloc[i, j]
                    if not np.isnan(corr_value):
                        corr_pairs.append({
                            'Variable 1': var1,
                            'Variable 2': var2,
                            'Correlation': corr_value,
                            'Strength': 'Very Strong' if abs(corr_value) > 0.8 else 
                                       'Strong' if abs(corr_value) > 0.6 else
                                       'Moderate' if abs(corr_value) > 0.4 else
                                       'Weak' if abs(corr_value) > 0.2 else 'Very Weak',
                            'Direction': 'Positive' if corr_value > 0 else 'Negative'
                        })
            
            # Sort by absolute correlation value
            corr_pairs_df = pd.DataFrame(corr_pairs)
            corr_pairs_df = corr_pairs_df.reindex(
                corr_pairs_df['Correlation'].abs().sort_values(ascending=False).index
            ).head(5)
            
            # Style the correlation values
            def highlight_correlation(val):
                if abs(val) > 0.8:
                    return 'background-color: #ff6b6b; color: white'
                elif abs(val) > 0.6:
                    return 'background-color: #ffa726; color: white'
                elif abs(val) > 0.4:
                    return 'background-color: #ffee58; color: black'
                else:
                    return 'background-color: #e8f5e8; color: black'
            
            st.dataframe(
                corr_pairs_df.round(4).style.applymap(
                    highlight_correlation, subset=['Correlation']
                ),
                use_container_width=True
            )
            
            # Bar chart of top correlations
            fig_top = px.bar(
                corr_pairs_df,
                x='Correlation',
                y=[f"{row['Variable 1']} vs {row['Variable 2']}" 
                   for _, row in corr_pairs_df.iterrows()],
                orientation='h',
                title="Top 5 Variable Correlations",
                color='Correlation',
                color_continuous_scale='RdBu_r'
            )
            fig_top.update_layout(height=400, yaxis_title="Variable Pairs")
            st.plotly_chart(fig_top, use_container_width=True)
            
            # Correlation insights
            st.subheader("Correlation Insights")
            
            strongest = corr_pairs_df.iloc[0]
            st.write(f"**Strongest Correlation:** {strongest['Variable 1']} vs {strongest['Variable 2']}")
            st.write(f"**Correlation Coefficient:** {strongest['Correlation']:.4f} ({strongest['Strength']}, {strongest['Direction']})")
            
            if strongest['Correlation'] > 0.8:
                st.info("This very strong positive correlation suggests these variables move together closely.")
            elif strongest['Correlation'] < -0.8:
                st.info("This very strong negative correlation suggests these variables move in opposite directions.")
            
            # Correlation network graph
            st.subheader("Correlation Network")
            
            # Filter strong correlations for network
            strong_corrs = corr_pairs_df[corr_pairs_df['Correlation'].abs() > 0.3]
            
            if not strong_corrs.empty:
                # Create network visualization
                import plotly.graph_objects as go
                import numpy as np
                
                # Get unique variables
                variables = list(set(strong_corrs['Variable 1'].tolist() + 
                                   strong_corrs['Variable 2'].tolist()))
                
                # Create position for nodes in a circle
                angles = np.linspace(0, 2*np.pi, len(variables), endpoint=False)
                x_pos = np.cos(angles)
                y_pos = np.sin(angles)
                
                # Create edges
                edge_x = []
                edge_y = []
                edge_colors = []
                
                for _, row in strong_corrs.iterrows():
                    x0 = x_pos[variables.index(row['Variable 1'])]
                    y0 = y_pos[variables.index(row['Variable 1'])]
                    x1 = x_pos[variables.index(row['Variable 2'])]
                    y1 = y_pos[variables.index(row['Variable 2'])]
                    
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                
                # Create network plot
                fig_network = go.Figure()
                
                # Add edges
                fig_network.add_trace(go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=2, color='lightblue'),
                    hoverinfo='none',
                    mode='lines'
                ))
                
                # Add nodes
                fig_network.add_trace(go.Scatter(
                    x=x_pos, y=y_pos,
                    mode='markers+text',
                    text=variables,
                    textposition="middle center",
                    marker=dict(size=20, color='lightcoral'),
                    hoverinfo='text',
                    hovertext=variables
                ))
                
                fig_network.update_layout(
                    title="Correlation Network (|r| > 0.3)",
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[
                        dict(
                            text="Variables with strong correlations are connected",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002, align="left"
                        )
                    ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
                st.plotly_chart(fig_network, use_container_width=True)

# ============================================================================
# Depression Analysis Page
# ============================================================================

elif page == "Depression Analysis":
    st.header("Comprehensive Depression Analysis")
    st.markdown("*Analyzing the relationship between Depression Index and Market Volatility*")
    
    time_series = load_time_series_data()
    ultimate_data = load_ultimate_dataset(limit=30000)
    
    if not time_series.empty:
        # Key Insights Section
        st.subheader("Key Insights")
        
        # Calculate key metrics
        if 'depression_index' in time_series.columns and 'volatility_7' in time_series.columns:
            depression_volatility_corr = time_series['depression_index'].corr(time_series['volatility_7'])
            avg_depression = time_series['depression_index'].mean()
            avg_volatility = time_series['volatility_7'].mean()
            high_depression_days = len(time_series[time_series['depression_index'] > avg_depression])
            total_days = len(time_series)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Depression-Volatility Correlation", f"{depression_volatility_corr:.4f}")
            with col2:
                st.metric("Average Depression Index", f"{avg_depression:.4f}")
            with col3:
                st.metric("Average Volatility (7d)", f"{avg_volatility:.6f}")
            with col4:
                st.metric("High Depression Days", f"{high_depression_days}/{total_days}")
        
        # Depression Index Trend Analysis
        st.subheader("Depression Index Trend Over Time")
        
        fig_depression_trend = go.Figure()
        fig_depression_trend.add_trace(go.Scatter(
            x=time_series['date'],
            y=time_series['depression_index'],
            mode='lines',
            name='Depression Index',
            line=dict(color='red', width=2)
        ))
        
        # Add volatility on secondary y-axis
        if 'volatility_7' in time_series.columns:
            fig_depression_trend.add_trace(go.Scatter(
                x=time_series['date'],
                y=time_series['volatility_7'],
                mode='lines',
                name='7-Day Volatility',
                yaxis='y2',
                line=dict(color='blue', width=2)
            ))
        
        fig_depression_trend.update_layout(
            title="Depression Index vs Market Volatility Over Time",
            xaxis_title="Date",
            yaxis=dict(title="Depression Index", side="left"),
            yaxis2=dict(title="Volatility (7-day)", side="right", overlaying="y"),
            height=500
        )
        st.plotly_chart(fig_depression_trend, use_container_width=True)
        
        # Depression Categories Analysis
        if 'depression_index_category' in time_series.columns:
            st.subheader("Market Behavior by Depression Level")
            
            # Group by depression category
            depression_stats = time_series.groupby('depression_index_category').agg({
                'depression_index': ['mean', 'count'],
                'volatility_7': ['mean', 'std'],
                'Return': ['mean', 'std'],
                'close': 'mean',
                'volume': 'mean'
            }).round(6)
            
            # Flatten column names
            depression_stats.columns = ['_'.join(col).strip() for col in depression_stats.columns.values]
            depression_stats = depression_stats.reset_index()
            
            st.dataframe(depression_stats, use_container_width=True)
            
            # Box plots for volatility by depression level
            col1, col2 = st.columns(2)
            
            with col1:
                fig_vol_box = px.box(
                    time_series,
                    x='depression_index_category',
                    y='volatility_7',
                    title="Volatility Distribution by Depression Level",
                    color='depression_index_category'
                )
                st.plotly_chart(fig_vol_box, use_container_width=True)
            
            with col2:
                fig_return_box = px.box(
                    time_series,
                    x='depression_index_category',
                    y='Return',
                    title="Returns Distribution by Depression Level",
                    color='depression_index_category'
                )
                st.plotly_chart(fig_return_box, use_container_width=True)
        
        # Scatter Plot: Depression Index vs Volatility
        st.subheader("Depression Index vs Volatility Relationship")
        
        if 'volatility_7' in time_series.columns:
            fig_scatter = px.scatter(
                time_series,
                x='depression_index',
                y='volatility_7',
                color='Return' if 'Return' in time_series.columns else None,
                size='volume' if 'volume' in time_series.columns else None,
                hover_data=['date'],
                title="Depression Index vs Market Volatility",
                labels={
                    'depression_index': 'Depression Index',
                    'volatility_7': '7-Day Volatility',
                    'Return': 'Daily Return'
                }
            )
            
            # Add trend line
            from scipy import stats
            if len(time_series.dropna()) > 2:
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    time_series['depression_index'].dropna(),
                    time_series['volatility_7'].dropna()
                )
                
                line_x = np.linspace(time_series['depression_index'].min(), 
                                   time_series['depression_index'].max(), 100)
                line_y = slope * line_x + intercept
                
                fig_scatter.add_trace(go.Scatter(
                    x=line_x,
                    y=line_y,
                    mode='lines',
                    name=f'Trend Line (R²={r_value**2:.3f})',
                    line=dict(color='red', dash='dash', width=3)
                ))
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # High vs Low Depression Analysis
        st.subheader("High vs Low Depression Impact Analysis")
        
        if 'depression_index' in time_series.columns:
            median_depression = time_series['depression_index'].median()
            high_depression = time_series[time_series['depression_index'] >= median_depression]
            low_depression = time_series[time_series['depression_index'] < median_depression]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**High Depression Days**")
                high_stats = {
                    'Count': len(high_depression),
                    'Avg Volatility': high_depression['volatility_7'].mean() if 'volatility_7' in high_depression.columns else 'N/A',
                    'Avg Return': high_depression['Return'].mean() if 'Return' in high_depression.columns else 'N/A',
                    'Avg Volume': high_depression['volume'].mean() if 'volume' in high_depression.columns else 'N/A'
                }
                for key, value in high_stats.items():
                    if isinstance(value, float):
                        st.metric(key, f"{value:.6f}")
                    else:
                        st.metric(key, str(value))
            
            with col2:
                st.write("**Low Depression Days**")
                low_stats = {
                    'Count': len(low_depression),
                    'Avg Volatility': low_depression['volatility_7'].mean() if 'volatility_7' in low_depression.columns else 'N/A',
                    'Avg Return': low_depression['Return'].mean() if 'Return' in low_depression.columns else 'N/A',
                    'Avg Volume': low_depression['volume'].mean() if 'volume' in low_depression.columns else 'N/A'
                }
                for key, value in low_stats.items():
                    if isinstance(value, float):
                        st.metric(key, f"{value:.6f}")
                    else:
                        st.metric(key, str(value))
        
        # Rolling Correlation Analysis
        st.subheader("Rolling Correlation Analysis")
        
        if 'volatility_7' in time_series.columns:
            # Calculate 30-day rolling correlation
            time_series_sorted = time_series.sort_values('date')
            rolling_corr = time_series_sorted['depression_index'].rolling(window=30).corr(
                time_series_sorted['volatility_7']
            )
            
            fig_rolling = go.Figure()
            fig_rolling.add_trace(go.Scatter(
                x=time_series_sorted['date'],
                y=rolling_corr,
                mode='lines',
                name='30-Day Rolling Correlation',
                line=dict(color='purple', width=2)
            ))
            
            fig_rolling.add_hline(y=0, line_dash="dash", line_color="gray", 
                                annotation_text="No Correlation")
            fig_rolling.update_layout(
                title="30-Day Rolling Correlation: Depression Index vs Volatility",
                xaxis_title="Date",
                yaxis_title="Correlation Coefficient",
                height=400
            )
            st.plotly_chart(fig_rolling, use_container_width=True)
    
    else:
        st.error("No time series data available for depression analysis.")

# ============================================================================
# Industry Volatility Analysis Page
# ============================================================================

elif page == "Industry Volatility Analysis":
    st.header("Industry Volatility Analysis by Depression Index")
    st.markdown("*Analyzing how different industries respond to depression levels*")
    
    ultimate_data = load_ultimate_dataset(limit=50000)
    industry_data = load_industry_analysis()
    
    if not ultimate_data.empty:
        # Filter data with required columns
        if 'volatility_7' in ultimate_data.columns and 'depression_index' in ultimate_data.columns and 'industry' in ultimate_data.columns:
            
            # Industry selector
            st.subheader("Select Industries for Analysis")
            
            available_industries = sorted(ultimate_data['industry'].dropna().unique())
            selected_industries = st.multiselect(
                "Choose industries to analyze",
                options=available_industries,
                default=available_industries[:8] if len(available_industries) > 8 else available_industries
            )
            
            if selected_industries:
                industry_subset = ultimate_data[ultimate_data['industry'].isin(selected_industries)]
                
                # Create depression level categories
                industry_subset['depression_level'] = pd.cut(
                    industry_subset['depression_index'],
                    bins=3,
                    labels=['Low Depression', 'Medium Depression', 'High Depression']
                )
                
                # Industry-Depression Volatility Analysis
                st.subheader("Volatility by Industry and Depression Level")
                
                # Group by industry and depression level
                volatility_analysis = industry_subset.groupby(['industry', 'depression_level']).agg({
                    'volatility_7': ['mean', 'std', 'count'],
                    'Return': ['mean', 'std'],
                    'depression_index': 'mean'
                }).round(6)
                
                # Flatten column names
                volatility_analysis.columns = ['_'.join(col).strip() for col in volatility_analysis.columns.values]
                volatility_analysis = volatility_analysis.reset_index()
                
                # Pivot for heatmap
                volatility_pivot = industry_subset.pivot_table(
                    values='volatility_7',
                    index='industry',
                    columns='depression_level',
                    aggfunc='mean'
                ).fillna(0)
                
                # Heatmap
                fig_heatmap = px.imshow(
                    volatility_pivot,
                    title="Average Volatility by Industry and Depression Level",
                    color_continuous_scale='Reds',
                    aspect="auto"
                )
                fig_heatmap.update_layout(height=max(400, len(selected_industries) * 30))
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Box plot comparison
                st.subheader("Volatility Distribution by Depression Level")
                
                fig_box_industry = px.box(
                    industry_subset,
                    x='depression_level',
                    y='volatility_7',
                    color='industry',
                    title="Volatility Distribution Across Industries by Depression Level"
                )
                fig_box_industry.update_layout(height=500)
                st.plotly_chart(fig_box_industry, use_container_width=True)
                
                # Statistical Analysis
                st.subheader("Statistical Summary")
                
                # ANOVA-style analysis
                summary_stats = []
                
                for industry in selected_industries:
                    industry_data_filtered = industry_subset[industry_subset['industry'] == industry]
                    
                    for level in ['Low Depression', 'Medium Depression', 'High Depression']:
                        level_data = industry_data_filtered[industry_data_filtered['depression_level'] == level]
                        
                        if not level_data.empty:
                            summary_stats.append({
                                'Industry': industry,
                                'Depression Level': level,
                                'Mean Volatility': level_data['volatility_7'].mean(),
                                'Std Volatility': level_data['volatility_7'].std(),
                                'Sample Size': len(level_data),
                                'Mean Return': level_data['Return'].mean() if 'Return' in level_data.columns else 0
                            })
                
                summary_df = pd.DataFrame(summary_stats)
                
                if not summary_df.empty:
                    st.dataframe(summary_df.round(6), use_container_width=True)
                    
                    # Volatility difference analysis
                    st.subheader("Volatility Sensitivity Analysis")
                    
                    # Calculate volatility difference between high and low depression
                    volatility_sensitivity = []
                    
                    for industry in selected_industries:
                        industry_stats = summary_df[summary_df['Industry'] == industry]
                        
                        low_vol = industry_stats[industry_stats['Depression Level'] == 'Low Depression']['Mean Volatility']
                        high_vol = industry_stats[industry_stats['Depression Level'] == 'High Depression']['Mean Volatility']
                        
                        if not low_vol.empty and not high_vol.empty:
                            vol_diff = high_vol.iloc[0] - low_vol.iloc[0]
                            vol_pct_change = (vol_diff / low_vol.iloc[0]) * 100 if low_vol.iloc[0] != 0 else 0
                            
                            volatility_sensitivity.append({
                                'Industry': industry,
                                'Low Depression Volatility': low_vol.iloc[0],
                                'High Depression Volatility': high_vol.iloc[0],
                                'Volatility Difference': vol_diff,
                                'Percentage Change': vol_pct_change,
                                'Sensitivity': 'High' if abs(vol_pct_change) > 50 else 
                                             'Medium' if abs(vol_pct_change) > 20 else 'Low'
                            })
                    
                    sensitivity_df = pd.DataFrame(volatility_sensitivity)
                    
                    if not sensitivity_df.empty:
                        # Sort by absolute percentage change
                        sensitivity_df = sensitivity_df.reindex(
                            sensitivity_df['Percentage Change'].abs().sort_values(ascending=False).index
                        )
                        
                        st.dataframe(sensitivity_df.round(4), use_container_width=True)
                        
                        # Sensitivity chart
                        fig_sensitivity = px.bar(
                            sensitivity_df.head(10),
                            x='Percentage Change',
                            y='Industry',
                            orientation='h',
                            title="Top 10 Industries: Volatility Sensitivity to Depression",
                            color='Percentage Change',
                            color_continuous_scale='RdYlBu_r'
                        )
                        fig_sensitivity.update_layout(height=400)
                        st.plotly_chart(fig_sensitivity, use_container_width=True)
                        
                        # Key insights
                        st.subheader("Key Insights")
                        
                        most_sensitive = sensitivity_df.loc[sensitivity_df['Percentage Change'].abs().idxmax()]
                        least_sensitive = sensitivity_df.loc[sensitivity_df['Percentage Change'].abs().idxmin()]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.info(f"**Most Sensitive Industry:** {most_sensitive['Industry']}")
                            st.write(f"Volatility changes by {most_sensitive['Percentage Change']:.2f}% between low and high depression periods.")
                        
                        with col2:
                            st.info(f"**Most Stable Industry:** {least_sensitive['Industry']}")
                            st.write(f"Volatility changes by only {least_sensitive['Percentage Change']:.2f}% between depression periods.")
                        
                        # Average sensitivity
                        avg_sensitivity = sensitivity_df['Percentage Change'].abs().mean()
                        st.success(f"**Average Volatility Sensitivity:** {avg_sensitivity:.2f}%")
                        
                        high_sensitivity_count = len(sensitivity_df[sensitivity_df['Sensitivity'] == 'High'])
                        total_industries = len(sensitivity_df)
                        
                        st.write(f"**{high_sensitivity_count}/{total_industries}** industries show high sensitivity to depression levels.")
            
            else:
                st.warning("Please select at least one industry to analyze.")
        
        else:
            st.error("Required columns (volatility_7, depression_index, industry) not found in the dataset.")
    
    else:
        st.error("No data available for industry volatility analysis.")

# ============================================================================
# Real-time Query Page
# ============================================================================

elif page == "Real-time Query":
    st.header("Custom SQL Query Interface")
    
    st.info("Write custom SQL queries to explore the data in real-time.")
    
    # Predefined queries
    st.subheader("Quick Queries")
    
    quick_queries = {
        "Table Columns": """
        SELECT table_name, column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        ORDER BY table_name, ordinal_position;
        """,
        "Ultimate Stock Analysis Columns": """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'ultimate_stock_analysis'
        ORDER BY ordinal_position;
        """,
        "Top 10 Stocks by Latest Price": """
        SELECT ticker, company_name, sector, close 
        FROM ultimate_stock_analysis 
        WHERE date = (SELECT MAX(date) FROM ultimate_stock_analysis) 
        ORDER BY close DESC LIMIT 10;
        """,
        "Sector Performance Summary": """
        SELECT sector, AVG(daily_return_mean) as avg_return, COUNT(*) as count 
        FROM sector_summary_statistics 
        GROUP BY sector 
        ORDER BY avg_return DESC;
        """,
        "Sample Data from Ultimate Table": """
        SELECT * FROM ultimate_stock_analysis 
        ORDER BY date DESC 
        LIMIT 5;
        """
    }
    
    selected_quick = st.selectbox("Select a quick query", ["Custom Query"] + list(quick_queries.keys()))
    
    if selected_quick != "Custom Query":
        query = quick_queries[selected_quick]
    else:
        query = ""
    
    # Query input
    st.subheader("SQL Query")
    custom_query = st.text_area(
        "Enter your SQL query:",
        value=query,
        height=150,
        help="Query the following tables: ultimate_stock_analysis, sector_daily_analysis, industry_daily_analysis, sector_summary_statistics, industry_summary_statistics, merged_time_series_data"
    )
    
    # Execute query
    if st.button("Execute Query", type="primary"):
        if custom_query.strip():
            try:
                with st.spinner("Executing query..."):
                    result = load_data_from_rds(custom_query, "custom query")
                    
                if not result.empty:
                    st.success(f"Query executed successfully! Found {len(result)} records.")
                    
                    # Display results
                    st.subheader("Query Results")
                    st.dataframe(result, use_container_width=True)
                    
                    # Download option
                    csv = result.to_csv(index=False)
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime='text/csv'
                    )
                else:
                    st.warning("Query returned no results.")
                    
            except Exception as e:
                st.error(f"Query failed: {str(e)}")
        else:
            st.warning("Please enter a SQL query.")

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Cloud Computing Project**")
with col2:
    st.markdown(f"*Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
with col3:
    st.markdown("*Deployed on AWS EC2 + RDS*")