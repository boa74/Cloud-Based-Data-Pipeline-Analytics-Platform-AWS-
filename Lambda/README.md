# AWS Lambda Functions

Daily data ingestion service triggered by EventBridge scheduler.

## Architecture
**EventBridge** (8 AM daily) → **Lambda** → **S3** (raw data storage)

## Function: `lambda_function.py`

**Trigger**: EventBridge rule - Daily at 8:00 AM UTC  
**Schedule**: `cron(0 8 * * ? *)`

**Data Sources**:
- Weather API (Open-Meteo) - Washington DC daily forecast
- Stock API (Yahoo Finance) - S&P 500 daily data

**Output**: Raw JSON files stored in S3:
- `raw/weather/weather_YYYY-MM-DD.json`
- `raw/sp500/sp500_YYYY-MM-DD.json`

## Setup Requirements

1. **EventBridge Rule**: Create scheduled rule with cron expression
2. **Lambda Permissions**: S3 write access to target bucket
3. **Environment Variable**: `BUCKET_NAME` (defaults to "apan5450-stock")

## Monitoring
- CloudWatch logs for execution status
- S3 bucket for successful data ingestion verification
