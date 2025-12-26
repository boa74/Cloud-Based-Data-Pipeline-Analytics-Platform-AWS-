
---

## 📄 `architecture/README.md`

```md
# AWS Architecture Overview

This document describes the high-level architecture of the cloud-based
data pipeline developed as part of a Cloud Computing course at
Columbia University.

---

## Architecture Summary

- External REST APIs are ingested using AWS Lambda and Python-based ETL scripts
- Lightweight, event-driven ingestion tasks run on AWS Lambda
- Resource-intensive ETL processing runs on Amazon EC2
- Raw and intermediate data is stored in Amazon S3
- Processed data is stored in PostgreSQL on Amazon RDS
- A Streamlit application running on EC2 provides a user-facing interface

---

## Design Decisions

- Amazon S3 is a managed service outside the VPC, so access is controlled
  through IAM roles rather than subnet placement
- AWS Lambda is used for lightweight ingestion and orchestration tasks,
  while EC2 handles heavier ETL workloads
- EC2 instances operate within a VPC, with security groups controlling
  inbound and outbound traffic
- The architecture prioritizes simplicity, security, and reproducibility
  over complex optimizations

---

## Data Flow

1. External APIs provide raw data
2. Lambda functions trigger ingestion or scheduling tasks
3. ETL scripts running on EC2 clean and transform data
4. Structured data is stored in PostgreSQL on RDS
5. Streamlit dashboard queries RDS and displays analytics results
