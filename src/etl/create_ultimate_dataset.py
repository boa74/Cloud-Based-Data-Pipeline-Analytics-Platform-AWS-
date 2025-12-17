"""
Create Ultimate Dataset: Complete Integration
Combines all individual stock data with company info, sector, industry, and all analysis metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_all_source_data():
    """Load all source datasets"""
    print("Loading all source datasets...")
    
    # Individual stock data with company info
    print("- Loading stock_data_wiki.csv...")
    stock_data = pd.read_csv('Data/exports/stock_data_wiki.csv')
    
    # Analysis data with depression index, weather, S&P 500
    print("- Loading merged_analysis_data.csv...")
    analysis_data = pd.read_csv('Data/exports/merged_analysis_data.csv')
    
    # Time series data for additional metrics
    print("- Loading merged_time_series_data.csv...")
    time_series_data = pd.read_csv('Data/final/merged_time_series_data.csv')
    
    return stock_data, analysis_data, time_series_data

def prepare_stock_data_with_metrics(stock_data):
    """Prepare individual stock data with all calculated metrics"""
    print("Processing individual stock data...")
    
    # Convert date column
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    
    # Remove rows with missing essential information
    stock_data = stock_data.dropna(subset=['sector', 'industry', 'company_name'])
    
    # Sort by ticker and date for calculations
    stock_data = stock_data.sort_values(['ticker', 'date'])
    
    print("Calculating stock metrics...")
    
    # Calculate metrics for each stock
    stock_data['daily_return'] = stock_data.groupby('ticker')['close'].pct_change()
    stock_data['price_range'] = stock_data['high'] - stock_data['low']
    stock_data['price_change'] = stock_data['close'] - stock_data['open']
    stock_data['price_change_pct'] = (stock_data['price_change'] / stock_data['open']) * 100
    
    # Calculate rolling volatility (7-day)
    stock_data['volatility_7'] = stock_data.groupby('ticker')['daily_return'].transform(
        lambda x: x.rolling(window=7, min_periods=1).std()
    )
    
    # Add number of stocks trading each day (for context)
    stock_data['num_stocks'] = stock_data.groupby('date')['ticker'].transform('count')
    
    # Clean column names to match target format
    stock_data = stock_data.rename(columns={
        'daily_return': 'Return',
        'volatility_7': 'Volatility_7',
        'price_range': 'price_range',
        'price_change_pct': 'price_change_pct'
    })
    
    return stock_data

def prepare_analysis_data(analysis_data, time_series_data):
    """Prepare analysis data with all external factors"""
    print("Processing analysis data...")
    
    # Convert dates
    analysis_data['date'] = pd.to_datetime(analysis_data['date'])
    time_series_data['date'] = pd.to_datetime(time_series_data['date'])
    
    # Select relevant columns from analysis_data
    analysis_cols = [
        'date', 'sp500_close', 'sp500_return', 'sp500_volatility_7d',
        'avg_rainfall', 'depression_index', 'depression_word_count', 
        'total_articles', 'avg_depression_per_article'
    ]
    
    analysis_clean = analysis_data[analysis_cols].copy()
    analysis_clean = analysis_clean.rename(columns={
        'sp500_close': 'Close_^GSPC',
        'avg_rainfall': 'avg_national_rainfall'
    })
    
    # Get additional metrics from time_series_data if available
    if 'depression_index_category' in time_series_data.columns:
        time_series_subset = time_series_data[['date', 'depression_index_category']].copy()
        analysis_clean = pd.merge(analysis_clean, time_series_subset, on='date', how='left')
    
    # Fill missing values
    analysis_clean['depression_index'] = analysis_clean['depression_index'].fillna(method='ffill')
    analysis_clean['depression_word_count'] = analysis_clean['depression_word_count'].fillna(0)
    analysis_clean['total_articles'] = analysis_clean['total_articles'].fillna(0)
    
    # Create depression index categories if not available
    if 'depression_index_category' not in analysis_clean.columns:
        analysis_clean['depression_index_category'] = pd.cut(
            analysis_clean['depression_index'], 
            bins=[0, 33, 66, 100], 
            labels=['Low', 'Medium', 'High']
        )
    
    return analysis_clean

def create_ultimate_dataset(stock_data, analysis_data):
    """Create the ultimate integrated dataset"""
    print("Creating ultimate integrated dataset...")
    
    # Merge stock data with analysis data
    ultimate_data = pd.merge(
        stock_data,
        analysis_data,
        on='date',
        how='inner'
    )
    
    print(f"Merged dataset shape: {ultimate_data.shape}")
    
    # Select and order columns according to specified format
    target_columns = [
        'date', 'ticker', 'company_name', 'sector', 'industry',
        'open', 'high', 'low', 'close', 'volume', 'num_stocks',
        'Close_^GSPC', 'Return', 'Volatility_7', 
        'depression_word_count', 'total_articles', 'depression_index',
        'avg_national_rainfall', 'price_range', 'price_change_pct', 
        'depression_index_category'
    ]
    
    # Keep only columns that exist
    available_columns = [col for col in target_columns if col in ultimate_data.columns]
    missing_columns = [col for col in target_columns if col not in ultimate_data.columns]
    
    if missing_columns:
        print(f"Warning: Missing columns: {missing_columns}")
    
    ultimate_data = ultimate_data[available_columns].copy()
    
    # Sort by date and ticker
    ultimate_data = ultimate_data.sort_values(['date', 'ticker'])
    
    # Add additional useful columns
    ultimate_data['year'] = ultimate_data['date'].dt.year
    ultimate_data['month'] = ultimate_data['date'].dt.month
    ultimate_data['quarter'] = ultimate_data['date'].dt.quarter
    ultimate_data['day_of_week'] = ultimate_data['date'].dt.dayofweek
    
    print(f"Final dataset shape: {ultimate_data.shape}")
    print(f"Date range: {ultimate_data['date'].min()} to {ultimate_data['date'].max()}")
    print(f"Number of unique stocks: {ultimate_data['ticker'].nunique()}")
    print(f"Number of unique sectors: {ultimate_data['sector'].nunique()}")
    print(f"Number of unique industries: {ultimate_data['industry'].nunique()}")
    
    return ultimate_data

def save_ultimate_dataset(ultimate_data):
    """Save the ultimate dataset"""
    print("Saving ultimate dataset...")
    
    # Create final directory if it doesn't exist
    os.makedirs('Data/final', exist_ok=True)
    
    # Save the complete dataset
    output_file = 'Data/final/ultimate_stock_analysis_dataset.csv'
    ultimate_data.to_csv(output_file, index=False)
    
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"✅ Saved ultimate dataset: {output_file}")
    print(f"📁 File size: {file_size_mb:.2f} MB")
    print(f"📊 Records: {len(ultimate_data):,} rows")
    print(f"📋 Columns: {len(ultimate_data.columns)} columns")
    
    # Save a sample for quick preview
    sample_data = ultimate_data.head(1000)
    sample_file = 'Data/final/ultimate_dataset_sample.csv'
    sample_data.to_csv(sample_file, index=False)
    print(f"📋 Sample file created: {sample_file} (first 1000 rows)")
    
    return output_file

def generate_dataset_summary(ultimate_data):
    """Generate comprehensive dataset summary"""
    print("\n" + "="*80)
    print("ULTIMATE DATASET SUMMARY")
    print("="*80)
    
    # Basic information
    print(f"📊 Dataset Dimensions: {ultimate_data.shape[0]:,} rows × {ultimate_data.shape[1]} columns")
    print(f"📅 Date Range: {ultimate_data['date'].min().date()} to {ultimate_data['date'].max().date()}")
    print(f"🏢 Unique Companies: {ultimate_data['ticker'].nunique():,}")
    print(f"🏭 Unique Sectors: {ultimate_data['sector'].nunique()}")
    print(f"🔧 Unique Industries: {ultimate_data['industry'].nunique()}")
    
    # Sector breakdown
    print(f"\n🏢 SECTOR BREAKDOWN:")
    sector_counts = ultimate_data.groupby('sector')['ticker'].nunique().sort_values(ascending=False)
    for sector, count in sector_counts.items():
        print(f"  {sector}: {count} companies")
    
    # Top industries by company count
    print(f"\n🏭 TOP 10 INDUSTRIES BY COMPANY COUNT:")
    industry_counts = ultimate_data.groupby('industry')['ticker'].nunique().sort_values(ascending=False).head(10)
    for industry, count in industry_counts.items():
        print(f"  {industry}: {count} companies")
    
    # Data quality
    print(f"\n📈 DATA QUALITY:")
    total_possible_records = ultimate_data['ticker'].nunique() * ultimate_data['date'].nunique()
    completeness = (len(ultimate_data) / total_possible_records) * 100
    print(f"  Data Completeness: {completeness:.2f}%")
    print(f"  Missing Values: {ultimate_data.isnull().sum().sum():,}")
    print(f"  Duplicate Records: {ultimate_data.duplicated().sum():,}")
    
    # Value ranges
    print(f"\n💰 VALUE RANGES:")
    print(f"  Stock Prices: ${ultimate_data['close'].min():.2f} - ${ultimate_data['close'].max():,.2f}")
    print(f"  Daily Returns: {ultimate_data['Return'].min():.4f} - {ultimate_data['Return'].max():.4f}")
    print(f"  Depression Index: {ultimate_data['depression_index'].min():.1f} - {ultimate_data['depression_index'].max():.1f}")
    
    # Column information
    print(f"\n📋 COLUMN INFORMATION:")
    for i, col in enumerate(ultimate_data.columns, 1):
        print(f"  {i:2d}. {col}")

def main():
    """Main execution function"""
    print("="*80)
    print("ULTIMATE DATASET CREATION PIPELINE")
    print("Combining all stock data with company info and external factors")
    print("="*80)
    
    try:
        # Load all source data
        stock_data, analysis_data, time_series_data = load_all_source_data()
        
        # Process stock data with metrics
        stock_processed = prepare_stock_data_with_metrics(stock_data)
        
        # Process analysis data
        analysis_processed = prepare_analysis_data(analysis_data, time_series_data)
        
        # Create ultimate dataset
        ultimate_data = create_ultimate_dataset(stock_processed, analysis_processed)
        
        # Save dataset
        output_file = save_ultimate_dataset(ultimate_data)
        
        # Generate summary
        generate_dataset_summary(ultimate_data)
        
        print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"📁 Ultimate dataset saved as: {output_file}")
        print(f"🔍 Use this file for comprehensive analysis including:")
        print("   • Individual stock performance")
        print("   • Company/Sector/Industry information") 
        print("   • Market conditions (S&P 500)")
        print("   • External factors (depression index, weather)")
        print("   • Technical indicators (volatility, returns)")
        
    except Exception as e:
        print(f"❌ Pipeline failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    main()