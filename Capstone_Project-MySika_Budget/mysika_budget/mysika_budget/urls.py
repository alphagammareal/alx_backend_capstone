from django.contrib import admin
from django.urls import path, include
from users.views import ProfileAPIView, LogoutAPIView
from django.contrib.auth.views import LogoutView  
from django.http import HttpResponse
from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@mysika.com',
            password='mysikapassword123' 
        )
        return HttpResponse("Superuser created successfully!<br><br>"
                           "Username: admin<br>"
                           "Password: mysikapassword123<br><br>"
                           "Now go to /admin/ and log in.<br>"
                           "Then DELETE this view for security!")
    return HttpResponse("Superuser already exists.")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('create-superuser-secret/', create_superuser),
    
    path('admin/logout/', LogoutView.as_view(next_page='/login/')),

    # Users authentication at root
    path('', include('users.urls', namespace='users')), 

    path("budgets/", include("budgets.urls")),
    

    # Frontend pages
    path('', include('frontend.urls')),

    # API auth endpoints
    path('api/auth/profile/', ProfileAPIView.as_view(), name='api_profile'),
    path('api/auth/logout/', LogoutAPIView.as_view(), name='api_logout'),

    # app APIs
    path('api/budgets/', include('budgets.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/transactions/', include('transactions.urls')),
    path("api/analytics/", include("analytics.urls")),
    path("api/investments/", include("investments.urls")),
]