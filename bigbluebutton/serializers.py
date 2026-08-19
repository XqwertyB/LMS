from rest_framework import serializers
from .models import Bigbluebutton_sub, Bigbluebutton_Model, BigbluebuttonMain
import re
from rest_framework.exceptions import ValidationError


class BigbluebuttonMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = BigbluebuttonMain
        fields = '__all__'


class Bigbluebutton_subSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bigbluebutton_sub
        fields = '__all__'


class Bigbluebutton_ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bigbluebutton_Model
        fields = '__all__'


class Bigbluebutton_ModelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bigbluebutton_Model
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('maxParticipants'):
            data = {'maxParticipants': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs

    def create(self, validated_data):
        # Generate a random password
        my_model = Bigbluebutton_Model(**validated_data)
        my_model.add_random_field()
        my_model.save()

        # Return the user object with the random password
        return my_model
