from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.portal_login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('students/', views.student_directory_view, name='students'),
    path('classes/', views.class_directory_view, name='classes'),
    path('lockout/', views.lockout_view, name='lockout'),
]

