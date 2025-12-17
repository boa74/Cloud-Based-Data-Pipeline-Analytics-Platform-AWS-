# rds_config.py
import psycopg2
from sqlalchemy import create_engine

RDS_HOST = ""
RDS_PORT = 5432
RDS_DB   = ""
RDS_USER = ""
RDS_PW   = ""  

def get_psycopg_connection():
    return psycopg2.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        database=RDS_DB,
        user=RDS_USER,
        password=RDS_PW,
    )

def get_sqlalchemy_engine():
    return create_engine(
        f"postgresql://{RDS_USER}:{RDS_PW}@{RDS_HOST}:{RDS_PORT}/{RDS_DB}"
    )
import pandas as pd
from Analysis_code.rds_connection import get_psycopg_connection

conn = get_psycopg_connection()

df_industry = pd.read_sql(
    "SELECT * FROM industry_daily_analysis;",
    conn
)

df_sector = pd.read_sql(
    "SELECT * FROM sector_daily_analysis;",
    conn
)

conn.close()
