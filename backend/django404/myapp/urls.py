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
    list_users_excluding_self,
    list_comments, 
    create_comment,
    list_likes, 
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
    path('posts/<uuid:post_id>/delete/', delete_post, name='delete-post'),  

    # ✅ Comments Endpoints
    path('posts/<uuid:post_id>/comments/', list_comments, name='list-comments'),
    path('posts/<uuid:post_id>/comments/create/', create_comment, name='create-comment'),

    # ✅ Likes Endpoints
    path('posts/<uuid:post_id>/likes/', list_likes, name='list-likes'),
    path('posts/<uuid:post_id>/likes/toggle/', toggle_like, name='toggle-like'),

    # ✅ User Management
    path('users/exclude-self/', list_users_excluding_self, name='list_users_excluding_self'),
]
