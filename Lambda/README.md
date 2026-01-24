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

### 1. Create Lambda Function
- Upload `lambda_function.py` to AWS Lambda
- Set environment variable: `BUCKET_NAME` = your-s3-bucket-name
- Configure timeout: 15 seconds (for API calls)

### 2. Create EventBridge Rule (AWS Console)
1. Go to **EventBridge** → **Rules** 
2. Click **Create Rule**
3. **Name**: `daily-data-ingestion` 
4. **Rule type**: Schedule
5. **Schedule pattern**: Cron expression
6. **Cron expression**: `0 8 * * ? *` (8:00 AM UTC daily)
7. **Target**: AWS Lambda function
8. **Function**: Select your Lambda function
9. **Create Rule**

### 3. Configure Permissions
Lambda needs S3 write permissions:
1. Go to **Lambda** → **Configuration** → **Permissions**
2. Click role name to open IAM
3. Attach policy: `AmazonS3FullAccess` (or create custom S3 write policy)

### 4. Test Setup
- **Manual test**: Test Lambda function in AWS console
- **Schedule verification**: Check CloudWatch logs after 8:00 AM UTC
- **Data verification**: Confirm JSON files appear in S3 bucket

## Monitoring
- CloudWatch logs for execution status
- S3 bucket for successful data ingestion verification
