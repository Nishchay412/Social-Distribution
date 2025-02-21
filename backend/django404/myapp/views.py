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

    
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
@permission_classes([AllowAny])  # ✅ Publicly accessible profile
def user_profile_by_username(request, username):
    try:
        # ✅ Fetch user by username
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
    

    
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser  # ✅ For handling image uploads

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])  # ✅ Only logged-in users can update their info
def update_user_profile(request):
    user = request.user  # ✅ Get logged-in user

    # ✅ Extract fields from request data
    data = request.data
    username = data.get("username", user.username)
    email = data.get("email", user.email)
    first_name = data.get("first_name", user.first_name)
    last_name = data.get("last_name", user.last_name)
    profile_picture = request.FILES.get("profile_picture", user.profile_image)  # ✅ Handle image upload

    # ✅ Update fields in the database
    user.username = username
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.profile_image = profile_picture  # ✅ Store new profile image

    # ✅ Save changes
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

@api_view(['GET'])  # List Posts by Logged-in User
@permission_classes([IsAuthenticated])
def list_user_posts(request):
    """
    Lists all posts created by the authenticated user.
    """
    user_posts = Post.objects.filter(author=request.user).order_by('-published')
    serializer = PostSerializer(user_posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])  # Only allows GET requests
@permission_classes([IsAuthenticated])  # Requires authentication
def list_user_posts_by_username(request, username):
    """
    Lists all posts created by a specific user (identified by their username).
    """
    try:
        user = User.objects.get(username=username)  # Fetch the user by username
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Fetch PUBLIC posts only (so users can't see deleted/private posts)
    user_posts = Post.objects.filter(author=user, visibility="PUBLIC").order_by('-published')

    # Serialize the posts to JSON format
    serializer = PostSerializer(user_posts, many=True)
    
    # Return the JSON response
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Requires user authentication
def list_public_posts_excluding_user(request):
    """
    Fetch all PUBLIC posts, excluding posts made by the authenticated user.
    """
    user = request.user  # Get the authenticated user

    # Fetch public posts excluding those created by the user
    posts = Post.objects.filter(visibility="PUBLIC").exclude(author=user).order_by('-published')

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)