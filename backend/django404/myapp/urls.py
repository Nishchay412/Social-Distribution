from django.urls import path
from .views import register_user  # Make sure this import is correct
from .views import login_user
from .views import logout_user
from .views import user_profile_by_username
from .views import update_user_profile
urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/<str:username>/', user_profile_by_username, name='user_profile_by_username'),  # ✅ Add logout URL
    path('update-profile/', update_user_profile, name='update-profile'),
]
