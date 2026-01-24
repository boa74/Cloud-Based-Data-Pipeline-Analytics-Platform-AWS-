# Database Schema Documentation

## Overview
This directory contains the PostgreSQL database schema for the Cloud-Based Data Pipeline & Analytics Platform. The schema defines the raw data tables that serve as the foundation for market analysis, sentiment tracking, and weather correlation studies.

---

## Schema File
- **`schema.sql`** - Complete database schema with table definitions and sample queries

---

## Database Tables

### 📈 **Financial Market Data**

#### `stock_daily`
**Purpose**: Individual stock trading data for S&P 500 companies
- **Primary Key**: (trade_date, ticker)
- **Fields**: trade_date, ticker, open_price, high_price, low_price, close_price, volume
- **Usage**: Foundation for individual stock analysis and sector/industry aggregations

#### `sp500_daily`
**Purpose**: S&P 500 index performance with calculated metrics
- **Primary Key**: trade_date
- **Fields**: trade_date, close_spx, high_spx, low_spx, open_spx, volume_spx, daily_return, volatility_7
- **Usage**: Market benchmark analysis and correlation studies

### 🌧️ **Weather Data**

#### `rainfall_daily`
**Purpose**: Daily precipitation data for all 50 US states
- **Primary Key**: obs_date
- **Fields**: obs_date, [50 state columns with rainfall amounts]
- **Usage**: Weather-market correlation analysis and alternative data research

### 😔 **Sentiment Data**

#### `depression_weekly_index`
**Purpose**: Weekly depression sentiment index values
- **Primary Key**: week_end_date
- **Fields**: week_end_date, depression_index
- **Usage**: Weekly sentiment trend analysis

#### `news_depression_daily`
**Purpose**: Daily depression-related word counts from news articles
- **Primary Key**: news_date
- **Fields**: news_date, depression_word_count, total_articles, avg_depression_per_article
- **Usage**: Daily sentiment analysis and behavioral finance research

### 📅 **Time Dimension**

#### `dim_date`
**Purpose**: Date dimension table for time-based analytics
- **Primary Key**: date_id
- **Fields**: date_id, year, month, day, dow (day of week), week
- **Usage**: Time series analysis and date-based aggregations

---

## Data Relationships

### Primary Data Flow:
```
Raw Tables (schema.sql) → ETL Processing → Analytical Tables → Dashboard
```

### Key Joins:
All tables are linked by date fields:
- `stock_daily.trade_date`
- `sp500_daily.trade_date` 
- `rainfall_daily.obs_date`
- `news_depression_daily.news_date`
- `depression_weekly_index.week_end_date`

### Sample Query:
The schema includes a sample query demonstrating multi-table joins to analyze correlations between:
- Stock performance (AAPL example)
- S&P 500 index performance
- Weather conditions (California rainfall)
- Depression sentiment signals

---

## Usage Instructions

### 1. **Database Setup**
```sql
-- Run the schema file to create all tables
\i schema.sql
```

### 2. **Data Loading**
After creating tables, use the ETL scripts to:
- Load raw data from external sources
- Process and transform data
- Create analytical datasets

### 3. **Analytical Queries**
Use the base tables for:
- Custom correlation analysis
- Historical trend studies  
- Alternative data research
- Behavioral finance studies

---

## ETL Integration

### Input to ETL Pipeline:
These raw tables serve as input to the ETL process that creates:
- `ultimate_stock_analysis` - Comprehensive individual stock dataset
- `sector_daily_analysis` - Sector-level aggregated data
- `industry_daily_analysis` - Industry-level aggregated data
- `merged_time_series_data` - Time series with all indicators

### Data Quality Considerations:
- **Date Alignment**: All tables use consistent date formats
- **Missing Data**: ETL processes handle null values and data gaps
- **Data Types**: Consistent use of double precision for numerical data
- **Primary Keys**: Ensure data integrity and enable efficient joins

---

## Research Applications

### Behavioral Finance:
- Depression sentiment impact on market volatility
- News sentiment correlation with trading volumes
- Psychological market indicators

### Alternative Data Analysis:
- Weather pattern correlation with market performance
- Non-traditional indicator effectiveness
- Cross-domain data relationships

### Risk Management:
- Multi-factor volatility analysis
- Systematic risk identification
- Correlation-based portfolio optimization

### Market Microstructure:
- Daily trading pattern analysis
- Volume-price relationships
- Market efficiency studies

---

## Technical Specifications

### Database: PostgreSQL
### Data Types:
- **Dates**: `date` format (YYYY-MM-DD)
- **Prices/Volumes**: `double precision` for accuracy
- **Identifiers**: `text` for flexibility
- **Counts**: `integer` for whole numbers

### Performance Considerations:
- Primary keys on date fields for efficient time-based queries
- Composite key (date, ticker) for stock data to ensure uniqueness
- Indexed date columns for fast time series analysis

### Scalability:
- Schema supports historical data loading
- Extensible design for additional data sources
- Optimized for analytical workloads

---

## Future Enhancements

### Potential Schema Extensions:
- **Company metadata table**: Sector/industry classifications
- **Economic indicators table**: GDP, inflation, interest rates
- **Social media sentiment**: Twitter/Reddit sentiment scores
- **News categorization**: Topic-based news classification
- **Market volatility indices**: VIX and other volatility measures

### Performance Optimizations:
- Partitioning strategies for large historical datasets
- Additional indices for frequently-queried fields
- Materialized views for complex aggregations