import random

import jwt
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from fcm_django.models import FCMDevice
from flowapp import settings
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models.user import User
from .serializer import ChangePasswordSerializer
from .serializer import CustomTokenObtainPairSerializer
from .serializer import EmailVerificationForgotPasswordSerializer
from .serializer import ForgotPasswordEmailSendSerializer
from .serializer import RegisterSerializer
from .serializer import SocialUserSerializer
from .serializer import UserProfileSerializer
from .serializer import UserSerializer
from .utils import Util
from .utils import fcm_update


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
        user_query = User.objects.filter(email__iexact=request.data["email"])
        if user_query.exists():
            return Response(
                {"email": ["Your email already register. please login with password."]},
                status=400,
            )

        users = serializer.save()
        user_data = serializer.data
        user_re_data = dict(user_data)
        user = user_query.first()
        token = RefreshToken.for_user(user).access_token

        fcm_update(
            request.data["fcm_token"],
            request.data["device_id"],
            user=user,
            device_type=request.data["device_type"]
            if "device_type" in request.data
            else None,
        )

        # Send verification mail
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
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            if not user.is_active == True or user.is_verified == True:
                user.is_active = True
                user.is_verified = True
                user.save()
            return Response(
                {"email": "Successfully activated"},
                template_name="signup_verification.html",
                status=status.HTTP_200_OK,
            )
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {"error": "Activation Expired"},
                template_name="signup_verification.html",
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.DecodeError as identifier:
            return Response(
                {"error": "Invalid token"},
                template_name="signup_verification.html",
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer

    # Email not register Error Response
    def get_object(self):
        try:
            return User.objects.get(email=self.request.data.get("email"))
        except:
            return None

    def post(self, request, *args, **kwargs):
        if not self.get_object():
            return Response(
                {"error": {"detail": ["Please enter valid email and password"]}},
                status=400,
            )

        return super().post(request, *args, **kwargs)


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

        # Check old password
        if not self.object.check_password(request.data["old_password"]):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class SocialUserView(generics.GenericAPIView):
    serializer_class = SocialUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

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

                fcm_update(
                    request.data["fcm_token"],
                    request.data["device_id"],
                    user=user,
                    device_type=request.data["device_type"]
                    if "device_type" in request.data
                    else None,
                )

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

                        fcm_update(
                            request.data["fcm_token"],
                            request.data["device_id"],
                            user=user,
                            device_type=request.data["device_type"]
                            if "device_type" in request.data
                            else None,
                        )

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
            fcm_update(
                request.data["fcm_token"],
                request.data["device_id"],
                user=user,
                device_type=request.data["device_type"]
                if "device_type" in request.data
                else None,
            )
            return user_access_token(user, self.get_serializer_context())

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        fcm_update(
            request.data["fcm_token"],
            request.data["device_id"],
            user=user,
            device_type=request.data["device_type"]
            if "device_type" in request.data
            else None,
        )
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
            response = {
                "status": "fail",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Email doesn't exists",
            }
            return Response(response)
        else:
            random_id = "".join(
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
                "message": "Verification code sent successfully",
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
