from django.shortcuts import redirect, render, get_object_or_404
from .models import BlogComment, BlogPost
from django.core.paginator import Paginator
from django.contrib import messages

def blog_list(request):
    posts = BlogPost.objects.order_by('-created_at')

    # Pagination: 6 posts per page
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
    }
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    comments = post.comments.all()

    if request.method == 'POST':
        if request.user.is_authenticated:
            content = request.POST.get('content')
            if content:
                BlogComment.objects.create(
                    post=post,
                    user=request.user,
                    content=content
                )
                messages.success(request, "Comment added successfully.")
                return redirect('blog_detail', slug=slug)
        else:
            return redirect('login')

    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'comments': comments
    })
