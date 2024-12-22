from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Project, Video, ProjectProgress

# Homepage View
def homepage(request):
    return render(request, 'minimalism/homepage.html')

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('homepage')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Register View
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('homepage')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Search View
def search(request):
    query = request.GET.get('q', '')
    results = Video.objects.filter(title__icontains=query)
    return render(request, 'search.html', {'results': results, 'query': query})

# Watch Video View
def watch_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    progress = None
    if request.user.is_authenticated:
        project = video.project
        progress, created = ProjectProgress.objects.get_or_create(user=request.user, project=project)
        progress.progress += 10  # เพิ่ม progress 10% (ตัวอย่าง)
        progress.save()
    return render(request, 'watch_video.html', {'video': video, 'progress': progress})
