from django.contrib import admin
from django.urls import path, include
from users.views import ProfileAPIView, LogoutAPIView
from django.contrib.auth.views import LogoutView  # Good import

urlpatterns = [
    path('admin/', admin.site.urls),

    # This fixes the admin logout perfectly!
    path('admin/logout/', LogoutView.as_view(next_page='/login/')),

    # Users authentication at root
    path('', include('users.urls', namespace='users')), 

    # Frontend pages
    path('', include('frontend.urls')),

    # API auth endpoints
    path('api/auth/profile/', ProfileAPIView.as_view(), name='api_profile'),
    path('api/auth/logout/', LogoutAPIView.as_view(), name='api_logout'),

    # Your app APIs
    path('api/budgets/', include('budgets.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/transactions/', include('transactions.urls')),
    path("api/analytics/", include("analytics.urls")),
    path("api/investments/", include("investments.urls")),
]