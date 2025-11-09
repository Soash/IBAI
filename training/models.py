from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField

class Training(models.Model):
    MEDIUM_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateField()
    medium = models.CharField(max_length=10, choices=MEDIUM_CHOICES, default='online')
    summary = models.TextField(max_length=500, help_text="Short summary to display in list view.")
    description = HTMLField()
    video = models.URLField(help_text="YouTube video URL")
    registration_link = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='trainings/', blank=True, null=True)

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
            while Training.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def video_embed_url(self):
        """Convert normal YouTube links to embeddable ones."""
        if "watch?v=" in self.video:
            return self.video.replace("watch?v=", "embed/")
        elif "youtu.be/" in self.video:
            return self.video.replace("youtu.be/", "www.youtube.com/embed/")
        return self.video
