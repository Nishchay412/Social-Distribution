from django.urls import path
from .views import (
    register_user,
    login_user,
    logout_user,
    toggle_comment_like,
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
    accept_follower_request,
    deny_follow_request,
    cancel_follower_request,
    get_followers,
    get_friends,
    get_followees,
    unfollow_user,
    add_friend,
    friends_posts,
    list_friends,
    list_non_friend_users,
    draft_posts,
    admin_update_user,
    register_admin_user,
    approve_user,
    list_pending_users,
    stream_posts,
    register_user_as_admin,
    get_non_followees,
    friend_post_detail,
    RemoteUsersView,
    HelloView,
    list_all_users,
    RemoteListAllUsersView,
    create_follow_request_inter_node,
    remote_create_follow_request,
    remote_get_follower_requests,
    aggregated_remote_list_all_users,
    accept_follow_request_inter_node
)

urlpatterns = [
    # ✅ Authentication Endpoints
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('posts/drafts/', draft_posts, name='draft-posts'),
    path('posts/stream/', stream_posts, name='stream-posts'),
    path('register-admin/', register_user_as_admin, name='register_user_as_admin'),

    # ✅ User Profile Endpoints
    path('profile/<str:username>/', user_profile_by_username, name='user-profile-by-username'),
    path('update-profile/', update_user_profile, name='update-profile'),
    path('api/admin/pending-users/', list_pending_users, name='list_pending_users'),
    path('api/admin/approve-user/<str:username>/', approve_user, name='approve_user'),
    
    # User Relationship Endpoints (by Christine Bao)
    path('<str:username>/relationship/', get_relationship, name='get_relationship'),  # Get relationship between user and logged-in user

    # Following Endpoints (by Christine Bao)
    path('profile/<str:username>/follow-request/', create_follow_request, name='create_follow_request'),  # Send follow request to user whose profile you are visiting
    path('profile/<str:username>/unfollow/', unfollow_user, name='unfollow_user'),  # Unfollow user whose profile you are visiting
    path('profile/<str:username>/cancel-follow-request/', cancel_follower_request, name='cancel_follewor_request'),  # Cancel follow request
    path('notifs/follow-requests/', get_follower_request_list, name='get_follower_request_list'),  # Get follow request notifications
    path('notifs/follow-requests/<str:username>/accept/', accept_follower_request, name='accept_follower_request'),  # Accept follow request
    path('notifs/follow-requests/<str:username>/deny/', deny_follow_request, name='deny_follow_request'),  # Deny follow request
    path('followers/<str:username>/', get_followers, name='get_followers'),  # Get list of followers for a user
    path('followees/<str:username>/', get_followees, name='get_followees'),  # Get list of users the given user is following
    path('users/friends/', get_friends, name='get_friends'),  # Get list of friends
    path('profile/<str:username>/cancel-follow-request/',cancel_follower_request,name='cancel_follower_request'),
    path('list-all-users/', list_all_users, name='list_all_users'),


    # Admin user update endpoint from main branch
    path('users/exclude-self/<str:username>/update-user/', admin_update_user, name='admin_update_user'),
    path('hello/', HelloView.as_view(), name='hello'),

    # User Posts by Username
    path('api/users/<str:username>/posts/', list_user_posts_by_username, name='list-user-posts-by-username'),
    path('users/non-followees/', get_non_followees, name='get_non_followees'),
    

    # ✅ Post Endpoints (QingqiuTan/Nishchay Ranjan/Riyasat Zaman)
    path('posts/', list_posts, name='list-posts'),
    path('posts/create/', create_post, name='create-post'),
    path('posts/<uuid:post_id>/', retrieve_post, name='retrieve-post'),
    path("posts/<uuid:post_id>/edit/", update_post, name="edit-post"),  
    path('posts/<uuid:post_id>/delete/', delete_post, name='delete-post'),  
    path('api/posts/public/', list_public_posts_excluding_user, name='public-posts-excluding-user'),
    path('api/admin-register/', register_admin_user, name='admin-register'),

    # ✅ Comments Endpoints (QingqiuTan)
    path('posts/<uuid:post_id>/comments/', list_comments, name='list-comments'),
    path('posts/<uuid:post_id>/comments/create/', create_comment, name='create-comment'),
    path('posts/<uuid:post_id>/comments/<uuid:comment_id>/likes/toggle/', toggle_comment_like, name='toggle-comment-like'),

    # ✅ Friend & Non-Friend Endpoints
    path('friends/add/<str:username>/', add_friend, name='add_friend'),
    path('friends/posts/', friends_posts, name='friends-posts'),
    path('friends/', list_friends, name='list-friends'),
    path('friends/posts/<uuid:post_id>/', friend_post_detail, name='friend-post-detail'),
    path('users/non-friends/', list_non_friend_users, name='list-non-friend-users'),

    # ✅ Likes Endpoints (QingqiuTan)
    path('posts/<uuid:post_id>/likes/', list_likes, name='list-likes'),
    path('posts/<uuid:post_id>/likes/toggle/', toggle_like, name='toggle-like'),
    path('posts/my/', list_user_posts, name='list-user-posts'),
    path('api/posts/public/', list_public_posts_excluding_user, name='public-posts-excluding-user'),

    # ✅ User Management Endpoints (Nishchay Ranjan/Christine Bao)
    path('users/exclude-self/', list_users_excluding_self, name='list_users_excluding_self'),
    path('users/exclude-self/<str:username>/update-user/', update_user_profile, name='admin_update_user'), 
    path('users/exclude-self/<str:username>/delete-user/', delete_user_by_username, name='delete_user'),
    path('get-remote-users/', RemoteUsersView.as_view(), name='get_remote_users'),
    path('remote-list-all-users/', RemoteListAllUsersView.as_view(), name='remote_list_all_users'),
    path('aggregated-remote-users/', aggregated_remote_list_all_users, name='aggregated_remote_list_all_users'),
    path('accept-follow-request-inter-node/<str:username>/', accept_follow_request_inter_node, name='accept_follow_request_inter_node'),

    path('aggregated-all-users/', aggregated_list_all_users, name='aggregated_all_users'),


    path('create-follow-request-inter-node/<str:username>/', create_follow_request_inter_node, name='create_follow_request_inter_node'),
    path('create-follow-request/<str:username>/', remote_create_follow_request, name='remote_create_follow_request'),
    path('remote-get-follower-requests/', remote_get_follower_requests, name='remote_get_follower_requests'),
    
    
    
]

