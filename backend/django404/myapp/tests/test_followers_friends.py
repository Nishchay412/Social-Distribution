from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from myapp.models import Following, Notif
 
User = get_user_model()
 
class FollowersFriendsAPITestCase(APITestCase):
 
     def setUp(self):
         """
         Set up test users:
         - self.user: the logged-in user (follower)
         - self.user2: the target user (followee)
         - self.user3: another user (unrelated user)
         """
         # Ensure we start fresh (avoid unique constraint errors)
         User.objects.all().delete()
 
         self.user = User.objects.create_user(username='user1', email='user1@example.com', password='testpass')
         self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpass')
         self.user3 = User.objects.create_user(username='user3', email='user3@example.com', password='testpass')
 
         # Authenticate the client as self.user
         self.client.force_authenticate(user=self.user)
 
     # Send a Follow Request
     def test_send_follow_request_success(self):
         url = reverse('create_follow_request', args=[self.user2.username])
         response = self.client.post(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
 
     def test_send_follow_request_to_self_fails(self):
         url = reverse('create_follow_request', args=[self.user.username])
         response = self.client.post(url)
         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
 
     def test_send_follow_request_already_following_fails(self):
         Following.objects.create(follower=self.user, followee=self.user2)
         url = reverse('create_follow_request', args=[self.user2.username])
         response = self.client.post(url)
         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
 
     # Accept a Follow Request
     def test_accept_follow_request_success(self):
         Notif.objects.create(receiver=self.user2, sender=self.user, notif_type="FOLLOW_REQUEST")
         url = reverse('accept_follower_request', args=[self.user.username])
         self.client.force_authenticate(user=self.user2)  # Log in as receiver
         response = self.client.post(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
 
     def test_accept_nonexistent_follow_request_fails(self):
         url = reverse('accept_follower_request', args=[self.user.username])
         self.client.force_authenticate(user=self.user2)
         response = self.client.post(url)
         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
 
     # Cancel a Follow Request
     def test_cancel_follow_request_success(self):
         Notif.objects.create(receiver=self.user2, sender=self.user, notif_type="FOLLOW_REQUEST")
         url = reverse('cancel_follower_request', args=[self.user2.username])
         response = self.client.delete(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
 
     def test_cancel_nonexistent_follow_request_fails(self):
         url = reverse('cancel_follower_request', args=[self.user2.username])
         response = self.client.delete(url)
         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
 
     # Unfollow a User
     def test_unfollow_user_success(self):
         Following.objects.create(follower=self.user, followee=self.user2)
         url = reverse('unfollow_user', args=[self.user2.username])
         response = self.client.delete(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
 
     def test_unfollow_non_following_user_fails(self):
         url = reverse('unfollow_user', args=[self.user2.username])
         response = self.client.delete(url)
         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
 
     # Get Followers List
     def test_get_followers_list(self):
         Following.objects.create(follower=self.user, followee=self.user2)
         url = reverse('get_followers', args=[self.user2.username])
         response = self.client.get(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertEqual(len(response.data), 1)  # Only one follower (self.user)
 
     def test_get_followers_list_empty(self):
         url = reverse('get_followers', args=[self.user2.username])
         response = self.client.get(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertEqual(len(response.data), 0)
 
     # Check Relationship Between Users
     def test_relationship_self(self):
         url = reverse('get_relationship', args=[self.user.username])
         response = self.client.get(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertEqual(response.data["relation"], "YOURSELF")
 
     def test_relationship_friends(self):
         Following.objects.create(follower=self.user, followee=self.user2)
         Following.objects.create(follower=self.user2, followee=self.user)
         url = reverse('get_relationship', args=[self.user2.username])
         response = self.client.get(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertEqual(response.data["relation"], "FRIEND")
 
     def test_relationship_followee(self):
         Following.objects.create(follower=self.user, followee=self.user2)
         url = reverse('get_relationship', args=[self.user2.username])
         response = self.client.get(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertEqual(response.data["relation"], "FOLLOWEE")
 
     def test_relationship_follower(self):
         Following.objects.create(follower=self.user2, followee=self.user)
         url = reverse('get_relationship', args=[self.user2.username])
         response = self.client.get(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertEqual(response.data["relation"], "FOLLOWER")
 
     def test_relationship_nobody(self):
         url = reverse('get_relationship', args=[self.user2.username])
         response = self.client.get(url)
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertEqual(response.data["relation"], "NOBODY")