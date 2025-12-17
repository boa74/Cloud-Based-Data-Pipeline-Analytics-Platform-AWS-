--Daily Stock Data 
CREATE TABLE stock_daily (
    trade_date   date        NOT NULL,
    ticker       text        NOT NULL,
    open_price   double precision,
    high_price   double precision,
    low_price    double precision,
    close_price  double precision,
    volume       double precision,
    PRIMARY KEY (trade_date, ticker)
);
--S&P 500 Index
CREATE TABLE sp500_daily (
    trade_date     date PRIMARY KEY,
    close_spx      double precision,
    high_spx       double precision,
    low_spx        double precision,
    open_spx       double precision,
    volume_spx     double precision,
    daily_return   double precision,
    volatility_7   double precision
);

--Daily Rainfall by State
CREATE TABLE rainfall_daily (
    obs_date      date PRIMARY KEY,
    alabama       double precision,
    alaska        double precision,
    arizona       double precision,
    arkansas      double precision,
    california    double precision,
    colorado      double precision,
    connecticut   double precision,
    delaware      double precision,
    florida       double precision,
    georgia       double precision,
    hawaii        double precision,
    idaho         double precision,
    illinois      double precision,
    indiana       double precision,
    iowa          double precision,
    kansas        double precision,
    kentucky      double precision,
    louisiana     double precision,
    maine         double precision,
    maryland      double precision,
    massachusetts double precision,
    michigan      double precision,
    minnesota     double precision,
    mississippi   double precision,
    missouri      double precision,
    montana       double precision,
    nebraska      double precision,
    nevada        double precision,
    new_hampshire double precision,
    new_jersey    double precision,
    new_mexico    double precision,
    new_york      double precision,
    north_carolina double precision,
    north_dakota  double precision,
    ohio          double precision,
    oklahoma      double precision,
    oregon        double precision,
    pennsylvania  double precision,
    rhode_island  double precision,
    south_carolina double precision,
    south_dakota  double precision,
    tennessee     double precision,
    texas         double precision,
    utah          double precision,
    vermont       double precision,
    virginia      double precision,
    washington    double precision,
    west_virginia double precision,
    wisconsin     double precision,
    wyoming       double precision
);

--Weekly Depression Index
CREATE TABLE depression_weekly_index (
    week_end_date    date PRIMARY KEY,
    depression_index integer
);

--Daily News Depression Counts
CREATE TABLE news_depression_daily (
    news_date                    date PRIMARY KEY,
    depression_word_count        integer,
    total_articles               integer,
    avg_depression_per_article   double precision
);


--On a given date, what were stocks doing, what was rainfall, what was the news depression signal, etc.?
SELECT
  s.trade_date,
  s.ticker,
  s.close_price,
  sp.close_spx,
  r.california,
  nd.depression_word_count
FROM stock_daily s
LEFT JOIN sp500_daily sp
  ON sp.trade_date = s.trade_date
LEFT JOIN rainfall_daily r
  ON r.obs_date = s.trade_date
LEFT JOIN news_depression_daily nd
  ON nd.news_date = s.trade_date
WHERE s.ticker = 'AAPL';

CREATE TABLE dim_date (
    date_id    date PRIMARY KEY,
    year       int,
    month      int,
    day        int,
    dow        int,
    week       int
);

