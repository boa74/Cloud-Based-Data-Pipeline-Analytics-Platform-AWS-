# ETL Pipeline Documentation

## Overview
This directory contains the Extract, Transform, Load (ETL) pipeline for the Cloud-Based Data Pipeline & Analytics Platform. The ETL process transforms raw data into analysis-ready datasets by cleaning, aggregating, and loading data into PostgreSQL RDS for dashboard consumption.

---

## Pipeline Scripts

### 📝 **Execution Order** (Must run sequentially)

#### 1. `01_data_cleaning.py`
**Purpose**: Data cleaning and date range filtering
- **Input**: Raw CSV files from data collection
- **Output**: `stock_data_wiki_clean.csv` and other cleaned datasets
- **Process**: 
  - Loads depression news data to define analysis timeframe
  - Filters stock data to match depression news date range (2017-01-01 to 2018-07-05)
  - Merges stock data with S&P 500 company information
  - Creates cleaned datasets for downstream processing

#### 2. `02_transform_industry.py` 
**Purpose**: Industry-level data aggregation and transformation
- **Input**: Cleaned datasets from step 1
- **Output**: `industry_daily_analysis.csv`
- **Process**:
  - Aggregates individual stock data by industry and date
  - Combines with depression index and weather data
  - Calculates industry-level metrics and correlations
  - Creates industry-focused analytical dataset

#### 3. `03_transform_complete.py`
**Purpose**: Complete data integration for individual stock analysis
- **Input**: All processed datasets from previous steps
- **Output**: `ultimate_stock_analysis.csv`
- **Process**:
  - Integrates individual stock data with all external factors
  - Adds company metadata (sector, industry classifications)
  - Combines depression sentiment, weather, and market indicators
  - Creates comprehensive dataset for detailed stock-level analysis

#### 4. `04_load_to_rds.py`
**Purpose**: Upload final datasets to PostgreSQL RDS
- **Input**: All final processed CSV files
- **Output**: Data loaded into RDS tables
- **Process**:
  - Establishes connection to PostgreSQL RDS instance
  - Creates tables if they don't exist
  - Uploads all final datasets to database
  - Enables dashboard and analytics access

---

## Data Flow Architecture

```
Raw Data Sources
       ↓
[01] Data Cleaning & Filtering
       ↓
Cleaned Datasets
       ↓
[02] Industry Aggregation ──┐
       ↓                    │
[03] Complete Integration ──┤
       ↓                    │
Final Analysis Datasets     │
       ↓                    ↓
[04] Load to RDS Database
       ↓
Dashboard & Analytics
```

---

## Prerequisites

### 🐍 **Python Dependencies**
Install required packages:
```bash
pip install -r ../requirements.txt
```

**Key packages:**
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `psycopg2` - PostgreSQL database adapter
- `sqlalchemy` - SQL toolkit and ORM

### 📊 **Required Data Files**
Ensure these CSV files are available before running:
- `ccnews_depression_daily_count_final.csv`
- `stock_data.csv`
- `company_info.csv`
- `sp500.csv`
- Weather and sentiment data files

### 🗄️ **Database Configuration**
Configure RDS connection in `04_load_to_rds.py`:
```python
DB_CONFIG = {
    'host': 'your-rds-endpoint',
    'port': 5432,
    'database': 'your-database-name', 
    'user': 'your-username',
    'password': 'your-password'
}
```

---

## Usage Instructions

### **Method 1: Run Complete Pipeline**
Execute all scripts in sequence:
```bash
# Navigate to ETL directory
cd etl/

# Run pipeline in order
python 01_data_cleaning.py
python 02_transform_industry.py  
python 03_transform_complete.py
python 04_load_to_rds.py
```

### **Method 2: Run Individual Steps**
For development/debugging, run scripts individually:

```bash
# Step 1: Clean raw data
python 01_data_cleaning.py

# Step 2: Create industry aggregations
python 02_transform_industry.py

# Step 3: Create complete integration
python 03_transform_complete.py

# Step 4: Upload to RDS
python 04_load_to_rds.py
```

### **Method 3: Automated Pipeline**
Create a shell script for automated execution:
```bash
#!/bin/bash
echo "Starting ETL Pipeline..."
python 01_data_cleaning.py && \
python 02_transform_industry.py && \
python 03_transform_complete.py && \
python 04_load_to_rds.py
echo "ETL Pipeline Complete!"
```

---

## Output Datasets

### 📈 **Final Analysis Tables**

#### `ultimate_stock_analysis`
**Purpose**: Individual stock analysis with all factors
- **Granularity**: Daily, per stock ticker
- **Fields**: Stock data + company info + sentiment + weather + market indicators
- **Usage**: Detailed stock-level correlation analysis

#### `industry_daily_analysis`
**Purpose**: Industry-level aggregated analysis
- **Granularity**: Daily, per industry sector
- **Fields**: Aggregated stock metrics + external factors
- **Usage**: Sector comparison and industry trend analysis

#### `merged_time_series_data`
**Purpose**: Time series data with all indicators
- **Granularity**: Daily time series
- **Fields**: Market indices + sentiment + weather + volatility
- **Usage**: Time series analysis and forecasting

### 📊 **Intermediate Datasets**
- `stock_data_wiki_clean.csv` - Cleaned stock data with company info
- `sector_daily_analysis.csv` - Sector-level aggregations
- Various merged datasets for quality control

---

## Quality Assurance

### 🔍 **Data Validation Checks**
Each script includes validation:
- **Row count verification**: Before/after processing
- **Date range consistency**: Ensuring proper time alignment
- **Missing data handling**: Null value identification and treatment
- **Data type validation**: Ensuring correct formats

### 📊 **Processing Statistics**
Scripts output processing statistics:
```
Original stock data: 1,234,567 rows
After filtering to date range: 987,654 rows
Final processed dataset: 876,543 rows
Date range: 2017-01-01 to 2018-07-05
```

### ⚠️ **Error Handling**
- Database connection error recovery
- Missing file error messages
- Data validation failure alerts
- Rollback capabilities for database operations

---

## Performance Considerations

### 💾 **Memory Usage**
- Large datasets processed in chunks where possible
- Garbage collection after major operations
- Memory-efficient pandas operations

### ⏱️ **Execution Time**
Typical execution times:
- `01_data_cleaning.py`: ~2-3 minutes
- `02_transform_industry.py`: ~5-7 minutes
- `03_transform_complete.py`: ~8-10 minutes
- `04_load_to_rds.py`: ~3-5 minutes
- **Total Pipeline**: ~20-25 minutes

### 🔄 **Optimization Tips**
- Run during off-peak hours for RDS performance
- Ensure adequate disk space for intermediate files
- Use SSD storage for faster I/O operations
- Monitor memory usage for large datasets

---

## Troubleshooting

### ❌ **Common Issues**

#### Connection Errors
```python
psycopg2.OperationalError: could not connect to server
```
**Solution**: Verify RDS endpoint, credentials, and security groups

#### Memory Errors
```python
MemoryError: Unable to allocate array
```
**Solution**: Process data in smaller chunks or increase system memory

#### Missing Files
```python
FileNotFoundError: [Errno 2] No such file or directory
```
**Solution**: Verify all required CSV files are present and paths are correct

### 🔧 **Debug Mode**
Enable detailed logging by modifying logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

### 📞 **Support**
- Check log files for detailed error messages
- Verify database connectivity before running pipeline
- Ensure all dependencies are installed correctly

---

## Integration with Other Components

### 🔗 **Database Schema Integration**
- Loads data into tables defined in [../sql/schema.sql](../sql/schema.sql)
- Follows naming conventions from database schema
- Maintains referential integrity with existing tables

### 📊 **Dashboard Integration**
- Processed data feeds directly into Streamlit dashboard
- Dashboard queries optimized tables created by ETL
- Real-time data availability after ETL completion

### 🏗️ **Architecture Integration**
- Part of the complete data pipeline architecture
- Integrates with Lambda functions for automated processing
- Supports both batch and incremental processing modes

---

## Future Enhancements

### 🚀 **Planned Improvements**
- **Incremental Processing**: Process only new/changed data
- **Parallel Processing**: Multi-threaded execution for better performance
- **Data Validation Framework**: Automated data quality checks
- **Error Recovery**: Automatic retry mechanisms
- **Monitoring Integration**: CloudWatch metrics and alerts

### 📈 **Scalability Enhancements**
- **Apache Airflow Integration**: Workflow orchestration
- **AWS Glue Migration**: Serverless ETL processing
- **Data Partitioning**: Improved query performance
- **Caching Layer**: Redis for intermediate results

### 🔄 **Process Improvements**
- **Configuration Management**: External config files
- **Environment Management**: Dev/staging/production pipelines
- **Testing Framework**: Unit tests for each transformation
- **Documentation Automation**: Auto-generated data lineage