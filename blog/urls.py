from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]
