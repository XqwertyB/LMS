from rest_framework.permissions import BasePermission

from employee.models import Employee
from students.models import Student


class RoleBasedPermission(BasePermission):
    """
    Bazaviy permission klass.
    Foydalanuvchi roli va tegishli model (Student/Employee/User) mavjudligini tekshiradi.
    """
    allowed_roles = set()
    check_student = False
    check_teacher = False
    check_admin = False

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        is_student = Student.objects.filter(user=user).exists() if self.check_student else False
        is_teacher = Employee.objects.filter(user=user).exists() if self.check_teacher else False
        is_admin = user.role == "admin" if self.check_admin else False

        return (is_student or is_teacher or is_admin) and user.role in self.allowed_roles


class IsStudent(RoleBasedPermission):
    allowed_roles = {'student'}
    check_student = True


class IsTeacher(RoleBasedPermission):
    allowed_roles = {'teacher'}
    check_teacher = True


class IsAdmin(RoleBasedPermission):
    allowed_roles = {'admin'}
    check_admin = True


class IsTeacherOrStudent(RoleBasedPermission):
    allowed_roles = {'teacher', 'student'}
    check_student = True
    check_teacher = True


class IsAdminOrTeacher(RoleBasedPermission):
    allowed_roles = {'admin', 'teacher'}
    check_teacher = True
    check_admin = True


class IsAdminOrStudent(RoleBasedPermission):
    allowed_roles = {'admin', 'student'}
    check_student = True
    check_admin = True


class IsAdminTeacherOrStudent(RoleBasedPermission):
    allowed_roles = {'admin', 'teacher', 'student'}
    check_student = True
    check_teacher = True
    check_admin = True
