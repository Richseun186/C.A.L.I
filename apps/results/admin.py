from django.contrib import admin
from .models import TermResultSummary

@admin.register(TermResultSummary)
class TermResultSummaryAdmin(admin.ModelAdmin):
    list_display = ('student', 'term_session', 'total_score', 'average', 'class_position', 'out_of', 'promotion_status', 'is_published')
    list_filter = ('term_session', 'promotion_status', 'is_published')
    search_fields = ('student__admission_number', 'student__user__first_name', 'student__user__last_name')
