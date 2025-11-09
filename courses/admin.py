from django.contrib import admin
from .models import Course, Category, ExamAttempt
from django.contrib import admin
from .models import Course, Lesson, Video, Exam, Comment
from .models import Exam, Question, Option, ExamProgress, VideoProgress, CourseProgress
import nested_admin

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = ('title', 'video_url', 'order', 'video_length_min')
    ordering = ('order',)

class ExamInline(admin.TabularInline):
    model = Exam
    extra = 1
    fields = ('title', 'order')
    ordering = ('order',)

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'order')
    ordering = ('order',)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('category', 'published')
    search_fields = ('title', 'description', 'instructor__username')
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('course',)
    ordering = ('course', 'order')
    search_fields = ('title', 'course__title')
    inlines = [VideoInline, ExamInline]

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'order')
    list_filter = ('lesson',)
    ordering = ('lesson', 'order')
    search_fields = ('title', 'lesson__title')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'course__title', 'content')
    
class OptionInline(nested_admin.NestedTabularInline):
    model = Option
    extra = 2
    min_num = 2
    max_num = 6
    fields = ('text', 'is_correct')

class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    extra = 1
    inlines = [OptionInline]
    fields = ('text', 'order')

@admin.register(Exam)
class ExamAdmin(nested_admin.NestedModelAdmin):
    list_display = ('title', 'lesson', 'order')
    list_filter = ('lesson',)
    search_fields = ('title', 'lesson__title')
    inlines = [QuestionInline]











# @admin.register(ExamProgress)
class ExamProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam__title', 'score', 'status',)
    list_filter = ('exam',)
    search_fields = ('user__username', 'exam__title')

# @admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam__title', 'score', 'attempted_at')
    list_filter = ('exam', 'attempted_at')
    search_fields = ('user__username', 'exam__title')

# @admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'video__title', 'status',)
    list_filter = ('status',)
    search_fields = ('user__username', 'video__title')
    
@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed','enrolled_at', 'completed_at')
    # list_filter = ('completed', 'updated_at')
    # search_fields = ('user__username', 'course__title')
    # readonly_fields = ('updated_at',)
    


    