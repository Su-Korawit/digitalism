from django.db import models
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    google_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # เพิ่ม related_name เพื่อลดความขัดแย้ง
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True
    )

# Project Model
class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "title")  # ป้องกันชื่อโปรเจกต์ซ้ำในแต่ละผู้ใช้
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return self.title

# Video Model
class Video(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="videos")
    video_id = models.CharField(max_length=20, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)  # เพิ่ม null=True
    description = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["project"]),  # สร้าง Index ให้กับฟิลด์ project
        ]

    def __str__(self):
        return self.title or "Untitled Video"

# Project Progress Model
class ProjectProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="progress")
    progress = models.IntegerField(default=0)  # เก็บค่าความคืบหน้าในหน่วยเปอร์เซ็นต์ (0-100)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "project")
        indexes = [
            models.Index(fields=["user", "project"]),
        ]

    def __str__(self):
        return f"{self.project.title}: {self.progress}%"

# Video Status Model
class VideoStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="statuses")
    watched = models.BooleanField(default=False)  # สถานะดูแล้วหรือยัง
    last_watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "video")
        indexes = [
            models.Index(fields=["user", "video"]),
        ]

    def __str__(self):
        return f"{self.video.title}: {'Watched' if self.watched else 'Not Watched'}"