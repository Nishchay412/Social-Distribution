from django.urls import path
from .views import (
    register_user,
    login_user,
    logout_user)  # Make sure this import is correct
from .views import (
    create_post,
    list_posts,
    retrieve_post,
    update_post,
    delete_post
)
urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),  # ✅ Add logout URL
    path('posts/', list_posts, name='list-posts'),
    path('posts/create/', create_post, name='create-post'),
    path('posts/<uuid:post_id>/', retrieve_post, name='retrieve-post'),
    path('posts/<uuid:post_id>/update/', update_post, name='update-post'),
    path('posts/<uuid:post_id>/delete/', delete_post, name='delete-post'),
]
