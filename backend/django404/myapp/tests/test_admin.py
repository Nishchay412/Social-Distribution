from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminAPITestCase(APITestCase):
    def setUp(self):
        #Create Users + Admin To Populate List
        self.test_user1 = User.objects.create_user(username='test1', password='test123', first_name='test1', last_name='test1', email='test1@test.com')
        self.test_user2 = User.objects.create_user(username='test2', password='test123', first_name='test2', last_name='test2', email='test2@test.com')
        self.test_admin2 = User.objects.create_superuser(username='admin2', password='admin123', email='admin@admin.com')
        
        #Create SuperUser/Admin
        self.test_admin1 = User.objects.create_user(username='admin1', password='admin123', email='admin1@admin.com')
        self.client.login(username='admin1', password='admin123') # Login as admin user
        self.client.force_authenticate(user=self.test_admin1) # Force authenticate
    
    def test_list_users(self):
        """
        Test List User API
        Check if admin is able to retrieve all existing users except self.
        Check if retrieved user info is correct.
        """
        url = reverse('list_users_excluding_self') # 'users/exclude-self/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK) # request went thru
        self.assertEqual(len(response.data), 3) # retrieves only 3 users
        self.assertEqual(response.data[0], {'username': self.test_user1.username, 'email': self.test_user1.email, 'first_name': self.test_user1.first_name, 'last_name': self.test_user1.last_name})
        self.assertEqual(response.data[1], {'username': self.test_user2.username, 'email': self.test_user2.email, 'first_name': self.test_user2.first_name, 'last_name': self.test_user2.last_name})
        self.assertEqual(response.data[2], {'username': self.test_admin2.username, 'email': self.test_admin2.email, 'first_name': self.test_admin2.first_name, 'last_name': self.test_admin2.last_name})

        # add another user for admin to detect
        self.test_user3 = User.objects.create_user(username='test3', password='test123', first_name='test3', last_name='test3', email='test3@test.com')
        url = reverse('list_users_excluding_self') # 'users/exclude-self/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # request went thru
        self.assertEqual(len(response.data), 4) # retrieves 4 users now
        self.assertEqual(response.data[3], {'username': self.test_user3.username, 'email': self.test_user3.email, 'first_name': self.test_user3.first_name, 'last_name': self.test_user3.last_name})

    def test_edit_users(self):
        """
        Test Edit User API
        Check if admin is able to edit
        """
        url = reverse('admin_update_user', args=[self.test_user1.username]) # 'users/exclude-self/<str:username>/update-user/'
        data = {'username': 'edwin', 'first_name':'Edwin', 'last_name': 'Doe', 'email':'edwindoe@gmail.com'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking user was edited
        url = reverse('list_users_excluding_self') # 'users/exclude-self/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # request went thru
        self.assertEqual(response.data[0], {'username': 'edwin', 'email': 'edwindoe@gmail.com', 'first_name':'Edwin', 'last_name': 'Doe'})

    def test_delete_users(self):
        """
        Test Delete User API
        Check if admin is able to delete user. Must not be able to delete another admin.
        """
        url = reverse('delete_user', args=[self.test_user2.username]) # 'users/exclude-self/<str:username>/delete-user/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # request went thru
        
        # Checking user was deleted
        url = reverse('list_users_excluding_self') # 'users/exclude-self/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # request went thru
        self.assertEqual(len(response.data),2) # retrieves 2 users now

        # Checking we CANNOT delete another admin
        url = reverse('delete_user', args=[self.test_admin2.username]) # 'users/exclude-self/<str:username>/delete-user/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # request was denied
        