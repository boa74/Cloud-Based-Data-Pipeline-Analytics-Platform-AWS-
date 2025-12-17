#!/usr/bin/env python3
"""
Create cleaned datasets matching the date range of depression news data
Filters stock data to match depression news timeframe (2017-01-01 to 2018-07-05)
"""

import pandas as pd

print("=" * 80)
print("CREATING CLEANED DATASETS FOR ANALYSIS")
print("=" * 80)

# ============================================================================
# 1. LOAD DEPRESSION NEWS DATA (this defines our date range)
# ============================================================================
print("\n1. Loading depression news data...")
depression = pd.read_csv('csv_exports/ccnews_depression_daily_count_final.csv')
depression['date'] = pd.to_datetime(depression['date'])

print(f"   Rows: {len(depression):,}")
print(f"   Date range: {depression['date'].min().date()} to {depression['date'].max().date()}")

# Store the date range
min_date = depression['date'].min()
max_date = depression['date'].max()

# ============================================================================
# 2. CREATE STOCK_DATA_WIKI_CLEAN.CSV (matching date range)
# ============================================================================
print("\n2. Creating stock_data_wiki_clean.csv...")

# Load stock data
stock = pd.read_csv('csv_exports/stock_data.csv')
stock['date'] = pd.to_datetime(stock['date'])
print(f"   Original stock data: {len(stock):,} rows")

# Load company info
company = pd.read_csv('csv_exports/company_info.csv')
print(f"   Company info: {len(company)} S&P 500 companies")

# Merge stock with company info
stock_wiki = stock.merge(company, on='ticker', how='inner')  # Only keep S&P 500 stocks
print(f"   After merging with S&P 500 companies: {len(stock_wiki):,} rows")

# Filter to depression news date range
stock_wiki_clean = stock_wiki[(stock_wiki['date'] >= min_date) & (stock_wiki['date'] <= max_date)]
print(f"   After filtering to depression date range: {len(stock_wiki_clean):,} rows")
print(f"   Date range: {stock_wiki_clean['date'].min().date()} to {stock_wiki_clean['date'].max().date()}")

# Save
stock_wiki_clean.to_csv('csv_exports/stock_data_wiki_clean.csv', index=False)
print("   ✓ Saved: csv_exports/stock_data_wiki_clean.csv")

# ============================================================================
# 3. VERIFY DATA ALIGNMENT
# ============================================================================
print("\n3. Verifying data alignment...")

print(f"\n   Depression news:")
print(f"     - Dates: {depression['date'].min().date()} to {depression['date'].max().date()}")
print(f"     - Rows: {len(depression):,}")
print(f"     - Unique dates: {depression['date'].nunique()}")

print(f"\n   Stock data (S&P 500 only, matching dates):")
print(f"     - Dates: {stock_wiki_clean['date'].min().date()} to {stock_wiki_clean['date'].max().date()}")
print(f"     - Rows: {len(stock_wiki_clean):,}")
print(f"     - Unique dates: {stock_wiki_clean['date'].nunique()}")
print(f"     - Unique tickers: {stock_wiki_clean['ticker'].nunique()}")
print(f"     - Companies with info: {stock_wiki_clean['company_name'].notna().sum():,}")

# ============================================================================
# 4. CREATE DAILY AGGREGATED STOCK DATA
# ============================================================================
print("\n4. Creating daily aggregated stock data...")

stock_daily = stock_wiki_clean.groupby('date').agg({
    'open': 'mean',
    'high': 'mean',
    'low': 'mean',
    'close': 'mean',
    'volume': 'sum',
    'ticker': 'count'  # Count of stocks traded that day
}).reset_index()

stock_daily = stock_daily.rename(columns={
    'open': 'avg_open',
    'high': 'avg_high',
    'low': 'avg_low',
    'close': 'avg_close',
    'volume': 'total_volume',
    'ticker': 'num_stocks_traded'
})

stock_daily.to_csv('csv_exports/stock_daily_aggregated_clean.csv', index=False)
print(f"   ✓ Saved: csv_exports/stock_daily_aggregated_clean.csv")
print(f"   Rows: {len(stock_daily):,}")

# ============================================================================
# 5. CREATE MERGED DATASET (Depression + Stock)
# ============================================================================
print("\n5. Creating merged dataset...")

merged = depression.merge(stock_daily, on='date', how='left')

# Add date features
merged['year'] = merged['date'].dt.year
merged['month'] = merged['date'].dt.month
merged['day_of_week'] = merged['date'].dt.dayofweek
merged['quarter'] = merged['date'].dt.quarter

merged.to_csv('csv_exports/depression_stock_merged_clean.csv', index=False)
print(f"   ✓ Saved: csv_exports/depression_stock_merged_clean.csv")
print(f"   Rows: {len(merged):,}")
print(f"   Columns: {len(merged.columns)}")

# ============================================================================
# 6. SUMMARY STATISTICS
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\nDate Range: {min_date.date()} to {max_date.date()} ({(max_date - min_date).days + 1} days)")

print("\nFiles Created:")
print("  1. stock_data_wiki_clean.csv")
print("     - S&P 500 stocks only")
print(f"     - {len(stock_wiki_clean):,} rows")
print(f"     - {stock_wiki_clean['ticker'].nunique()} unique tickers")
print(f"     - Columns: date, ticker, open, high, low, close, volume, company_name, sector, industry")

print("\n  2. stock_daily_aggregated_clean.csv")
print("     - Daily averages across all S&P 500 stocks")
print(f"     - {len(stock_daily):,} rows (one per trading day)")
print("     - Columns: date, avg_open, avg_high, avg_low, avg_close, total_volume, num_stocks_traded")

print("\n  3. depression_stock_merged_clean.csv")
print("     - Depression news + Daily stock aggregates")
print(f"     - {len(merged):,} rows")
print(f"     - Columns: {', '.join(merged.columns[:8])}...")

print("\n" + "=" * 80)
print("✅ CLEANING COMPLETE - All datasets aligned to depression news date range!")
print("=" * 80)

# Display sample of merged data
print("\nSample merged data:")
print(merged.head(10).to_string())
