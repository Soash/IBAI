from django.contrib import admin
from .models import Intern, InternComment

@admin.register(Intern)
class InternAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'is_active', 'order')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active', 'date')
    filter_horizontal = ('instructors',)

@admin.register(InternComment)
class InternCommentAdmin(admin.ModelAdmin):
    list_display = ('intern', 'user', 'created_at')
    search_fields = ('intern__name', 'user__username', 'content')
    list_filter = ('created_at',)
    
    