from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthTestCase(APITestCase):
    def setUp(self):
        """
        Create a user and define login/logout URLs.
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            is_approved=True
        )
        self.login_url = "/login/"
        self.logout_url = "/logout/"

    def test_login_success(self):
        """
        Verify a user with valid credentials can log in and receive JWT tokens.
        """
        data = {
            "username": "testuser",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)  # JWT access token
        self.assertIn("refresh", response.data) # JWT refresh token
        self.assertEqual(response.data["user"]["username"], "testuser")

    def test_login_failure_invalid_credentials(self):
        """
        Verify an error is returned if the user provides incorrect credentials.
        """
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Invalid username or password")

    def test_login_failure_no_username(self):
        """
        Verify login fails if username is missing.
        """
        data = {
            "username": "",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        # Adjust the expected error message if your endpoint differs
        self.assertEqual(response.data["error"], "Invalid username or password")

    def test_login_failure_no_password(self):
        """
        Verify login fails if password is missing.
        """
        data = {
            "username": "testuser",
            "password": ""
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        # Adjust the expected error message if your endpoint differs
        self.assertEqual(response.data["error"], "Invalid username or password")

    def test_logout_success(self):
        """
        Verify a user can log out successfully using a valid refresh token.
        """
        # First, log in the user to get tokens
        login_response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "password123"
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
    
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]
    
        # Set the access token in the request headers
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
    
        # Logout using the refresh token
        response = self.client.post(self.logout_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_failure_invalid_token(self):
        """
        Verify logout fails if an invalid refresh token is provided.
        """
        # Log in to get a valid access token
        login_response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "password123"
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
    
        access_token = login_response.data["access"]
    
        # Set the access token in the request headers
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
    
        # Attempt logout with an invalid refresh token
        response = self.client.post(self.logout_url, {"refresh": "invalidtoken"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    

    def test_logout_failure_not_authenticated(self):
        """
        Verify logout fails if the user is not authenticated (no access token).
        """
        # No credentials set, so the user is effectively not logged in
        response = self.client.post(self.logout_url, {"refresh": "someRandomToken"})
        # Depending on your implementation, this might be 401 or 403
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # If your code specifically returns 401, you can assert:
        # self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # If it returns 403, change accordingly.
