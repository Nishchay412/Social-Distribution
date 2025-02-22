from django.urls import path
from .views import (
    register_user,
    login_user,
    logout_user,
    user_profile_by_username,
    update_user_profile,
    create_post,
    list_posts,
    retrieve_post,
    update_post,
    delete_post,
    list_user_posts,
    list_user_posts_by_username,
    list_public_posts_excluding_user,
    list_users_excluding_self,
    list_comments, create_comment,
    list_likes, create_like,
    toggle_like,
)

urlpatterns = [
    # ✅ Authentication Endpoints
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),

    # ✅ User Profile Endpoints
    path('profile/<str:username>/', user_profile_by_username, name='user-profile-by-username'),
    path('update-profile/', update_user_profile, name='update-profile'),

    # ✅ Post Endpoints
    path('posts/', list_posts, name='list-posts'),
    path('posts/create/', create_post, name='create-post'),
    path('posts/<uuid:post_id>/', retrieve_post, name='retrieve-post'),
    path("posts/<uuid:post_id>/edit/", update_post, name="edit-post"),  
    path('posts/<uuid:post_id>/delete/', delete_post, name='delete-post'),  # ✅ Corrected path

    # ✅ Comments Endpoints
    path('posts/<uuid:post_id>/comments/', list_comments, name='list-comments'),
    path('posts/<uuid:post_id>/comments/create/', create_comment, name='create-comment'),

    # ✅ Likes Endpoints
    path('posts/<uuid:post_id>/likes/', list_likes, name='list-likes'),
    path('posts/<uuid:post_id>/likes/create/', create_like, name='create-like'),
    path('posts/<uuid:post_id>/likes/toggle/', toggle_like, name='toggle-like'),


    # ✅ User-specific Post Endpoints
    path('posts/my/', list_user_posts, name='list-user-posts'),  # Posts by logged-in user
    path('posts/user/<str:username>/', list_user_posts_by_username, name='list-user-posts-by-username'),  # Posts by any user
    path('api/posts/public/', list_public_posts_excluding_user, name='list-public-posts-excluding-user'),
    path('users/exclude-self/', list_users_excluding_self, name='list_users_excluding_self'),
]
