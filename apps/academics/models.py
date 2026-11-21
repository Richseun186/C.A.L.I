from django.db import models
from django.conf import settings

class LevelGroupCategory(models.TextChoices):
    EARLY_YEARS = 'EARLY_YEARS', 'Early Years (Pre-Nursery, Nursery 1-2/3)'
    PRIMARY = 'PRIMARY', 'Primary (Primary 1-6)'
    JSS = 'JSS', 'Junior Secondary (JSS 1-3)'
    SS = 'SS', 'Senior Secondary (SS 1-3)'

class AssessmentMode(models.TextChoices):
    NUMERIC_AND_SKILLS = 'NUMERIC_AND_SKILLS', 'Numeric Scores + Skill Ratings'
    STANDARD_CA_EXAM = 'STANDARD_CA_EXAM', 'Standard CA + Exam'

class LevelGroup(models.Model):
    name = models.CharField(max_length=50) # e.g. Early Years, Primary, JSS, SS
    category = models.CharField(max_length=20, choices=LevelGroupCategory.choices, unique=True)
    assessment_mode = models.CharField(max_length=30, choices=AssessmentMode.choices, default=AssessmentMode.STANDARD_CA_EXAM)
    ca1_max = models.PositiveSmallIntegerField(default=20)
    ca2_max = models.PositiveSmallIntegerField(default=20)
    exam_max = models.PositiveSmallIntegerField(default=60)
    enable_positions = models.BooleanField(default=True) # False for Early Years
    theme_color = models.CharField(max_length=30, default='sky') # sky, emerald, amber, indigo

    def __str__(self):
        return self.name

class AcademicSession(models.Model):
    name = models.CharField(max_length=20, unique=True) # e.g. 2026/2027
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

class AcademicTerm(models.TextChoices):
    FIRST = 'FIRST', 'First Term'
    SECOND = 'SECOND', 'Second Term'
    THIRD = 'THIRD', 'Third Term'

class TermSession(models.Model):
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='terms')
    term = models.CharField(max_length=10, choices=AcademicTerm.choices)
    is_current = models.BooleanField(default=False)
    next_term_resumption = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('session', 'term')
        ordering = ['session', 'term']

    def __str__(self):
        return f"{self.get_term_display()} - {self.session.name}"

class SchoolClass(models.Model):
    level_group = models.ForeignKey(LevelGroup, on_delete=models.PROTECT, related_name='classes')
    name = models.CharField(max_length=50) # e.g. Nursery 1, Primary 4, JSS 2, SS 3
    code = models.CharField(max_length=20, unique=True) # e.g. NUR1, PR4, JS2, SS3
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'School Classes'

    def __str__(self):
        return self.name

class ClassArm(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='arms')
    arm_name = models.CharField(max_length=20) # e.g. Gold, Diamond, Emerald, A, B
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_arms', limit_choices_to={'role__in': ['CLASS_TEACHER', 'HEADMISTRESS', 'PRINCIPAL']}
    )

    class Meta:
        unique_together = ('school_class', 'arm_name')
        ordering = ['school_class__order', 'arm_name']

    def __str__(self):
        return f"{self.school_class.name} {self.arm_name}"

class Department(models.TextChoices):
    NONE = 'NONE', 'None (General)'
    SCIENCE = 'SCIENCE', 'Science'
    ARTS = 'ARTS', 'Arts / Humanities'
    COMMERCIAL = 'COMMERCIAL', 'Commercial / Business'

class MasterSubjectBank(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, unique=True)
    level_category = models.CharField(max_length=20, choices=LevelGroupCategory.choices)
    department = models.CharField(max_length=20, choices=Department.choices, default=Department.NONE)
    is_trade_subject = models.BooleanField(default=False, help_text="WAEC Trade/Entrepreneurship subject")
    is_core = models.BooleanField(default=True, help_text="Compulsory Nigerian curriculum subject")
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['level_category', 'department', 'name']
        unique_together = ('level_category', 'name')
        verbose_name = 'Nigerian Subject Bank'
        verbose_name_plural = 'Nigerian Subject Bank'

    def __str__(self):
        dept_str = f" ({self.get_department_display()})" if self.department != Department.NONE else ""
        return f"{self.name}{dept_str} - {self.get_level_category_display()}"

class Subject(models.Model):
    level_group = models.ForeignKey(LevelGroup, on_delete=models.PROTECT, related_name='subjects')
    master_subject = models.ForeignKey(MasterSubjectBank, on_delete=models.SET_NULL, null=True, blank=True, related_name='school_subjects')
    name = models.CharField(max_length=100) # e.g., Number Work, Mathematics
    code = models.CharField(max_length=30)
    department = models.CharField(max_length=20, choices=Department.choices, default=Department.NONE)
    is_elective = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text="Offered in CALI Schools")

    class Meta:
        unique_together = ('level_group', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.level_group.name})"

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=30, unique=True, db_index=True)
    raw_pin = models.CharField(max_length=128, blank=True) # Optional hashed 6-digit access PIN
    current_arm = models.ForeignKey(ClassArm, on_delete=models.PROTECT, related_name='students')
    department = models.CharField(max_length=20, choices=Department.choices, default=Department.NONE)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    date_of_birth = models.DateField(null=True, blank=True)
    passport_photo = models.ImageField(upload_to='passports/', null=True, blank=True)

    class Meta:
        ordering = ['admission_number']

    def __str__(self):
        return f"{self.admission_number} - {self.user.get_full_name()}"

class ParentStudentLink(models.Model):
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wards')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='parents')
    relationship = models.CharField(max_length=30, default='Parent')

    class Meta:
        unique_together = ('parent', 'student')

    def __str__(self):
        return f"{self.parent.get_full_name()} -> {self.student.admission_number}"
