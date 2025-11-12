from django.shortcuts import redirect, render, get_object_or_404
from .models import BlogComment, BlogPost, Vlog
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def blog_list(request):
    search_query = request.GET.get('q', '')
    posts = BlogPost.objects.order_by('-created_at')

    # Filter by search query
    if search_query:
        posts = posts.filter(title__icontains=search_query)

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


def vlog_list(request):
    search_query = request.GET.get('q', '')
    vlogs = Vlog.objects.all().order_by('-id')

    # Filter by search query
    if search_query:
        vlogs = vlogs.filter(title__icontains=search_query)

    # Pagination (90 per page)
    paginator = Paginator(vlogs, 90)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/vlog.html', {
        'vlogs': page_obj,          # paginated vlogs
        'page_obj': page_obj,
        'search_query': search_query,
    })

def toggle_like(request, vlog_id):
    vlog = Vlog.objects.get(pk=vlog_id)

    # use session to track liked state
    liked_vlogs = request.session.get('liked_vlogs', [])
    if vlog_id in liked_vlogs:
        vlog.likes = max(0, vlog.likes - 1)
        liked_vlogs.remove(vlog_id)
        liked = False
    else:
        vlog.likes += 1
        liked_vlogs.append(vlog_id)
        liked = True

    vlog.save()
    request.session['liked_vlogs'] = liked_vlogs

    return JsonResponse({'liked': liked, 'likes': vlog.likes})

