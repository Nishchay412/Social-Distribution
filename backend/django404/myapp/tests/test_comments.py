from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from myapp.models import Post, Comment
import uuid

User = get_user_model()

class CommentAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='commenter', password='testpass')# Create a user
        self.client.login(username='commenter', password='testpass')# Log in as the user
        self.post = Post.objects.create(author=self.user, title='Post for Comments')# Create a post
        self.client.force_authenticate(user=self.user) # Force authentication for the test client

    def test_list_comments(self):
        Comment.objects.create(post=self.post, author=self.user, text='First comment')# Create a comment
        Comment.objects.create(post=self.post, author=self.user, text='Second comment')# Create another comment

        url = reverse('list-comments', args=[self.post.id])  # /posts/<uuid>/comments/
        response = self.client.get(url)# Make a GET request to the endpoint

        self.assertEqual(response.status_code, status.HTTP_200_OK)# Assert that the response status code is 200
        self.assertEqual(len(response.data), 2)#Assert that the response contains two comments
        self.assertEqual(response.data[0]['text'], 'Second comment')#Assert that the first comment is 'First comment'

    def test_create_comment(self):
        url = reverse('create-comment', args=[self.post.id])  # /posts/<uuid>/comments/create/
        data = {'text': 'My new comment'}# Create a comment
        response = self.client.post(url, data, format='json')# Make a POST request to the endpoint
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)# Assert that the response status code is 201
        self.assertEqual(response.data['text'], 'My new comment')# Assert that the response contains the new comment
        self.assertTrue(Comment.objects.filter(text='My new comment').exists())# Assert that the comment was created in the database