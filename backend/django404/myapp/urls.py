from django.urls import path
from .views import (
    register_user,
    login_user,
    logout_user,
    user_profile_by_username,
    delete_user_by_username,
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
    list_public_posts_excluding_user,
    list_user_posts_by_username,
    list_user_posts,
    get_relationship,
    create_follow_request,
    get_follower_request_list,
    resolve_follower_request,
    get_followers,
    unfollow_user,
    add_friend,
    friends_posts,
    list_friends,
    list_non_friend_users,
    draft_posts
)

urlpatterns = [
    # ✅ Authentication Endpoints
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('posts/drafts/', draft_posts, name='draft-posts'),

    # ✅ User Profile Endpoints
    path('profile/<str:username>/', user_profile_by_username, name='user-profile-by-username'),
    path('update-profile/', update_user_profile, name='update-profile'),
    
    # User Relationship Endpoints 
    # @author Christine Bao
    path('<str:username>/relationship/', get_relationship, name='get_relationship'), #get relationship between user and logged-in user

    # Following Endpoints 
    # @author Christine Bao
    path('profile/<str:username>/follow_request/', create_follow_request, name='create_follow_request'), #send follow request to user whose profile you are visitng
    path('profile/<str:username>/unfollow/', unfollow_user, name='unfollow_user'), #unfollow user whose profile you are visitng
    path('notifs/follow_requests/', get_follower_request_list, name='get_follower_request_list'), #get follower_request notifs from user whose profile you are on
    path('notifs/follow_requests/resolve/', resolve_follower_request, name='resolve_follower_request'), #get follower_request notifs from user whose profile you are on
    path('followers/<str:username>/', get_followers, name='get_followers'), #get list of followers of user you are on
    
    # User Posts by Username
    path('api/users/<str:username>/posts/', list_user_posts_by_username, name='list-user-posts-by-username'),

    # ✅ Post Endpoints QingqiuTan/Nishchay Ranjan/Riyasat Zaman
    path('posts/', list_posts, name='list-posts'),
    path('posts/create/', create_post, name='create-post'),
    path('posts/<uuid:post_id>/', retrieve_post, name='retrieve-post'),
    path("posts/<uuid:post_id>/edit/", update_post, name="edit-post"),  
    path('posts/<uuid:post_id>/delete/', delete_post, name='delete-post'),  
    path('api/posts/public/', list_public_posts_excluding_user, name='public-posts-excluding-user'),

    # ✅ Comments Endpoints QingqiuTan
    path('posts/<uuid:post_id>/comments/', list_comments, name='list-comments'),
    path('posts/<uuid:post_id>/comments/create/', create_comment, name='create-comment'),

    path('friends/add/<str:username>/', add_friend, name='add_friend'),
    path('friends/posts/', friends_posts, name='friends-posts'),
    path('friends/', list_friends, name='list-friends'),
    path('users/non-friends/', list_non_friend_users, name='list-non-friend-users'),  # ✅ Corrected endpoint

    # ✅ Likes Endpoints QingqiuTan
    path('posts/<uuid:post_id>/likes/', list_likes, name='list-likes'),
    path('posts/<uuid:post_id>/likes/toggle/', toggle_like, name='toggle-like'),
    path('posts/my/', list_user_posts, name='list-user-posts'),
    path('api/posts/public/', list_public_posts_excluding_user, name='public-posts-excluding-user'),

    # ✅ User Management Nishchay Ranjan/Christine Bao
    path('users/exclude-self/', list_users_excluding_self, name='list_users_excluding_self'),
    path('users/exclude-self/<str:username>/update-user/', update_user_profile, name='admin_update_user'), 
    path('users/exclude-self/<str:username>/delete-user/', delete_user_by_username, name='delete_user'),
]
