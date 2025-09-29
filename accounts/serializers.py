import re

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=5, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_username(self, value):
        if not re.match(r"^[A-Za-z0-9_]{2,}$", value):
            raise serializers.ValidationError(
                "Username must contain only latin letters, digits, and underscores, min 2 chars, no spaces or special/cyrillic characters."
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_staff", "first_name", "last_name"]
        read_only_fields = ["id", "email", "is_staff"]
