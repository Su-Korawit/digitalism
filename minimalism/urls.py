from django.urls import path
from . import views

urlpatterns = [
    path('', views.sign_in, name='sign_in'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
    path('search/', views.app_search, name='app_search'),
    path("project/", views.create_project, name="create_project"),
    path("project/<int:project_id>/", views.project_detail, name="project_detail"),
    path("projects/", views.project_list, name="project_list"),
]