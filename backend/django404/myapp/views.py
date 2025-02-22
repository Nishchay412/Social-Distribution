from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser  # For handling image uploads
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterUserSerializer, PostSerializer, CommentSerializer, LikeSerializer
from .models import Post, Comment, Like

User = get_user_model()

# ✅ User Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])  
def register_user(request):
    serializer = RegisterUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])  
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user)

        profile_image_url = (
            request.build_absolute_uri(user.profile_image.url) if user.profile_image else None
        )

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_image": profile_image_url,
            }
        })

    return Response({"error": "Invalid username or password"}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def logout_user(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful."}, status=200)
    except Exception:
        return Response({"error": "Invalid token."}, status=400)

# ✅ User Profile Views
@api_view(['GET'])
@permission_classes([AllowAny])  
def user_profile_by_username(request, username):
    try:
        user = User.objects.get(username=username)
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_picture": request.build_absolute_uri(user.profile_image.url) if user.profile_image else None
        })
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])  
def update_user_profile(request):
    user = request.user  
    data = request.data
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.profile_image = request.FILES.get("profile_picture", user.profile_image)  

    user.save()
    return Response({
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_picture": user.profile_image.url if user.profile_image else None
        }
    })

# ✅ Post Management Views
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    """
    Allows the author of the post to delete it.
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if post.author != request.user:
        return Response({"error": "You are not authorized to delete this post"}, status=status.HTTP_403_FORBIDDEN)

    post.delete()
    return Response({"message": "Post deleted successfully"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def list_users_excluding_self(request):
    """
    Lists all users excluding the authenticated user.
    """
    users = User.objects.exclude(id=request.user.id)
    serializer = RegisterUserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ Comments & Likes Features (New from `main`)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_comments(request, post_id):
    try:
        post = Post.objects.get(id=post_id, visibility="PUBLIC")
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    comments = post.comments.all().order_by('-created')
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    try:
        post = Post.objects.get(id=post_id, visibility="PUBLIC")
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(post=post, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_likes(request, post_id):
    try:
        post = Post.objects.get(id=post_id, visibility="PUBLIC")
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    likes = post.likes.all().order_by('-created')
    serializer = LikeSerializer(likes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, post_id):
    """
    Toggles a like on a post: if the user has already liked it, cancel the like.
    Otherwise, create a new like.
    """
    try:
        post = Post.objects.get(id=post_id, visibility="PUBLIC")
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    existing_like = Like.objects.filter(post=post, author=request.user).first()
    if existing_like:
        existing_like.delete()
        return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
    else:
        like = Like.objects.create(post=post, author=request.user)
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
