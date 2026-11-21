from django.contrib import admin
from .models import ScoreSheet, StudentScore, DevelopmentalSkill, StudentSkillRating

class StudentScoreInline(admin.TabularInline):
    model = StudentScore
    extra = 0
    fields = ('student', 'ca1', 'ca2', 'exam', 'total', 'grade', 'remark', 'subject_position')
    readonly_fields = ('total', 'grade', 'remark', 'subject_position')

@admin.register(ScoreSheet)
class ScoreSheetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'term_session', 'class_arm', 'subject', 'teacher', 'status')
    list_filter = ('status', 'term_session', 'class_arm__school_class__level_group')
    search_fields = ('class_arm__school_class__name', 'subject__name', 'teacher__first_name', 'teacher__last_name')
    inlines = [StudentScoreInline]

@admin.register(DevelopmentalSkill)
class DevelopmentalSkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'level_group', 'order')
    list_filter = ('level_group', 'category')
    search_fields = ('name',)

@admin.register(StudentSkillRating)
class StudentSkillRatingAdmin(admin.ModelAdmin):
    list_display = ('student', 'term_session', 'skill', 'rating')
    list_filter = ('term_session', 'skill__category')
    search_fields = ('student__admission_number',)
