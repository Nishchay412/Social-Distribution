from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from myapp.models import Post, Like

User = get_user_model()

class LikeAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='liker', password='testpass')
        self.client.login(username='liker', password='testpass')
        self.client.force_authenticate(user=self.user) # Force authentication for the test client
        self.post = Post.objects.create(author=self.user, title='Like Me')

    def test_toggle_like(self):
        """
        Test toggling a like on a post.
        """
        url = reverse('toggle-like', args=[self.post.id])
        # First call: creates a like
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(post=self.post, author=self.user).exists())

        # Second call: removes the like
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Like.objects.filter(post=self.post, author=self.user).exists())