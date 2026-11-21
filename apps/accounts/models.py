import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from simple_history.models import HistoricalRecords

class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, username=None, password=None, **extra_fields):
        if not email and not username:
            raise ValueError("Users must have an email address or username/admission number.")
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)
        if not username:
            username = email.split('@')[0] if email else 'admin'
        return self.create_user(email=email, username=username, password=password, **extra_fields)

class UserRole(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
    PROPRIETOR = 'PROPRIETOR', 'Proprietor / Head of School'
    PRINCIPAL = 'PRINCIPAL', 'Principal (Secondary)'
    HEADMISTRESS = 'HEADMISTRESS', 'Headmistress (Primary/Early Years)'
    EXAM_OFFICER = 'EXAM_OFFICER', 'Exam Officer'
    CLASS_TEACHER = 'CLASS_TEACHER', 'Class Teacher'
    SUBJECT_TEACHER = 'SUBJECT_TEACHER', 'Subject Teacher'
    PARENT = 'PARENT', 'Parent'
    STUDENT = 'STUDENT', 'Student'

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True)
    phone = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.STUDENT, db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        indexes = [
            models.Index(fields=['email', 'role']),
            models.Index(fields=['username', 'role']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
