from django.urls import path
from . import views

urlpatterns = [
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-assignments/', views.student_assignments, name='student_assignments'),
    path('student-courses/', views.student_courses, name='student_courses'),
    path('student-enrolled-courses/', views.student_enrolled_courses, name='student_enrolled_courses'),
    path('student-message/', views.student_message, name='student_message'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path('student-quiz/', views.student_quiz, name='student_quiz'),
    path('student-reviews/', views.student_reviews, name='student_reviews'),
    path('student-settings/', views.student_settings, name='student_settings'),
    path('student-wishlist/', views.student_wishlist, name='student_wishlist'),
]

