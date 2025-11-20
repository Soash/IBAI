from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

def get_session_choices():
    current_year = datetime.now().year
    return [(f"{y}-{y+1}", f"{y}-{y+1}") for y in range(current_year + 1, 2009, -1)]

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    facebook_link = models.URLField(max_length=200, blank=True, null=True)
    linkedin_link = models.URLField(max_length=200, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)

    # New Fields
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('professional', 'Professional'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=True, null=True)

    DESIGNATION_CHOICES = [
        ('Professor', 'Professor'),
        ('Associate_Professor', 'Associate Professor'),
        ('Assistant_Professor', 'Assistant Professor'),
        ('Lecturer', 'Lecturer'),
        ('PhD_Student', 'PhD student'),
        ('MSc_Student', 'MSc Student'),
        ('BSc_Student', 'BSc Student'),
        ('Other', 'Other'),
    ]
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES, blank=True, null=True)

    university_name = models.CharField(max_length=255, blank=True, null=True)

    session = models.CharField(max_length=9, choices=get_session_choices(), blank=True, null=True)

    def __str__(self):
        return self.username


