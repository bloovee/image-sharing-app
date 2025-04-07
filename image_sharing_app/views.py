from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import Image, Comment, UserProfile
from .forms import ImageUploadForm, CommentForm, UserRegisterForm, UserProfileForm

def home(request):
    images = Image.objects.all().order_by('-created_at')
    return render(request, 'image_sharing_app/home.html', {'images': images})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'image_sharing_app/register.html', {'form': form})

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.author = request.user
            image.save()
            messages.success(request, 'Your image has been uploaded!')
            return redirect('image_detail', pk=image.pk)
    else:
        form = ImageUploadForm()
    return render(request, 'image_sharing_app/image_upload.html', {'form': form})

def image_detail(request, pk):
    image = get_object_or_404(Image, pk=pk)
    comments = image.comments.all()
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.parent_image = image
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('image_detail', pk=pk)
    else:
        comment_form = CommentForm()
    return render(request, 'image_sharing_app/image_detail.html', {
        'image': image,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def like_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    if request.user in image.likes.all():
        image.likes.remove(request.user)
        liked = False
    else:
        image.likes.add(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'total_likes': image.total_likes()
    })

def search(request):
    query = request.GET.get('q', '')
    if query:
        images = Image.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(author__username__icontains=query)
        ).order_by('-created_at')
    else:
        images = []
    return render(request, 'image_sharing_app/search.html', {'images': images, 'query': query})

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    images = Image.objects.filter(author=user).order_by('-created_at')
    return render(request, 'image_sharing_app/user_profile.html', {'profile_user': user, 'images': images})

@login_required
def delete_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    if request.user == image.author:
        if request.method == 'POST':
            image.delete()
            messages.success(request, 'Image has been deleted successfully.')
            return redirect('home')
        return render(request, 'image_sharing_app/image_delete.html', {'image': image})
    else:
        messages.error(request, 'You do not have permission to delete this image.')
        return redirect('image_detail', pk=pk)

@login_required
def edit_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    if request.user == image.author:
        if request.method == 'POST':
            form = ImageUploadForm(request.POST, request.FILES, instance=image)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your image has been updated!')
                return redirect('image_detail', pk=pk)
        else:
            form = ImageUploadForm(instance=image)
        return render(request, 'image_sharing_app/image_edit.html', {'form': form, 'image': image})
    else:
        messages.error(request, 'You do not have permission to edit this image.')
        return redirect('image_detail', pk=pk)

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('home')
    return redirect('home')

@login_required
def profile_settings(request):
    print(f"Profile settings view accessed by {request.user.username}")
    print(f"Request method: {request.method}")
    
    if request.method == 'POST':
        print(f"Request POST data keys: {request.POST.keys()}")
        print(f"Request FILES keys: {request.FILES.keys() if request.FILES else 'No files'}")
        
        form = UserProfileForm(request.POST, request.FILES, user=request.user)
        print(f"Form is bound: {form.is_bound}")
        
        if form.is_valid():
            print("Form is valid")
            try:
                # Debug logging for avatar upload
                if 'avatar' in request.FILES:
                    print(f"Avatar upload detected: {request.FILES['avatar']}")
                    print(f"File size: {request.FILES['avatar'].size} bytes")
                    print(f"Content type: {request.FILES['avatar'].content_type}")
                
                profile = form.save()
                
                # Debug logging for saved profile
                if profile.avatar:
                    print(f"Avatar URL after save: {profile.avatar.url}")
                    print(f"Avatar path: {profile.avatar.path}")
                
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile_settings')
            except Exception as e:
                print(f"Error in profile update: {str(e)}")
                import traceback
                print(traceback.format_exc())
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(user=request.user)
    
    return render(request, 'image_sharing_app/profile_settings.html', {'form': form})
