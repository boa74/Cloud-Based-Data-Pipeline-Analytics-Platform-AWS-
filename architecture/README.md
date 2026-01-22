# AWS Architecture Overview

This document describes the high-level architecture of a cloud-based data pipeline
developed as part of a Cloud Computing course at Columbia University.
The system ingests external data on a daily schedule, stores raw data in S3,
transforms it on EC2, loads curated tables into PostgreSQL on RDS, and serves
analytics through a Streamlit dashboard.

---

## Architecture Summary

- **Orchestration**: Amazon EventBridge triggers an ingestion AWS Lambda on a daily schedule (08:00 America/New_York).
- **Ingestion**: AWS Lambda fetches external REST API data and writes **raw JSON** to Amazon S3.
- **Transformation**: Python-based ETL scripts running on Amazon EC2 clean/transform data for relational storage.
- **Storage**:
  - Raw data in **Amazon S3** (date-partitioned objects)
  - Curated/structured data in **Amazon RDS (PostgreSQL)**
- **Serving Layer**: A **Streamlit** application on EC2 queries RDS and displays analytics.

---

## High-Level Data Flow

1. **External APIs** provide raw JSON data
2. **EventBridge (08:00 ET daily)** triggers the ingestion Lambda
3. **Lambda** fetches data and stores it in **S3 (raw layer)**
4. **EC2 ETL** reads raw data from S3, transforms/validates it, and loads it into **RDS (PostgreSQL)**
5. **Streamlit (EC2)** queries RDS and renders interactive dashboards

---

## Components

### 1) Amazon EventBridge (Schedule)
- **Purpose**: Daily orchestration trigger for ingestion
- **Schedule**: **08:00 America/New_York** (daily)
- **Target**: Ingestion AWS Lambda function

> Note: Scheduling is handled by EventBridge. The Lambda function is designed to run whenever invoked.

---

### 2) AWS Lambda (Ingestion)
- **Purpose**: Lightweight ingestion job that calls external REST APIs and stores raw results in S3
- **Input**: EventBridge scheduled invocation
- **Output**: Raw JSON stored in S3 (date-based keys)

**Data sources (examples)**:
- Weather API (Open-Meteo)
- Market index data (S&P 500 via public endpoint)

---

### 3) Amazon S3 (Raw Storage)
- **Purpose**: Durable storage for raw API responses and intermediate artifacts
- **Recommended layout (example)**:
  - `raw/weather/weather_YYYY-MM-DD.json`
  - `raw/sp500/sp500_YYYY-MM-DD.json`

#### Idempotency Policy
- Raw objects are written using deterministic, date-partitioned keys.
- If the pipeline is re-run for the same date, it may overwrite the same key.
  (S3 Versioning is recommended to preserve historical revisions during development.)

---

### 4) Amazon EC2 (ETL / Transform)
- **Purpose**: Run resource-intensive ETL steps that are easier to debug/reproduce in a VM environment
- **Responsibilities**:
  - Read raw JSON/CSV from S3
  - Clean/transform data (types, timestamps, schema alignment)
  - Compute derived metrics where applicable
  - Load curated tables into RDS (PostgreSQL)

---

### 5) Amazon RDS (PostgreSQL)
- **Purpose**: Store curated datasets in relational tables for analytics and dashboard queries
- **Responsibilities**:
  - Enforce schema constraints
  - Support SQL analytics for downstream visualization

---

### 6) Streamlit on EC2 (Serving / Visualization)
- **Purpose**: Provide a simple user-facing interface for analytics
- **Behavior**:
  - Queries RDS using SQL
  - Displays charts and analysis results

---

## Design Decisions (Why This Setup)

- **Lambda for ingestion, EC2 for ETL**:
  - Lambda is well-suited for lightweight API calls and writing raw outputs to S3.
  - EC2 provides a reproducible environment for heavier ETL workloads and debugging.
- **S3 as the raw layer**:
  - Keeps raw data immutable and auditable
  - Decouples ingestion from transformation
- **RDS for curated data**:
  - Provides a structured, query-friendly layer for analytics and dashboard use
- **Security model**:
  - S3 access is controlled via IAM policies/roles.
  - EC2 and RDS communicate within a VPC with security groups controlling network access.

---

## Limitations / Future Improvements

- Replace any unstable public endpoints with dedicated data providers (or add retries/backoff + monitoring).
- Add data quality checks (row counts, schema validation, missing-data alerts).
- Add monitoring/alerts for failed ingestion runs (CloudWatch metrics + alarms).
- Consider expanding to Step Functions for clearer orchestration as the pipeline grows.

---

## What to Look For in the Repo

- Ingestion Lambda code (external API fetch → S3 raw write)
- ETL scripts on EC2 (S3 raw → RDS tables)
- Streamlit dashboard code (RDS → charts)
- Environment variable configuration and IAM permissions documentation
