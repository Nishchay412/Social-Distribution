from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class ListUsersAPITestCase(APITestCase):
    def setUp(self):
        #Create Users + Admin To Populate List
        self.test_user1 = User.objects.create_user(username='test1', password='test123',email='test1@example.com')
        self.test_user2 = User.objects.create_user(username='test2', password='test123',email='test2@example.com')
        self.test_admin2 = User.objects.create_user(username='admin2', password='admin123',email='test3@example.com')

        self.user = self.test_user1
        self.client.force_authenticate(user=self.user)
        self.client.force_authenticate(user=self.test_user1)
        self.client.force_authenticate(user=self.test_user2)
        self.client.force_authenticate(user=self.test_admin2)
        
        #Create SuperUser/Admin
        self.admin = User.objects.create_user(username='admin', password='admin123')
        self.client.login(username='admin', password='admin123') # Login as admin user
        self.client.force_authenticate(user=self.user) # Force authenticate
    
    def test_list_users(self):
        url = reverse('list_users_excluding_self') # 'users/exclude-self/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        