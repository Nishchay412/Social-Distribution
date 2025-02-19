from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .serializers import RegisterUserSerializer, PostSerializer  # Import the correct serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Post


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated users to register
def register_user(request):
    serializer = RegisterUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=201)
    return Response(serializer.errors, status=400)


from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([AllowAny])  # Allows anyone to log in
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # ✅ Include additional user data in the response
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

from rest_framework.permissions import IsAuthenticated
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # ✅ Only logged-in users can logout
def logout_user(request):
    try:
        # ✅ Get refresh token from request body
        refresh_token = request.data.get("refresh")

        # ✅ Blacklist the token
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"message": "Logout successful."}, status=200)
    except Exception as e:
        return Response({"error": "Invalid token."}, status=400)

@api_view(['POST'])#Create a Post
@permission_classes([IsAuthenticated])
def create_post(request):
    """
    Creates a new post. The authenticated user is set as the author.
    """
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        post = serializer.save(author=request.user)  # author= currently logged-in user
        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])#List All Posts
@permission_classes([IsAuthenticated])  
def list_posts(request):
    """
    Lists all posts that are 'PUBLIC' (not deleted).
    """
    posts = Post.objects.exclude(visibility='DELETED').order_by('-published')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])#Retrieve a Single Post
@permission_classes([IsAuthenticated]) 
def retrieve_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id, visibility='PUBLIC')
        
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PostSerializer(post)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])#Update (Edit) a Post
@permission_classes([IsAuthenticated])
def update_post(request, post_id):
    """
    Only the original author can update.
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if post.author != request.user:
        return Response({"error": "You are not the author of this post"}, status=status.HTTP_403_FORBIDDEN)

    serializer = PostSerializer(post, data=request.data, partial=True)  # partial=True for PATCH
    if serializer.is_valid():
        serializer.save()  # keeps same author
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])#Delete a Post (Hard‐Delete)
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if post.author != request.user:
        return Response({"error": "Not your post"}, status=status.HTTP_403_FORBIDDEN)

    post.delete()  # physically remove from DB
    return Response({"message": "Post deleted"}, status=status.HTTP_200_OK)