from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Avg, Count
from apps.assessments.models import StudentScore
from apps.results.models import TermResultSummary
from apps.academics.models import LevelGroupCategory

def get_grade_and_remark(score: Decimal, level_category: str) -> tuple[str, str]:
    """
    Computes Grade and Official Remark according to Nigerian national standards.
    - Early Years: Descriptive ratings
    - Primary & JSS: Standard A-F Scale
    - SS: WAEC Standard 9-Point Scale (A1 to F9)
    """
    s = float(score)

    if level_category == LevelGroupCategory.EARLY_YEARS:
        if s >= 85: return ('EX', 'Exceeding Expectations')
        if s >= 70: return ('ME', 'Meeting Expectations')
        if s >= 50: return ('DV', 'Developing')
        return ('EM', 'Emerging / Needs Support')

    elif level_category in [LevelGroupCategory.PRIMARY, LevelGroupCategory.JSS]:
        if s >= 80: return ('A', 'Distinction')
        if s >= 70: return ('B', 'Very Good')
        if s >= 60: return ('C', 'Credit')
        if s >= 50: return ('P', 'Pass')
        return ('F', 'Fail')

    else:  # Senior Secondary (WAEC scale)
        if s >= 75: return ('A1', 'Excellent')
        if s >= 70: return ('B2', 'Very Good')
        if s >= 65: return ('B3', 'Good')
        if s >= 60: return ('C4', 'Credit')
        if s >= 55: return ('C5', 'Credit')
        if s >= 50: return ('C6', 'Credit')
        if s >= 45: return ('D7', 'Pass')
        if s >= 40: return ('E8', 'Pass')
        return ('F9', 'Fail')

@transaction.atomic
def calculate_subject_positions(score_sheet):
    """
    Computes subject rankings for a given subject score sheet.
    """
    scores = list(StudentScore.objects.filter(score_sheet=score_sheet).order_by('-total'))
    rank = 1
    for i, s in enumerate(scores):
        if i > 0 and s.total < scores[i - 1].total:
            rank = i + 1
        s.subject_position = rank
        s.save(update_fields=['subject_position'])

@transaction.atomic
def calculate_class_term_summary(class_arm, term_session):
    """
    Aggregates student overall totals, averages, and class rankings.
    """
    students = class_arm.students.all()
    summaries = []

    for student in students:
        agg = StudentScore.objects.filter(
            score_sheet__term_session=term_session,
            student=student
        ).aggregate(total_sum=Sum('total'), avg_score=Avg('total'))

        summary, _ = TermResultSummary.objects.get_or_create(
            student=student,
            term_session=term_session
        )
        summary.total_score = agg['total_sum'] or Decimal('0.00')
        summary.average = round(agg['avg_score'] or Decimal('0.00'), 2)
        summary.out_of = students.count()
        summary.save()
        summaries.append(summary)

    # Sort descending by average and assign rank
    summaries.sort(key=lambda x: x.average, reverse=True)
    pos = 1
    for idx, summ in enumerate(summaries):
        if idx > 0 and summ.average < summaries[idx - 1].average:
            pos = idx + 1
        summ.class_position = pos
        summ.save(update_fields=['class_position', 'out_of'])
