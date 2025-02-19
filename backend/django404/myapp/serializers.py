from rest_framework import serializers
from django.contrib.auth import get_user_model  # ✅ Correct way to get custom User model

User = get_user_model()  # ✅ Get the custom User model

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)  # ✅ Uses create_user() to hash passwords
