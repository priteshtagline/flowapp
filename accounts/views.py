from rest_framework import generics
from rest_framework.response import Response
from .models.user import User

from .serializer import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer,
    FcmTokenSerializer,
    GoogleSocialAuthSerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from .serializer import ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from push_notifications.models import APNSDevice, GCMDevice
from fcm_django.models import FCMDevice


def fcm_device_create(fcm_array, user, name):
    FCMDevice.objects.create(**fcm_array, user=user, name=name)


def user_access_token(user, context, is_created=False):
    refresh = RefreshToken.for_user(user)
    response = {
        "access": str(refresh.access_token),
        "user": UserSerializer(user, context=context).data,
    }
    if is_created:
        response["message"] = "User created successfully."

    return Response(response)


class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if User.objects.filter(email__iexact=request.data["email"]).exists():
            return Response(
                {
                    "error": {
                        "email": [
                            "Your email already register. please login with password."
                        ]
                    }
                },
                status=400,
            )

        user = serializer.save()

        FCM_update = {}
        FCM_update["registration_id"] = ""
        if "fcm_token" in request.data:
            FCM_update["registration_id"] = request.data["fcm_token"]
        if "device_type" in request.data:
            FCM_update["type"] = request.data["device_type"]

        if FCM_update["registration_id"] != "":
            FCM_update["device_id"] = user.device_id
            fcm_device_create(FCM_update, user, user.first_name)
        return user_access_token(user, self.get_serializer_context(), is_created=True)


class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
                "data": [],
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class FCMTokenAPI(generics.CreateAPIView):
    serializer_class = FcmTokenSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)
        fcm_data = serializer.data
        user = self.request.user

        default = {"registration_id": fcm_data["registration_id"]}
        if self.request.user.id:
            default["user"] = self.request.user

        try:
            if fcm_data["device_type"] == "ios":
                APNSDevice.objects.update_or_create(
                    device_id=fcm_data["device_id"], defaults=default
                )
            else:
                GCMDevice.objects.update_or_create(
                    device_id=fcm_data["device_id"],
                    cloud_message_type="FCM",
                    defaults=default,
                )
        except:
            return Response({"error": {"device_id": ["device id is invalid"]}})

        return Response(serializer.data)


from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.serializers import SocialLoginSerializer
from rest_auth.registration.views import SocialLoginView

from .adapters import GoogleOAuth2AdapterIdToken


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2AdapterIdToken
    callback_url = "http://localhost:8000/api/v1/users/login/google/callback/"
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer
