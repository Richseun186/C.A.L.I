from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from apps.academics.models import (
    TermSession, ClassArm, Subject, StudentProfile, LevelGroup
)

class ResultStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft / In Progress'
    SUBMITTED = 'SUBMITTED', 'Submitted to Class Teacher'
    REVIEWED = 'REVIEWED', 'Reviewed by Exam Officer'
    APPROVED = 'APPROVED', 'Approved & Locked by Principal'
    PUBLISHED = 'PUBLISHED', 'Published to Parents'

class ScoreSheet(models.Model):
    term_session = models.ForeignKey(TermSession, on_delete=models.CASCADE, related_name='score_sheets')
    class_arm = models.ForeignKey(ClassArm, on_delete=models.CASCADE, related_name='score_sheets')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='score_sheets')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='score_sheets')
    status = models.CharField(max_length=20, choices=ResultStatus.choices, default=ResultStatus.DRAFT, db_index=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('term_session', 'class_arm', 'subject')
        ordering = ['class_arm', 'subject']

    def __str__(self):
        return f"{self.class_arm} - {self.subject} ({self.term_session}) [{self.get_status_display()}]"

    @property
    def is_locked(self):
        return self.status in [ResultStatus.APPROVED, ResultStatus.PUBLISHED]

class StudentScore(models.Model):
    score_sheet = models.ForeignKey(ScoreSheet, on_delete=models.CASCADE, related_name='scores')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='subject_scores')
    ca1 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    ca2 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    exam = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, db_index=True)
    grade = models.CharField(max_length=5, blank=True)
    remark = models.CharField(max_length=50, blank=True)
    subject_position = models.PositiveSmallIntegerField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('score_sheet', 'student')
        indexes = [
            models.Index(fields=['score_sheet', 'student']),
            models.Index(fields=['total']),
        ]

    def clean(self):
        if self.score_sheet.status == ResultStatus.APPROVED:
            raise ValidationError("This score sheet is locked and approved. Scores cannot be altered.")

    def save(self, *args, **kwargs):
        self.total = (self.ca1 or 0) + (self.ca2 or 0) + (self.exam or 0)
        super().save(*args, **kwargs)

class SkillCategory(models.TextChoices):
    AFFECTIVE = 'AFFECTIVE', 'Affective Domain (Social / Character)'
    PSYCHOMOTOR = 'PSYCHOMOTOR', 'Psychomotor Domain (Physical / Skills)'
    EARLY_DEVELOPMENT = 'EARLY_DEVELOPMENT', 'Early Years Developmental Milestones'

class DevelopmentalSkill(models.Model):
    level_group = models.ForeignKey(LevelGroup, on_delete=models.CASCADE, related_name='skills')
    category = models.CharField(max_length=30, choices=SkillCategory.choices)
    name = models.CharField(max_length=100) # e.g., Punctuality, Neatness, Pencil Grip, Sharing
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['level_group', 'category', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class StudentSkillRating(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='skill_ratings')
    term_session = models.ForeignKey(TermSession, on_delete=models.CASCADE)
    skill = models.ForeignKey(DevelopmentalSkill, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Needs Support, 2: Fair, 3: Good, 4: Very Good, 5: Excellent"
    )

    class Meta:
        unique_together = ('student', 'term_session', 'skill')

    def __str__(self):
        return f"{self.student.admission_number} - {self.skill.name}: {self.rating}"
