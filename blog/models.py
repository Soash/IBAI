from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from tinymce.models import HTMLField
from courses.models import Category

User = get_user_model()

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = HTMLField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.user} on {self.post}'
    
class Vlog(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    author = models.CharField(blank=True, null=True)
    youtube_url = models.URLField(help_text="Embed YouTube video link (e.g., https://www.youtube.com/embed/abcdef)")
    likes = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

class ResearchPaper(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    publication_date = models.DateField()
    journal = models.CharField(max_length=255)
    abstract = models.TextField()
    link = models.URLField()
    image = models.ImageField(upload_to='research_papers/', blank=True, null=True)

class Thesis(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = HTMLField()
    image = models.ImageField(upload_to='thesis_images/', blank=True, null=True)
    published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title







    