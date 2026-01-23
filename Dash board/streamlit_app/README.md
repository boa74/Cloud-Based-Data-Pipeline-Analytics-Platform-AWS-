# Cloud Computing Project Dashboard - Analysis & Purpose Documentation

## Overview
This Streamlit dashboard provides comprehensive financial market analysis using data from PostgreSQL RDS, deployed on AWS EC2. The application analyzes relationships between market performance, economic indicators, and sentiment data to support investment decisions and behavioral finance research.

---

## Analysis Modules & Purposes

### 1. **Overview Analysis**
**What was analyzed:**
- Sector performance metrics (average daily returns, risk profiles)
- Industry performance statistics and rankings
- Risk vs return scatter plots across sectors
- Top performing sectors identification

**Purpose:**
- Provide high-level market performance summary
- Identify best performing sectors and industries for investment focus
- Visualize risk-return relationships to guide portfolio allocation decisions
- Support strategic asset allocation through sector comparison

---

### 2. **S&P 500 Indicators Analysis**
**What was analyzed:**
- S&P 500 index correlations with external market indicators
- Volatility (7-day rolling), depression sentiment index, national rainfall data
- Depression word count from news articles
- Rolling correlation analysis over time
- Multi-axis time series relationships

**Purpose:**
- Test how external factors (weather patterns, public sentiment) correlate with market movements
- Identify potential leading indicators for market prediction
- Analyze stability and strength of correlations over different time periods
- Support development of alternative investment strategies based on non-traditional indicators

---

### 3. **Sector Analysis**
**What was analyzed:**
- Sector-level performance metrics over customizable time periods
- Daily returns, closing prices, trading volumes, price change percentages
- Interactive date filtering and sector selection
- Comparative performance visualization across sectors

**Purpose:**
- Enable detailed sector performance comparison and trend analysis
- Support sector rotation investment strategies
- Identify cyclical patterns and seasonal trends in different market sectors
- Provide granular data for sector-specific investment decisions

---

### 4. **Industry Analysis**
**What was analyzed:**
- Industry-level performance rankings and statistics
- Top performing industries by average daily returns
- Individual industry detailed metrics and characteristics
- Industry-specific risk and return profiles

**Purpose:**
- Drill down from sector to industry level for more targeted analysis
- Identify specific industry opportunities within broader market sectors
- Support focused industry investment strategies
- Enable industry-specific stock selection within chosen sectors

---

### 5. **Stock Analysis**
**What was analyzed:**
- Individual stock performance tracking over time
- Stock price charts and daily return patterns
- Volatility measurements and trends
- Company classification information (sector, industry)

**Purpose:**
- Analyze individual equity performance and risk characteristics
- Support stock selection within chosen industries and sectors
- Track specific company performance metrics for portfolio management
- Enable detailed fundamental and technical analysis of individual securities

---

### 6. **Correlation Analysis**
**What was analyzed:**
- Comprehensive correlation matrix of all numerical market variables
- Network visualization of variable relationships
- Top 5 strongest correlations identification and ranking
- Interactive correlation exploration tools

**Purpose:**
- Identify hidden relationships and dependencies between market variables
- Support diversification strategies by finding uncorrelated or negatively correlated assets
- Understand systematic risk factors affecting multiple market components
- Enable advanced portfolio construction based on correlation insights

---

### 7. **Depression Analysis** (Behavioral Finance Focus)
**What was analyzed:**
- Relationship between depression sentiment index and market volatility
- Market behavior during high vs low depression sentiment periods
- Rolling correlation analysis between sentiment and market performance
- Depression level categorization impact on returns and volatility

**Purpose:**
- Test behavioral finance hypothesis that negative sentiment affects market volatility
- Understand psychological and emotional impacts on market performance
- Develop sentiment-based trading and investment strategies
- Validate market efficiency theories through sentiment analysis

---

### 8. **Industry Volatility Analysis**
**What was analyzed:**
- Industry-specific responses to varying sentiment and depression levels
- Volatility patterns across industries during different sentiment periods
- Industry sensitivity analysis to external sentiment factors
- Heatmap visualization of volatility by industry and sentiment level

**Purpose:**
- Identify which industries are most/least sensitive to sentiment changes
- Support defensive vs aggressive investment strategies based on market sentiment
- Understand sector rotation opportunities during sentiment shifts
- Enable sentiment-aware industry allocation strategies

---

### 9. **Real-time Query Interface**
**What was analyzed:**
- Custom SQL query capabilities on live database
- Ad-hoc data exploration and validation
- Database schema exploration and data quality checks
- Flexible analysis beyond predefined dashboard components

**Purpose:**
- Provide flexibility for custom analysis and research hypothesis testing
- Enable data validation and quality assurance checks
- Support exploratory data analysis for new research questions
- Allow advanced users to perform custom queries and analysis

---

## Overall Research Objectives

### Primary Hypotheses Tested:
1. **Behavioral Finance Impact**: Whether psychological factors (depression/sentiment) significantly affect market behavior and volatility
2. **Cross-Market Correlations**: How different asset classes, sectors, and external factors interact and influence each other
3. **Risk Management**: Understanding volatility patterns across sectors, industries, and time periods for better risk assessment
4. **Market Efficiency**: Testing whether sentiment and external factors provide predictive value for market movements

### Investment Strategy Support:
- **Portfolio Construction**: Data-driven insights for optimal asset allocation across sectors and industries
- **Risk Management**: Volatility analysis and correlation insights for risk-adjusted portfolio construction
- **Timing Strategies**: Sentiment and indicator analysis for market timing decisions
- **Sector Rotation**: Performance analysis to support dynamic sector allocation strategies

### Academic Research Applications:
- **Behavioral Finance**: Testing psychological market impact theories
- **Market Microstructure**: Understanding how various factors influence market dynamics
- **Alternative Data**: Validating use of non-traditional indicators (weather, sentiment) in financial analysis
- **Risk Factor Analysis**: Identifying systematic risk factors across different market segments

---

## Technical Implementation

### Data Sources:
- **Stock Market Data**: Individual stock prices, volumes, returns for S&P 500 companies
- **Sector/Industry Classifications**: GICS sector and industry groupings
- **Economic Indicators**: S&P 500 index, volatility measures
- **Sentiment Data**: Depression-related word counts from news articles
- **Weather Data**: National rainfall averages
- **Time Series Data**: Comprehensive historical market and indicator data

### Technology Stack:
- **Frontend**: Streamlit interactive dashboard
- **Backend**: PostgreSQL RDS database
- **Deployment**: AWS EC2 with real-time database connectivity
- **Analysis Libraries**: Pandas, NumPy, SciPy, Plotly for visualization
- **Statistical Analysis**: Correlation analysis, rolling statistics, trend analysis

### Key Features:
- **Real-time Data**: Live connection to PostgreSQL RDS
- **Interactive Visualizations**: Dynamic charts, heatmaps, and scatter plots
- **Custom Analysis**: SQL query interface for ad-hoc analysis
- **Responsive Design**: Multi-column layouts optimized for different screen sizes
- **Caching**: Optimized performance with intelligent data caching

---

## Usage Guidelines

### For Investment Professionals:
- Use sector and industry analysis for portfolio allocation decisions
- Leverage correlation analysis for risk management and diversification
- Monitor sentiment indicators for timing and strategy adjustments

### For Researchers:
- Utilize the depression analysis for behavioral finance research
- Explore custom queries for hypothesis testing
- Analyze rolling correlations for market dynamics research

### For Students:
- Study sector performance patterns for market understanding
- Explore correlation networks to understand market relationships
- Use individual stock analysis for security valuation practice

---

## Future Enhancements

### Potential Extensions:
- **Machine Learning Models**: Predictive modeling based on identified correlations
- **Real-time Alerts**: Notification system for significant market events or correlation changes
- **Extended Data Sources**: Integration of additional alternative data sources
- **Advanced Analytics**: Statistical significance testing, regression analysis, time series forecasting
- **Portfolio Optimization**: Modern portfolio theory implementation with correlation insights