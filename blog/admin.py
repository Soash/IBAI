from django.contrib import admin, messages
from .models import BlogComment, BlogPost

@admin.action(description="Duplicate selected blog posts")
def duplicate_blog_posts(modeladmin, request, queryset):
    for obj in queryset:
        # Count existing copies
        base_title = obj.title
        existing_copies = BlogPost.objects.filter(title__startswith=f"{base_title} (Copy").count()
        # Create new copy
        obj.pk = None  # reset primary key
        obj.slug = f"{obj.slug}-copy-{existing_copies + 1}"  # ensure slug uniqueness
        obj.title = f"{base_title} (Copy {existing_copies + 1})"
        obj.save()
    messages.success(request, "Selected posts duplicated successfully!")

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'published')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('published', 'created_at', 'author')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    actions = [duplicate_blog_posts]


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at', 'post', 'user')
    search_fields = ('content',)
    date_hierarchy = 'created_at'
