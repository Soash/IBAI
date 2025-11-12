from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('vlogs/', views.vlog_list, name='vlog_list'),
    path('vlogs/like/<int:vlog_id>/', views.toggle_like, name='toggle_like'),

    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]
