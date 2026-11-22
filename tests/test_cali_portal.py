from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.academics.models import (
    LevelGroup, LevelGroupCategory, AssessmentMode,
    AcademicSession, AcademicTerm, TermSession,
    SchoolClass, ClassArm, Subject, StudentProfile, ParentStudentLink
)
from apps.assessments.models import ScoreSheet, StudentScore, ResultStatus
from apps.finance.models import StudentFeeStatus
from apps.results.calculation import get_grade_and_remark
from apps.accounts.auth_backends import SchoolAuthBackend
from django.template.context import BaseContext

# Python 3.15 compatibility patch for test template context copier
def _safe_context_copy(self):
    duplicate = object.__new__(self.__class__)
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate
BaseContext.__copy__ = _safe_context_copy

User = get_user_model()

class CaliPortalTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Session & Term
        self.session = AcademicSession.objects.create(
            name='2026/2027', start_date='2026-09-01', end_date='2027-07-20', is_active=True
        )
        self.term_session = TermSession.objects.create(
            session=self.session, term=AcademicTerm.FIRST, is_current=True
        )

        # Level Group
        self.lg_ss = LevelGroup.objects.create(
            category=LevelGroupCategory.SS,
            name='Senior Secondary',
            ca1_max=20, ca2_max=20, exam_max=60
        )

        # Class & Arm
        self.school_class = SchoolClass.objects.create(level_group=self.lg_ss, name='SS 1', code='SS1')
        self.arm = ClassArm.objects.create(school_class=self.school_class, arm_name='Gold')

        # Subject & Score Sheet
        self.subject = Subject.objects.create(level_group=self.lg_ss, name='Mathematics', code='MTH')
        self.sheet = ScoreSheet.objects.create(
            term_session=self.term_session, class_arm=self.arm, subject=self.subject, status=ResultStatus.DRAFT
        )

        # Student
        self.student_user = User.objects.create_user(
            username='CALI/2026/999', first_name='Tunde', last_name='Bakare', role='STUDENT'
        )
        self.student_user.set_password('123456')
        self.student_user.save()

        self.student = StudentProfile.objects.create(
            user=self.student_user, admission_number='CALI/2026/999', current_arm=self.arm
        )

        self.score_entry = StudentScore.objects.create(
            score_sheet=self.sheet, student=self.student, ca1=Decimal('15.0'), ca2=Decimal('15.0'), exam=Decimal('45.0')
        )

    def test_grade_calculation_engine(self):
        """Tests that WAEC 9-point scale correctly computes A1 to F9"""
        grade, remark = get_grade_and_remark(Decimal('78.0'), LevelGroupCategory.SS)
        self.assertEqual(grade, 'A1')
        self.assertEqual(remark, 'Excellent')

        grade_c, _ = get_grade_and_remark(Decimal('58.0'), LevelGroupCategory.SS)
        self.assertEqual(grade_c, 'C5')

        # Primary test
        pri_grade, pri_rem = get_grade_and_remark(Decimal('85.0'), LevelGroupCategory.PRIMARY)
        self.assertEqual(pri_grade, 'A')

    def test_auth_with_admission_number_and_pin(self):
        """Tests that students/parents authenticate seamlessly with Admission Number + PIN"""
        user = SchoolAuthBackend().authenticate(request=None, username='CALI/2026/999', password='123456')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'CALI/2026/999')

    def test_htmx_score_update(self):
        """Tests debounced HTMX cell update recalculates total and grade"""
        self.client.force_login(self.student_user)
        response = self.client.post(
            reverse('assessments:update-score-cell', kwargs={'score_id': self.score_entry.id}),
            {'field': 'exam', 'value': '55.0'}
        )
        self.assertEqual(response.status_code, 200)
        self.score_entry.refresh_from_db()
        self.assertEqual(self.score_entry.exam, Decimal('55.0'))
        self.assertEqual(self.score_entry.total, Decimal('85.0'))
        self.assertEqual(self.score_entry.grade, 'A1')

    def test_fee_paywall_gatekeeper(self):
        """Tests that report cards are strictly locked when fees are unpaid"""
        # Set fee status to unpaid
        StudentFeeStatus.objects.create(
            student=self.student, term_session=self.term_session,
            total_billed=Decimal('100000.00'), total_paid=Decimal('20000.00'), balance=Decimal('80000.00'), has_cleared_fees=False
        )

        self.client.force_login(self.student_user)
        url = reverse('results:view-report', kwargs={
            'term_session_id': self.term_session.id,
            'student_id': self.student.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Terminal Result Locked")
        self.assertContains(response, "80000.00")

    def test_student_and_class_directories_accessible_by_admin(self):
        """Tests that administrators can access both Student and Class directories"""
        admin_user = User.objects.create_user(
            username='admin@calischools.ng', email='admin@calischools.ng', role='SUPER_ADMIN', is_staff=True
        )
        admin_user.set_password('AdminPass123!')
        admin_user.save()

        self.client.force_login(admin_user)

        # 1. Test student directory
        res_students = self.client.get(reverse('portal:students'))
        self.assertEqual(res_students.status_code, 200)
        self.assertContains(res_students, "Enrolled Students & Pupils")
        self.assertContains(res_students, "CALI/2026/999")
        self.assertContains(res_students, "Tunde Bakare")

        # 2. Test class directory
        res_classes = self.client.get(reverse('portal:classes'))
        self.assertEqual(res_classes.status_code, 200)
        self.assertContains(res_classes, "Academic Classes & Arms")
        self.assertContains(res_classes, "SS 1")

        # 3. Test admin dashboard has student roster and clickable stat links
        res_dash = self.client.get(reverse('portal:dashboard'))
        self.assertEqual(res_dash.status_code, 200)
        self.assertContains(res_dash, reverse('portal:students'))
        self.assertContains(res_dash, reverse('portal:classes'))

    def test_admin_bypasses_fee_paywall_for_inspection(self):
        """Tests that school admin can inspect report card even if fees are unpaid"""
        admin_user = User.objects.create_user(
            username='principal@calischools.ng', email='principal@calischools.ng', role='PRINCIPAL', is_staff=True
        )
        admin_user.set_password('AdminPass123!')
        admin_user.save()

        # Fee unpaid
        StudentFeeStatus.objects.get_or_create(
            student=self.student, term_session=self.term_session,
            defaults={
                'total_billed': Decimal('100000.00'),
                'total_paid': Decimal('0.00'),
                'balance': Decimal('100000.00'),
                'has_cleared_fees': False
            }
        )

        self.client.force_login(admin_user)
        url = reverse('results:view-report', kwargs={
            'term_session_id': self.term_session.id,
            'student_id': self.student.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Should not be locked with paywall
        self.assertNotContains(response, "Terminal Result Locked")
        self.assertContains(response, "CALI/2026/999")
