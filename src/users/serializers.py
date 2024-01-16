from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(required=False, max_length=150)

    class Meta:
        model = User
        fields = ["id", "email", "password", "full_name"]
        extra_kwargs = {
            "password": {"write_only": True},
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class UserEditSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source="full_name", required=False)

    class Meta:
        model = User
        fields = ["id", "email", "fullName"]
        partial = True


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
