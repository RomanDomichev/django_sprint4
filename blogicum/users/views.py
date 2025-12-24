# blogicum/users/views.py (добавить импорт Paginator)
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from blog.models import Post
from django.db.models import Count
from .forms import CustomUserChangeForm
from blog.views import annotate_comment_count #


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    #
    post_list = Post.objects.filter(author=profile_user)
    #
    post_list = annotate_comment_count(post_list)

    if request.user != profile_user:
        post_list = post_list.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    paginator = Paginator(post_list.order_by('-pub_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)

def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/registration_form.html', {'form': form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'blog/user.html', {'form': form})