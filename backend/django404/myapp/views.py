from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser  # For handling image uploads
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterUserSerializer, PostSerializer
from .models import Post

User = get_user_model()

# User Authentication Views

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
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
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

#  User Profile Views

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

# Post Management Views

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def create_post(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        post = serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def list_posts(request):
    posts = Post.objects.exclude(visibility='DELETED').order_by('-published')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def retrieve_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        
        # Allow authors to see their own private posts
        if post.visibility == 'PRIVATE' and post.author != request.user:
            return Response({"error": "This post is private."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if post.author != request.user:
        return Response({"error": "You are not the author of this post"}, status=status.HTTP_403_FORBIDDEN)

    serializer = PostSerializer(post, data=request.data, partial=True)  
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if post.author != request.user:
        return Response({"error": "Not your post"}, status=status.HTTP_403_FORBIDDEN)

    post.delete()  
    return Response({"message": "Post deleted"}, status=status.HTTP_200_OK)
