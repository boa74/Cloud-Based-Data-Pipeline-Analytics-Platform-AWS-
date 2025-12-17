# Cloud Computing Project - Code Documentation

## 📁 Project Structure

```
submission/
├── README.md                          # This documentation file
├── requirements.txt                   # Python dependencies
├── src/                              # Source code directory
│   ├── streamlit_app/                # Dashboard application
│   │   └── app_cloud.py             # Main Streamlit dashboard
│   ├── etl/                          # ETL pipeline scripts
│   │   ├── upload_to_rds.py         # Data upload to RDS
│   │   ├── create_ultimate_dataset.py # Ultimate dataset creation
│   │   ├── create_final_dataset.py   # Final dataset processing
│   │   └── create_cleaned_datasets.py # Data cleaning pipeline
│   └── analysis/                     # Analysis scripts
│       ├── Cloud_Computing_Project_analysis.py # Main analysis
│       └── rds_connection.py         # RDS connection utilities
├── sql/                              # Database schema
│   └── Cloud_Computing_Project_SQLSchema.sql # PostgreSQL schema
└── docs/                             # Documentation
    └── ARCHITECTURE_FLOW.md          # Architecture overview
```

## 🎯 Project Overview

This project demonstrates a comprehensive **Cloud Computing Data Pipeline** using AWS services to analyze the relationship between market volatility, depression index, and various economic indicators.

### Key Technologies:
- **AWS S3**: Raw data storage
- **AWS RDS (PostgreSQL)**: Structured data storage  
- **AWS EC2**: Compute instances for ETL and dashboard
- **Streamlit**: Interactive web dashboard
- **Python**: Data processing and analysis
- **Plotly**: Data visualization

## 📊 Data Architecture

```
S3 (Raw Data) → EC2 (ETL Processing) → RDS (PostgreSQL) → EC2 (Streamlit Dashboard)
```

### Data Flow:
1. **Raw CSV files** stored in S3 bucket
2. **ETL pipeline** processes and cleans data on EC2
3. **Cleaned data** stored in PostgreSQL RDS
4. **Interactive dashboard** reads from RDS and displays analytics

## 🔧 Core Components

### 1. **Streamlit Dashboard** (`src/streamlit_app/app_cloud.py`)

**Purpose**: Interactive web application for data visualization and analysis

**Key Features**:
- 📊 **Overview**: Key metrics and performance indicators
- 🏢 **Sector Analysis**: Sector-level performance tracking
- 🏭 **Industry Analysis**: Industry-specific insights
- 📈 **Stock Analysis**: Individual stock performance
- 🔗 **Correlation Analysis**: Complete correlation matrix with top 5 strongest correlations
- 😔 **Depression Analysis**: Relationship between depression index and market volatility
- 🏭 **Industry Volatility Analysis**: How different industries respond to depression levels
- ⚡ **Real-time Query**: Custom SQL query interface

**Technical Implementation**:
- **Database Connection**: PostgreSQL RDS with connection pooling
- **Caching**: 10-minute TTL caching for performance optimization
- **Error Handling**: Comprehensive error handling and user feedback
- **Responsive Design**: Multi-column layouts and interactive charts

```python
# Key code structure
@st.cache_resource
def get_db_connection():
    # PostgreSQL connection with error handling
    
@st.cache_data(ttl=600)
def load_data_from_rds(query, description="data"):
    # Data loading with caching
    
# Navigation and page routing
page = st.sidebar.selectbox("Select Analysis Page", [...])
```

### 2. **ETL Pipeline** (`src/etl/`)

#### **A. Data Upload** (`upload_to_rds.py`)
**Purpose**: Upload processed datasets to PostgreSQL RDS

**Key Functions**:
- Database connection management
- Batch data insertion with error handling
- Table creation and schema validation

```python
def upload_dataframe_to_rds(df, table_name, connection_params):
    # Bulk upload with transaction handling
```

#### **B. Ultimate Dataset Creation** (`create_ultimate_dataset.py`)
**Purpose**: Merge all data sources into comprehensive analysis dataset

**Process**:
1. Load stock data, depression data, and rainfall data
2. Calculate technical indicators (volatility, returns)
3. Merge datasets on date
4. Create categorical variables for analysis

#### **C. Final Dataset Processing** (`create_final_dataset.py`)
**Purpose**: Create aggregated views and summary statistics

**Output Tables**:
- `sector_daily_analysis`: Sector-level daily metrics
- `industry_daily_analysis`: Industry-level daily metrics
- `merged_time_series_data`: Complete time series for correlation analysis

#### **D. Data Cleaning** (`create_cleaned_datasets.py`)
**Purpose**: Clean and standardize raw data

**Cleaning Steps**:
- Date format standardization
- Missing value handling
- Outlier detection and treatment
- Column name normalization

### 3. **Analysis Scripts** (`src/analysis/`)

#### **A. Main Analysis** (`Cloud_Computing_Project_analysis.py`)
**Purpose**: Comprehensive statistical analysis and insights generation

**Analysis Types**:
- **Correlation Analysis**: Pearson correlation coefficients
- **Volatility Analysis**: Rolling volatility calculations
- **Sector Performance**: Risk-return profiling
- **Time Series Analysis**: Trend and seasonality detection

#### **B. RDS Connection** (`rds_connection.py`)
**Purpose**: Centralized database connection utilities

**Features**:
- Connection pooling
- Retry logic
- Environment variable management
- Query execution helpers

### 4. **Database Schema** (`sql/Cloud_Computing_Project_SQLSchema.sql`)

**Purpose**: PostgreSQL database structure definition

**Key Tables**:

```sql
-- Ultimate stock analysis table
CREATE TABLE ultimate_stock_analysis (
    date DATE,
    ticker VARCHAR(10),
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume BIGINT,
    volatility_7 DECIMAL,
    depression_index DECIMAL,
    -- ... additional columns
);

-- Sector daily analysis
CREATE TABLE sector_daily_analysis (
    date DATE,
    sector VARCHAR(100),
    daily_return DECIMAL,
    volatility_7d DECIMAL,
    depression_index DECIMAL,
    -- ... sector metrics
);
```

## 🔍 Key Analysis Features

### **1. Depression Index Analysis**
- **Correlation with Volatility**: Measures relationship between market stress and depression indicators
- **Time Series Trends**: Tracks depression index over time with market overlays
- **Category Analysis**: Compares market behavior across depression levels (Low/Medium/High)
- **Rolling Correlations**: 30-day moving correlations for trend analysis

### **2. Correlation Analysis**
- **Complete Matrix**: All numerical variables correlation heatmap
- **Top 5 Correlations**: Strongest relationships with statistical significance
- **Network Visualization**: Interactive correlation network for strong relationships (|r| > 0.3)
- **Strength Classification**: Very Strong (>0.8), Strong (>0.6), Moderate (>0.4), Weak (>0.2)

### **3. Industry Volatility Analysis**
- **Depression Sensitivity**: How each industry responds to depression levels
- **Volatility Heatmaps**: Industry × Depression Level volatility matrix
- **Sensitivity Rankings**: Percentage change in volatility between depression states
- **Statistical Summaries**: ANOVA-style analysis of variance across conditions

## 🚀 Deployment Architecture

### **AWS Services Used**:

1. **Amazon S3**
   - **Purpose**: Raw data storage
   - **Configuration**: Public read access for data files
   - **Cost**: ~$0.02/month for small datasets

2. **Amazon RDS (PostgreSQL)**
   - **Instance**: db.t3.micro (Free Tier eligible)
   - **Storage**: 20GB General Purpose SSD
   - **Configuration**: Multi-AZ for high availability
   - **Cost**: Free Tier for 12 months

3. **Amazon EC2**
   - **Instance Type**: t2.micro (Free Tier eligible)
   - **OS**: Amazon Linux 2
   - **Applications**: ETL processing + Streamlit dashboard
   - **Cost**: Free Tier for 750 hours/month

### **Deployment Process**:

```bash
# 1. ETL Pipeline Execution
python3 src/etl/create_cleaned_datasets.py
python3 src/etl/create_ultimate_dataset.py
python3 src/etl/upload_to_rds.py

# 2. Dashboard Launch
streamlit run src/streamlit_app/app_cloud.py --server.port 8501 --server.address 0.0.0.0
```

## 📈 Performance Optimizations

### **1. Database Optimizations**
- **Connection Pooling**: Reduces connection overhead
- **Query Caching**: 10-minute TTL for frequently accessed data
- **Indexed Columns**: Date and ticker columns for fast lookups
- **Batch Processing**: Bulk inserts for large datasets

### **2. Application Optimizations**
- **Streamlit Caching**: `@st.cache_data` for expensive operations
- **Lazy Loading**: Data loaded only when needed
- **Progressive Enhancement**: Basic functionality first, advanced features optional
- **Error Boundaries**: Graceful degradation on data issues

## 🔧 Installation and Setup

### **Prerequisites**:
```bash
# Python 3.8+
pip install -r requirements.txt

# AWS CLI configured with access keys
aws configure
```

### **Environment Variables**:
```bash
# Database Configuration
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=postgres

# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
```

### **Running the Application**:
```bash
# Local development
streamlit run src/streamlit_app/app_cloud.py

# Production deployment
streamlit run src/streamlit_app/app_cloud.py --server.port 8501 --server.address 0.0.0.0
```

## 📊 Data Sources

1. **S&P 500 Stock Data**: Daily OHLCV data for S&P 500 companies
2. **Depression Index**: News-based sentiment analysis for depression indicators  
3. **Rainfall Data**: National rainfall averages as external economic factor
4. **Company Information**: Sector and industry classifications

## 🎓 Academic Value

This project demonstrates:

- **Cloud Architecture Design**: Multi-tier application deployment
- **Data Pipeline Engineering**: ETL processes with error handling
- **Statistical Analysis**: Correlation, volatility, and time series analysis
- **Data Visualization**: Interactive dashboards with business insights
- **Database Design**: Normalized schema with performance optimization
- **DevOps Practices**: Environment management and deployment automation

## 📝 Key Learning Outcomes

1. **AWS Services Integration**: Practical experience with S3, RDS, and EC2
2. **Data Engineering**: Real-world ETL pipeline development
3. **Statistical Computing**: Advanced analysis using Python scientific stack
4. **Web Application Development**: Interactive dashboard creation
5. **Database Management**: PostgreSQL administration and optimization
6. **Cloud Cost Management**: Free Tier utilization and cost optimization

---

## 🎯 Conclusion

This project successfully demonstrates a complete cloud-based data analytics pipeline, combining modern cloud services with sophisticated data analysis techniques. The application provides actionable insights into market behavior and economic indicators while showcasing best practices in cloud architecture and data engineering.

The modular design allows for easy extension and maintenance, while the comprehensive documentation ensures reproducibility and educational value for cloud computing coursework.