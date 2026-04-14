from django.core.management.base import BaseCommand
from django.utils import timezone

from academics.models import SchoolClass, StudentProfile
from finance.models import FeeInvoice, FeeStructure
from users.models import CustomUser


class Command(BaseCommand):
    help = "Seed basic school data for quick demo use."

    def handle(self, *args, **options):
        admin, _ = CustomUser.objects.get_or_create(
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
        admin.set_password("admin1234")
        admin.save()

        teacher, _ = CustomUser.objects.get_or_create(
            username="teacher1",
            defaults={
                "first_name": "Rafi",
                "last_name": "Sir",
                "role": CustomUser.Roles.TEACHER,
                "email": "teacher@example.com",
            },
        )
        teacher.set_password("teacher1234")
        teacher.save()

        school_class, _ = SchoolClass.objects.get_or_create(
            name="Class 6",
            section="A",
            defaults={"class_teacher": teacher},
        )

        student_user, _ = CustomUser.objects.get_or_create(
            username="student1",
            defaults={
                "first_name": "Amina",
                "last_name": "Rahman",
                "role": CustomUser.Roles.STUDENT,
                "email": "student@example.com",
            },
        )
        student_user.set_password("student1234")
        student_user.save()

        student_profile, _ = StudentProfile.objects.get_or_create(
            user=student_user,
            defaults={
                "classroom": school_class,
                "roll_number": "6A-001",
                "admission_date": timezone.now().date(),
                "guardian_name": "Karim Rahman",
                "guardian_phone": "01700000000",
            },
        )

        fee_structure, _ = FeeStructure.objects.get_or_create(
            title="Term Fee",
            classroom=school_class,
            defaults={"amount": 5000, "due_date": timezone.now().date()},
        )

        FeeInvoice.objects.get_or_create(
            student=student_profile,
            fee_structure=fee_structure,
            defaults={"amount_due": fee_structure.amount, "amount_paid": 0},
        )

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write("admin/admin1234 | teacher1/teacher1234 | student1/student1234")
