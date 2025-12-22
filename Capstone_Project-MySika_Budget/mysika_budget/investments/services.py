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
    def fetch_gse_prices():
        url = "https://afx.kwayisi.org/gse/"
        response = requests.get(url)
        if response.status_code != 200:
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            return {}

        stocks = {}
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 4:
                ticker = cells[0].text.strip()
                price_str = cells[3].text.strip()
                if price_str:
                    try:
                        price = Decimal(price_str)
                        stocks[ticker] = price
                    except ValueError:
                        pass
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