from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
import random

from academics.models import SchoolClass, StudentProfile, TeacherProfile, Subject
from attendance.models import Attendance
from exams.models import Exam, ExamResult
from finance.models import FeeStructure, FeeInvoice, FeePayment
from users.models import CustomUser


class Command(BaseCommand):
    help = "Seed comprehensive school data for demo use."

    def handle(self, *args, **options):
        # Create admin user
        admin, created = CustomUser.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "System",
                "last_name": "Admin",
                "role": CustomUser.Roles.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "email": "admin@example.com",
            },
        )
        if created:
            admin.set_password("admin1234")
            admin.save()

        # Create accountant user
        accountant, created = CustomUser.objects.get_or_create(
            username="accountant",
            defaults={
                "first_name": "Zahir",
                "last_name": "Khan",
                "role": CustomUser.Roles.ACCOUNTANT,
                "email": "accountant@example.com",
            },
        )
        if created:
            accountant.set_password("accountant1234")
            accountant.save()

        # Create multiple teachers
        teacher_names = [
            ("Rafi", "Ahmed"),
            ("Fatima", "Islam"),
            ("Hassan", "Khan"),
            ("Aisha", "Begum"),
            ("Karim", "Sheikh"),
        ]
        teachers = []
        for fname, lname in teacher_names:
            user, created = CustomUser.objects.get_or_create(
                username=f"teacher_{fname.lower()}",
                defaults={
                    "first_name": fname,
                    "last_name": lname,
                    "role": CustomUser.Roles.TEACHER,
                    "email": f"{fname.lower()}@example.com",
                    "phone": f"0170{random.randint(1000000, 9999999)}",
                },
            )
            if created:
                user.set_password("teacher1234")
                user.save()
            teachers.append(user)

            # Create teacher profile
            TeacherProfile.objects.get_or_create(
                user=user,
                defaults={
                    "qualification": "B.Sc. in Education",
                    "subject_expertise": "Mixed",
                    "experience_years": random.randint(2, 15),
                },
            )

        # Create classes
        class_data = [
            ("Class 6", "A"),
            ("Class 6", "B"),
            ("Class 7", "A"),
            ("Class 8", "A"),
        ]
        classes = []
        for class_name, section in class_data:
            school_class, created = SchoolClass.objects.get_or_create(
                name=class_name,
                section=section,
                defaults={"class_teacher": random.choice(teachers)},
            )
            classes.append(school_class)

        # Create subjects
        subject_data = [
            ("Bengali", "BNG"),
            ("English", "ENG"),
            ("Mathematics", "MATH"),
            ("Science", "SCI"),
            ("Social Studies", "SS"),
        ]
        subjects = []
        for subject_name, code in subject_data:
            subject, created = Subject.objects.get_or_create(
                name=subject_name,
                defaults={"code": code},
            )
            subjects.append(subject)

        # Create students
        student_names = [
            ("Amina", "Rahman"),
            ("Bilal", "Ahmed"),
            ("Chiara", "Hassan"),
            ("Diya", "Sharma"),
            ("Emad", "Khan"),
            ("Fatin", "Islam"),
            ("Gita", "Devi"),
            ("Hasan", "Ali"),
            ("Isha", "Patel"),
            ("Jamal", "Ibrahim"),
        ]
        students = []
        roll_num = 1
        for classroom in classes:
            for idx, (fname, lname) in enumerate(student_names[:8], 1):
                user, created = CustomUser.objects.get_or_create(
                    username=f"student_{classroom.name.replace(' ', '')}_{idx}",
                    defaults={
                        "first_name": fname,
                        "last_name": lname,
                        "role": CustomUser.Roles.STUDENT,
                        "email": f"{fname.lower()}_{idx}@student.example.com",
                    },
                )
                if created:
                    user.set_password("student1234")
                    user.save()

                student_profile, created = StudentProfile.objects.get_or_create(
                    user=user,
                    school_class=classroom,
                    defaults={
                        "roll_number": f"{classroom.name.split()[-1]}{classroom.section}-{idx:03d}",
                        "admission_date": timezone.now().date() - timedelta(days=random.randint(30, 365)),
                        "guardian_name": f"Guardian of {fname}",
                        "guardian_phone": f"0170{random.randint(1000000, 9999999)}",
                    },
                )
                students.append((student_profile, classroom))

        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(students)} students"))

        # Create exams
        exam_data = [
            ("Midterm Exam", "2026-04-30"),
            ("Final Exam", "2026-05-30"),
            ("Unit Test 1", "2026-03-15"),
        ]
        exams = []
        for exam_name, exam_date in exam_data:
            for subject in subjects:
                exam, created = Exam.objects.get_or_create(
                    name=exam_name,
                    subject=subject,
                    defaults={
                        "date": exam_date,
                        "total_marks": 100,
                    },
                )
                if created:
                    exams.append(exam)

        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(exams)} exams"))

        # Create exam results
        for exam in exams:
            for student_profile, classroom in students:
                if classroom == exam.subject_code or True:  # Assign to all for demo
                    marks = random.randint(40, 100)
                    ExamResult.objects.get_or_create(
                        exam=exam,
                        student=student_profile,
                        defaults={"marks": marks},
                    )

        self.stdout.write(self.style.SUCCESS(f"✓ Created exam results"))

        # Create attendance records (last 30 days)
        attendance_count = 0
        today = timezone.now().date()
        for days_ago in range(30):
            attendance_date = today - timedelta(days=days_ago)
            for student_profile, classroom in students:
                status = random.choice(["Present", "Absent", "Late"])
                Attendance.objects.get_or_create(
                    student=student_profile,
                    date=attendance_date,
                    defaults={"status": status},
                )
                attendance_count += 1

        self.stdout.write(self.style.SUCCESS(f"✓ Created {attendance_count} attendance records"))

        # Create fee structures and invoices
        for classroom in classes:
            fee_structure, created = FeeStructure.objects.get_or_create(
                title=f"Term Fee - {classroom.name} {classroom.section}",
                classroom=classroom,
                defaults={
                    "amount": 5000,
                    "due_date": timezone.now().date() + timedelta(days=30),
                },
            )

            for student_profile, std_classroom in students:
                if std_classroom == classroom:
                    invoice, created = FeeInvoice.objects.get_or_create(
                        student=student_profile,
                        fee_structure=fee_structure,
                        defaults={
                            "amount_due": fee_structure.amount,
                            "amount_paid": random.choice([0, 2500, 5000]),
                        },
                    )

                    # Create payment if amount paid > 0
                    if invoice.amount_paid > 0:
                        FeePayment.objects.get_or_create(
                            invoice=invoice,
                            defaults={
                                "amount": invoice.amount_paid,
                                "payment_date": timezone.now().date() - timedelta(days=random.randint(1, 15)),
                                "payment_method": random.choice(["Cash", "Check", "Bank Transfer"]),
                            },
                        )

        self.stdout.write(self.style.SUCCESS("✓ Seed complete! Demo data created successfully."))
        self.stdout.write(self.style.SUCCESS(f"  Admin: admin / admin1234"))
        self.stdout.write(self.style.SUCCESS(f"  Teacher: teacher_rafi / teacher1234"))
        self.stdout.write(self.style.SUCCESS(f"  Student: student_class6a_1 / student1234"))
        self.stdout.write("admin/admin1234 | teacher1/teacher1234 | student1/student1234")
