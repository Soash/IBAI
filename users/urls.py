# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('accounts/login/', views.user_login, name='user_login'),
    path('register/', views.user_registration, name='user_registration'),
    path('logout/', views.user_logout, name='user_logout'),
    path('password_reset/', views.password_reset, name='password_reset'),
]

