from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser  # For handling image uploads
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterUserSerializer, PostSerializer, CommentSerializer, LikeSerializer
from .models import Post, Comment, Like
from django.utils import timezone  # Import timezone to set deleted_at timestamps

User = get_user_model()

# User Authentication Views

@api_view(['POST'])
@permission_classes([AllowAny])  
def register_user(request):
    """
    Registers user and creates a serilizer for it
    Needs username, first name, last name, email, and password
    Saves user to database
    """
    serializer = RegisterUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=201)
    return Response(serializer.errors, status=400)
from rest_framework.permissions import IsAdminUser

@api_view(['POST'])
@permission_classes([IsAdminUser])
def register_admin_user(request):
    """
    Registers a user and creates a serializer for it.
    Needs username, first name, last name, email, and password.
    Saves user to the database.
    """
    serializer = RegisterUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    User login
    Takes username and password and returns tokens if the account is approved.
    """
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)

    if user:
        # Check if the user is approved by the admin
        if not user.is_approved:
            return Response(
                {"error": "Your account is pending approval by the admin."},
                status=403
            )

        refresh = RefreshToken.for_user(user)

        # Convert ImageField to Full URL
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
                "admin": user.is_staff,  # Admin property to log in to the correct dashboard
            }
        })

    return Response({"error": "Invalid username or password"}, status=400)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def approve_user(request, username):
    """
    Approves a user account by setting is_approved to True.
    Only accessible by admin users.
    """
    user = get_object_or_404(User, username=username)
    if user.is_approved:
        return Response({"detail": "User is already approved."}, status=400)
    
    user.is_approved = True
    user.save()
    return Response({"detail": f"User {user.username} approved."}, status=200)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_pending_users(request):
    """
    Lists all users that are not yet approved.
    """
    pending_users = User.objects.filter(is_approved=False)
    serializer = RegisterUserSerializer(pending_users, many=True)
    return Response(serializer.data, status=200)


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

# Delete user
@api_view(['DELETE'])
@permission_classes([IsAuthenticated]) 
def delete_user_by_username(request, username):
    """
    Delete a user. 
    Expects username of user to be deleted.
    Cannot delete admin/superusers
    """
    # TODO Double check user is an admin
    admin = request.user

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND);

    if user.is_superuser or user.is_staff:
        return Response({"error": "You cannot delete another Admin."}, status=status.HTTP_403_FORBIDDEN)

    user.delete()
    return Response({"message": "User has been deleted"}, status=status.HTTP_200_OK)

import base64
import uuid
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_user(request, username):
    # Check if the current user has admin privileges
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=403)

    # Retrieve the user to update
    user = get_object_or_404(User, username=username)
    data = request.data

    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)

    # Handle profile picture upload
    if "profile_picture" in request.FILES:
        user.profile_image = request.FILES["profile_picture"]
    elif data.get("profile_picture") and data.get("profile_picture").startswith("data:image"):
        format, imgstr = data.get("profile_picture").split(";base64,")
        ext = format.split("/")[-1]
        file_name = f"profile_{uuid.uuid4()}.{ext}"
        user.profile_image.save(file_name, ContentFile(base64.b64decode(imgstr)), save=True)

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
    posts = Post.objects.filter(deleted_at__isnull=True).order_by('-published')  # Exclude soft-deleted posts
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
    Soft delete a post by setting deleted_at timestamp instead of removing it from the database.
    Only the post's author can delete it.
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if post.author != request.user:
        return Response({"error": "You are not the author of this post"}, status=status.HTTP_403_FORBIDDEN)

    post.deleted_at = timezone.now()  # Mark the post as deleted
    post.visibility = "DELETED"  # Change visibility to DELETED
    post.save()

    return Response({"message": "Post soft deleted"}, status=status.HTTP_200_OK)


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
@permission_classes([IsAuthenticated])
def friends_and_public_posts(request):
    """
    Fetch both:
    1. Friends' posts (with visibility PUBLIC, UNLISTED, or FRIENDS)
    2. Public posts (excluding those made by the authenticated user)
    """
    user = request.user
    friends = user.friends.all()

    # Fetch friends' posts with the allowed visibilities
    friends_posts = Post.objects.filter(
        author__in=friends,
        visibility__in=["PUBLIC", "UNLISTED", "FRIENDS"]
    )

    # Fetch public posts excluding those created by the user
    public_posts = Post.objects.filter(
        visibility="PUBLIC"
    ).exclude(author=user)

    # Combine both QuerySets using `|` (union)
    posts = (friends_posts | public_posts).distinct().order_by("-published")

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_friend(request, username):
    """
    Add friend, takes in username of user to be befriended.
    """
    # Get the target user by username
    target_user = get_object_or_404(User, username=username)

    # Prevent a user from friending themselves
    if request.user == target_user:
        return Response({"error": "Cannot add yourself as a friend."}, status=400)

    # Check if they are already friends
    if target_user in request.user.friends.all():
        return Response({"error": "You are already friends with this user."}, status=400)

    # Create the mutual friendship
    request.user.friends.add(target_user)
    target_user.friends.add(request.user)

from .serializers import RegisterUserSerializer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    """
    Get the friends of the authenticated user
    """
    friends = request.user.friends.all()
    serializer = RegisterUserSerializer(friends, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friends_posts(request):
    """
    Get the posts made by friends of the authenticated user
    """
    user = request.user
    friends = user.friends.all()

    # Show only PUBLIC, UNLISTED, or FRIENDS posts (excluding DELETED and DRAFT).
    posts = (
        Post.objects
            .filter(
                author__in=friends,
                visibility__in=["PUBLIC", "UNLISTED", "FRIENDS"]
            )
            .exclude(visibility="DELETED")
            .exclude(visibility="DRAFT")  # <--- Exclude drafts
            .order_by("-published")
    )

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=200)

from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stream_posts(request):
    user = request.user
    # Get your user's friends (assuming a self-referential many-to-many field)
    friends = user.friends.all()

    # Build the query for posts to include in the stream:
    posts = Post.objects.filter(
        Q(visibility="PUBLIC") |
        Q(visibility="UNLISTED") |  # If unlisted posts should be visible to everyone with the link, include them here
        Q(visibility="FRIENDS", author__in=friends) |
        Q(visibility="PRIVATE", author=user)
    ).exclude(visibility="DELETED").order_by("-published")

    # (Assume you have a PostSerializer to serialize these posts)
    from .serializers import PostSerializer
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)

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
@permission_classes([IsAuthenticated])  # ✅ Requires authentication
def list_non_friend_users(request):
    """
    Lists all users excluding the authenticated user and their friends.
    """
    # Get all friends of the authenticated user
    friends = request.user.friends.all()

    # Exclude the authenticated user and their friends from the user list
    non_friends = User.objects.exclude(id__in=friends.values_list('id', flat=True)).exclude(id=request.user.id)

    # Serialize user data
    serializer = RegisterUserSerializer(non_friends, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def draft_posts(request):
    # Return draft posts for the logged-in user.
    posts = Post.objects.filter(author=request.user, visibility="DRAFT").order_by("-published")
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)

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
    

