from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('subject-bank/', views.subject_bank_manager, name='subject-bank'),
    path('subject-bank/toggle/<int:master_id>/', views.toggle_subject_offering, name='toggle-subject'),
    path('subject-bank/bulk-core/<str:level_cat>/', views.bulk_activate_core, name='bulk-core'),
]
