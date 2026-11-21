from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.assessments.models import ScoreSheet, StudentScore, ResultStatus
from apps.results.calculation import get_grade_and_remark, calculate_subject_positions

@login_required
def score_sheet_detail(request, sheet_id):
    sheet = get_object_or_404(
        ScoreSheet.objects.select_related(
            'class_arm__school_class__level_group',
            'subject',
            'term_session__session'
        ),
        id=sheet_id
    )

    scores = sheet.scores.select_related('student__user').order_by('student__admission_number')
    level = sheet.class_arm.school_class.level_group

    return render(request, 'gradebook/sheet.html', {
        'sheet': sheet,
        'scores': scores,
        'level': level,
    })

@login_required
def update_score_cell(request, score_id):
    score_entry = get_object_or_404(
        StudentScore.objects.select_related(
            'score_sheet__class_arm__school_class__level_group',
            'student__user'
        ),
        id=score_id
    )

    sheet = score_entry.score_sheet
    if sheet.is_locked:
        return HttpResponseForbidden("Score sheet is locked and approved. Alterations are forbidden.")

    field = request.POST.get('field')  # 'ca1', 'ca2', or 'exam'
    raw_val = request.POST.get('value', '0').strip()

    level = sheet.class_arm.school_class.level_group
    max_limits = {
        'ca1': level.ca1_max,
        'ca2': level.ca2_max,
        'exam': level.exam_max
    }

    try:
        val = Decimal(raw_val) if raw_val else Decimal('0.00')
        max_allowed = max_limits.get(field, 100)
        if val < 0 or val > max_allowed:
            return HttpResponse(
                f'<span class="text-xs text-rose-600 font-bold">Max {max_allowed}!</span>',
                status=422
            )
    except (InvalidOperation, ValueError):
        return HttpResponse('<span class="text-xs text-rose-600 font-bold">Invalid</span>', status=422)

    # Update the score field
    setattr(score_entry, field, val)
    score_entry.total = (score_entry.ca1 or 0) + (score_entry.ca2 or 0) + (score_entry.exam or 0)
    
    # Calculate grade and remark according to LevelGroup category
    grade, remark = get_grade_and_remark(score_entry.total, level.category)
    score_entry.grade = grade
    score_entry.remark = remark
    score_entry.save()

    return render(request, 'gradebook/partials/score_row.html', {
        'score': score_entry,
        'sheet': sheet,
        'saved_field': field
    })

@login_required
def transition_sheet_status(request, sheet_id, new_status):
    sheet = get_object_or_404(ScoreSheet, id=sheet_id)
    valid_transitions = {
        ResultStatus.SUBMITTED: ['SUBJECT_TEACHER', 'CLASS_TEACHER', 'EXAM_OFFICER', 'SUPER_ADMIN'],
        ResultStatus.REVIEWED: ['EXAM_OFFICER', 'SUPER_ADMIN'],
        ResultStatus.APPROVED: ['HEADMISTRESS', 'PRINCIPAL', 'SUPER_ADMIN', 'PROPRIETOR'],
        ResultStatus.PUBLISHED: ['HEADMISTRESS', 'PRINCIPAL', 'SUPER_ADMIN', 'PROPRIETOR'],
    }

    allowed_roles = valid_transitions.get(new_status, [])
    if request.user.role not in allowed_roles:
        messages.error(request, f"You are not authorized to set this sheet to {new_status}.")
        return redirect('assessments:sheet-detail', sheet_id=sheet.id)

    sheet.status = new_status
    sheet.save()

    # Recompute positions if approved
    if new_status == ResultStatus.APPROVED:
        calculate_subject_positions(sheet)

    messages.success(request, f"Score sheet successfully updated to {sheet.get_status_display()}.")
    return redirect('assessments:sheet-detail', sheet_id=sheet.id)
