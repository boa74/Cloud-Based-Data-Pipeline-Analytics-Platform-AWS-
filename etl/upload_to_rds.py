#!/usr/bin/env python3
"""
ETL Pipeline: Upload Final Datasets to RDS
Uploads the 6 final processed CSV files to PostgreSQL RDS
"""

import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

# RDS Connection Information
DB_CONFIG = {
    'host': 'host',
    'port':'port',
    'database': 'database', 
    'user': 'user',
    'password': 'password'
}

# File mapping: local file -> RDS table name
FILE_TABLE_MAPPING = {
    'Data/final/sector_daily_analysis.csv': 'sector_daily_analysis',
    'Data/final/industry_daily_analysis.csv': 'industry_daily_analysis', 
    'Data/final/sector_summary_statistics.csv': 'sector_summary_statistics',
    'Data/final/industry_summary_statistics.csv': 'industry_summary_statistics',
    'Data/final/correlation_statistics_full.csv': 'correlation_statistics',
    'Data/final/merged_time_series_data.csv': 'merged_time_series_data'
}

# ============================================================================
# Database Connection Functions
# ============================================================================

def create_db_engine():
    """Create SQLAlchemy engine for RDS connection"""
    try:
        connection_string = (
            f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        
        engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 30}
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info("Database connection established successfully")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise

def drop_table_if_exists(engine, table_name):
    """Drop table if it exists"""
    try:
        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
            conn.commit()
        logger.info(f"Dropped table {table_name} if it existed")
    except Exception as e:
        logger.warning(f"Could not drop table {table_name}: {e}")

# ============================================================================
# Data Processing Functions
# ============================================================================

def clean_dataframe_for_upload(df, table_name):
    """Clean dataframe before uploading to PostgreSQL"""
    logger.info(f"Cleaning dataframe for table: {table_name}")
    
    # Make a copy to avoid modifying original
    df_clean = df.copy()
    
    # Convert date columns to proper datetime
    date_columns = ['date', 'trade_date', 'Date']
    for col in date_columns:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            
    # Handle infinity values
    numeric_columns = df_clean.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_columns:
        df_clean[col] = df_clean[col].replace([float('inf'), float('-inf')], None)
        
    # Clean column names (PostgreSQL-friendly)
    df_clean.columns = [col.lower().replace(' ', '_').replace('-', '_').replace('.', '_') 
                       for col in df_clean.columns]
    
    # Handle special characters in text columns
    text_columns = df_clean.select_dtypes(include=['object']).columns
    for col in text_columns:
        if df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str).replace('nan', None)
    
    # Remove completely empty rows
    df_clean = df_clean.dropna(how='all')
    
    logger.info(f"Cleaned dataframe: {len(df_clean)} rows, {len(df_clean.columns)} columns")
    return df_clean

def create_table_schema(df, table_name, engine):
    """Create optimized table schema based on dataframe"""
    
    schema_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    
    for col in df.columns:
        col_type = str(df[col].dtype)
        
        if 'datetime' in col_type:
            pg_type = "TIMESTAMP"
        elif 'int' in col_type:
            pg_type = "BIGINT"
        elif 'float' in col_type:
            pg_type = "DOUBLE PRECISION"
        elif 'bool' in col_type:
            pg_type = "BOOLEAN"
        else:
            # For text columns, determine appropriate length
            if df[col].dtype == 'object':
                max_len = df[col].astype(str).str.len().max()
                if pd.isna(max_len) or max_len == 0:
                    pg_type = "TEXT"
                elif max_len <= 50:
                    pg_type = "VARCHAR(100)"
                elif max_len <= 255:
                    pg_type = "VARCHAR(500)"
                else:
                    pg_type = "TEXT"
            else:
                pg_type = "TEXT"
        
        schema_sql += f"    {col} {pg_type},\n"
    
    # Remove last comma and close
    schema_sql = schema_sql.rstrip(',\n') + "\n);"
    
    # Add indexes for common query patterns
    if 'date' in df.columns:
        schema_sql += f"\nCREATE INDEX IF NOT EXISTS idx_{table_name}_date ON {table_name}(date);"
    
    if 'sector' in df.columns:
        schema_sql += f"\nCREATE INDEX IF NOT EXISTS idx_{table_name}_sector ON {table_name}(sector);"
        
    if 'industry' in df.columns:
        schema_sql += f"\nCREATE INDEX IF NOT EXISTS idx_{table_name}_industry ON {table_name}(industry);"
    
    return schema_sql

# ============================================================================
# Upload Functions
# ============================================================================

def upload_dataframe_to_rds(df, table_name, engine, if_exists='replace'):
    """Upload dataframe to RDS with error handling and optimization"""
    
    try:
        logger.info(f"Starting upload of {table_name}...")
        logger.info(f"DataFrame shape: {df.shape}")
        
        # Clean dataframe
        df_clean = clean_dataframe_for_upload(df, table_name)
        
        if len(df_clean) == 0:
            logger.warning(f"No data to upload for {table_name}")
            return False
            
        # Drop existing table if replacing
        if if_exists == 'replace':
            drop_table_if_exists(engine, table_name)
        
        # Upload data in chunks for large datasets
        chunk_size = 10000 if len(df_clean) > 50000 else 5000
        
        logger.info(f"Uploading {len(df_clean)} rows in chunks of {chunk_size}...")
        
        # Upload data
        df_clean.to_sql(
            table_name,
            engine,
            if_exists=if_exists,
            index=False,
            chunksize=chunk_size,
            method='multi'
        )
        
        # Verify upload
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = result.fetchone()[0]
            
        logger.info(f"✅ Successfully uploaded {table_name}: {row_count} rows")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to upload {table_name}: {str(e)}")
        return False

def upload_all_files():
    """Upload all final CSV files to RDS"""
    
    logger.info("="*60)
    logger.info("Starting RDS Upload Pipeline")
    logger.info("="*60)
    
    # Create database engine
    engine = create_db_engine()
    
    results = {}
    total_files = len(FILE_TABLE_MAPPING)
    successful_uploads = 0
    
    for file_path, table_name in FILE_TABLE_MAPPING.items():
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                results[table_name] = False
                continue
                
            logger.info(f"\nProcessing: {file_path} -> {table_name}")
            
            # Load CSV file
            logger.info(f"Loading CSV file: {file_path}")
            df = pd.read_csv(file_path)
            
            # Upload to RDS
            success = upload_dataframe_to_rds(df, table_name, engine)
            results[table_name] = success
            
            if success:
                successful_uploads += 1
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            results[table_name] = False
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("Upload Summary")
    logger.info("="*60)
    
    for table_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{table_name}: {status}")
    
    logger.info(f"\nOverall: {successful_uploads}/{total_files} files uploaded successfully")
    
    if successful_uploads == total_files:
        logger.info("🎉 All files uploaded successfully!")
    else:
        logger.warning(f"⚠️  {total_files - successful_uploads} files failed to upload")
    
    # Close engine
    engine.dispose()
    
    return results

def verify_uploads():
    """Verify that all tables were created and have data"""
    
    logger.info("\n" + "="*60) 
    logger.info("Verifying Uploads")
    logger.info("="*60)
    
    engine = create_db_engine()
    
    try:
        with engine.connect() as conn:
            # List all tables
            tables_query = """
            SELECT table_name, 
                   (xpath('/row/cnt/text()', xml_count))[1]::text::int as row_count
            FROM (
                SELECT table_name, 
                       query_to_xml(format('SELECT COUNT(*) as cnt FROM %I', table_name), false, true, '') as xml_count
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ({})
            ) t
            """.format(','.join([f"'{name}'" for name in FILE_TABLE_MAPPING.values()]))
            
            result = conn.execute(text(tables_query))
            
            logger.info("Table verification:")
            total_rows = 0
            for row in result:
                table_name, row_count = row
                logger.info(f"  {table_name}: {row_count:,} rows")
                total_rows += row_count if row_count else 0
                
            logger.info(f"\nTotal rows across all tables: {total_rows:,}")
            
    except Exception as e:
        logger.error(f"Error during verification: {e}")
    finally:
        engine.dispose()

# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    
    try:
        # Upload all files
        results = upload_all_files()
        
        # Verify uploads
        verify_uploads()
        
        # Final status
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        if success_count == total_count:
            logger.info("\n🎉 RDS Upload Pipeline completed successfully!")
            return True
        else:
            logger.error(f"\n❌ RDS Upload Pipeline completed with {total_count - success_count} failures")
            return False
            
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)