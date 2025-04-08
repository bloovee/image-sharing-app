from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='image_sharing_app/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_image, name='upload_image'),
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
    path('image/<int:pk>/like/', views.like_image, name='like_image'),
    path('image/<int:pk>/delete/', views.delete_image, name='delete_image'),
    path('image/<int:pk>/edit/', views.edit_image, name='edit_image'),
    path('search/', views.search, name='search'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('settings/', views.profile_settings, name='profile_settings'),
    path('health/', views.health_check, name='health_check'),
] 