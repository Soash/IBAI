from django.urls import path
from . import views

urlpatterns = [
    path('training/', views.training_list, name='training_list'),
    path('training/online/', views.online_training_list, name='online_training_list'),
    path('training/<slug:slug>/', views.training_detail, name='training_detail'),
    
    path('training/<slug:slug>/add_comment/', views.add_comment_training, name='add_comment_training'),
    path('training/comment/<int:comment_id>/delete/', views.delete_training_comment, name='delete_training_comment'),
]
