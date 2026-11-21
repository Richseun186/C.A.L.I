from django.db import models
from simple_history.models import HistoricalRecords
from apps.academics.models import TermSession, StudentProfile, SchoolClass

class ClassFeeStructure(models.Model):
    term_session = models.ForeignKey(TermSession, on_delete=models.CASCADE, related_name='fee_structures')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='fee_structures')
    compulsory_tuition = models.DecimalField(max_digits=10, decimal_places=2)
    other_levies = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('term_session', 'school_class')

    @property
    def total_fee(self):
        return self.compulsory_tuition + self.other_levies

    def __str__(self):
        return f"{self.school_class.name} Fee ({self.term_session}): NGN {self.total_fee:,.2f}"

class StudentFeeStatus(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='fee_records')
    term_session = models.ForeignKey(TermSession, on_delete=models.CASCADE, related_name='student_fees')
    total_billed = models.DecimalField(max_digits=10, decimal_places=2)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    has_cleared_fees = models.BooleanField(default=False, db_index=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('student', 'term_session')

    def save(self, *args, **kwargs):
        self.balance = self.total_billed - self.total_paid
        self.has_cleared_fees = (self.balance <= 0)
        super().save(*args, **kwargs)

    def __str__(self):
        status = "CLEARED" if self.has_cleared_fees else f"OWING NGN {self.balance:,.2f}"
        return f"{self.student.admission_number} - {self.term_session}: {status}"

class PaymentTransaction(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='payments')
    term_session = models.ForeignKey(TermSession, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    channel = models.CharField(max_length=30, default='PAYSTACK') # PAYSTACK, FLUTTERWAVE, BANK_TRANSFER, CASH
    is_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - NGN {self.amount:,.2f} ({'SUCCESS' if self.is_successful else 'PENDING'})"
