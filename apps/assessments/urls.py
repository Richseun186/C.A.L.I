from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('sheet/<int:sheet_id>/', views.score_sheet_detail, name='sheet-detail'),
    path('score/update/<int:score_id>/', views.update_score_cell, name='update-score-cell'),
    path('sheet/<int:sheet_id>/transition/<str:new_status>/', views.transition_sheet_status, name='transition-sheet'),
]
