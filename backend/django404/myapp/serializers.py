from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like, CommentLike,Node
import markdown


User = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):
    """ Serializer for User model with password hashing. """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)  # ✅ Uses create_user() to hash passwords

#Yicheng Lin
class NodeSerializer(serializers.ModelSerializer):
    """ Ensures safe handling of node data without exposing passwords. """

    class Meta:
        model = Node
        fields = ['id', 'base_url', 'username', 'is_active']
        read_only_fields = ['id']  # Prevent clients from modifying node ID

    def create(self, validated_data):
        """ Prevents exposing password in API responses. """
        node = Node.objects.create(**validated_data)
        return node

    def update(self, instance, validated_data):
        """ Ensure password is not updated accidentally. """
        validated_data.pop("password", None)  # Ignore password updates
        return super().update(instance, validated_data)

#QingqiuTan
class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    likes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        # 'post' links the comment to its Post;
        # 'author_username' is shown for convenience but is not editable.
        # 'text' holds the actual comment content.
        # 'created' is automatically set by the server/model upon creation.
        fields = ['id', 'post', 'author_username', 'text', 'created', 'likes_count']
        # Marking these fields as read-only prevents clients from manipulating identifiers or timestamps.
        read_only_fields = ['id','post','author_username', 'created','likes_count']

    def get_likes_count(self, obj):
        return obj.likes.count()

#QingqiuTan/Nishchay Ranjan/Riyasat Zaman
""" Serializer for Post model with author_username as a read-only field. """
class PostSerializer(serializers.ModelSerializer):
    # Expose the author's username in the serialized output, but don't let it be modified by the client.
    author_username = serializers.ReadOnlyField(source='author.username')
    # Provide a convenient field so clients can see how many likes the post has without making extra requests.
    likes_count = serializers.SerializerMethodField()
    # Similarly, expose comment counts to reduce the need for separate queries.
    comments_count = serializers.SerializerMethodField()
    # Serialize related comments in a read-only fashion. This way, clients can see comments
    # directly alongside the post data, but can't create or edit comments through the PostSerializer.
    title = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    comments = CommentSerializer(many=True, read_only=True)
    content_html = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        # These fields capture the essential data for a post, including user info, title/content,
        # publication details, and derived statistics (likes_count, comments_count).
        fields = [
            'id',
            'author_username',
            'title',
            'content',
            'content_html',
            'image',
            'visibility',
            'published',
            'likes_count', 
            'comments_count',
            'content_html',
            'comments',
            'updated',
            'deleted_at'
        ]
        # Marking certain fields as read-only ensures that system-managed data (like 'id', 'published') 
        # and relationships (like author_username, comments) cannot be overridden.
        read_only_fields = ['id', 'author_username', 'published','updated', 'likes_count', 'comments_count','comments']  # ✅ Prevents modification of these fields
    def get_likes_count(self, obj):
        # Returns the total number of likes for this post, allowing quick reference in the serialized output.
        return obj.likes.count()

    def get_comments_count(self, obj):
        # Returns the total number of comments on this post, also for quick reference
        return obj.comments.count()
    
    def get_content_html(self, obj):
        # Convert the CommonMark content to HTML
        return markdown.markdown(obj.content or '')
    
    def validate(self, data):
        # If there's no title, no content, and no image, raise an error
        if not data.get('title') and not data.get('content') and not data.get('image'):
            raise serializers.ValidationError("At least one of title/content/image is required.")
        return data
    
#QingqiuTan
class LikeSerializer(serializers.ModelSerializer):
    # Display the username of the user who liked the post, but don't allow manual edits.
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Like
        # These fields identify which post was liked, who liked it, and when the like happened.
        fields = ['id', 'post', 'author_username', 'created']
        # We protect 'id', 'author_username', and 'created' from client-side modifications.
        read_only_fields = ['id', 'author_username', 'created']


class CommentLikeSerializer(serializers.ModelSerializer):
    """ Serializer for CommentLike model with author_username as a read-only field. """
    author_username = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = CommentLike
        fields = ['id', 'author_username', 'comment', 'created']
        read_only_fields = ['id', 'author_username', 'created', 'comment']

