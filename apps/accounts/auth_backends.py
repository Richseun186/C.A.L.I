from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model

User = get_user_model()

class SchoolAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        username = username.strip()

        # 1. Staff check by email
        if '@' in username:
            try:
                user = User.objects.get(email__iexact=username, is_active=True)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None

        # 2. Student check by Admission Number
        try:
            from apps.academics.models import StudentProfile
            student = StudentProfile.objects.select_related('user').get(
                admission_number__iexact=username,
                user__is_active=True
            )
            # Check user password or student pin
            if student.user.check_password(password) or (student.raw_pin and check_password(password, student.raw_pin)):
                return student.user
        except Exception:
            pass

        # 3. Parent check by Phone Number
        try:
            parent = User.objects.filter(phone=username, role='PARENT', is_active=True).first()
            if parent and parent.check_password(password):
                return parent
        except Exception:
            pass

        # 4. Fallback check by standard username
        try:
            user = User.objects.get(username__iexact=username, is_active=True)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

        return None
