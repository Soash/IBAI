from django.urls import path
from . import views

urlpatterns = [
    path('training/', views.training_list, name='training_list'),
    path('training/<slug:slug>/', views.training_detail, name='training_detail'),
]
