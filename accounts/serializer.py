from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password


# Register serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user


# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # The default result (access/refresh tokens)
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        # Custom data you want to include
        data.update({"id": self.user.id})
        data.update({"email": self.user.email})
        data.update({"firstname": self.user.first_name})
        data.update({"lastname": self.user.last_name})
        # and everything else you want to send in the response
        return data


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_conf = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["old_password", "password", "password_conf"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_conf"]:
            raise serializers.ValidationError({"password": "password did not match"})
        return super().validate(attrs)

    def validated_old_password(self, value):
        email = self.context["request"].user
        if not email.check_password(value):
            raise serializers.ValidationError(
                {"old password": "old password is not correct"}
            )
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "dob", "phone_number"]
