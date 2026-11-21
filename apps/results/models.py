from django.db import models
from simple_history.models import HistoricalRecords
from apps.academics.models import TermSession, StudentProfile

class PromotionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Decision'
    PROMOTED = 'PROMOTED', 'Promoted to Next Class'
    PROMOTED_ON_TRIAL = 'PROMOTED_ON_TRIAL', 'Promoted on Trial'
    REPEAT = 'REPEAT', 'To Repeat Class'
    GRADUATED = 'GRADUATED', 'Graduated'

class TermResultSummary(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='term_summaries')
    term_session = models.ForeignKey(TermSession, on_delete=models.CASCADE, related_name='term_summaries')
    total_score = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    average = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    class_position = models.PositiveSmallIntegerField(null=True, blank=True)
    out_of = models.PositiveSmallIntegerField(null=True, blank=True)
    times_school_opened = models.PositiveSmallIntegerField(default=110)
    times_present = models.PositiveSmallIntegerField(default=110)
    class_teacher_remark = models.TextField(blank=True)
    head_teacher_remark = models.TextField(blank=True)
    promotion_status = models.CharField(
        max_length=30, choices=PromotionStatus.choices, default=PromotionStatus.PENDING
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('student', 'term_session')
        ordering = ['student', 'term_session']

    def __str__(self):
        return f"{self.student.admission_number} - {self.term_session} (Avg: {self.average})"

    @property
    def attendance_percentage(self):
        if self.times_school_opened > 0:
            return round((self.times_present / self.times_school_opened) * 100, 1)
        return 0.0
