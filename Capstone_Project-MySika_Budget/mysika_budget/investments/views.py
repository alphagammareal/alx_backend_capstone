from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Investment
from .serializers import InvestmentSerializer
from .services import MarketDataService


# Create your views here.
class InvestmentViewSet(ModelViewSet):
    serializer_class = InvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        investment = serializer.save(user=self.request.user)
        MarketDataService.update_stock_price(investment.stock)