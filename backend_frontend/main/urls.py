from django.urls import path
from . import views

urlpatterns = [
    path('', views.campaign_index, name='campaign_index'),
    path('campaign/create/', views.create_campaign, name='create_campaign'),
    path('campaign/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('profile/', views.profile_dashboard, name='profile_dashboard'),
    path('campaign/edit/<int:pk>/', views.edit_campaign, name='edit_campaign'),
]