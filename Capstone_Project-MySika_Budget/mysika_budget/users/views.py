from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from wallets.models import Wallet


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, "login.html")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            Wallet.objects.get_or_create(user=user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not all([full_name, email, password1, password2]):
            messages.error(request, "All fields are required.")
            return render(request, "register.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, "register.html")

        try:
            user = User.objects.create_user(
                email=email,
                password=password1,
                full_name=full_name
            )
           
            login(request, user)
            Wallet.objects.get_or_create(user=user)

            messages.success(request, "Registration successful!")
            return redirect("dashboard")

        except Exception as e:
            messages.error(request, "An error occurred during registration.")
            return render(request, "register.html")

    return render(request, "register.html")


@login_required
def profile_view(request):
    return render(request, "profile.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("users:login") 


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"})