
from bs4 import BeautifulSoup


import requests
import logging
from decimal import Decimal
from django.conf import settings
from .models import PriceSnapshot

logger = logging.getLogger(__name__)

class MarketDataService:

    @staticmethod
    def fetch_us_stock_price(symbol):
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": settings.ALPHA_VANTAGE_API_KEY,
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            return Decimal(data["Global Quote"]["05. price"])
        except Exception as e:
            logger.error(f"US stock fetch failed for {symbol}: {e}")
            return None

    @staticmethod
    def fetch_gse_prices():
        url = "https://afx.kwayisi.org/gse/"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"GSE fetch failed: {e}")
            return {}

        stocks = {}
        lines = response.text.splitlines()
        in_table = False

        for line in lines:
            line = line.strip()

            if line.startswith('| Ticker |') or line.startswith('| Symbol |'):
                in_table = True
                continue

            if in_table and line.startswith('|'):
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    try:
                        ticker = parts[0].strip('*').upper()
                        price = Decimal(parts[3].replace(',', ''))
                        stocks[ticker] = price
                    except Exception:
                        continue

            if in_table and not line:
                break

        return stocks

    @staticmethod
    def update_stock_price(stock):
        try:
            if stock.market == "US":
                price = MarketDataService.fetch_us_stock_price(stock.symbol)
            elif stock.market == "GSE":
                gse_prices = MarketDataService.fetch_gse_prices()
                price = gse_prices.get(stock.symbol.upper())
            else:
                price = None

            if price:
                PriceSnapshot.objects.create(
                    stock=stock,
                    price=price
                )
                return price

        except Exception as e:
            logger.error(f"Stock update failed for {stock.symbol}: {e}")

        return None
