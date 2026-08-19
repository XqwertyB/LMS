from datetime import datetime

from rest_framework import serializers

from shared.serializers import EmployeeStatusSerializer
from students.serializers import S_GenderSerializer
from universty.serializers import DepartmentSerializer
from .models import Employee


class TeacherSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    gender = S_GenderSerializer()
    e_status = EmployeeStatusSerializer()
    birth_date = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'user', 'department', 'e_status', 'gender', 'employee_id_number',
                  'role', 'first_name', 'second_name', 'full_name', 'father_name', 'birth_date']

    def get_birth_date(self, obj):
        try:
            timestamp = int(obj.birth_date)
            date = datetime.fromtimestamp(timestamp)
            return date.strftime('%Y-%m-%d')
        except (ValueError, OSError, TypeError):
            return None


class UserSerializer(serializers.Serializer):
    access_token = serializers.CharField()
