from django.urls import path
from .views import register_user  # Make sure this import is correct
from .views import login_user
from .views import logout_user
urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),  # ✅ Add logout URL
]
