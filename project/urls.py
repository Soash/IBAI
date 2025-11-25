from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('nested_admin/', include('nested_admin.urls')),
    path('admin/', admin.site.urls),
    path('', include('core.urls')), 
    path('', include('users.urls')), 
    path('', include('dashboard.urls')),
    path('', include('courses.urls')),
    path('', include('training.urls')),
    path('', include('intern.urls')),
    path('', include('blog.urls')),
    path('payments/', include('payments.urls')),
    path('tinymce/', include('tinymce.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


