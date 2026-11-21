from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from apps.academics.models import (
    MasterSubjectBank, Subject, LevelGroup, LevelGroupCategory, Department
)

@login_required
def subject_bank_manager(request):
    """
    Curriculum & Subject Bank selector for School Admins.
    Allows toggling which national curriculum subjects CALI Schools offers.
    """
    if not request.user.is_staff and request.user.role not in ['SUPER_ADMIN', 'PROPRIETOR', 'PRINCIPAL', 'HEADMISTRESS', 'EXAM_OFFICER']:
        return HttpResponseForbidden("Only school administrators can configure offered subjects.")

    # Get active tab from GET or default to 'SS'
    active_level = request.GET.get('level', LevelGroupCategory.SS)

    # Master subjects for this level group
    master_subjects = MasterSubjectBank.objects.filter(level_category=active_level)

    # Department filter for SS
    dept_filter = request.GET.get('dept', '')
    if dept_filter and active_level == LevelGroupCategory.SS:
        master_subjects = master_subjects.filter(department=dept_filter)

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        master_subjects = master_subjects.filter(name__icontains=query)

    # Fetch corresponding level group
    level_group = LevelGroup.objects.filter(category=active_level).first()

    # Create mapping of active school subjects
    active_codes = set()
    if level_group:
        active_codes = set(
            Subject.objects.filter(level_group=level_group, is_active=True).values_list('code', flat=True)
        )

    # Annotate master subjects with active status
    subject_items = []
    for ms in master_subjects:
        subject_items.append({
            'master': ms,
            'is_offered': (ms.code in active_codes)
        })

    context = {
        'subject_items': subject_items,
        'active_level': active_level,
        'level_group': level_group,
        'dept_filter': dept_filter,
        'query': query,
        'categories': LevelGroupCategory.choices,
        'total_active_count': len(active_codes),
        'total_bank_count': master_subjects.count()
    }

    return render(request, 'academics/subject_bank.html', context)

@login_required
def toggle_subject_offering(request, master_id):
    """
    HTMX endpoint to activate/deactivate an offered subject in CALI Schools.
    """
    if not request.user.is_staff and request.user.role not in ['SUPER_ADMIN', 'PROPRIETOR', 'PRINCIPAL', 'HEADMISTRESS', 'EXAM_OFFICER']:
        return HttpResponseForbidden("Unauthorized")

    master = get_object_or_404(MasterSubjectBank, id=master_id)
    level_group = LevelGroup.objects.filter(category=master.level_category).first()

    if not level_group:
        return HttpResponse("Level group not found", status=400)

    # Find or create School Subject record
    subject, created = Subject.objects.get_or_create(
        level_group=level_group,
        name=master.name,
        defaults={
            'code': master.code,
            'department': master.department,
            'master_subject': master,
            'is_active': True,
            'is_elective': not master.is_core
        }
    )

    if not created:
        subject.is_active = not subject.is_active
        subject.master_subject = master
        subject.save(update_fields=['is_active', 'master_subject'])

    return render(request, 'academics/partials/subject_toggle_button.html', {
        'master': master,
        'is_offered': subject.is_active
    })

@login_required
def bulk_activate_core(request, level_cat):
    """
    One-click activate all compulsory/core subjects for a level group.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden("Unauthorized")

    level_group = get_object_or_404(LevelGroup, category=level_cat)
    core_masters = MasterSubjectBank.objects.filter(level_category=level_cat, is_core=True)

    activated = 0
    for ms in core_masters:
        subj, _ = Subject.objects.get_or_create(
            level_group=level_group,
            name=ms.name,
            defaults={
                'code': ms.code,
                'department': ms.department,
                'master_subject': ms,
                'is_active': True,
                'is_elective': False
            }
        )
        if not subj.is_active:
            subj.is_active = True
            subj.save(update_fields=['is_active'])
        activated += 1

    messages.success(request, f"Activated all {activated} compulsory core subjects for {level_group.name}!")
    return redirect(f"/academics/subject-bank/?level={level_cat}")
