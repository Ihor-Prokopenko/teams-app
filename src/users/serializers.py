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
    email = serializers.EmailField()
    password = serializers.CharField()

