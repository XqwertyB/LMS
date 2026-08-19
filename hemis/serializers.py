import re

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError


from .models import HemisModel,HemisToken,Hemis_Base


class HemisTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = HemisToken
        fields = '__all__'


class HemisModelSerializer(serializers.ModelSerializer):
    hemis_tokens = HemisTokenSerializer(many=True)

    class Meta:
        model = HemisModel
        fields = '__all__'


class HemisBModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = HemisModel
        fields = '__all__'


class HemisBaseSerializer(serializers.ModelSerializer):
    hemis_base = HemisBModelSerializer(many=False)

    class Meta:
        model = Hemis_Base
        fields = '__all__'