from django.shortcuts import render
from courses.models import Course, Category

def home(request):
    courses = Course.objects.all()
    categories = Category.objects.all()
    context = {
        'courses': courses,
        'categories': categories
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

