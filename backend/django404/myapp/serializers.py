from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post

User = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]  # ✅ Include additional fields

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)  # ✅ Uses create_user() to hash passwords

class PostSerializer(serializers.ModelSerializer): #Includes all fields from Post model
    class Meta:
        model = Post
        fields = '__all__' 
