from django.shortcuts import render
from courses.models import Course, Category
from training.models import Training, TrainingComment
from blog.models import ResearchPaper, BlogPost

def home(request):
    courses = Course.objects.all()
    categories = Category.objects.exclude(slug='news')
    trainings = Training.objects.all()
    researches = ResearchPaper.objects.all()[:3]
    blogs = BlogPost.objects.all()
    training_comments = TrainingComment.objects.all()
    context = {
        'courses': courses,
        'categories': categories,
        'trainings': trainings,
        'researches': researches,
        'blogs': blogs,
        'training_comments': training_comments,
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

