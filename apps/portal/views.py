from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.academics.models import TermSession, StudentProfile
from apps.results.models import TermResultSummary

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')
    current_term = TermSession.objects.filter(is_current=True).first()
    return render(request, 'portal/landing.html', {'current_term': current_term})

def portal_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('portal:dashboard')
        else:
            messages.error(request, "Invalid Admission Number, Phone/Email, or Access PIN. Please verify and try again.")
            return redirect('portal:landing')
    return redirect('portal:landing')

@login_required
def dashboard_view(request):
    user = request.user
    current_term = TermSession.objects.filter(is_current=True).first()

    # Route based on role
    if user.role == 'PARENT':
        # Get all wards linked to this parent
        wards = StudentProfile.objects.filter(parents__parent=user).select_related(
            'user', 'current_arm__school_class__level_group'
        )
        return render(request, 'portal/parent_dashboard.html', {
            'wards': wards,
            'current_term': current_term
        })
    elif user.role == 'STUDENT':
        try:
            student = user.student_profile
            return redirect('results:view-report', term_session_id=current_term.id, student_id=student.id)
        except Exception:
            messages.error(request, "Student profile record not found.")
            return redirect('portal:landing')
    elif user.role in ['CLASS_TEACHER', 'SUBJECT_TEACHER', 'HEADMISTRESS', 'PRINCIPAL', 'EXAM_OFFICER', 'SUPER_ADMIN', 'PROPRIETOR']:
        from apps.assessments.models import ScoreSheet
        from apps.academics.models import StudentProfile, SchoolClass
        
        is_admin_user = user.role in ['SUPER_ADMIN', 'PROPRIETOR', 'PRINCIPAL', 'HEADMISTRESS', 'EXAM_OFFICER'] or user.is_staff
        all_sheets = ScoreSheet.objects.all().select_related('subject', 'class_arm__school_class__level_group', 'teacher') if is_admin_user else None
        student_count = StudentProfile.objects.count() if is_admin_user else 0
        class_count = SchoolClass.objects.count() if is_admin_user else 0

        return render(request, 'portal/staff_dashboard.html', {
            'current_term': current_term,
            'is_admin_user': is_admin_user,
            'all_sheets': all_sheets,
            'student_count': student_count,
            'class_count': class_count
        })

    return redirect('portal:landing')

def lockout_view(request, credentials=None):
    return render(request, 'portal/lockout.html', status=429)
