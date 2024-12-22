from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('search/', views.search, name='search'),
    path('watch/', views.watch_video, name='watch'),
]
