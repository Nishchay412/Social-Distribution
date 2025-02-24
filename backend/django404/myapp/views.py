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

        # ✅ Convert ImageField to Full URL
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
                "profile_image": profile_image_url,  # ✅ Full URL now
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def create_post(request):
    """
    Creates a new Post. The authenticated user is set as the author.
    """
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        post = serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def list_posts(request):
    """
    Lists all existing posts (except those marked 'DELETED'), ordered by newest first.
    This endpoint is accessible only to logged-in users.
    """
    posts = Post.objects.exclude(visibility='DELETED').order_by('-published')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def retrieve_post(request, post_id):
    """
    Retrieves a single Post by its ID. Respects privacy settings:
    - If the Post is marked 'PRIVATE', only the author can view it.
    """
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
    """
    Updates an existing Post. Only the post's author can modify it.
    Supports full ('PUT') or partial ('PATCH') updates.
    """
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
    """
    Deletes a post if the requesting user is the author. 
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if post.author != request.user:
        return Response({"error": "Not your post"}, status=status.HTTP_403_FORBIDDEN)

    post.delete()  
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



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # ✅ Requires authentication
def list_users_excluding_self(request):
    """
    Lists all users excluding the authenticated user.
    """
    # Get all users except the currently logged-in user
    users = User.objects.exclude(id=request.user.id)
    
    # Serialize user data
    serializer = RegisterUserSerializer(users, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_comments(request, post_id):
    """
    Lists all comments for a given PUBLIC post, in descending order by creation date.
    If the post doesn't exist or isn't PUBLIC, returns a 404.
    """
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
    """
    Creates a new Comment on a PUBLIC post. 
    Ensures the post exists and sets the comment's author to the requesting user.
    """
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
    """
    Lists all likes on a PUBLIC post, in descending order of creation date.
    If the post is not found or isn't PUBLIC, returns a 404.
    """
    try:
        post = Post.objects.get(id=post_id, visibility="PUBLIC")
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    likes = post.likes.all().order_by('-created')
    serializer = LikeSerializer(likes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_like(request, post_id):
    """
    Creates a Like on a PUBLIC post if the user has not already liked it.
    Returns 400 if the user already liked the post.
    """
    try:
        post = Post.objects.get(id=post_id, visibility="PUBLIC")
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the user already liked the post
    if Like.objects.filter(post=post, author=request.user).exists():
        return Response({"error": "Already liked"}, status=status.HTTP_400_BAD_REQUEST)
    
    like = Like.objects.create(post=post, author=request.user)
    serializer = LikeSerializer(like)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

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
        # If like exists, delete it (cancel like)
        existing_like.delete()
        return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
    else:
        # Otherwise, create a new like
        like = Like.objects.create(post=post, author=request.user)
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

