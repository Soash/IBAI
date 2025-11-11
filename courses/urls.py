from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('courses/delete/<int:comment_id>/', views.delete_course_comment, name='delete_course_comment'),
    
    path('courses/<slug:course_slug>/<slug:lesson_slug>/<int:item_order>/', views.course_item, name='course_item'),

    path('certificate/<str:certificate_id>/', views.reportlab_certificate, name='reportlab_certificate'),
    path('verify-certificate/', views.verify_certificate, name='verify_certificate'),
]
