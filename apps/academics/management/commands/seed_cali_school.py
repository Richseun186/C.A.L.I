import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from apps.accounts.models import UserRole
from apps.academics.models import (
    LevelGroup, LevelGroupCategory, AssessmentMode,
    AcademicSession, AcademicTerm, TermSession,
    SchoolClass, ClassArm, Department, Subject,
    StudentProfile, ParentStudentLink
)
from apps.assessments.models import (
    ScoreSheet, StudentScore, ResultStatus,
    DevelopmentalSkill, SkillCategory, StudentSkillRating
)
from apps.results.models import TermResultSummary, PromotionStatus
from apps.results.calculation import calculate_class_term_summary, calculate_subject_positions, get_grade_and_remark
from apps.finance.models import ClassFeeStructure, StudentFeeStatus

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial CALI Schools structure, subjects, sample staff, parents, and students'

    def handle(self, *args, **options):
        self.stdout.write("Starting CALI Schools data seeding...")

        # 1. Super Admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@calischools.ng',
                'first_name': 'IT',
                'last_name': 'Director',
                'role': UserRole.SUPER_ADMIN,
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('AdminPass123!')
        admin_user.save()

        # 2. Staff Accounts
        nurs_teacher, _ = User.objects.get_or_create(
            username='nursery_teacher',
            defaults={
                'email': 'nursery.teacher@calischools.ng',
                'first_name': 'Grace',
                'last_name': 'Okafor',
                'role': UserRole.CLASS_TEACHER,
                'is_staff': True
            }
        )
        nurs_teacher.set_password('TeachPass123!')
        nurs_teacher.save()

        prim_teacher, _ = User.objects.get_or_create(
            username='primary_teacher',
            defaults={
                'email': 'primary.teacher@calischools.ng',
                'first_name': 'Emeka',
                'last_name': 'Adeyemi',
                'role': UserRole.CLASS_TEACHER,
                'is_staff': True
            }
        )
        prim_teacher.set_password('TeachPass123!')
        prim_teacher.save()

        sec_teacher, _ = User.objects.get_or_create(
            username='sec_teacher',
            defaults={
                'email': 'secondary.teacher@calischools.ng',
                'first_name': 'Babatunde',
                'last_name': 'Aliyu',
                'role': UserRole.CLASS_TEACHER,
                'is_staff': True
            }
        )
        sec_teacher.set_password('TeachPass123!')
        sec_teacher.save()

        # 3. Academic Session & Term
        session, _ = AcademicSession.objects.get_or_create(
            name='2026/2027',
            defaults={
                'start_date': datetime.date(2026, 9, 14),
                'end_date': datetime.date(2027, 7, 23),
                'is_active': True
            }
        )
        term_session, _ = TermSession.objects.get_or_create(
            session=session,
            term=AcademicTerm.FIRST,
            defaults={
                'is_current': True,
                'next_term_resumption': datetime.date(2027, 1, 11)
            }
        )

        # 4. Level Groups
        lg_ey, _ = LevelGroup.objects.get_or_create(
            category=LevelGroupCategory.EARLY_YEARS,
            defaults={
                'name': 'Early Years',
                'assessment_mode': AssessmentMode.NUMERIC_AND_SKILLS,
                'ca1_max': 20,
                'ca2_max': 20,
                'exam_max': 60,
                'enable_positions': False,
                'theme_color': 'amber'
            }
        )

        lg_pri, _ = LevelGroup.objects.get_or_create(
            category=LevelGroupCategory.PRIMARY,
            defaults={
                'name': 'Primary Section',
                'assessment_mode': AssessmentMode.STANDARD_CA_EXAM,
                'ca1_max': 10,
                'ca2_max': 10,
                'exam_max': 80,
                'enable_positions': True,
                'theme_color': 'emerald'
            }
        )

        lg_jss, _ = LevelGroup.objects.get_or_create(
            category=LevelGroupCategory.JSS,
            defaults={
                'name': 'Junior Secondary',
                'assessment_mode': AssessmentMode.STANDARD_CA_EXAM,
                'ca1_max': 20,
                'ca2_max': 20,
                'exam_max': 60,
                'enable_positions': True,
                'theme_color': 'sky'
            }
        )

        lg_ss, _ = LevelGroup.objects.get_or_create(
            category=LevelGroupCategory.SS,
            defaults={
                'name': 'Senior Secondary',
                'assessment_mode': AssessmentMode.STANDARD_CA_EXAM,
                'ca1_max': 20,
                'ca2_max': 20,
                'exam_max': 60,
                'enable_positions': True,
                'theme_color': 'indigo'
            }
        )

        # 5. Classes & Arms
        cls_nur2, _ = SchoolClass.objects.get_or_create(level_group=lg_ey, name='Nursery 2', code='NUR2', order=3)
        arm_nur2, _ = ClassArm.objects.get_or_create(school_class=cls_nur2, arm_name='Rainbow', class_teacher=nurs_teacher)

        cls_pri4, _ = SchoolClass.objects.get_or_create(level_group=lg_pri, name='Primary 4', code='PR4', order=7)
        arm_pri4, _ = ClassArm.objects.get_or_create(school_class=cls_pri4, arm_name='Gold', class_teacher=prim_teacher)

        cls_ss2, _ = SchoolClass.objects.get_or_create(level_group=lg_ss, name='SS 2', code='SS2', order=12)
        arm_ss2, _ = ClassArm.objects.get_or_create(school_class=cls_ss2, arm_name='Science', class_teacher=sec_teacher)

        # 6. Subjects
        sub_num, _ = Subject.objects.get_or_create(level_group=lg_ey, name='Number Work', code='EY-NUM')
        sub_let, _ = Subject.objects.get_or_create(level_group=lg_ey, name='Letter Work & Phonics', code='EY-LET')
        sub_rhym, _ = Subject.objects.get_or_create(level_group=lg_ey, name='Rhymes & Songs', code='EY-RHY')
        sub_soc, _ = Subject.objects.get_or_create(level_group=lg_ey, name='Social Habits', code='EY-SOC')

        sub_mat, _ = Subject.objects.get_or_create(level_group=lg_pri, name='Mathematics', code='PR-MTH')
        sub_eng, _ = Subject.objects.get_or_create(level_group=lg_pri, name='English Language', code='PR-ENG')
        sub_sci, _ = Subject.objects.get_or_create(level_group=lg_pri, name='Basic Science & Tech', code='PR-BST')
        sub_com, _ = Subject.objects.get_or_create(level_group=lg_pri, name='Computer & Digital Literacy', code='PR-CMP')

        sub_mth_s, _ = Subject.objects.get_or_create(level_group=lg_ss, name='General Mathematics', code='SS-MTH')
        sub_eng_s, _ = Subject.objects.get_or_create(level_group=lg_ss, name='English Language', code='SS-ENG')
        sub_phy, _ = Subject.objects.get_or_create(level_group=lg_ss, name='Physics', code='SS-PHY', department=Department.SCIENCE)
        sub_chm, _ = Subject.objects.get_or_create(level_group=lg_ss, name='Chemistry', code='SS-CHM', department=Department.SCIENCE)

        # 7. Developmental Skills for Early Years and Primary
        dev_pencil, _ = DevelopmentalSkill.objects.get_or_create(
            level_group=lg_ey, name='Pencil Grip & Handwriting Coordination', category=SkillCategory.EARLY_DEVELOPMENT
        )
        dev_sharing, _ = DevelopmentalSkill.objects.get_or_create(
            level_group=lg_ey, name='Sharing & Social Interaction', category=SkillCategory.EARLY_DEVELOPMENT
        )
        aff_neat, _ = DevelopmentalSkill.objects.get_or_create(
            level_group=lg_pri, name='Neatness & Personal Hygiene', category=SkillCategory.AFFECTIVE
        )
        aff_punct, _ = DevelopmentalSkill.objects.get_or_create(
            level_group=lg_pri, name='Punctuality & Attendance', category=SkillCategory.AFFECTIVE
        )

        # 8. Sample Parent with 3 Children across all levels
        parent_user, _ = User.objects.get_or_create(
            username='08031234567',
            defaults={
                'email': 'parent@calischools.ng',
                'phone': '08031234567',
                'first_name': 'Dr. Johnson',
                'last_name': 'Oluwaseun',
                'role': UserRole.PARENT
            }
        )
        parent_user.set_password('123456')
        parent_user.save()

        # Child 1: Nursery 2
        u1, _ = User.objects.get_or_create(
            username='CALI/2026/001',
            defaults={'first_name': 'Tomiwa', 'last_name': 'Oluwaseun', 'role': UserRole.STUDENT}
        )
        u1.set_password('123456')
        u1.save()
        p1, _ = StudentProfile.objects.get_or_create(
            user=u1,
            defaults={
                'admission_number': 'CALI/2026/001',
                'raw_pin': make_password('123456'),
                'current_arm': arm_nur2,
                'gender': 'M',
                'date_of_birth': datetime.date(2022, 4, 15)
            }
        )
        ParentStudentLink.objects.get_or_create(parent=parent_user, student=p1)

        # Child 2: Primary 4
        u2, _ = User.objects.get_or_create(
            username='CALI/2024/042',
            defaults={'first_name': 'Chidinma', 'last_name': 'Oluwaseun', 'role': UserRole.STUDENT}
        )
        u2.set_password('123456')
        u2.save()
        p2, _ = StudentProfile.objects.get_or_create(
            user=u2,
            defaults={
                'admission_number': 'CALI/2024/042',
                'raw_pin': make_password('123456'),
                'current_arm': arm_pri4,
                'gender': 'F',
                'date_of_birth': datetime.date(2016, 8, 22)
            }
        )
        ParentStudentLink.objects.get_or_create(parent=parent_user, student=p2)

        # Child 3: SS 2 Science
        u3, _ = User.objects.get_or_create(
            username='CALI/2021/108',
            defaults={'first_name': 'Femi', 'last_name': 'Oluwaseun', 'role': UserRole.STUDENT}
        )
        u3.set_password('123456')
        u3.save()
        p3, _ = StudentProfile.objects.get_or_create(
            user=u3,
            defaults={
                'admission_number': 'CALI/2021/108',
                'raw_pin': make_password('123456'),
                'current_arm': arm_ss2,
                'department': Department.SCIENCE,
                'gender': 'M',
                'date_of_birth': datetime.date(2010, 11, 5)
            }
        )
        ParentStudentLink.objects.get_or_create(parent=parent_user, student=p3)

        # 9. Fee Status (Child 1 & 3 paid in full, Child 2 has partial unpaid balance for testing the gate)
        StudentFeeStatus.objects.get_or_create(
            student=p1, term_session=term_session,
            defaults={'total_billed': Decimal('120000.00'), 'total_paid': Decimal('120000.00'), 'balance': Decimal('0.00'), 'has_cleared_fees': True}
        )
        # Child 2 has outstanding fees to demonstrate Paywall
        StudentFeeStatus.objects.get_or_create(
            student=p2, term_session=term_session,
            defaults={'total_billed': Decimal('150000.00'), 'total_paid': Decimal('100000.00'), 'balance': Decimal('50000.00'), 'has_cleared_fees': False}
        )
        StudentFeeStatus.objects.get_or_create(
            student=p3, term_session=term_session,
            defaults={'total_billed': Decimal('220000.00'), 'total_paid': Decimal('220000.00'), 'balance': Decimal('0.00'), 'has_cleared_fees': True}
        )

        # 10. Sample Score Sheets & Scores
        # Early Years Score Sheets
        s_sheet1, _ = ScoreSheet.objects.get_or_create(term_session=term_session, class_arm=arm_nur2, subject=sub_num, teacher=nurs_teacher)
        s_score1, _ = StudentScore.objects.get_or_create(
            score_sheet=s_sheet1, student=p1,
            defaults={'ca1': Decimal('18.0'), 'ca2': Decimal('19.0'), 'exam': Decimal('54.0'), 'total': Decimal('91.0'), 'grade': 'EX', 'remark': 'Brilliant counting'}
        )
        StudentSkillRating.objects.get_or_create(student=p1, term_session=term_session, skill=dev_pencil, defaults={'rating': 5})
        StudentSkillRating.objects.get_or_create(student=p1, term_session=term_session, skill=dev_sharing, defaults={'rating': 4})
        TermResultSummary.objects.get_or_create(
            student=p1, term_session=term_session,
            defaults={
                'total_score': Decimal('91.0'),
                'average': Decimal('91.0'),
                'times_present': 108,
                'times_school_opened': 110,
                'class_teacher_remark': 'Tomiwa shows outstanding eagerness to learn and shares joyfully with peers.',
                'head_teacher_remark': 'Excellent foundational milestones achieved.',
                'promotion_status': PromotionStatus.PROMOTED,
                'is_published': True
            }
        )

        # Primary 4 Score Sheet
        s_sheet2, _ = ScoreSheet.objects.get_or_create(term_session=term_session, class_arm=arm_pri4, subject=sub_mat, teacher=prim_teacher)
        StudentScore.objects.get_or_create(
            score_sheet=s_sheet2, student=p2,
            defaults={'ca1': Decimal('9.0'), 'ca2': Decimal('8.5'), 'exam': Decimal('68.0'), 'total': Decimal('85.5'), 'grade': 'A', 'remark': 'Distinction in Math'}
        )
        StudentSkillRating.objects.get_or_create(student=p2, term_session=term_session, skill=aff_neat, defaults={'rating': 5})
        StudentSkillRating.objects.get_or_create(student=p2, term_session=term_session, skill=aff_punct, defaults={'rating': 4})
        TermResultSummary.objects.get_or_create(
            student=p2, term_session=term_session,
            defaults={
                'total_score': Decimal('85.5'),
                'average': Decimal('85.5'),
                'class_position': 2,
                'out_of': 25,
                'times_present': 105,
                'times_school_opened': 110,
                'class_teacher_remark': 'Chidinma is a very disciplined pupil with great quantitative reasoning skills.',
                'head_teacher_remark': 'Keep up this standard in the upcoming term.',
                'promotion_status': PromotionStatus.PROMOTED,
                'is_published': True
            }
        )

        # SS 2 Score Sheet
        s_sheet3, _ = ScoreSheet.objects.get_or_create(term_session=term_session, class_arm=arm_ss2, subject=sub_phy, teacher=sec_teacher)
        StudentScore.objects.get_or_create(
            score_sheet=s_sheet3, student=p3,
            defaults={'ca1': Decimal('18.0'), 'ca2': Decimal('17.0'), 'exam': Decimal('48.0'), 'total': Decimal('83.0'), 'grade': 'A1', 'remark': 'Excellent in Physics'}
        )
        TermResultSummary.objects.get_or_create(
            student=p3, term_session=term_session,
            defaults={
                'total_score': Decimal('83.0'),
                'average': Decimal('83.0'),
                'class_position': 1,
                'out_of': 18,
                'times_present': 110,
                'times_school_opened': 110,
                'class_teacher_remark': 'Femi has exceptional problem-solving and scientific analytical skills.',
                'head_teacher_remark': 'Outstanding academic record. Well done!',
                'promotion_status': PromotionStatus.PROMOTED,
                'is_published': True
            }
        )

        self.stdout.write(self.style.SUCCESS("CALI Schools database seeded successfully!"))
        self.stdout.write(self.style.NOTICE("Test Credentials:"))
        self.stdout.write("  Super Admin: admin@calischools.ng / AdminPass123!")
        self.stdout.write("  Nursery Teacher: nursery.teacher@calischools.ng / TeachPass123!")
        self.stdout.write("  Primary Teacher: primary.teacher@calischools.ng / TeachPass123!")
        self.stdout.write("  Secondary Teacher: secondary.teacher@calischools.ng / TeachPass123!")
        self.stdout.write("  Parent (3 Wards): Phone: 08031234567 / PIN: 123456")
        self.stdout.write("  Student 1 (Nursery 2): CALI/2026/001 / PIN: 123456 (Fees Cleared)")
        self.stdout.write("  Student 2 (Primary 4): CALI/2024/042 / PIN: 123456 (Fees Owing -> Tests Paywall)")
        self.stdout.write("  Student 3 (SS 2): CALI/2021/108 / PIN: 123456 (Fees Cleared -> Tests WAEC Report & Confetti)")
