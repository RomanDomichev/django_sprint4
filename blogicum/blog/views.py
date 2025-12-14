# blogicum/blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

POSTS_PER_PAGE = 10

def index(request):
    template_name = 'blog/index.html'

    post_list = Post.objects.select_related('category').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj
    }
    return render(request, template_name, context)

def post_detail(request, post_id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.select_related('category'),
        pub_date__lte=timezone.now(),
        pk=post_id,
        is_published=True,
        category__is_published=True
    )

    comments = post.comments.all()

    form = None
    

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect('blog:post_detail', post_id=post_id)
        else:
            form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, template_name, context)

def category_posts(request, slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=slug,
        is_published=True
    )

    post_list = Post.objects.select_related('category', 'location').filter(
        category=category,
        pub_date__lte=timezone.now(),
        is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    

    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template_name, context)

@login_required
def create_post(request):

    template_name = 'blog/create.html'
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():

            post = form.save(commit=False)
            post.author = request.user

            post.save()

            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()

    context = {'form': form}
    return render(request, template_name, context)

@login_required
def edit_post(request, post_id):
    template_name = 'blog/create.html'

    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)
    
    context = {'form': form}
    return render(request, template_name, context)

@login_required
def add_comment(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    
    return redirect('blog:post_detail', post_id=post_id)

@login_required
def edit_comment(request, post_id, comment_id):

    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    template_name = 'blog/comment.html'
    context = {'form': form, 'comment': comment}
    return render(request, template_name, context)

@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    template_name = 'blog/comment.html'
    context = {'comment': comment}
    return render(request, template_name, context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    form = PostForm(instance=post)
    context = {'form': form}
    return render(request, 'blog/create.html', context)