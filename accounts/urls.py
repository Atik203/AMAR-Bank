
from django.urls import path

from .views import (UserLoginView, UserPasswordChangeView,
                    UserProfileUpdateView, UserRegistrationView, user_logout)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', UserProfileUpdateView.as_view(), name='profile'),
    path('change-password/', UserPasswordChangeView.as_view(), name='change_password'),
]
