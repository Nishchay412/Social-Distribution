from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .serializers import RegisterUserSerializer  # Import the correct serializer
from django.contrib.auth.models import User

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
