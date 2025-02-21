from django.urls import path
from .views import register_user  # Make sure this import is correct
from .views import login_user
from .views import logout_user
from .views import user_profile_by_username
from .views import update_user_profile
from .views import (
    create_post,
    list_posts,
    retrieve_post,
    update_post,
    delete_post,
    list_user_posts,
    list_user_posts_by_username
)
urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/<str:username>/', user_profile_by_username, name='user_profile_by_username'),  # ✅ Add logout URL
    path('update-profile/', update_user_profile, name='update-profile'),
      path('posts/', list_posts, name='list-posts'),
    path('posts/create/', create_post, name='create-post'),
    path('posts/<uuid:post_id>/', retrieve_post, name='retrieve-post'),
    path('posts/<uuid:post_id>/update/', update_post, name='update-post'),
    path('posts/<uuid:post_id>/delete/', delete_post, name='delete-post'),
    path('posts/my/', list_user_posts, name='list-user-posts'),
    path('api/posts/user/<str:username>/', list_user_posts_by_username, name='list-user-posts-by-username'),
]
