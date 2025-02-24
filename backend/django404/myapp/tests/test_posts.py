from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from myapp.models import Post
import uuid

User = get_user_model()

class PostAPITestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass'
        )
        # Force authentication for the test client
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        url = reverse('create-post')  # e.g. /posts/create/
        data = {
            'title': 'My New Post',
            'content': 'Hello world!',
            # 'image': some_image_file, etc.
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], 'My New Post')

    def test_list_posts(self):
        # Make a few posts
        Post.objects.create(author=self.user, title='Post1')
        Post.objects.create(author=self.user, title='Post2')
    
        url = reverse('list-posts')  # e.g. /posts/
        response = self.client.get(url)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_post(self):
        post = Post.objects.create(author=self.user, title='Retrieve Me')
        url = reverse('retrieve-post', args=[post.id])  # e.g. /posts/<uuid:post_id>/
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Retrieve Me')

    def test_edit_post(self):
        post = Post.objects.create(author=self.user, title='Old Title')
        url = reverse('edit-post', args=[post.id])  # e.g. /posts/<uuid>/edit/
        data = {'title': 'New Title'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')

    def test_delete_post(self):
        post = Post.objects.create(author=self.user, title='To Delete')
        url = reverse('delete-post', args=[post.id])  # e.g. /posts/<uuid>/delete/
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Post.objects.filter(id=post.id).exists())