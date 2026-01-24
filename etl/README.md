# ETL Pipeline

## Quick Start
```bash
# Run complete pipeline
python 01_data_cleaning.py
python 02_transform_industry.py  
python 03_transform_complete.py
python 04_load_to_rds.py
```

## Scripts (run in order)

**01_data_cleaning.py**
- Cleans raw data and filters to 2017-2018 timeframe
- Output: `stock_data_wiki_clean.csv`

**02_transform_industry.py** 
- Aggregates stock data by industry
- Output: `industry_daily_analysis.csv`

**03_transform_complete.py**
- Creates comprehensive individual stock dataset
- Output: `ultimate_stock_analysis.csv`

**04_load_to_rds.py**
- Uploads final datasets to PostgreSQL RDS
- Configure database connection in script

## Requirements
```bash
pip install -r ../requirements.txt
```

Required CSV files:
- `stock_data.csv`
- `company_info.csv` 
- `ccnews_depression_daily_count_final.csv`
- Weather and sentiment data files

## Database Setup
Edit connection details in `04_load_to_rds.py`:
```python
DB_CONFIG = {
    'host': 'your-rds-endpoint',
    'database': 'your-database-name', 
    'user': 'your-username',
    'password': 'your-password'
}
```

## Troubleshooting
- **Connection errors**: Check RDS endpoint and credentials
- **Missing files**: Verify CSV files are present
- **Memory errors**: Process smaller data chunks