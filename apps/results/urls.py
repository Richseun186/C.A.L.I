from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('view/<int:term_session_id>/<int:student_id>/', views.view_or_download_report_card, {'format': 'html'}, name='view-report'),
    path('download/<int:term_session_id>/<int:student_id>/pdf/', views.view_or_download_report_card, {'format': 'pdf'}, name='report-card-pdf'),
]
