from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from myapp.models import Post
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class PostAPITestCase(APITestCase):
    def setUp(self):
        """Create a test user and authenticate."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        """Test creating a simple post without an image."""
        url = reverse('create-post')  # e.g. /posts/create/
        data = {
            'title': 'My New Post',
            'content': 'Hello world!',
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], 'My New Post')

    def test_list_posts(self):
        """Test listing multiple posts."""
        Post.objects.create(author=self.user, title='Post1')
        Post.objects.create(author=self.user, title='Post2')

        url = reverse('list-posts')  # e.g. /posts/
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_post(self):
        """Test retrieving a single post by ID."""
        post = Post.objects.create(author=self.user, title='Retrieve Me')
        url = reverse('retrieve-post', args=[post.id])  # e.g. /posts/<uuid:post_id>/
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Retrieve Me')

    def test_edit_post(self):
        """Test editing an existing post."""
        post = Post.objects.create(author=self.user, title='Old Title')
        url = reverse('edit-post', args=[post.id])  # e.g. /posts/<uuid>/edit/
        data = {'title': 'New Title'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')

    def test_delete_post(self):
        """Test deleting a post."""
        post = Post.objects.create(author=self.user, title='To Delete')
        url = reverse('delete-post', args=[post.id])  # e.g. /posts/<uuid>/delete/
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    @staticmethod
    def generate_image_file():
        """Helper function to generate a fake image for testing."""
        image = BytesIO()
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image, 'JPEG')
        image.seek(0)
        return SimpleUploadedFile("test.jpg", image.read(), content_type="image/jpeg")

    def test_create_post_with_image(self):
        """Test creating a post with an image upload."""
        url = reverse('create-post')
        image_file = self.generate_image_file()
        data = {
            'title': 'Post with Image',
            'content': 'This post contains an image',
            'image': image_file
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', response.data)
        self.assertIsNotNone(response.data['image'])

    def test_markdown_rendering(self):
        """Test that Markdown content is properly converted to HTML."""
        post = Post.objects.create(
            author=self.user,
            title='Markdown Test',
            content='**Bold Text**\n\n_Italic Text_\n\n# Heading 1\n\n- Item 1\n- Item 2'
        )
        url = reverse('retrieve-post', args=[post.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_html = (
            "<p><strong>Bold Text</strong></p>\n"
            "<p><em>Italic Text</em></p>\n"
            "<h1>Heading 1</h1>\n"
            "<ul>\n<li>Item 1</li>\n<li>Item 2</li>\n</ul>"
        )

        self.assertIn('content_html', response.data)
        self.assertEqual(response.data['content_html'].strip(), expected_html.strip())

    def test_unauthorized_edit_post(self):
        """Test that an unauthorized user cannot edit someone else's post."""
        other_user = User.objects.create_user(username='otheruser', email='otheruser@example.com', password='testpass')
        post = Post.objects.create(author=other_user, title='Not Yours')

        url = reverse('edit-post', args=[post.id])
        data = {'title': 'Unauthorized Edit'}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_delete_post(self):
        """Test that an unauthorized user cannot delete someone else's post."""
        other_user = User.objects.create_user(username='otheruser', email='otheruser@example.com', password='testpass')
        post = Post.objects.create(author=other_user, title='Not Yours')

        url = reverse('delete-post', args=[post.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
