"""
ETL Script: Create Final Dataset for Industry-Level Analysis
Combines stock data with industry information, depression index, and weather data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_and_clean_data():
    """Load all required datasets"""
    print("Loading datasets...")
    
    # Load stock data with industry information
    print("- Loading stock_data_wiki.csv...")
    stock_data = pd.read_csv('Data/exports/stock_data_wiki.csv')
    
    # Load merged analysis data (depression index, weather)
    print("- Loading merged_analysis_data.csv...")
    analysis_data = pd.read_csv('Data/exports/merged_analysis_data.csv')
    
    # Load S&P 500 data for broader market context
    print("- Loading sp500.csv...")
    sp500_data = pd.read_csv('Data/exports/sp500.csv')
    
    return stock_data, analysis_data, sp500_data

def prepare_stock_data(stock_data):
    """Prepare and aggregate stock data by industry and date"""
    print("Processing stock data...")
    
    # Convert date column
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    
    # Remove rows with missing industry/sector information
    stock_data = stock_data.dropna(subset=['sector', 'industry'])
    
    # Calculate daily returns and volatility for each stock
    stock_data = stock_data.sort_values(['ticker', 'date'])
    stock_data['daily_return'] = stock_data.groupby('ticker')['close'].pct_change()
    stock_data['price_range'] = stock_data['high'] - stock_data['low']
    stock_data['price_change'] = stock_data['close'] - stock_data['open']
    stock_data['price_change_pct'] = (stock_data['price_change'] / stock_data['open']) * 100
    
    # Aggregate by sector and date
    sector_daily = stock_data.groupby(['date', 'sector']).agg({
        'open': 'mean',
        'high': 'mean', 
        'low': 'mean',
        'close': 'mean',
        'volume': 'sum',
        'daily_return': 'mean',
        'price_range': 'mean',
        'price_change_pct': 'mean',
        'ticker': 'count'  # number of stocks per sector
    }).reset_index()
    
    sector_daily = sector_daily.rename(columns={'ticker': 'num_stocks_in_sector'})
    
    # Aggregate by industry and date  
    industry_daily = stock_data.groupby(['date', 'industry']).agg({
        'open': 'mean',
        'high': 'mean',
        'low': 'mean', 
        'close': 'mean',
        'volume': 'sum',
        'daily_return': 'mean',
        'price_range': 'mean',
        'price_change_pct': 'mean',
        'ticker': 'count'
    }).reset_index()
    
    industry_daily = industry_daily.rename(columns={'ticker': 'num_stocks_in_industry'})
    
    return sector_daily, industry_daily

def prepare_analysis_data(analysis_data):
    """Prepare depression index and weather data"""
    print("Processing analysis data...")
    
    # Convert date column
    analysis_data['date'] = pd.to_datetime(analysis_data['date'])
    
    # Select relevant columns
    analysis_cols = [
        'date', 'sp500_close', 'sp500_return', 'sp500_volatility_7d',
        'avg_rainfall', 'depression_index', 'depression_word_count', 
        'total_articles', 'avg_depression_per_article'
    ]
    
    analysis_clean = analysis_data[analysis_cols].copy()
    
    # Fill missing values
    analysis_clean['depression_index'] = analysis_clean['depression_index'].fillna(method='ffill')
    analysis_clean['depression_word_count'] = analysis_clean['depression_word_count'].fillna(0)
    analysis_clean['total_articles'] = analysis_clean['total_articles'].fillna(0)
    analysis_clean['avg_depression_per_article'] = analysis_clean['avg_depression_per_article'].fillna(0)
    
    return analysis_clean

def create_final_datasets(sector_daily, industry_daily, analysis_data):
    """Merge all data and create final datasets"""
    print("Creating final datasets...")
    
    # Merge sector data with analysis data
    sector_final = pd.merge(
        sector_daily,
        analysis_data,
        on='date',
        how='inner'
    )
    
    # Merge industry data with analysis data
    industry_final = pd.merge(
        industry_daily, 
        analysis_data,
        on='date',
        how='inner'
    )
    
    # Add time-based features
    for df in [sector_final, industry_final]:
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_year'] = df['date'].dt.dayofyear
        
        # Create depression index categories
        df['depression_index_category'] = pd.cut(
            df['depression_index'], 
            bins=[0, 33, 66, 100], 
            labels=['Low', 'Medium', 'High']
        )
        
        # Calculate rolling volatility (7-day)
        df = df.sort_values(['sector' if 'sector' in df.columns else 'industry', 'date'])
        group_col = 'sector' if 'sector' in df.columns else 'industry'
        df['rolling_volatility_7d'] = df.groupby(group_col)['daily_return'].transform(
            lambda x: x.rolling(window=7, min_periods=1).std()
        )
        
    return sector_final, industry_final

def calculate_industry_statistics(industry_final):
    """Calculate summary statistics by industry"""
    print("Calculating industry statistics...")
    
    industry_stats = industry_final.groupby('industry').agg({
        'daily_return': ['mean', 'std', 'min', 'max'],
        'close': ['mean', 'min', 'max'],
        'volume': 'mean',
        'price_change_pct': ['mean', 'std'],
        'depression_index': 'mean',
        'num_stocks_in_industry': 'first'
    }).round(4)
    
    # Flatten column names
    industry_stats.columns = [f"{col[0]}_{col[1]}" for col in industry_stats.columns]
    industry_stats = industry_stats.reset_index()
    
    return industry_stats

def calculate_sector_statistics(sector_final):
    """Calculate summary statistics by sector"""
    print("Calculating sector statistics...")
    
    sector_stats = sector_final.groupby('sector').agg({
        'daily_return': ['mean', 'std', 'min', 'max'],
        'close': ['mean', 'min', 'max'], 
        'volume': 'mean',
        'price_change_pct': ['mean', 'std'],
        'depression_index': 'mean',
        'num_stocks_in_sector': 'first'
    }).round(4)
    
    # Flatten column names
    sector_stats.columns = [f"{col[0]}_{col[1]}" for col in sector_stats.columns]
    sector_stats = sector_stats.reset_index()
    
    return sector_stats

def save_final_datasets(sector_final, industry_final, sector_stats, industry_stats):
    """Save all final datasets to CSV files"""
    print("Saving final datasets...")
    
    # Create final directory if it doesn't exist
    os.makedirs('Data/final', exist_ok=True)
    
    # Save main datasets
    sector_final.to_csv('Data/final/sector_daily_analysis.csv', index=False)
    print(f"- Saved sector_daily_analysis.csv: {len(sector_final)} rows")
    
    industry_final.to_csv('Data/final/industry_daily_analysis.csv', index=False) 
    print(f"- Saved industry_daily_analysis.csv: {len(industry_final)} rows")
    
    # Save summary statistics
    sector_stats.to_csv('Data/final/sector_summary_statistics.csv', index=False)
    print(f"- Saved sector_summary_statistics.csv: {len(sector_stats)} rows")
    
    industry_stats.to_csv('Data/final/industry_summary_statistics.csv', index=False)
    print(f"- Saved industry_summary_statistics.csv: {len(industry_stats)} rows")

def main():
    """Main ETL pipeline"""
    print("="*60)
    print("ETL Pipeline: Creating Final Dataset for Industry Analysis")
    print("="*60)
    
    try:
        # Load data
        stock_data, analysis_data, sp500_data = load_and_clean_data()
        
        # Process stock data
        sector_daily, industry_daily = prepare_stock_data(stock_data)
        
        # Process analysis data
        analysis_clean = prepare_analysis_data(analysis_data)
        
        # Create final datasets
        sector_final, industry_final = create_final_datasets(
            sector_daily, industry_daily, analysis_clean
        )
        
        # Calculate statistics
        sector_stats = calculate_sector_statistics(sector_final)
        industry_stats = calculate_industry_statistics(industry_final)
        
        # Save results
        save_final_datasets(sector_final, industry_final, sector_stats, industry_stats)
        
        print("\n" + "="*60)
        print("ETL Pipeline completed successfully!")
        print("="*60)
        
        # Print summary
        print(f"\nDataset Summary:")
        print(f"- Sectors: {len(sector_stats)} unique sectors")
        print(f"- Industries: {len(industry_stats)} unique industries") 
        print(f"- Date range: {sector_final['date'].min()} to {sector_final['date'].max()}")
        print(f"- Total sector-day observations: {len(sector_final)}")
        print(f"- Total industry-day observations: {len(industry_final)}")
        
        print(f"\nTop 5 sectors by average daily return:")
        top_sectors = sector_stats.nlargest(5, 'daily_return_mean')[['sector', 'daily_return_mean']]
        for _, row in top_sectors.iterrows():
            print(f"  {row['sector']}: {row['daily_return_mean']:.4f}")
            
        print(f"\nFiles saved to Data/final/:")
        print("  - sector_daily_analysis.csv")
        print("  - industry_daily_analysis.csv")
        print("  - sector_summary_statistics.csv")
        print("  - industry_summary_statistics.csv")
        
    except Exception as e:
        print(f"Error in ETL pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()