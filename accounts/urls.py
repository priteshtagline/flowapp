from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import (
    RegisterApi,
    CustomTokenObtainPairView,
    ChangePasswordView,
    UserProfileView,
    SocialUserView,
    VerifyEmail,
    ForgotPassword,
    ForgotPasswordConfirm,
)
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path("api/register/", RegisterApi.as_view()),
    path("api/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/forgot_password/", ForgotPassword.as_view(), name="forgot_password"),
    path(
        "api/forgot_password/confirm/",
        ForgotPasswordConfirm.as_view(),
        name="forgot_password_confirm",
    ),
    path("api/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("api/profile/", UserProfileView.as_view(), name="UserProfile"),
    path(
        "signin/social-media/",
        SocialUserView.as_view(),
        name="social_media_signin",
    ),
    path("email-verify/", csrf_exempt(VerifyEmail.as_view()), name="email-verify"),
]
