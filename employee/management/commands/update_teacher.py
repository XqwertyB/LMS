from django.core.management.base import BaseCommand
from django.db import transaction

from employee.models import Employee
from user.models import User


class Command(BaseCommand):
    help = "User va Employee o‘rtasidagi OneToOne bog‘lanishni tiklaydi (employee_id_number == username)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🔄 Bog‘lanish jarayoni boshlandi..."))

        users = {u.username: u for u in User.objects.filter(role='teacher')}
        employees = Employee.objects.all()

        updated_employees = []

        for emp in employees:
            user = users.get(emp.employee_id_number)
            if user:
                emp.user = user
                updated_employees.append(emp)

        if not updated_employees:
            self.stdout.write(self.style.WARNING("ℹ️ Hech qanday employee yangilanishga muhtoj emas."))
            return

        with transaction.atomic():
            Employee.objects.bulk_update(updated_employees, ["user"])

        self.stdout.write(self.style.SUCCESS(
            f"✅ {len(updated_employees)} ta Employee foydalanuvchiga bog‘landi!"
        ))
