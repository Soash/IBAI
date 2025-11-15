from django.shortcuts import render, get_object_or_404
from .models import Training, TrainingComment
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

def training_list(request):
    trainings = Training.objects.filter(is_active=True, medium='offline')
    has_branch = trainings.filter(branch__isnull=False).exists()
    return render(request, 'training/training_list.html', {'trainings': trainings, 'has_branch': has_branch})

def online_training_list(request):
    trainings = Training.objects.filter(is_active=True, medium='online')
    return render(request, 'training/training_list.html', {'trainings': trainings})

def training_detail(request, slug):
    training = get_object_or_404(Training, slug=slug)
    total_comments = TrainingComment.objects.filter(training=training).count()
    comments = TrainingComment.objects.filter(training=training).order_by('-created_at')
    return render(request, 'training/training_detail.html', {'training': training, 'total_comments': total_comments, 'comments': comments})


@login_required
def add_comment_training(request, slug):
    """
    Handles posting a comment for a course.
    """
    training = get_object_or_404(Training, slug=slug)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            TrainingComment.objects.create(training=training, user=request.user, content=content)
            messages.success(request, "Your comment has been posted.")
        else:
            messages.warning(request, "Comment cannot be empty.")
    else:
        messages.warning(request, "Invalid request method.")

    return redirect('training_detail', slug=slug)


@login_required
def delete_training_comment(request, comment_id):
    comment = get_object_or_404(TrainingComment, id=comment_id, user=request.user)
    training_slug = comment.training.slug
    comment.delete()
    messages.success(request, "Your comment was deleted successfully.")
    return redirect('training_detail', slug=training_slug)


