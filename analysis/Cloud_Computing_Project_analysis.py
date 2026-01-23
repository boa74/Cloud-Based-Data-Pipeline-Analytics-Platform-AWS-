#analysis.py
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import statsmodels.api as sm
from scipy.stats import pearsonr


#DB connection

# Fill in with your actual RDS info
# DB connection

DB_USER = "apanuser"
DB_PASS = "apanuser1"
DB_HOST = "apan5450-postgres.clkygjbv9yeo.us-east-1.rds.amazonaws.com"
DB_PORT = 5432
DB_NAME = "apan5450-postgres"   


engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


#Load data from RDS

# S&P 500 (daily)
sp500 = pd.read_sql("""
    SELECT trade_date,
           close_spx,
           daily_return
    FROM sp500_daily
    ORDER BY trade_date;
""", engine)

sp500["trade_date"] = pd.to_datetime(sp500["trade_date"])

# News depression counts (daily)
news = pd.read_sql("""
    SELECT news_date,
           depression_word_count,
           total_articles,
           avg_depression_per_article
    FROM news_depression_daily
    ORDER BY news_date;
""", engine)

news["news_date"] = pd.to_datetime(news["news_date"])

#Rainfall (daily, 50 states)
rain = pd.read_sql("""
    SELECT *
    FROM rainfall_daily
    ORDER BY obs_date;
""", engine)

rain["obs_date"] = pd.to_datetime(rain["obs_date"])

#Weekly depression index
dep_idx = pd.read_sql("""
    SELECT week_end_date,
           depression_index
    FROM depression_weekly_index
    ORDER BY week_end_date;
""", engine)

dep_idx["week_end_date"] = pd.to_datetime(dep_idx["week_end_date"])


#Prepare merged daily dataset


#Merge SP500 + news on date
daily = (
    news.merge(sp500, left_on="news_date", right_on="trade_date", how="inner")
)

# Merge rainfall on date
daily = daily.merge(
    rain, left_on="news_date", right_on="obs_date", how="inner"
)

#Compute national average rainfall (mean of all state columns)
state_cols = [c for c in rain.columns if c not in ["obs_date"]]
daily["avg_rainfall_us"] = daily[state_cols].mean(axis=1)

# Keep only columns we need
daily = daily[[
    "news_date",
    "depression_word_count",
    "daily_return",
    "avg_rainfall_us"
]].dropna()

print("Daily merged shape:", daily.shape)


#H1:Regression – depression count on stock return


# Optionally, use *lagged* return (yesterday’s return) to avoid simultaneity
daily = daily.sort_values("news_date")
daily["daily_return_lag1"] = daily["daily_return"].shift(1)
h1_df = daily.dropna(subset=["daily_return_lag1", "depression_word_count"])

X_h1 = sm.add_constant(h1_df[["daily_return_lag1"]])
y_h1 = h1_df["depression_word_count"]

model_h1 = sm.OLS(y_h1, X_h1).fit()
print("\n=== H1: Depression word count ~ lagged S&P500 return ===")
print(model_h1.summary())


#H2: Correlation – rainfall vs depression count

h2_df = daily.dropna(subset=["avg_rainfall_us", "depression_word_count"])

corr, pval = pearsonr(
    h2_df["avg_rainfall_us"],
    h2_df["depression_word_count"]
)

print("\n=== H2: Correlation(avg_rainfall_us, depression_word_count) ===")
print(f"Pearson r = {corr:.3f}, p-value = {pval:.3g}")

# You can also run a simple regression if you want:
X_h2 = sm.add_constant(h2_df[["avg_rainfall_us"]])
y_h2 = h2_df["depression_word_count"]
model_h2 = sm.OLS(y_h2, X_h2).fit()
print("\nOLS version of H2: Depression word count ~ avg_rainfall_us")
print(model_h2.summary())


#Weekly aggregation for H3

# Build weekly depression news series by summing or averaging by week-end date
# First, we need a week-ending date that matches the survey index.
daily["week_end_date"] = daily["news_date"] + pd.to_timedelta(
    (6 - daily["news_date"].dt.weekday), unit="D"
)

weekly_news = (
    daily.groupby("week_end_date", as_index=False)
         .agg(
             avg_depression_word_count=("depression_word_count", "mean"),
             total_depression_words=("depression_word_count", "sum")
         )
)

weekly = weekly_news.merge(dep_idx, on="week_end_date", how="inner").dropna()

print("\nWeekly merged shape:", weekly.shape)


#H3: Regression – depression index vs average news depression word count

X_h3 = sm.add_constant(weekly[["depression_index"]])
y_h3 = weekly["avg_depression_word_count"]

model_h3 = sm.OLS(y_h3, X_h3).fit()
print("\n=== H3: avg_depression_word_count ~ depression_index ===")
print(model_h3.summary())


