import requests
from decimal import Decimal
from django.conf import settings

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
    def update_stock_price(stock):
        if stock.market == "US":
            price = MarketDataService.fetch_us_stock_price(stock.symbol)
        else:
            # GSE fallback (manual/admin-driven)
            return None

        if price:
            PriceSnapshot.objects.create(
                stock=stock,
                price=price
            )

        return price
