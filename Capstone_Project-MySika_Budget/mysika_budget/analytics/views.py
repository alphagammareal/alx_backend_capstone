from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import AnalyticsService
from .serializers import (
    IncomeExpenseSerializer,
    CategoryBreakdownSerializer,
    CashflowSerializer,
)

# Create your views here.
class IncomeExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = AnalyticsService.income_vs_expense(request.user)
        serializer = IncomeExpenseSerializer(data)
        return Response(serializer.data)


class CategoryBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = AnalyticsService.category_breakdown(request.user)
        serializer = CategoryBreakdownSerializer(data, many=True)
        return Response(serializer.data)


class CashflowView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = AnalyticsService.last_30_days_cashflow(request.user)
        serializer = CashflowSerializer(data, many=True)
        return Response(serializer.data)