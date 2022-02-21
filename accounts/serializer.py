from dataclasses import fields
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from fcm_django.models import FCMDevice
from backend.models.story import Story


# Register serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "dob",
            "phone_number",
            "password",
            "device_id",
            "device_type",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        print("from create")
        validated_data["password"] = make_password(validated_data["password"])
        return super(RegisterSerializer, self).create(validated_data)


# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "provider_type",
            "device_id",
            "device_type",
            "password",
        )
        extra_kwargs = {
            "device_id": {
                "required": False,
            },
            "device_type": {
                "required": False,
            },
            "password": {
                "required": False,
                "write_only": True,
            },
        }

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super(UserSerializer, self).update(instance, validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": {
            "error": {"detail": ["No active account found with the given credentials."]}
        }
    }

    def __init__(self, *args, **kwargs):
        FCM_update = {}
        FCM_update["registration_id"] = ""
        if "fcm_token" in kwargs["data"]:
            FCM_update["registration_id"] = kwargs["data"]["fcm_token"]
        if "device_type" in kwargs["data"]:
            FCM_update["type"] = kwargs["data"]["device_type"]

        users = User.objects.filter(Q(email__iexact=kwargs["data"]["email"]))
        user = users.first()
        # users.update(device_type=kwargs["data"]["device_type"])
        if user and user.check_password(kwargs["data"]["email"]):
            if FCM_update["registration_id"] != "":
                FCM_update["user"] = user
                FCM_update["name"] = user.first_name
                FCM_update["device_id"] = user.device_id
                FCMDevice.objects.create(**FCM_update)
        super().__init__(*args, **kwargs)

    def validate(self, user_data):
        user_response = super(CustomTokenObtainPairSerializer, self).validate(
            user_data,
        )
        # Access token with to include user detail.
        user_response.pop("refresh")
        user_response.update({"user": UserSerializer(self.user).data})

        return user_response


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "dob", "phone_number"]


class FcmTokenSerializer(serializers.Serializer):
    DEVICE_TYPE = (
        ("android", "android"),
        ("ios", "ios"),
    )
    registration_id = serializers.CharField(max_length=255)
    device_id = serializers.CharField(max_length=255)
    device_type = serializers.ChoiceField(choices=DEVICE_TYPE)
