import os
import json
import datetime as dt
import urllib.request
import boto3

s3 = boto3.client("s3")

BUCKET_NAME = os.environ.get("BUCKET_NAME", "apan5450-stock")


def fetch_json(url: str) -> dict:
    """Simple HTTP GET using urllib and return JSON dict."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = resp.read()
    return json.loads(data)


def lambda_handler(event, context):
    today = dt.date.today()
    date_str = today.strftime("%Y-%m-%d")

    # 1) Weather (example: Washington DC daily)
    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=38.9"
        "&longitude=-77.0"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=America%2FNew_York"
    )

    # 2) S&P 500 (Yahoo Finance chart API, 1y, 1d)
    stock_url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/^GSPC"
        "?range=1y&interval=1d"
    )

    try:
        weather_json = fetch_json(weather_url)
        stock_json = fetch_json(stock_url)

        # 1) Save raw weather JSON to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"raw/weather/weather_{date_str}.json",
            Body=json.dumps(weather_json).encode("utf-8"),
            ContentType="application/json",
        )

        # 2) Save raw stock JSON to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"raw/sp500/sp500_{date_str}.json",
            Body=json.dumps(stock_json).encode("utf-8"),
            ContentType="application/json",
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Weather and stock data stored successfully",
                "date": date_str
            }),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error in Lambda",
                "error": str(e),
            }),
        }
