from rest_framework import serializers
from .models import APILogsModel


class APILogsSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = APILogsModel
        fields = [
            'id',
            'api',
            'headers',
            'body',
            'method',
            'client_ip_address',
            'response',
            'status_code',
            'execution_time',
            'instance_before_change',
            'user',
            'user_full_name',
            'added_on',
        ]
