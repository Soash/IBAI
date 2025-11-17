from django.urls import path
from . import views

urlpatterns = [
    path('intern/', views.intern_list, name='intern_list'),
    path('intern/<slug:slug>/', views.intern_detail, name='intern_detail'),
    path('intern/comment/delete/<int:comment_id>/', views.delete_intern_comment, name='delete_intern_comment'),
]
