import email
from gc import get_objects
from rest_framework import generics
from rest_framework.response import Response

from backend.models.story import Story
from .models.user import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.mail import EmailMessage, send_mail
from flowapp import settings
from django.contrib.auth.hashers import make_password
from .serializer import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer,
    FcmTokenSerializer,
    SocialUserSerializer,
    EmailVerificationSerializer,
    ForgotPasswordEmailSendSerializer,
    EmailVerificationForgotPasswordSerializer,
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
import random
from django.contrib.sites.models import Site


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
        users = serializer.save()
        user_data = serializer.data
        user_re_data = dict(user_data)
        user = User.objects.get(email=user_data["email"])
        token = RefreshToken.for_user(user).access_token

        FCM_update = {}
        FCM_update["registration_id"] = ""
        if "fcm_token" in request.data:
            FCM_update["registration_id"] = request.data["fcm_token"]
        if "device_type" in request.data:
            FCM_update["type"] = request.data["device_type"]

        if FCM_update["registration_id"] != "":
            FCM_update["device_id"] = user_re_data["device_id"]
            fcm_device_create(FCM_update, users, user_re_data["first_name"])
        current_site = request.META["HTTP_HOST"]
        relativeLink = reverse("email-verify")
        absurl = "http://" + current_site + relativeLink + "?token=" + str(token)
        email_body = (
            "Hi " + user.email + " Use the link below to verify your email \n" + absurl
        )
        data = {
            "email_body": email_body,
            "to_email": user.email,
            "email_subject": "Verify your email",
        }
        Util.send_email(data)
        response = {
            "status": "success",
            "code": status.HTTP_201_CREATED,
            "message": "Verification link sent successfully",
        }
        return Response(response)


class VerifyEmail(generics.GenericAPIView):
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            user.is_active = True
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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

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


class ForgotPassword(generics.GenericAPIView):
    serializer_class = ForgotPasswordEmailSendSerializer
    queryset = User.objects.all()

    def get_object(self):
        return User.objects.all()

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.data
        if not instance.filter(email=user["email"]).exists():
            return Response(status.HTTP_400_BAD_REQUEST)
        else:
            random_id = " ".join(
                [str(random.randint(0, 999)).zfill(3) for _ in range(2)]
            )
            instance.filter(email=user["email"]).update(
                email_verification_code=random_id
            )
            user_from_model = instance.get(email=user["email"])

            email_body = (
                "Hi "
                + "CODE :- "
                + user_from_model.email_verification_code
                + " Use the link below to verify your email \n"
            )
            data = {
                "email_body": email_body,
                "to_email": user_from_model.email,
                "email_subject": "Verify code for forgot password",
            }
            Util.send_email(data)
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Email sent successfully",
            }
        return Response(response)


class ForgotPasswordConfirm(generics.UpdateAPIView):
    serializer_class = EmailVerificationForgotPasswordSerializer
    queryset = User.objects.all()

    def get_object(self):
        return User.objects.all()

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification = serializer.data
        user = instance.get(email=verification["email"])

        if user.email_verification_code != verification["verification_code"]:
            response = {
                "status": "fail",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "please enter right verification code",
            }
            return Response(response)
        else:
            instance.filter(email=verification["email"]).update(
                password=make_password(verification["password"]),
                email_verification_code="",
            )
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
            }
        return Response(response)
