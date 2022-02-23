from rest_framework import generics
from rest_framework.response import Response
from .models.user import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.mail import EmailMessage, send_mail
from flowapp import settings
from .serializer import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer,
    FcmTokenSerializer,
    SocialUserSerializer,
    EmailVerificationSerializer,
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
        user_data = serializer.data
        user_re_data = dict(user_data)

        FCM_update = {}
        FCM_update["registration_id"] = ""
        if "fcm_token" in request.data:
            FCM_update["registration_id"] = request.data["fcm_token"]
        if "device_type" in request.data:
            FCM_update["type"] = request.data["device_type"]

        if FCM_update["registration_id"] != "":
            FCM_update["device_id"] = user_re_data["device_id"]
            fcm_device_create(FCM_update, user, user_re_data["first_name"])
        # current_site = get_current_site(request).domain
        relativeLink = reverse("email-verify")
        absurl = (
            "http://"
            + "192.168.1.61:8000"
            + relativeLink
            + "?token="
            + str(user_re_data["token"]["access"])
        )
        email_body = (
            "Hi "
            + user_re_data["email"]
            + " Use the link below to verify your email \n"
            + absurl
        )
        data = {
            "email_body": email_body,
            "to_email": user_re_data["email"],
            "email_subject": "Verify your email",
        }
        Util.send_email(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return user_access_token(user, self.get_serializer_context(), is_created=True)


class VerifyEmail(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        print("*" * 100)
        token = request.GET.get("token")
        print("token", token)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            print("payload", payload)
            user = User.objects.get(id=payload["user_id"])
            print("user", user)
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response(
                {"email": "Successfully activated"}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {"error": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError as identifier:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


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


class SocialUserView(generics.GenericAPIView):
    serializer_class = SocialUserSerializer


class SocialUserView(generics.GenericAPIView):
    serializer_class = SocialUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        # get_user = User.objects.filter(
        #     Q(email__iexact=request.data['email']) | (Q(email__isnull=True) & ~Q(provider_type='guest') & Q(device_id=request.data['device_id'])))

        # if get_user.exists():
        #     get_user.update(**serializer.data)
        #     return user_access_token(get_user.first(), self.get_serializer_context(), is_created=False)

        # user = serializer.save()

        FCM_update = {}
        FCM_update["registration_id"] = ""
        if "fcm_token" in request.data:
            FCM_update["registration_id"] = request.data.get("fcm_token")
        if "device_type" in request.data:
            FCM_update["type"] = request.data.get("device_type")
        if "device_id" in request.data:
            FCM_update["device_id"] = request.data.get("device_id")

        if request.data["provider_type"] == "apple":
            if (
                "user_identifier_key" not in request.data
                or request.data["user_identifier_key"] == ""
            ):
                return Response(
                    {"user_identifier_key": "Apple user identifier key is missing"}
                )
            elif User.objects.filter(
                user_identifier_key=request.data["user_identifier_key"]
            ).exists():
                User.objects.filter(
                    user_identifier_key=request.data["user_identifier_key"]
                ).update(
                    provider_type=request.data["provider_type"],
                    device_id=request.data["device_id"],
                )

                user = User.objects.filter(
                    user_identifier_key=request.data["user_identifier_key"]
                ).first()

                if FCM_update["registration_id"] != "":
                    fcm_device_create(FCM_update, user, user.email)

                return user_access_token(user, self.get_serializer_context())

            else:
                if "email" in request.data:
                    if User.objects.filter(
                        email__iexact=request.data["email"]
                    ).exists():
                        User.objects.filter(email__iexact=request.data["email"]).update(
                            provider_type=request.data["provider_type"],
                            user_identifier_key=request.data["user_identifier_key"],
                            device_id=request.data["device_id"],
                        )
                        user = User.objects.filter(
                            user_identifier_key=request.data["user_identifier_key"]
                        ).first()

                        if FCM_update["registration_id"] != "":
                            fcm_device_create(FCM_update, user, user.email)

                        return user_access_token(user, self.get_serializer_context())

        elif User.objects.filter(email__iexact=request.data["email"]).exists():
            if request.data["provider_type"] not in ["google", "facebook", "apple"]:
                return Response(
                    {
                        "message": "Social media signin with google, facebook or apple is supported",
                    }
                )

            User.objects.filter(email__iexact=request.data["email"]).update(
                provider_type=request.data["provider_type"],
                device_id=request.data["device_id"],
            )

            user = User.objects.get(email__iexact=request.data["email"])
            if FCM_update["registration_id"] != "":
                fcm_device_create(FCM_update, user, user.email)

            return user_access_token(user, self.get_serializer_context())

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if FCM_update["registration_id"] != "":
            fcm_device_create(FCM_update, user, user.email)
        return user_access_token(user, self.get_serializer_context(), is_created=True)
