from dotenv import load_dotenv
import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from googleapiclient.discovery import build
import json
from django.contrib.auth.decorators import login_required
from .models import Project, Video
from django.shortcuts import render, get_object_or_404

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# SIGN IN

# ดึง Custom User Model
User = get_user_model()

@csrf_exempt
def sign_in(request):
    """
    Render หน้า sign_in.html พร้อมส่ง Google Client ID
    """
    print(GOOGLE_CLIENT_ID)
    return render(request, 'minimalism/sign_in.html', {
        'google_client_id': GOOGLE_CLIENT_ID,
    })


@csrf_exempt
def auth_receiver(request):
    """
    รับ Token จาก Google และล็อกอินผู้ใช้เข้าสู่ระบบ
    """
    token = request.POST.get('credential')  # รับ Token จาก Google

    if not token:
        return HttpResponse(status=400, content="Missing Google token")

    try:
        # Verify token กับ Google
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        return HttpResponse(status=403, content="Invalid token")

    # ดึงข้อมูลผู้ใช้จาก Google
    google_id = user_data.get('sub')
    email = user_data.get('email')
    first_name = user_data.get('given_name', '')
    last_name = user_data.get('family_name', '')

    if not google_id or not email:
        return HttpResponse(status=400, content="Invalid Google data")

    # ค้นหาหรือสร้างผู้ใช้ในฐานข้อมูล
    user, created = User.objects.get_or_create(
        google_id=google_id,
        defaults={
            'email': email,
            'username': email,  # ใช้อีเมลเป็น username
            'first_name': first_name,
            'last_name': last_name,
        }
    )

    if created:
        print("New user created")

    # ล็อกอินผู้ใช้
    login(request, user)

    # รีไดเรกต์ไปหน้าแรก
    return redirect('sign_in')


def sign_out(request):
    """
    ลบ session ผู้ใช้และออกจากระบบ
    """
    logout(request)
    return redirect('sign_in')

# END SIGN IN

# APP_SEARCH

# ฟังก์ชันสำหรับค้นหาวิดีโอ
def search_videos(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=7
    )
    response = request.execute()
    return response['items']

# ฟังก์ชันสำหรับค้นหา Playlist
def search_playlists(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="playlist",
        maxResults=2
    )
    response = request.execute()
    return response['items']

# ฟังก์ชันสำหรับดึงข้อมูลวิดีโอใน Playlist
def get_videos_in_playlist(playlist_id):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    videos = []

    try:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=1000  # ดึงวิดีโอสูงสุด 50 รายการ
        )
        response = request.execute()

        for item in response.get('items', []):
            video_id = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            thumbnail = item['snippet']['thumbnails']['medium']['url']
            videos.append({
                "videoId": video_id,
                "title": title,
                "thumbnail": thumbnail
            })

    except Exception as e:
        print(f"Error fetching videos in playlist: {e}")

    return videos

# ฟังก์ชันหลักสำหรับแสดงผล
def app_search(request):
    query = request.GET.get('q', '')  # รับคำค้นหาจาก URL
    videos = []
    playlists = []

    if query:
        # ค้นหาวิดีโอและ Playlist
        videos = search_videos(query)
        playlists = search_playlists(query)

        # ดึงข้อมูลวิดีโอในแต่ละ Playlist
        for playlist in playlists:
            playlist_id = playlist['id']['playlistId']
            playlist_videos = get_videos_in_playlist(playlist_id)
            playlist['videos'] = playlist_videos  # เพิ่มข้อมูลวิดีโอเข้าไปในแต่ละ Playlist

    # ส่งข้อมูลไปยัง Template
    return render(request, 'minimalism/app_search.html', {
        'videos': videos,
        'playlists': playlists,
        'query': query,
        'google_client_id': GOOGLE_CLIENT_ID
    })


@login_required
def create_project(request):
    if request.method == "GET":
        project_name = request.GET.get("project_name")
        project_description = request.GET.get("project_description", "")
        project_videos_json = request.GET.get("project_videos_json")

        # Validate project name
        if not project_name:
            return render(request, "minimalism/app_project.html", {"error_message": "Project name is required."})

        # Create or update project
        project, created = Project.objects.get_or_create(
            user=request.user,
            title=project_name,
            defaults={"description": project_description},
        )

        # Add videos to project
        if project_videos_json:
            videos_data = json.loads(project_videos_json)
            for video_data in videos_data:
                Video.objects.create(
                    project=project,
                    video_id=video_data["videoId"],
                    title=video_data["title"],
                )

        return redirect("project_detail", project_id=project.id)

    return render(request, "minimalism/app_project.html")

# END SEARCH

# PROJECT

@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, "minimalism/app_project.html", {"projects": projects})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    videos = project.videos.all()
    return render(request, "minimalism/app_project.html", {"project": project, "videos": videos})