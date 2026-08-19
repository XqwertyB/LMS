from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from config.permissions import AllowOnlyTrustedOrigins
from hemis.models import Hemis_sub, Hemis_Base, HemisToken
from shared.permissions import IsAdmin
# h_bachelor_speciality
from .models import Roletype

import datetime


class GetRoletype(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'})
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_training_type',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = Roletype.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = Roletype()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Roletype.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})
