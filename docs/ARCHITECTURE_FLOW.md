# Architecture Data Flow Guide

## Overall Data Flow

```
┌─────────┐      ┌──────────────┐      ┌─────────┐      ┌──────────────┐
│   S3    │─────▶│  EC2 (ETL)   │─────▶│   RDS   │─────▶│ EC2 (Streamlit)│
│ (CSV)   │      │  (Python)    │      │ (DB)    │      │  (Dashboard)  │
└─────────┘      └──────────────┘      └─────────┘      └──────────────┘
  Raw Data       Data Processing      Data Storage       Visualization
```

## Step-by-Step Workflow

### 📦 Step 1: Upload Data to S3

**Purpose**: Safely store raw CSV files in cloud storage

**Tasks**:
1. Create S3 bucket
2. Create `raw_data/` folder
3. Upload CSV files:
   - `sp500.csv`
   - `ccnews_depression_daily_count_final.csv`
   - `rainfall.csv`
   - `depression_index.csv`

**Status**: ✅ S3 bucket is already created, just need to upload CSV files!

**Verification**:
```
s3://your-bucket-name/
└── raw_data/
    ├── sp500.csv
    ├── ccnews_depression_daily_count_final.csv
    ├── rainfall.csv
    └── depression_index.csv
```

---

### 🔄 Step 2: Run ETL Pipeline on EC2

**Purpose**: Download data from S3, clean it, and transform it for RDS format

**Tasks**:
1. Create EC2 instance
2. Upload project files
3. Configure environment variables (`.env` file)
4. Run ETL script: `python3 etl/s3_to_rds_pipeline.py`

**What happens?**
```
Tasks executed on EC2:
├── Download CSV files from S3
├── Clean data (date formats, column names)
├── Calculate metrics (daily_return, volatility, etc.)
└── Upload to RDS
```

**Requirements**:
- ✅ EC2 instance (t2.micro recommended)
- ✅ Access Key ID & Secret Key (for S3 access)
- ✅ RDS connection info (DB_HOST, DB_USER, DB_PASS, etc.)

---

### 💾 Step 3: Store Data in RDS

**Purpose**: Store cleaned data in structured PostgreSQL database

**Tasks**:
1. Create RDS PostgreSQL instance
2. Create database schema (run SQL)
3. Automatic data upload from ETL pipeline

**Database Tables**:
- `sp500_daily` - S&P 500 daily data
- `news_depression_daily` - News depression data
- `rainfall_daily` - Rainfall data
- `depression_weekly_index` - Depression index data

**Verification**:
```sql
SELECT COUNT(*) FROM sp500_daily;
SELECT COUNT(*) FROM news_depression_daily;
-- etc...
```

---

### 📊 Step 4: Run Streamlit Dashboard on EC2

**Purpose**: Read data from RDS and create interactive visualization dashboard

**Tasks**:
1. Run Streamlit app: `streamlit run streamlit_app/app.py`
2. Access via browser: `http://your-ec2-ip:8501`
3. Data visualization and analysis

**What you can see**:
- 📈 S&P 500 stock charts
- 📰 News depression trends
- 🌧️ Rainfall analysis
- 📊 Correlation analysis
- 📉 Statistical analysis

---

## Current Status Check

### ✅ Completed
- [ ] S3 bucket created
- [ ] Access Key setup method learned

### 📝 Next Steps

**In order:**

1. **Upload CSV files to S3**
   - S3 Console → Select bucket → `raw_data/` folder → Upload
   - Upload CSV files from local storage

2. **Create RDS PostgreSQL**
   - RDS Console → Create Database
   - Select PostgreSQL
   - Free tier: db.t3.micro
   - Save endpoint URL after setup

3. **Create EC2 instance**
   - EC2 Console → Launch Instance
   - Free tier: t2.micro
   - Create and save SSH key
   - Configure Security Group (SSH, Streamlit port)

4. **Set up project on EC2**
   - Connect to EC2 via SSH
   - Upload project files
   - Create `.env` file (enter S3, RDS info)
   - Install packages

5. **Create database schema**
   - Connect to RDS
   - Run SQL schema file

6. **Run ETL pipeline**
   ```bash
   python3 etl/s3_to_rds_pipeline.py
   ```
   - S3 → Download → Process → Upload to RDS

7. **Run Streamlit dashboard**
   ```bash
   streamlit run streamlit_app/app.py
   ```
   - Read RDS data for visualization

---

## Detailed Step-by-Step Guides

### 📦 S3 File Upload

1. AWS Console → S3
2. Select bucket
3. Navigate to `raw_data/` folder (create if not exists)
4. Click "Upload" button
5. Select local CSV files:
   - `sp500.csv`
   - `ccnews_depression_daily_count_final.csv`
   - `rainfall.csv`
   - `depression_index.csv`
6. Click Upload

### 🔄 ETL Pipeline Execution

**Run on EC2:**

```bash
# 1. Navigate to project directory
cd Cloud_Computing_Project

# 2. Check environment variables (.env file)
cat .env

# 3. Run ETL pipeline
python3 etl/s3_to_rds_pipeline.py
```

**What does it do?**
- Download `raw_data/sp500.csv` from S3
- Clean and calculate data
- Upload to RDS `sp500_daily` table
- Process other files similarly

### 📊 Streamlit Dashboard

**Run on EC2:**

```bash
streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0
```

**In browser:**
- Access `http://your-ec2-public-ip:8501`
- Display charts by reading data from RDS

---

## Complete Workflow Summary

```
1. Preparation Phase
   ├── Create S3 bucket ✅ (Completed)
   ├── Upload CSV files to S3 ⬅️ Next task
   ├── Create RDS ⬅️ Next task
   └── Create EC2 ⬅️ Next task

2. Configuration Phase
   ├── Upload project to EC2
   ├── Set up .env file (S3, RDS info)
   ├── Install packages
   └── Create RDS schema

3. Execution Phase
   ├── Run ETL pipeline (S3 → RDS)
   └── Run Streamlit dashboard (RDS → Visualization)
```

---

## Question: How far have you completed?

Please check the following:

- [x] S3 bucket creation completed
- [ ] CSV file upload to S3 completed?
- [ ] RDS PostgreSQL creation completed?
- [ ] EC2 instance creation completed?
- [ ] Access Key creation completed?

Let me know your current status so I can provide more specific guidance for the next steps!

---

## Reference Documents

- **Complete Setup Guide**: `AWS_SETUP_GUIDE.md`
- **Checklist**: `QUICK_START_CHECKLIST.md`
- **Access Key Setup**: `AWS_ACCESS_KEYS_GUIDE.md`
- **Cost Guide**: `COST_ESTIMATION.md`


