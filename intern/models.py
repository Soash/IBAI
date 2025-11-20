from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField
from django.conf import settings

class Intern(models.Model):
    MEDIUM_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    BRANCH_CHOICES = [
        ('dhaka', 'Dhaka'),
        ('chittagong', 'Chittagong'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateField()
    # medium = models.CharField(max_length=10, choices=MEDIUM_CHOICES, default='online')
    summary = models.TextField(max_length=500, help_text="Short summary to display in list view.")
    description = HTMLField()
    video = models.URLField(help_text="YouTube video URL")
    registration_link = models.URLField(blank=True, null=True)
    # branch = models.CharField(max_length=15, choices=BRANCH_CHOICES, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='interns/', blank=True, null=True)
    
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='intern_instructor', blank=True, null=True)
    instructors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='intern_instructors', blank=True)
    
    syllabus = models.URLField(help_text="Link to the syllabus document or page", blank=True, null=True)
    
    current_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True) 
    
    

    class Meta:
        ordering = ['order', '-date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Ensure slug uniqueness
            while Intern.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class InternComment(models.Model):
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE, related_name='intern_comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='intern_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.course.title}"










