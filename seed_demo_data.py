#!/usr/bin/env python
import os
import sys
import django
from datetime import timedelta, date
import random

# Add the management directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management.settings')
django.setup()

from academics.models import SchoolClass, StudentProfile, TeacherProfile, Subject
from attendance.models import Attendance
from exams.models import Exam, ExamResult
from finance.models import FeeStructure, FeeInvoice, FeePayment
from users.models import CustomUser
from django.utils import timezone

# Create classes
class_data = [
    ("Class 6", "A"),
    ("Class 6", "B"),
    ("Class 7", "A"),
]

print("🏫 Creating classes...")
classes = []
for class_name, section in class_data:
    school_class, created = SchoolClass.objects.get_or_create(
        name=class_name,
        section=section,
    )
    if created:
        print(f"  ✓ Created {class_name} {section}")
    classes.append(school_class)

# Create subjects for each class
print("📖 Creating subjects...")
subject_data = [
    ("Bengali", "BNG"),
    ("English", "ENG"),
    ("Mathematics", "MATH"),
    ("Science", "SCI"),
    ("Social Studies", "SS"),
]
subjects = []
for classroom in classes:
    for subject_name, code in subject_data:
        subject, created = Subject.objects.get_or_create(
            name=subject_name,
            code=f"{code}-{classroom.id}",
            classroom=classroom,
        )
        if created:
            print(f"  ✓ Created {subject_name} for {classroom.name}{classroom.section}")
        subjects.append(subject)

# Create students
print("👥 Creating students...")
student_names = [
    ("Amina", "Rahman"),
    ("Bilal", "Ahmed"),
    ("Chiara", "Hassan"),
    ("Diya", "Sharma"),
    ("Emad", "Khan"),
    ("Fatin", "Islam"),
    ("Gita", "Devi"),
    ("Hasan", "Ali"),
]
students = []
student_counter = 1
for classroom in classes:
    for idx, (fname, lname) in enumerate(student_names, 1):
        # Create unique username for each student across all classes
        username = f"student_{student_counter:03d}"
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                "first_name": f"{fname}_{classroom.name.split()[-1]}",
                "last_name": lname,
                "role": CustomUser.Roles.STUDENT,
                "email": f"{fname.lower()}_{classroom.name.split()[-1]}_{idx}@student.example.com",
            },
        )
        if created:
            user.set_password("student1234")
            user.save()
            print(f"  ✓ Created user {user.first_name} {user.last_name}")

        student_profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                "classroom": classroom,
                "roll_number": f"{classroom.name.split()[-1]}{classroom.section}-{idx:03d}",
                "admission_date": timezone.now().date() - timedelta(days=random.randint(30, 365)),
                "guardian_name": f"Guardian of {user.first_name}",
                "guardian_phone": f"0170{random.randint(1000000, 9999999)}",
            },
        )
        if created:
            print(f"  ✓ Created profile for {user.first_name} {user.last_name} in {classroom.name}{classroom.section}")
        students.append((student_profile, classroom))
        student_counter += 1

# Create exams
print("📝 Creating exams...")
exam_data = [
    ("Midterm Exam", "2026-04-30"),
    ("Final Exam", "2026-05-30"),
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
            print(f"  ✓ Created {exam_name} for {subject.name}")

# Create exam results
print("📊 Creating exam results...")
result_count = 0
for exam in exams:
    for student_profile, classroom in students:
        marks = random.randint(40, 100)
        result, created = ExamResult.objects.get_or_create(
            exam=exam,
            student=student_profile,
            defaults={"marks": marks},
        )
        if created:
            result_count += 1
print(f"  ✓ Created {result_count} exam results")

# Create attendance records
print("✓ Creating attendance records...")
attendance_count = 0
today = timezone.now().date()
for days_ago in range(15):
    attendance_date = today - timedelta(days=days_ago)
    for student_profile, classroom in students:
        status = random.choice(["Present", "Absent", "Late"])
        record, created = Attendance.objects.get_or_create(
            student=student_profile,
            date=attendance_date,
            defaults={"status": status},
        )
        if created:
            attendance_count += 1
print(f"  ✓ Created {attendance_count} attendance records")

# Create fee structures and invoices
print("💰 Creating invoices and payments...")
invoice_count = 0
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
            if created:
                invoice_count += 1
                print(f"  ✓ Created invoice for {student_profile.user.first_name}")

            # Create payment if amount paid > 0
            if invoice.amount_paid > 0:
                payment, created = FeePayment.objects.get_or_create(
                    invoice=invoice,
                    defaults={
                        "amount": invoice.amount_paid,
                        "payment_date": timezone.now().date() - timedelta(days=random.randint(1, 15)),
                        "payment_method": random.choice(["Cash", "Check", "Bank Transfer"]),
                    },
                )

print("\n✅ Seed complete! Demo data created successfully.")
print(f"   Total students: {len(students)}")
print(f"   Total classes: {len(classes)}")
print(f"   Total subjects: {len(subjects)}")
print(f"   Total invoices: {invoice_count}")
