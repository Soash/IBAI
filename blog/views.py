from django.shortcuts import redirect, render, get_object_or_404
from .models import BlogComment, BlogPost
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
    
    viewed_posts = request.session.get('viewed_posts', [])
    if post.id not in viewed_posts:
        post.view_count += 1
        post.save(update_fields=['view_count'])
        viewed_posts.append(post.id)
        request.session['viewed_posts'] = viewed_posts
        
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


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(BlogComment, id=comment_id, user=request.user)
    post_slug = comment.post.slug
    comment.delete()
    messages.success(request, "Your comment was deleted successfully.")
    return redirect('blog_detail', slug=post_slug)
