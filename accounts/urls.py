from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import (
    RegisterApi,
    CustomTokenObtainPairView,
    ChangePasswordView,
    UserProfileView,
    FCMTokenAPI,
    GoogleSocialAuthView,
)
from django.urls import path, include


urlpatterns = [
    path("api/register/", RegisterApi.as_view()),
    path("api/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),
    path(
        "api/password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("api/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("api/profile/", UserProfileView.as_view(), name="UserProfile"),
    path("api/email/", GoogleSocialAuthView.as_view(), name="signwithgoogle"),
    path("device-register/", FCMTokenAPI.as_view(), name="device_fcm_register"),
]
