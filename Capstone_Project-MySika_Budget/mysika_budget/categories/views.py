from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Category
from .serializers import CategorySerializer

# Create your views here.
class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Category.objects.filter(user=self.request.user)
        category_type = self.request.query_params.get("type")
        if category_type:
            qs = qs.filter(category_type=category_type.upper())
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)