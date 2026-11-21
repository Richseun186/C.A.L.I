from django.contrib import admin
from .models import (
    LevelGroup, AcademicSession, TermSession,
    SchoolClass, ClassArm, Subject, StudentProfile, ParentStudentLink,
    MasterSubjectBank
)

@admin.register(MasterSubjectBank)
class MasterSubjectBankAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'level_category', 'department', 'is_core', 'is_trade_subject')
    list_filter = ('level_category', 'department', 'is_core', 'is_trade_subject')
    search_fields = ('name', 'code')

class TermSessionInline(admin.TabularInline):
    model = TermSession
    extra = 3

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_editable = ('is_active',)
    inlines = [TermSessionInline]

@admin.register(LevelGroup)
class LevelGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'assessment_mode', 'ca1_max', 'ca2_max', 'exam_max', 'enable_positions')

class ClassArmInline(admin.TabularInline):
    model = ClassArm
    extra = 2

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'level_group', 'order')
    list_filter = ('level_group',)
    inlines = [ClassArmInline]

@admin.register(ClassArm)
class ClassArmAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'school_class', 'arm_name', 'class_teacher')
    list_filter = ('school_class__level_group', 'school_class')
    search_fields = ('school_class__name', 'arm_name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'level_group', 'department', 'is_elective')
    list_filter = ('level_group', 'department', 'is_elective')
    search_fields = ('name', 'code')

class ParentLinkInline(admin.TabularInline):
    model = ParentStudentLink
    extra = 1

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'get_name', 'current_arm', 'department', 'gender')
    list_filter = ('current_arm__school_class__level_group', 'current_arm__school_class', 'department', 'gender')
    search_fields = ('admission_number', 'user__first_name', 'user__last_name')
    inlines = [ParentLinkInline]

    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Pupil Name'
