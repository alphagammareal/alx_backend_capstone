import requests
from decimal import Decimal
from django.conf import settings
from bs4 import BeautifulSoup

from .models import Stock, PriceSnapshot

class MarketDataService:

    @staticmethod
    def fetch_us_stock_price(symbol):
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": settings.ALPHA_VANTAGE_API_KEY,
        }

        response = requests.get(url, params=params)
        data = response.json()

        try:
            price = Decimal(data["Global Quote"]["05. price"])
            return price
        except (KeyError, ValueError):
            return None

    @staticmethod
    @staticmethod
    def fetch_gse_prices():
        url = "https://afx.kwayisi.org/gse/"
        response = requests.get(url)
        if response.status_code != 200:
            return {}

        text = response.text
        stocks = {}

        # Find the Markdown table section (starts after "Live share prices..." or similar)
        lines = text.splitlines()
        in_table = False
        for line in lines:
            line = line.strip()
            if line.startswith('| Ticker |') or line.startswith('| Symbol |'): 
                in_table = True
                continue
            if in_table and line.startswith('|'):
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    ticker = parts[0].strip('*')  
                    price_str = parts[3].replace(',', '')  
                    try:
                        price = Decimal(price_str)
                        stocks[ticker.upper()] = price
                    except (ValueError, IndexError):
                        pass
            if in_table and not line:  # Empty line ends table
                break
        return stocks

    @staticmethod
    def update_stock_price(stock):
        if stock.market == "US":
            price = MarketDataService.fetch_us_stock_price(stock.symbol)
        elif stock.market == "GSE":
            gse_prices = MarketDataService.fetch_gse_prices()
            price = gse_prices.get(stock.symbol)
        else:
            price = None

        if price:
            PriceSnapshot.objects.create(
                stock=stock,
                price=price
            )
            return price
        return None