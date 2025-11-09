from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    keywords = models.CharField(max_length=255, blank=True, null=True, help_text="3 keywords")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    original_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    discount_percentage = models.PositiveIntegerField(default=0, help_text="Enter discount percentage if any", blank=True, null=True)
    
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    intro_video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    course_level = models.CharField(max_length=50, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner')
    language = models.CharField(max_length=50, choices=[('english', 'English'), ('bangla', 'Bangla')], default='bangla')
    certificate_available = models.BooleanField(default=True)
    
    @property
    def total_duration(self):
        # Sum the video_length_min of all video lectures in all lessons of this course
        return sum(
            video.video_length_min or 0
            for lesson in self.lessons.all()
            for video in lesson.video.all()
        )
    
    # calculate total videos
    @property
    def total_videos(self):
        return sum(
            lesson.video.count()
            for lesson in self.lessons.all()
        )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.course.title}"

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.course.title})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    @property
    def items_ordered(self):
        items = list(self.video.all()) + list(self.exam.all())
        return sorted(items, key=lambda x: x.order)
    
class Video(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='video')
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True, null=True)
    video_length_min = models.PositiveIntegerField(blank=True, null=True)
    order = models.PositiveIntegerField()
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    @property
    def item_type(self):
        return 'video'

class Exam(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exam')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()
     
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def item_type(self):
        return 'exam'





class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"

###########################################################################

class CourseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_progress")
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)
    enrolled = models.BooleanField(default=True)
    enrolled_at = models.DateTimeField(auto_now=True)
    certificate_id = models.CharField(max_length=100, unique=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class VideoProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_progress')
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='progress')
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user.username} - {self.video} - {self.status}"

class ExamProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey("Exam", on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'exam')

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"

class ExamAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey("Exam", on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    attempted_at = models.DateTimeField(auto_now_add=True)


    

    
    
    