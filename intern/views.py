from django.shortcuts import render, get_object_or_404
from .models import Intern

def intern_list(request):
    interns = Intern.objects.filter(is_active=True)
    return render(request, 'intern/intern_list.html', {'interns': interns})

def intern_detail(request, slug):
    intern = get_object_or_404(Intern, slug=slug)
    return render(request, 'intern/intern_detail.html', {'intern': intern})
