from django.shortcuts import redirect, render, get_object_or_404
from .models import Intern, InternComment
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def intern_list(request):
    interns = Intern.objects.filter(is_active=True).order_by('-order')
    return render(request, 'intern/intern_list.html', {'interns': interns})

def intern_detail(request, slug):
    intern = get_object_or_404(Intern, slug=slug)
    
    comments = intern.intern_comments.all()
    total_comments = comments.count()
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            content = request.POST.get('content')
            if content:
                InternComment.objects.create(
                    intern=intern,
                    user=request.user,
                    content=content
                )
                messages.success(request, "Comment added successfully.")
                return redirect('intern_detail', slug=slug)
        else:
            return redirect('login')
        
    return render(request, 'intern/intern_detail.html', {'intern': intern, 'comments': comments, 'total_comments': total_comments})

@login_required
def delete_intern_comment(request, comment_id):
    comment = get_object_or_404(InternComment, id=comment_id, user=request.user)
    slug = comment.intern.slug
    comment.delete()
    messages.success(request, "Your comment was deleted successfully.")
    return redirect('intern_detail', slug=slug)

