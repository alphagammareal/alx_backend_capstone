from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer
from .models import User



#   REGISTER VIEW
class RegisterView(generics.CreateAPIView):
    """
    Allows new users to register.
    Only POST method is allowed.
    """
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]  

#   PROFILE VIEW
class ProfileView(generics.RetrieveAPIView):
    """
    Returns the authenticated user's profile.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
