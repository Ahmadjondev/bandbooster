from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('google-auth/', views.google_auth, name='google_auth'),
    path('google-callback/', views.google_callback, name='google_callback'),
    path('ielts-mock/', views.ielts_mock, name='ielts_mock'),
]
