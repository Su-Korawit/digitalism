from dotenv import load_dotenv
import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
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
