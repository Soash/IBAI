from django.shortcuts import render, get_object_or_404
from .models import Training

def training_list(request):
    trainings = Training.objects.filter(is_active=True, medium='offline')
    has_branch = trainings.filter(branch__isnull=False).exists()
    return render(request, 'training/training_list.html', {'trainings': trainings, 'has_branch': has_branch})

def online_training_list(request):
    trainings = Training.objects.filter(is_active=True, medium='online')
    return render(request, 'training/training_list.html', {'trainings': trainings})

def training_detail(request, slug):
    training = get_object_or_404(Training, slug=slug)
    return render(request, 'training/training_detail.html', {'training': training})

