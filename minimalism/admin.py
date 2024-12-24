from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Project, Video, ProjectProgress, VideoStatus

# Register CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'google_id', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'google_id')
    ordering = ('username',)

# Register Project
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# Register Video
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'youtube_url', 'added_at')
    search_fields = ('title', 'youtube_url')
    list_filter = ('added_at',)
    ordering = ('-added_at',)

# Register ProjectProgress
@admin.register(ProjectProgress)
class ProjectProgressAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'progress', 'last_updated')
    list_filter = ('progress', 'last_updated')
    ordering = ('-last_updated',)

# Register VideoStatus
@admin.register(VideoStatus)
class VideoStatusAdmin(admin.ModelAdmin):
    list_display = ('video', 'user', 'watched', 'last_watched_at')
    list_filter = ('watched', 'last_watched_at')
    ordering = ('-last_watched_at',)
