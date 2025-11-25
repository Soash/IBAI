from django.urls import path
from . import views

urlpatterns = [
    path('blogs/', views.blog_list, name='blog_list'),
    path('vlogs/', views.vlog_list, name='vlog_list'),
    path('research-papers/', views.research_papers, name='research_papers'),
    path('thesis-support/', views.thesis_list, name='thesis_list'),
    
    path('vlogs/like/<int:vlog_id>/', views.toggle_like, name='toggle_like'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('thesis/<slug:slug>/', views.thesis_details, name='thesis_details'),
      
]
