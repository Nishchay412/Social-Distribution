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