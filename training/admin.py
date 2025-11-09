from django.contrib import admin
from .models import Training

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('name', 'medium', 'date', 'is_active', 'order')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('medium', 'is_active', 'date')
