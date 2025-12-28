from django.contrib import admin
from .models import Training, TrainingComment

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('name', 'medium', 'date', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('medium', 'is_active', 'date')
    filter_horizontal = ('instructors',)



@admin.register(TrainingComment)
class TrainingCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "training", "user", "short_content", "created_at")
    list_filter = ("training", "user", "created_at")
    search_fields = ("content", "user__username", "training__name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    short_content.short_description = "Comment"
    