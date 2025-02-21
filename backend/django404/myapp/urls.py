from django.urls import path
from .views import (
    register_user, login_user, logout_user,
    user_profile_by_username, update_user_profile,
    create_post, list_posts, retrieve_post, update_post, delete_post
)

urlpatterns = [
    # Authentication Endpoints
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),

    # User Profile Endpoints
    path("profile/<str:username>/", user_profile_by_username, name="profile-by-username"),
    path("profile/update/", update_user_profile, name="update-profile"),

    # Post Management Endpoints
    path("posts/", list_posts, name="list-posts"),
    path("posts/create/", create_post, name="create-post"),
    path("posts/<uuid:post_id>/", retrieve_post, name="retrieve-post"),
    path("posts/<uuid:post_id>/edit/", update_post, name="edit-post"),  #Changed from 'update' to 'edit'
    path("posts/<uuid:post_id>/delete/", delete_post, name="delete-post"),
]
