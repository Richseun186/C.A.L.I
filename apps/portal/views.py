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
        from apps.finance.models import StudentFeeStatus
        
        is_admin_user = user.role in ['SUPER_ADMIN', 'PROPRIETOR', 'PRINCIPAL', 'HEADMISTRESS', 'EXAM_OFFICER'] or user.is_staff
        all_sheets = ScoreSheet.objects.all().select_related('subject', 'class_arm__school_class__level_group', 'teacher') if is_admin_user else None
        student_count = StudentProfile.objects.count() if is_admin_user else 0
        class_count = SchoolClass.objects.count() if is_admin_user else 0

        # Roster preview for Admin Console
        recent_students = []
        if is_admin_user:
            qs = StudentProfile.objects.select_related(
                'user', 'current_arm__school_class__level_group'
            ).prefetch_related('parents__parent').order_by('current_arm__school_class__name', 'user__first_name')
            fee_map = {}
            if current_term:
                for fs in StudentFeeStatus.objects.filter(term_session=current_term):
                    fee_map[fs.student_id] = fs
            for s in qs:
                s.fee_status_record = fee_map.get(s.id)
                recent_students.append(s)

        return render(request, 'portal/staff_dashboard.html', {
            'current_term': current_term,
            'is_admin_user': is_admin_user,
            'all_sheets': all_sheets,
            'student_count': student_count,
            'class_count': class_count,
            'recent_students': recent_students,
        })

    return redirect('portal:landing')


@login_required
def student_directory_view(request):
    """
    Comprehensive School Student & Pupil Directory for Administrators and Teachers.
    Allows searching, filtering by class arm, inspecting fee status, and viewing terminal reports.
    """
    user = request.user
    is_staff_or_teacher = (
        user.is_staff or 
        user.role in ['SUPER_ADMIN', 'PROPRIETOR', 'PRINCIPAL', 'HEADMISTRESS', 'EXAM_OFFICER', 'CLASS_TEACHER', 'SUBJECT_TEACHER']
    )
    if not is_staff_or_teacher:
        messages.error(request, "Access restricted to school staff and administrators.")
        return redirect('portal:dashboard')

    current_term = TermSession.objects.filter(is_current=True).first()
    from apps.academics.models import StudentProfile, ClassArm
    from apps.finance.models import StudentFeeStatus
    from django.db.models import Q

    students_qs = StudentProfile.objects.select_related(
        'user', 'current_arm__school_class__level_group'
    ).prefetch_related('parents__parent').order_by('current_arm__school_class__name', 'admission_number')

    # Filter by class arm
    arm_filter = request.GET.get('arm', '').strip()
    if arm_filter and arm_filter.isdigit():
        students_qs = students_qs.filter(current_arm_id=int(arm_filter))

    # Search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        students_qs = students_qs.filter(
            Q(admission_number__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__phone_number__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    # Pre-fetch fee statuses
    fee_map = {}
    if current_term:
        for fs in StudentFeeStatus.objects.filter(term_session=current_term):
            fee_map[fs.student_id] = fs

    student_list = []
    cleared_count = 0
    pending_count = 0
    for s in students_qs:
        s.fee_status_record = fee_map.get(s.id)
        if s.fee_status_record and s.fee_status_record.has_cleared_fees:
            cleared_count += 1
        else:
            pending_count += 1
        student_list.append(s)

    all_arms = ClassArm.objects.select_related('school_class__level_group').order_by('school_class__order', 'arm_name')

    return render(request, 'portal/student_directory.html', {
        'students': student_list,
        'current_term': current_term,
        'all_arms': all_arms,
        'selected_arm': int(arm_filter) if arm_filter and arm_filter.isdigit() else None,
        'search_query': search_query,
        'total_count': len(student_list),
        'cleared_count': cleared_count,
        'pending_count': pending_count,
    })


@login_required
def class_directory_view(request):
    """
    Academic Classes & Arms Directory.
    Shows class hierarchy, arm teachers, enrolled pupil counts, and active score sheets.
    """
    user = request.user
    is_staff_or_teacher = (
        user.is_staff or 
        user.role in ['SUPER_ADMIN', 'PROPRIETOR', 'PRINCIPAL', 'HEADMISTRESS', 'EXAM_OFFICER', 'CLASS_TEACHER', 'SUBJECT_TEACHER']
    )
    if not is_staff_or_teacher:
        messages.error(request, "Access restricted to school staff and administrators.")
        return redirect('portal:dashboard')

    current_term = TermSession.objects.filter(is_current=True).first()
    from apps.academics.models import SchoolClass
    from apps.assessments.models import ScoreSheet

    classes = SchoolClass.objects.select_related('level_group').prefetch_related(
        'arms__students__user',
        'arms__class_teacher'
    ).order_by('order', 'name')

    class_data = []
    total_school_students = 0
    for c in classes:
        arms_list = []
        class_student_sum = 0
        for arm in c.arms.all():
            st_count = arm.students.count()
            class_student_sum += st_count
            sheets_count = ScoreSheet.objects.filter(class_arm=arm, term_session=current_term).count() if current_term else 0
            arms_list.append({
                'arm': arm,
                'student_count': st_count,
                'sheets_count': sheets_count,
                'teacher': arm.class_teacher
            })
        total_school_students += class_student_sum
        class_data.append({
            'school_class': c,
            'arms': arms_list,
            'total_students': class_student_sum
        })

    return render(request, 'portal/class_directory.html', {
        'class_data': class_data,
        'current_term': current_term,
        'total_classes': len(class_data),
        'total_school_students': total_school_students,
    })


def lockout_view(request, credentials=None):
    return render(request, 'portal/lockout.html', status=429)
