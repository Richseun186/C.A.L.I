from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.academics.models import StudentProfile, TermSession, LevelGroupCategory
from apps.assessments.models import StudentScore, StudentSkillRating
from apps.results.models import TermResultSummary
from apps.finance.models import StudentFeeStatus

@login_required
def view_or_download_report_card(request, term_session_id, student_id, format='html'):
    """
    Unified result delivery endpoint.
    Checks fee clearance -> Renders interactive HTML or prints A4 PDF.
    """
    student = get_object_or_404(
        StudentProfile.objects.select_related(
            'user', 'current_arm__school_class__level_group'
        ),
        id=student_id
    )
    term_session = get_object_or_404(TermSession, id=term_session_id)

    # 1. Authorization Check: Parent or the Student themselves or School Staff
    if request.user.role == 'PARENT':
        if not student.parents.filter(parent=request.user).exists():
            return HttpResponseForbidden("Unauthorized access to this student's report.")
    elif request.user.role == 'STUDENT' and request.user != student.user:
        return HttpResponseForbidden("Unauthorized access.")

    # 2. Strict School Fees Gate
    fee_status = StudentFeeStatus.objects.filter(
        student=student, term_session=term_session
    ).first()

    if not fee_status or not fee_status.has_cleared_fees:
        return render(request, 'portal/fee_paywall.html', {
            'student': student,
            'term_session': term_session,
            'fee_status': fee_status,
            'paystack_public_key': getattr(settings, 'PAYSTACK_PUBLIC_KEY', '')
        })

    # 3. Retrieve Result Data
    scores = StudentScore.objects.filter(
        score_sheet__term_session=term_session, student=student
    ).select_related('score_sheet__subject').order_by('score_sheet__subject__name')

    summary = TermResultSummary.objects.filter(
        student=student, term_session=term_session
    ).first()

    skills = StudentSkillRating.objects.filter(
        student=student, term_session=term_session
    ).select_related('skill')

    level_group = student.current_arm.school_class.level_group
    category = level_group.category

    # Template selection per Level Group
    template_map = {
        LevelGroupCategory.EARLY_YEARS: 'reports/early_years.html',
        LevelGroupCategory.PRIMARY: 'reports/primary.html',
        LevelGroupCategory.JSS: 'reports/secondary.html',
        LevelGroupCategory.SS: 'reports/secondary.html',
    }
    template_name = template_map.get(category, 'reports/primary.html')

    context = {
        'student': student,
        'term_session': term_session,
        'scores': scores,
        'summary': summary,
        'skills': skills,
        'level_group': level_group,
        'is_pdf': (format == 'pdf'),
        'school_logo_url': request.build_absolute_uri('/static/img/cali_logo.png')
    }

    if format == 'html':
        return render(request, template_name, context)

    # PDF Compilation via WeasyPrint (with fallback for Windows dev environments without GTK3)
    try:
        from weasyprint import HTML, CSS
        html_string = render_to_string(template_name, context, request=request)
        base_url = request.build_absolute_uri('/')
        
        pdf_file = HTML(string=html_string, base_url=base_url).write_pdf(
            stylesheets=[
                CSS(string='''
                    @page {
                        size: A4 portrait;
                        margin: 8mm 10mm 8mm 10mm;
                        @bottom-center {
                            content: "CALI Schools Portal • Secure Multi-Term Result • Page " counter(page) " of " counter(pages);
                            font-family: sans-serif;
                            font-size: 8pt;
                            color: #64748b;
                        }
                    }
                ''')
            ]
        )

        response = HttpResponse(pdf_file, content_type='application/pdf')
        filename = f"CALI_Report_{student.admission_number.replace('/', '_')}_{term_session.term}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    except (ImportError, OSError):
        # Fallback to high-fidelity printable HTML view with auto-trigger for print dialog
        context['auto_print'] = True
        return render(request, template_name, context)
