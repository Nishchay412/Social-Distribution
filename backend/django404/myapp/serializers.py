from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]  # ✅ Include additional fields

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)  # ✅ Uses create_user() to hash passwords

"""We add a author_username read‐only field so clients see who authored it, but can’t change it."""
class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'author_username',
            'title',
            'content',
            'image',
            'visibility',
            'published',
        ]
        read_only_fields = ['id', 'author_username', 'published']  # ✅ Prevents modification of these fields