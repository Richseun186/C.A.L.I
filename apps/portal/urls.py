from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.portal_login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('lockout/', views.lockout_view, name='lockout'),
]
