from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser  # For handling image uploads
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterUserSerializer, PostSerializer, CommentSerializer, LikeSerializer, FollowingSerializer, NotifSerializer, CommentLikeSerializer
from .models import Post, Comment, Like, Following, Notif, CommentLike
import base64
import uuid
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema



User = get_user_model()

# Define common responses for reuse
user_registration_responses = {
    201: openapi.Response('User registered successfully'),
    400: openapi.Response('Validation errors')
}

@swagger_auto_schema(
    method='post',
    request_body=RegisterUserSerializer,
    responses=user_registration_responses,
    operation_summary="Register a new user",
    operation_description="Registers a new user with username, first name, last name, email, and password."
)

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

@swagger_auto_schema(
    method='post',
    request_body=RegisterUserSerializer,
    responses=user_registration_responses,
    operation_summary="Register a new admin user",
    operation_description="Registers a new admin user. Only admin users can access this endpoint."
)

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

@swagger_auto_schema(
    method='post',
    operation_summary="User Login",
    operation_description="Logs in a user using username and password, returning JWT tokens if credentials are valid and the account is approved.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="The user's username"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="The user's password")
        }
    ),
    responses={
        200: openapi.Response('Login successful'),
        400: openapi.Response('Invalid username or password'),
        403: openapi.Response('Account pending approval')
    }
)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
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

@swagger_auto_schema(
    method='get',
    operation_summary="Get Friend's Post Detail",
    operation_description="Retrieve the details of a friend's post by its ID.",
    responses={
        200: openapi.Response('Post details'),
        404: openapi.Response('Post not found')
    }
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friend_post_detail(request, post_id):
    """
    Returns the details of a single friend's post.
    """
    post = get_object_or_404(Post, id=post_id)
    serializer = PostSerializer(post, context={'request': request})
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    operation_summary="Approve User",
    operation_description="Approves a user account by setting is_approved to True. Only admin users can perform this action.",
    responses={
        200: openapi.Response('User approved'),
        400: openapi.Response('User already approved or invalid request')
    }
)

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

@swagger_auto_schema(
    method='get',
    operation_summary="List Pending Users",
    operation_description="Lists all users that are not yet approved.",
    responses={200: openapi.Response('List of pending users')}
)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_pending_users(request):
    """
    Lists all users that are not yet approved.
    """
    pending_users = User.objects.filter(is_approved=False)
    serializer = RegisterUserSerializer(pending_users, many=True)
    return Response(serializer.data, status=200)

@swagger_auto_schema(
    method='post',
    operation_summary="Logout User",
    operation_description="Logs out the user by blacklisting the provided refresh token.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token to blacklist")
        }
    ),
    responses={
        200: openapi.Response('Logout successful'),
        400: openapi.Response('Invalid token')
    }
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
@csrf_exempt
def logout_user(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful."}, status=200)
    except Exception:
        return Response({"error": "Invalid token."}, status=400)

# =========================
# User Profile Views
# =========================
@swagger_auto_schema(
    method='get',
    operation_summary="Get User Profile by Username",
    operation_description="Retrieve a user profile by their username.",
    responses={
        200: openapi.Response('User profile data'),
        404: openapi.Response('User not found')
    }
)

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
    TODO - permission class should be checking if current user is a superuser/admin
    Delete a user. 
    Expects username of user to be deleted.
    Cannot delete admin/superusers

    @author Christine Bao
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND);

    if user.is_superuser or user.is_staff:
        return Response({"error": "You cannot delete another Admin."}, status=status.HTTP_403_FORBIDDEN)

    user.delete()
    return Response({"message": "User has been deleted"}, status=status.HTTP_200_OK)


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
        serializer.save(author=request.user)
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
@permission_classes([IsAuthenticated])
def get_relationship(request, username):
    """
    TODO - if possilbe, i was thinking we use this to check if profile visiting is own user 
    (have profiles all be the same, but if its one's own profile than add edit button + functionality)

    Get relationship between two users 
    'curr_user' is currently logged in user, get username from request.data['username']
    'check_user' is the user we are checking to see what relationship we have with them, get username from username
    
    Expected to return 'message' of the relationship and a 'relation' of either ['YOURSELF', 'FRIEND', 'FOLLOWEE', 'FOLLOWER', 'PENDING']
    'PENDING' is if 'curr_user' sent a follow request.

    @author Christine Bao
    """
    curr_user = get_object_or_404(User, username=request.user)
    check_user = get_object_or_404(User, username=username)
    if curr_user.id == check_user.id:
        return Response({"message":"This is you", "relation":"YOURSELF"}, status=status.HTTP_200_OK)
    
    # Checks if curr_user and check_user have any outgoing follow requests first
    if Notif.objects.filter(receiver=check_user.id, sender=curr_user.id):
        return Response({"message":"This is a user you sent a follow request to.", "relation":"PENDING"}, status=status.HTTP_200_OK)

    # Checks if curr_user and check_user have Following relationship
    if Following.objects.filter(followee_id=check_user.id, follower_id=curr_user.id).exists() and Following.objects.filter(followee_id=curr_user.id, follower_id=check_user.id).exists():
        return Response({"message":"This is a user you are friends with.", "relation":"FRIEND"}, status=status.HTTP_200_OK)
    elif Following.objects.filter(followee_id=check_user.id, follower_id=curr_user.id).exists():
        return Response({"message":"This is a user you follow.", "relation":"FOLLOWEE"}, status=status.HTTP_200_OK)
    elif Following.objects.filter(followee_id=curr_user.id, follower_id=check_user.id).exists():
        return Response({"message":"This is a user you are followed by.", "relation":"FOLLOWER"}, status=status.HTTP_200_OK)

    return Response({"message":"This is a user is no one special.", "relation":"NOBODY"}, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_follow_request(request, username):
    """
    Create Notif of follow_request type 
    'receiver' is author receiving the follow request, get username from username
    'sender' is the user sending the follow request, get username from request
    """
    receiver = get_object_or_404(User, username=username)
    sender = get_object_or_404(User, username=request.user)

    # Can't send another notif if request already sent
    if Notif.objects.filter(sender_id=sender.id, receiver_id=receiver.id):
        return Response({"message":"You already sent them a follow request!"}, status=status.HTTP_204_NO_CONTENT)

    # Cannot send yourself a follow request
    if receiver.id == sender.id: 
        return Response({"message":"You cannot send yourself a follow request!"}, status=status.HTTP_403_FORBIDDEN)
    # Cannot send follow request to someone you already follow
    if Following.objects.filter(followee_id=receiver.id, follower_id=sender.id).exists():
        return Response({"error": "Already following this user"}, status=status.HTTP_403_FORBIDDEN)
    
    data = {"receiver":receiver.id, "sender":sender.id, "notif_type":"FOLLOW_REQUEST"}
    try:
        serializer = NotifSerializer(data=data)
        if serializer.is_valid():
            serializer.save(receiver_id = receiver.id, sender_id = sender.id, notif_type = 'FOLLOW_REQUEST')
            return Response({"message":"Follow Request Sent!"}, status=status.HTTP_200_OK)
    except:
        return Response({"error":"Follow Request couldn't be made"}, status=status.HTTP_400_BAD_REQUEST)
    

def get_local_user_by_username(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None

from django.conf import settings
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

# views.py

from django.conf import settings
from django.shortcuts import get_object_or_404
import requests

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

# Assume you have imported your models and serializers:
# from myapp.models import User, Notif, Following
# from myapp.serializers import NotifSerializer

# Import your models and serializers.
# from myapp.models import User, Notif, Following
# from myapp.serializers import NotifSerializer

def get_local_user_by_username(username):
    """
    Helper function to check if a user exists in the local database.
    """
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def aggregated_remote_list_all_users(request):
    """
    Aggregates all users from all remote nodes.
    It iterates through all nodes in settings.NODE_CONFIG that are not the current node,
    fetches the users from each remote endpoint (/list-all-users/), and returns the combined list.
    """
    current_instance = getattr(settings, "INSTANCE_NAME", "node1")
    
    # # Filter out the current node from the NODE_CONFIG.
    remote_nodes = { key: node for key, node in settings.NODE_CONFIG.items() if key != current_instance }
    
    for node_key, node in remote_nodes.items():
        url = f"{node['url']}/list-all-users/"
        api_keys.append(node['api_key'])
        headers = {"X-Node-Api-Key": node['api_key']}
        try:
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                
                # Optionally tag the results with the remote node key.
                for user in data:
                    user["remote_node"] = node_key

                aggregated_data.extend(data)
        except Exception as e:
            # You may log the exception here.
            pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def aggregated_list_all_users(request):
    """
    Aggregates user lists from all nodes:
      - Gets local users from the current node.
      - Iterates over all remote nodes (all keys in NODE_CONFIG except the current one),
        fetches the users from each remote endpoint (/list-all-users/),
        and returns the combined list.
    """
    aggregated_data = []

    # 1. Get local users.
    local_users = User.objects.all()
    local_serializer = RegisterUserSerializer(local_users, many=True)
    local_data = local_serializer.data
    # Optionally tag local users as coming from the current node.
    for user in local_data:
        user["remote_node"] = settings.INSTANCE_NAME
    aggregated_data.extend(local_data)

    # 2. Get remote users.
    current_instance = getattr(settings, "INSTANCE_NAME", "node1")
    remote_nodes = { key: node for key, node in settings.NODE_CONFIG.items() if key != current_instance }

    for node_key, node in remote_nodes.items():
        url = f"{node['url']}/list-all-users/"
        headers = {"X-Node-Api-Key": node['api_key']}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Tag each remote user with the node key.
                for user in data:
                    user["remote_node"] = node_key
                aggregated_data.extend(data)
        except Exception as e:
            # Optionally log the error
            pass

    return Response(aggregated_data, status=status.HTTP_200_OK)


def get_destination_node_from_request():
    # For testing, we assume the target user is on node2.
    return "node2"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_follow_request_inter_node(request, username):
    """
    Inter-node follow request endpoint on the sending node.
    - If the target user exists locally, process the follow request normally.
    - If the target user is not local, forward the request to the remote node.
    """
    # Get the sender (the authenticated user on the current node)
    sender = get_object_or_404(User, username=request.user)
    # Try to find the target user locally.
    receiver = get_local_user_by_username(username)
    
    # --- LOCAL PROCESSING ---
    if receiver:
        if Notif.objects.filter(sender_id=sender.id, receiver_id=receiver.id).exists():
            return Response({"message": "You already sent them a follow request!"}, status=status.HTTP_204_NO_CONTENT)
        if receiver.id == sender.id:
            return Response({"message": "You cannot send yourself a follow request!"}, status=status.HTTP_403_FORBIDDEN)
        if Following.objects.filter(followee_id=receiver.id, follower_id=sender.id).exists():
            return Response({"error": "Already following this user"}, status=status.HTTP_403_FORBIDDEN)
        
        data = {
            "receiver": receiver.id,
            "sender": sender.id,
            "notif_type": "FOLLOW_REQUEST"
        }
        try:
            serializer = NotifSerializer(data=data)
            if serializer.is_valid():
                serializer.save(receiver_id=receiver.id, sender_id=sender.id, notif_type="FOLLOW_REQUEST")
                return Response({"message": "Follow Request Sent!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Follow Request couldn't be made: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    # --- REMOTE PROCESSING (Forwarding) ---
    # Determine the current instance (e.g., "node1", "node2", "node3")
    current_instance = getattr(settings, "INSTANCE_NAME", "node1")
    remote_node = None

    # Determine the destination node (this function must be implemented)
    destination_node = get_destination_node_from_request()  # IMPLEMENT THIS FUNCTION
    
    # Set remote node configuration based on current instance and destination
    if current_instance == "node1":
        if destination_node == "node2":
            remote_node = settings.NODE_CONFIG.get("node2")
        elif destination_node == "node3":
            remote_node = settings.NODE_CONFIG.get("node3")
    elif current_instance == "node2":
        if destination_node == "node1":
            remote_node = settings.NODE_CONFIG.get("node1")
        elif destination_node == "node3":
            remote_node = settings.NODE_CONFIG.get("node3")
    elif current_instance == "node3":
        if destination_node == "node1":
            remote_node = settings.NODE_CONFIG.get("node1")
        elif destination_node == "node2":
            remote_node = settings.NODE_CONFIG.get("node2")
    
    if not remote_node:
        return Response({"error": "Remote node configuration not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Build the remote URL (assuming the remote node has an endpoint set up similarly)
    remote_url = f"{remote_node['url']}/create-follow-request/{username}/"
    
    # Build the payload with sender's username (as a string)
    payload = {"sender_username": request.user.username}
    
    headers = {
        "X-Node-Api-Key": remote_node['api_key']
    }
    
    try:
        remote_response = requests.post(remote_url, json=payload, headers=headers, timeout=5)
        if remote_response.status_code == 200:
            return Response(remote_response.json(), status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send remote follow request."}, status=remote_response.status_code)
    except Exception as e:
        return Response({"error": f"Exception occurred during remote call: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])  # Remote endpoint does not require a JWT.
def remote_create_follow_request(request, username):
    """
    Remote endpoint on the receiving node for processing forwarded follow requests.
    Expects a JSON payload with "sender_username". If the sender does not exist locally,
    it creates a stub user.
    """
    # Verify the inter-node API key.
    provided_key = request.headers.get("X-Node-Api-Key")
    if provided_key != settings.NODE_API_KEY:
        return Response({"error": "Invalid API key"}, status=403)
    
    # Look up the target (receiver) on the local database.
    receiver = get_object_or_404(User, username=username)
    
    # Get the sender's username from the payload.
    sender_username = request.data.get("sender_username")
    if not sender_username:
        return Response({"error": "Sender username missing."}, status=400)
    
    # Try to find the sender locally; if not found, create a stub user.
    try:
        sender = User.objects.get(username=sender_username)
    except User.DoesNotExist:
        # Create a minimal stub record for the remote user.
        sender = User.objects.create(username=sender_username)
        # Optionally, mark this record as a stub by setting a flag if your model supports it.
    
    if Notif.objects.filter(sender_id=sender.id, receiver_id=receiver.id).exists():
        return Response({"message": "Follow request already sent."}, status=204)
    
    data = {
        "receiver": receiver.id,
        "sender": sender.id,
        "notif_type": "FOLLOW_REQUEST"
    }
    try:
        serializer = NotifSerializer(data=data)
        if serializer.is_valid():
            serializer.save(receiver_id=receiver.id, sender_id=sender.id, notif_type="FOLLOW_REQUEST")
            return Response({"message": "Remote follow request received!"}, status=200)
        else:
            return Response(serializer.errors, status=400)
    except Exception as e:
        return Response({"error": f"Failed to create remote follow request: {str(e)}"}, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])  # No JWT required for inter-node calls.
def remote_get_follower_requests(request):
    """
    Remote endpoint to return follower request notifications for a given receiver.
    Expects a query parameter 'receiver' (the username of the receiver).
    Uses the API key to authenticate the inter-node call.
    """
    provided_key = request.headers.get("X-Node-Api-Key")
    if provided_key != settings.NODE_API_KEY:
        return Response({"error": "Invalid API key"}, status=403)
    
    # Receiver username must be passed as a query parameter.
    receiver_username = request.query_params.get("receiver")
    if not receiver_username:
        return Response({"error": "Receiver username missing."}, status=400)
    
    receiver = get_object_or_404(User, username=receiver_username)
    notifs = Notif.objects.filter(receiver=receiver.id).order_by("-created_at")
    serializer = NotifSerializer(notifs, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_follower_request_list(request):
    """
    Get a list of Notifs of type follower_request of followee user
    'receiver' is user receiving notifs (user logged in)
    Get reciever username from request data
    Return list of Notifs of type follower_request
    
    @author Christine Bao
    """
    receiver = get_object_or_404(User, username=request.user)

    try:
        follower_request_list = (
            Notif.objects
                .filter(receiver=receiver.id)
                .order_by("-created_at")
            )

        serializer = NotifSerializer(follower_request_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except:
        return Response({"error":"Error: Unable to retrieve follower requests"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_follow_request_inter_node(request, username):
    """
    Accept a follow request in an inter-node scenario.
    
    - The current logged-in user (followee) accepts the follow request.
    - If the sender (follower) does not exist locally, create a stub user.
    - Ensure that a follow request notification exists.
    - Create a Following relationship.
      If the relationship is mutual, mark it as friends.
    - Delete the follow request notification.
    """
    # Get the followee (the currently authenticated user)
    followee = get_object_or_404(User, username=request.user)
    
    # Attempt to retrieve the sender (follower) from the local DB.
    # If the sender doesn't exist (i.e. it's a remote user), create a stub.
    try:
        follower = User.objects.get(username=username)
    except User.DoesNotExist:
        follower = User.objects.create(username=username)
        # Optionally, add extra fields (first_name, last_name, etc.) if available
        # and mark the user as a stub (e.g., follower.is_stub = True).
    
    # Check if a follow request notification exists.
    if not Notif.objects.filter(
        receiver_id=followee.id, 
        sender_id=follower.id, 
        notif_type="FOLLOW_REQUEST"
    ).exists():
        return Response({"error": "No follow request found to accept."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Prevent following yourself.
    if follower.id == followee.id:
        return Response({"error": "Cannot follow yourself."}, status=status.HTTP_403_FORBIDDEN)
    
    # Prevent duplicate following.
    if Following.objects.filter(followee_id=followee.id, follower_id=follower.id).exists():
        return Response({"error": "Already following this user."}, status=status.HTTP_403_FORBIDDEN)
    
    data = {"followee": followee.id, "follower": follower.id}
    try:
        # If mutual following exists, mark the relationship as friends.
        if Following.objects.filter(followee_id=follower.id, follower_id=followee.id).exists():
            relationship = Following.objects.get(followee_id=follower.id, follower_id=followee.id)
            relationship.friends = "YES"
            relationship.save()
            data["friends"] = "YES"
        
        serializer = FollowingSerializer(data=data)
        if serializer.is_valid():
            serializer.save(followee_id=followee.id, follower_id=follower.id)
            # Delete the notification.
            Notif.objects.filter(
                receiver_id=followee.id, 
                sender_id=follower.id, 
                notif_type="FOLLOW_REQUEST"
            ).delete()
            return Response({"message": "Follow request accepted. You are now following this user."}, status=200)
        else:
            return Response(serializer.errors, status=400)
    except Exception as e:
        return Response({"error": f"Something went wrong, user not followed: {str(e)}"}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_follower_request (request, username):
    """
    TODO 
    - maybe shouldn't allow admins to follow or be followed

    Accept follow request
    Allowing a follow request adds a Following relationship between the two users and deletes the follower request notif.

    @author Christine Bao
    """
    # Get followee and follower
    followee = get_object_or_404(User, username=request.user)
    follower = get_object_or_404(User, username=username)
    
    # Must have a notif to accept follow request
    if Notif.objects.filter(receiver_id=followee.id, sender_id=follower.id).exists() == False:
        return Response({"error": "Send a follow request first."}, status=status.HTTP_400_BAD_REQUEST)
    # Cannot follow yourself
    if follower.id == followee.id:
        return Response({"error": "Cannot follow yourself."}, status=status.HTTP_403_FORBIDDEN)
    # Cannot follow someone twice
    if Following.objects.filter(followee_id=followee.id, follower_id=follower.id).exists():
        return Response({"error": "Already following this user"}, status=status.HTTP_403_FORBIDDEN)

    # If not friends and following
    data = {"followee": followee.id, "follower": follower.id}
    try:
        # Mark users as friends if they follow each other
        if Following.objects.filter(followee_id=follower.id, follower_id=followee.id).exists():
            relationship = Following.objects.get(followee_id=follower.id, follower_id=followee.id)
            relationship.friends = 'YES'
            relationship.save()
            data = {"followee": followee.id, "follower": follower.id, "friends":"YES"}
            
        serializer = FollowingSerializer(data=data)
        if serializer.is_valid():
            serializer.save(followee_id = followee.id, follower_id = follower.id)
            Notif.objects.filter(receiver_id=followee.id, sender_id=follower.id).delete() # get Notif id to delete follow_request
            return Response({"message": "You have followed this user."}, status=status.HTTP_200_OK)
    except:
        return Response({"message": "Something went wrong, user not followed"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deny_follow_request(request, username):
    """
    Deny Follow Request
    'receiver' is the User we no longer want to follow but still have a pending follow request
    'sender' is the User who is cancelling the friend request
    """
    # Get sender and receiver of the follow request
    sender = get_object_or_404(User, username=username)
    receiver = get_object_or_404(User, username=request.user)

    try: # delete Notif Request                                
        if Notif.objects.filter(receiver_id=receiver.id, sender_id=sender.id).exists():                                         
            Notif.objects.filter(receiver_id=receiver.id, sender_id=sender.id).delete() 
            return Response({"message":"Follow Request Denied!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error":"There's nothing to delete."}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"error":"Unable to Deny Follow Request."}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_follower_request(request, username):
    """
    Cancel Follow Request
    'receiver' is the User we no longer want to follow but still have a pending follow request
    'sender' is the User who is cancelling the friend request
    """
    receiver = get_object_or_404(User, username=username)
    try:
        notif = Notif.objects.get(
            sender=request.user, 
            receiver=receiver, 
            notif_type="FOLLOW_REQUEST"
        )
        notif.delete()
        return Response({"message": "Follow request canceled."}, status=status.HTTP_200_OK)
    except Notif.DoesNotExist:
        return Response({"error": "No such follow request."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deny_follow_request_inter_node(request, username):
    """
    Deny a follow request in an inter-node scenario.
    
    - The currently authenticated user (receiver) denies the follow request.
    - If the sender (follower) does not exist locally (i.e. it's a remote user), create a stub user.
    - Ensure that a follow request notification exists.
    - Delete the follow request notification.
    """
    # Get the receiver (the currently authenticated user)
    receiver = get_object_or_404(User, username=request.user)

    # Attempt to retrieve the sender (follower) from the local DB.
    # If the sender doesn't exist (i.e. it's a remote user), create a stub.
    try:
        sender = User.objects.get(username=username)
    except User.DoesNotExist:
        sender = User.objects.create(username=username)
        # Optionally, set additional fields or mark the user as a stub (e.g., sender.is_stub = True)

    # Check if a follow request notification exists.
    if not Notif.objects.filter(
        receiver_id=receiver.id, 
        sender_id=sender.id, 
        notif_type="FOLLOW_REQUEST"
    ).exists():
        return Response({"error": "No follow request found to deny."}, status=status.HTTP_400_BAD_REQUEST)

    # Attempt to delete the follow request notification.
    try:
        Notif.objects.filter(
            receiver_id=receiver.id, 
            sender_id=sender.id, 
            notif_type="FOLLOW_REQUEST"
        ).delete()
        return Response({"message": "Follow request denied."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"Unable to deny follow request: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, username):
    """
    Unfollow a User
    
    1. If you try to unfollow yourself => 403
    2. If you are not following the user => 400
    3. Otherwise, remove the follow relationship => 200
    """
    # "followee" is the user being unfollowed
    followee = get_object_or_404(User, username=username)
    # "follower" is the current, authenticated user
    follower = request.user

    # 1. Cannot unfollow yourself
    if follower.id == followee.id:
        return Response(
            {"error": "Cannot unfollow yourself."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if a following relationship exists
    existing_rel = Following.objects.filter(followee_id=followee.id, follower_id=follower.id).first()
    if not existing_rel:
        # 2. If you’re not following them, return 400
        return Response(
            {"error": "You can't unfollow someone you don't follow"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # 3. Remove the following relationship
    existing_rel.delete()

    # If there's a reverse relationship (the other user following you) in "friends" mode, set it to "NO"
    reverse_rel = Following.objects.filter(followee_id=follower.id, follower_id=followee.id).first()
    if reverse_rel:
        reverse_rel.friends = 'NO'
        reverse_rel.save()

    return Response(
        {"message": "You have unfollowed this user."}, 
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_followers(request, username):
    """
    TODO 
    - test if this works

    Get followers of author.
    Get author from request.data (user logged in) or by username (another user).
    Returns list of users who follow the author.

    @author Christine Bao
    """
    author = get_object_or_404(User, username=username)
    
    try:
        followers = (
            Following.objects
                .filter(followee_id = author.id)
                .order_by("-followed_at")
        )
        serializer = FollowingSerializer(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({"message":"Error: Cannot retrieve followers"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_followees(request, username):
    """
    TODO 
    - test if this works

    Get followees of author.
    Get author from request.data (user logged in) or by username (another user).
    Returns list of users who follow the author.

    @author Christine Bao
    """
    author = get_object_or_404(User, username=username)
    
    try:
        followers = (
            Following.objects
                .filter(follower_id = author.id)
                .order_by("-followed_at")
        )
        serializer = FollowingSerializer(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({"message":"Error: Cannot retrieve followers"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_non_followees(request):
    """
    Returns a list of all users that the current user is not following.
    Excludes the current user from the list.
    """
    current_user = request.user
    # Get IDs of all users that the current user is following
    followed_user_ids = Following.objects.filter(follower=current_user).values_list('followee_id', flat=True)
    
    # Query all users excluding those already followed and excluding self
    non_followees = User.objects.exclude(id__in=followed_user_ids).exclude(id=current_user.id)
    
    serializer = RegisterUserSerializer(non_followees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friends(request):
    """
    TODO 
    - test if this works

    Get friends of author.
    Get author from request.data (user logged in) or by username (another user).
    Returns list of users who follow the author.

    @author Christine Bao
    """
    author = get_object_or_404(User, username=request.user)
    
    try:
        followers = (
            Following.objects
                .filter(follower_id=author.id, friends='YES')
                .order_by("-followed_at")
        )

        serializer = FollowingSerializer(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({"message":"Error: Cannot retrieve followers"}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_friend(request, username):
    """
    TODO - to be removed
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



from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests

class RemoteUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        remote_node = settings.NODE_CONFIG.get("node2")
        if not remote_node:
            return Response({"error": "Node 2 configuration not found in settings."}, status=500)

        url = f"{remote_node['url']}/users/"
        headers = {
            "X-Node-Api-Key": remote_node['api_key']
        }

        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return Response(response.json(), status=200)
            return Response({"error": "Failed to fetch users from node2."}, status=response.status_code)
        except Exception as e:
            return Response({"error": f"Exception occurred: {str(e)}"}, status=500)

class HelloView(APIView):
    # Allow anyone to access this endpoint
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Hello"})



    



from .serializers import RegisterUserSerializer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    """
    TODO - to be removed
    Get the friends of the authenticated user
    """
    friends = request.user.friends.all()
    serializer = RegisterUserSerializer(friends, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friends_posts(request):
    """
    Show the posts made by all the users the authenticated user is following.
    """
    user = request.user
    # First, get all follow relationships where the current user is the follower.
    followees_ids = Following.objects.filter(follower=user).values_list("followee_id", flat=True)

    # Then, filter posts by authors in followees_ids, only returning PUBLIC, UNLISTED, or FRIENDS.
    # Exclude DELETED and DRAFT.
    posts = (
        Post.objects
            .filter(
                author_id__in=followees_ids,
                visibility__in=["PUBLIC", "UNLISTED", "FRIENDS"]
            )
            .exclude(visibility="DELETED")
            .exclude(visibility="DRAFT")
            .order_by("-published")
    )

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=200)











# register an user while being an admin --> same functionality just the view needs to be for isadminonly

@api_view(['POST'])
@permission_classes([IsAdminUser])  
def register_user_as_admin(request):
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

from django.db.models import Q

from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Post, Following
from .serializers import PostSerializer

from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Post, Following
from .serializers import PostSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stream_posts(request):
    """
    Returns a stream of posts (excluding your own) including:
      - PUBLIC posts (visible to everyone, excluding your own)
      - UNLISTED posts made by users you follow (via the Following model)
      - FRIENDS posts made by users you follow
    Excludes posts with visibility "DELETED" and sorts posts by the most recent update.
    """
    user = request.user

    # Get IDs of all followees for the current user.
    followee_ids = Following.objects.filter(follower=user).values_list("followee_id", flat=True)

    posts = Post.objects.filter(
        (
          Q(visibility="PUBLIC") & ~Q(author=user)
        ) |
        (
          Q(visibility="UNLISTED", author__in=followee_ids)
        ) |
        (
          Q(visibility="FRIENDS", author__in=followee_ids)
        )
    ).exclude(visibility="DELETED").order_by("-updated")

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

class RemoteListAllUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Determine current instance name; default to "node1" if not set.
        current_instance = getattr(settings, "INSTANCE_NAME", "node1")
        
        # Choose the remote node: if we're node1, target node2; if node2, target node1.
        if current_instance == "node1":
            remote_node = settings.NODE_CONFIG.get("node2")
        elif current_instance == "node2":
            remote_node = settings.NODE_CONFIG.get("node1")
        else:
            return Response({"error": "Current node is not recognized."}, status=500)

        if not remote_node:
            return Response({"error": "Remote node configuration not found."}, status=500)

        # Build the URL to the remote node's endpoint.
        url = f"{remote_node['url']}/list-all-users/"
        headers = {
            "X-Node-Api-Key": remote_node['api_key']
        }

        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return Response(response.json(), status=200)
            return Response({"error": "Failed to fetch users from remote node."}, status=response.status_code)
        except Exception as e:
            return Response({"error": f"Exception occurred: {str(e)}"}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny]) 
def list_all_users(request):
    """
    Lists all users.
    """
    users = User.objects.all()  # Retrieves all users
    serializer = RegisterUserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # ✅ Requires authentication
def list_non_friend_users(request):
    """
    TODO - to be changed to accomadate new Following model for followers-only and friends-only posts

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
    TODO - think about how we want comments to appear in friends-only or follower-only posts

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
    Creates a new Comment on a post.
    Ensures the post exists and sets the comment's author to the requesting user.
    """
    # Look up the post only by its ID (removing the visibility filter)
    post = get_object_or_404(Post, id=post_id)
    
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
    Toggles a like on a PUBLIC post. If the user has already liked the post, the like is removed.
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    # Filter by both post and the requesting user
    existing_like = Like.objects.filter(post=post, author=request.user).first()
    if existing_like:
        existing_like.delete()
        return Response({"message": "You unliked this post."}, status=status.HTTP_200_OK)
    else:
        new_like = Like.objects.create(post=post, author=request.user)
        # optionally serialize new_like
        return Response({"message": "You liked this post."}, status=status.HTTP_201_CREATED)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_comment_like(request, post_id, comment_id):
    """
    Toggles a like on a comment. If the user has already liked the comment, the like is removed.
    """
    try:
        comment = Comment.objects.get(id=comment_id, post__id=post_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    existing_like = CommentLike.objects.filter(comment=comment, author=request.user).first()
    if existing_like:
        existing_like.delete()
        return Response({"message": "You unliked this comment."}, status=status.HTTP_200_OK)
    else:
        CommentLike.objects.create(comment=comment, author=request.user)
        return Response({"message": "You liked this comment."}, status=status.HTTP_201_CREATED)

##############################################################################################################
#Remote api endpoints
##############################################################################################################
class CrossNodePostViewSet(viewsets.ModelViewSet):
    """
    Enhanced Post ViewSet with cross-node capabilities.
    """
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    serializer_class = CrossNodePostSerializer
    
    def get_queryset(self):
        # Filter out deleted posts for normal listing
        if self.action == 'list':
            return Post.objects.filter(deleted_at__isnull=True).exclude(visibility='DELETED')
        
        # For other actions, include all posts
        return Post.objects.all()
    
    def perform_create(self, serializer):
        post = serializer.save()
        # Queue post for distribution to followers
        self.sync_post_to_followers(post)
    
    def perform_update(self, serializer):
        post = serializer.save()
        # Queue post updates for distribution
        self.sync_post_to_followers(post)
    
    def perform_destroy(self, instance):
        # Soft delete the post and mark for sync
        instance.deleted_at = timezone.now()
        instance.visibility = 'DELETED'
        instance.needs_sync = True
        instance.save()
        # Distribute deletion to followers
        self.sync_post_to_followers(instance)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a soft-deleted post"""
        post = self.get_object()
        
        # Check if it's actually deleted
        if not post.is_deleted():
            return Response({"detail": "Post is not deleted"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Restore the post
        post.deleted_at = None
        post.visibility = 'PUBLIC'  # Or maybe restore to original visibility
        post.needs_sync = True
        post.save()
        
        # Sync the restored post
        self.sync_post_to_followers(post)
        
        return Response({"detail": "Post restored successfully"})
    
    def sync_post_to_followers(self, post):
        """
        Sync post to remote followers
        In a production environment, this would be a background task
        """
        try:
            # Skip for non-local posts or private posts
            if not post.local_copy or post.visibility in ['PRIVATE', 'DRAFT']:
                return
            
            # Get remote followers based on visibility
            remote_followers = RemoteFollower.objects.filter(local_user=post.author)
            
            # Skip if no followers
            if not remote_followers.exists():
                return
            
            # Group followers by node
            followers_by_node = {}
            for follower in remote_followers:
                if follower.remote_node not in followers_by_node:
                    followers_by_node[follower.remote_node] = []
                followers_by_node[follower.remote_node].append(follower.remote_username)
            
            # Get active nodes
            active_nodes = Node.objects.filter(is_active=True)
            node_configs = {}
            
            # Convert Node models to config dictionary
            for node in active_nodes:
                node_configs[node.id] = {
                    'url': node.base_url,
                    'username': node.username,
                    'password': node.password  # Assuming this is stored securely
                }
            
            # For each node with followers
            for node_id, followers in followers_by_node.items():
                # Skip if already synced and no changes needed
                if node_id in post.remote_nodes_sent and not post.needs_sync:
                    continue
                
                # Get node configuration
                node_config = node_configs.get(node_id)
                if not node_config:
                    logger.error(f"No configuration found for node: {node_id}")
                    continue
                
                # Prepare post data
                post_data = post.to_dict()
                post_data['followers'] = followers
                
                # Add image if exists and post not deleted
                if post.image and not post.is_deleted():
                    post_data['image_content'] = self.get_base64_file(post.image)
                
                # Send to remote node
                self.send_post_to_remote_node(node_id, node_config, post_data, post)
            
            # Mark post as no longer needing sync
            post.needs_sync = False
            post.save(update_fields=['needs_sync', 'updated'])
                
        except Exception as e:
            logger.error(f"Error syncing post {post.id} to followers: {str(e)}")
    
    def get_base64_file(self, file_field):
        """Convert file to base64 for transmission"""
        try:
            file_field.open()
            file_content = file_field.read()
            file_field.close()
            return base64.b64encode(file_content).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding file: {str(e)}")
            return None
    
    def send_post_to_remote_node(self, node_id, node_config, post_data, post):
        """Send post to a remote node"""
        remote_url = f"{node_config['url']}/receive-post/"
        
        # Authentication method depends on your implementation
        # Option 1: Use API key authentication
        headers = {
            "X-Node-Api-Key": node_config.get('api_key', ''),
            "Content-Type": "application/json"
        }
        
        # Option 2: Use basic auth or token auth as needed
        auth = None
        if 'username' in node_config and 'password' in node_config:
            auth = (node_config['username'], node_config['password'])
        
        try:
            # Use appropriate auth method
            if auth:
                response = requests.post(
                    remote_url, 
                    json=post_data,
                    auth=auth,
                    timeout=10
                )
            else:
                response = requests.post(
                    remote_url, 
                    json=post_data,
                    headers=headers,
                    timeout=10
                )
            
            if response.status_code == 200:
                # Record that we've sent to this node
                post.add_remote_node_sent(node_id)
                logger.info(f"Successfully sent post {post.id} to node {node_id}")
            else:
                logger.error(f"Failed to send post to node {node_id}: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Exception sending post to node {node_id}: {str(e)}")

@api_view(['POST'])
def receive_post(request):
    """
    Endpoint to receive posts from remote nodes
    """
    # Validate authentication
    # Option 1: API key validation
    api_key = request.headers.get('X-Node-Api-Key')
    if api_key:
        # Find the node with this API key
        try:
            node = Node.objects.get(api_key=api_key, is_active=True)
            sender_node_id = node.id
        except Node.DoesNotExist:
            return Response({"error": "Invalid API key"}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Option 2: Basic auth validation (use your preferred auth method)
    elif request.user.is_authenticated:
        # Check if user is a node
        try:
            node = Node.objects.get(username=request.user.username, is_active=True)
            sender_node_id = node.id
        except Node.DoesNotExist:
            return Response({"error": "Not authorized as a node"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Deserialize the post data
    serializer = RemotePostSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Save the post
        post = serializer.save()
        
        # Handle post deletion
        if post.is_deleted():
            logger.info(f"Received deletion for post {post.id} from node {sender_node_id}")
        else:
            logger.info(f"Received post {post.id} from node {sender_node_id}")
        
        return Response(
            {"message": "Post received successfully", "post_id": str(post.id)}, 
            status=status.HTTP_200_OK
        )
                        
    except Exception as e:
        logger.error(f"Error processing remote post: {str(e)}")
        return Response(
            {"error": f"Error processing post: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_remote_follower(request):
    """Register a remote follower for a local user"""
    remote_username = request.data.get('username')
    remote_node = request.data.get('node')
    
    if not remote_username or not remote_node:
        return Response(
            {"error": "Username and node are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Find the node
        node = Node.objects.get(id=remote_node, is_active=True)
        
        # Create the remote follower
        RemoteFollower.objects.get_or_create(
            local_user=request.user,
            remote_username=remote_username,
            remote_node=remote_node
        )
        
        return Response(
            {"message": "Remote follower registered successfully"}, 
            status=status.HTTP_201_CREATED
        )
    except Node.DoesNotExist:
        return Response(
            {"error": f"Node {remote_node} not found or inactive"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Error registering follower: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_remote_follower(request):
    """Unregister a remote follower"""
    remote_username = request.data.get('username')
    remote_node = request.data.get('node')
    
    if not remote_username or not remote_node:
        return Response(
            {"error": "Username and node are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Find and delete the follower
        follower = RemoteFollower.objects.filter(
            local_user=request.user,
            remote_username=remote_username,
            remote_node=remote_node
        ).first()
        
        if follower:
            follower.delete()
            return Response(
                {"message": "Remote follower unregistered successfully"}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Follower not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        return Response(
            {"error": f"Error unregistering follower: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

