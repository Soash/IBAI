from django.shortcuts import render
from courses.models import Course, Category
from training.models import Training

def home(request):
    courses = Course.objects.all()
    categories = Category.objects.all()
    trainings = Training.objects.filter(is_training=True)
    context = {
        'courses': courses,
        'categories': categories,
        'trainings': trainings
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

