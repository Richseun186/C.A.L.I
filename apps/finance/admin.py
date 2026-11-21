from django.contrib import admin
from .models import ClassFeeStructure, StudentFeeStatus, PaymentTransaction

@admin.register(ClassFeeStructure)
class ClassFeeStructureAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'term_session', 'compulsory_tuition', 'other_levies', 'total_fee')
    list_filter = ('term_session', 'school_class__level_group')

@admin.register(StudentFeeStatus)
class StudentFeeStatusAdmin(admin.ModelAdmin):
    list_display = ('student', 'term_session', 'total_billed', 'total_paid', 'balance', 'has_cleared_fees')
    list_filter = ('term_session', 'has_cleared_fees')
    search_fields = ('student__admission_number', 'student__user__first_name', 'student__user__last_name')
    list_editable = ('has_cleared_fees',)

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'student', 'term_session', 'amount', 'channel', 'is_successful', 'created_at')
    list_filter = ('is_successful', 'channel', 'term_session')
    search_fields = ('reference', 'student__admission_number')
