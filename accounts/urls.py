from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import RegisterApi
from django.urls import path, include


urlpatterns = [
    path("api/register", RegisterApi.as_view()),
    path(
        "api/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),
    path(
        "api/password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
]
