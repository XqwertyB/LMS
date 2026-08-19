from django.utils import timezone
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from config.permissions import AllowOnlyTrustedOrigins
from hemis.models import Hemis_sub, Hemis_Base, HemisToken
from shared.permissions import IsAdmin
# h_bachelor_speciality
from .models import Bspeciality, Mspeciality, Ospeciality, Dspeciality, AllSpeciality
import datetime
from learning_process.models import Educationtype
from universty.models import Faculty_type, Faculty
from django.db.models import Q


class GetBspeciality(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except Hemis_Base.DoesNotExist:
            return Response({'error': 'Hemis modulida birktrilmagan'})

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
            if not token:
                return Response({'error': 'Faol token mavjud emas!'})
        except Exception as e:
            return Response({'error': str(e)})

        if not hemis.openapi:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
            }
            params = {'classifier': 'h_bachelor_speciality', 'page': '1', 'limit': '200'}
            start_time = datetime.datetime.now()
            respon = requests.get(hemis.base_url + hemis.path_url, headers=headers, params=params)

            try:
                data = respon.json()['data']['items'][0]['options']
            except (KeyError, IndexError):
                return Response({'error': 'API dan noto‘g‘ri javob keldi'})

            added_count = 0
            updated_count = 0

            for i in data:
                obj = Bspeciality.objects.filter(base_spec_id=i['id'])
                #obj = Bspeciality.objects.filter(code=i['code'],name=i['name'])
                if not obj.exists():
                    Bspeciality.objects.create(
                        base_spec_id=i['id'],
                        code=i['code'],
                        name=i['name']
                    )
                    added_count += 1
            else:
                #updated_objs = obj.first.update(base_spec_id=i['id'],updated_at=timezone.now())
                updated_objs = obj.update(name=i['name'], code=i['code'], updated_at=timezone.now())
                updated_count += updated_objs

            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()

            return Response({
                'success': 'Baza qo‘shildi va yangilandi!',
                'added': added_count,
                'updated': updated_count,
                'time': elapsed_time
            })

        else:
            return Response({'error': 'Tokensiz murojaat qilib bo‘lmidi'})


class GetMspeciality(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except Hemis_Base.DoesNotExist:
            return Response({'error': 'Hemis modulida birktrilmagan'})

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
            if not token:
                return Response({'error': 'Faol token mavjud emas!'})
        except Exception as e:
            return Response({'error': str(e)})

        if not hemis.openapi:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
            }
            params = {'classifier': 'h_master_speciality', 'page': '1', 'limit': '200'}
            start_time = datetime.datetime.now()
            respon = requests.get(hemis.base_url + hemis.path_url, headers=headers, params=params)

            try:
                data = respon.json()['data']['items'][0]['options']
            except (KeyError, IndexError):
                return Response({'error': 'API dan noto‘g‘ri javob keldi'})

            added_count = 0
            updated_count = 0

            for i in data:
                obj = Mspeciality.objects.filter(base_spec_id=i['id'])
                if not obj.exists():
                    Mspeciality.objects.create(
                        base_spec_id=i['id'],
                        code=i['code'],
                        name=i['name']
                    )
                    added_count += 1
                else:
                    updated_objs = obj.update(name=i['name'], code=i['code'], updated_at=timezone.now())
                    updated_count += updated_objs

            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()

            return Response({
                'success': 'Baza qo‘shildi va yangilandi!',
                'added': added_count,
                'updated': updated_count,
                'time': elapsed_time
            })
        else:
            return Response({'error': 'Tokensiz murojaat qilib bo‘lmidi'})


class GetOspeciality(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except Hemis_Base.DoesNotExist:
            return Response({'error': 'Hemis modulida birktrilmagan'})

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
            if not token:
                return Response({'error': 'Faol token mavjud emas!'})
        except Exception as e:
            return Response({'error': str(e)})

        if not hemis.openapi:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
            }
            params = {'classifier': 'h_speciality_ordinatura', 'page': '1', 'limit': '200'}
            start_time = datetime.datetime.now()
            respon = requests.get(hemis.base_url + hemis.path_url, headers=headers, params=params)

            try:
                data = respon.json()['data']['items'][0]['options']
            except (KeyError, IndexError):
                return Response({'error': 'API dan noto‘g‘ri javob keldi'})

            added_count = 0
            updated_count = 0

            for i in data:
                obj = Ospeciality.objects.filter(base_spec_id=i['id'])
                if not obj.exists():
                    Ospeciality.objects.create(
                        base_spec_id=i['id'],
                        code=i['code'],
                        name=i['name']
                    )
                    added_count += 1
                else:
                    updated_objs = obj.update(name=i['name'], code=i['code'], updated_at=timezone.now())
                    updated_count += updated_objs

            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()

            return Response({
                'success': 'Baza qo‘shildi va yangilandi!',
                'added': added_count,
                'updated': updated_count,
                'time': elapsed_time
            })
        else:
            return Response({'error': 'Tokensiz murojaat qilib bo‘lmidi'})



class GetDspeciality(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except Hemis_Base.DoesNotExist:
            return Response({'error': 'Hemis modulida birktrilmagan'})

        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
            if not token:
                return Response({'error': 'Faol token mavjud emas!'})
        except Exception as e:
            return Response({'error': str(e)})

        if not hemis.openapi:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
            }
            params = {'classifier': 'h_science_branch', 'page': '1', 'limit': '200'}
            start_time = datetime.datetime.now()
            respon = requests.get(hemis.base_url + hemis.path_url, headers=headers, params=params)

            try:
                data = respon.json()['data']['items'][0]['options']
            except (KeyError, IndexError):
                return Response({'error': 'API dan noto‘g‘ri javob keldi'})

            added_count = 0
            updated_count = 0

            for i in data:
                obj = Dspeciality.objects.filter(base_spec_id=i['id'])
                if not obj.exists():
                    Dspeciality.objects.create(
                        base_spec_id=i['id'],
                        code=i['code'],
                        name=i['name']
                    )
                    added_count += 1
                else:
                    updated_objs = obj.update(name=i['name'], code=i['code'], updated_at=timezone.now())
                    updated_count += updated_objs

            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()

            return Response({
                'success': 'Baza qo‘shildi va yangilandi!',
                'added': added_count,
                'updated': updated_count,
                'time': elapsed_time
            })
        else:
            return Response({'error': 'Tokensiz murojaat qilib bo‘lmidi'})


class AllGetspeciality(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=12)
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
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()
            start_time = datetime.datetime.now()
            page = data['data']['pagination']['page']
            pagecount = data['data']['pagination']['pageCount'] + 1

            departmentx = Faculty.objects.filter(status_action=True)

            for depitem in departmentx:
                for i in range(int(page), int(pagecount), 1):
                    params = {
                        'page': str(i),
                        'limit': '200',
                        '_department': depitem.hemisid
                    }
                    prespon = requests.get(baseurl + pathurl, headers=headers, params=params)
                    rdata = prespon.json()['data']['items']
                    for item in rdata:
                        try:
                            old = AllSpeciality.objects.get(spec_id=item['id'])
                            old.code = item['code']
                            old.name = item['name']
                            locality_type = Faculty_type.objects.filter(code=item['localityType']['code']).exists()
                            if not locality_type:
                                return Response({'error': 'Hemisdan locality type biriktrilmagan!'})
                            locality_type = Faculty_type.objects.get(code=item['localityType']['code'])
                            educationType = Educationtype.objects.filter(code=item['educationType']['code']).exists()
                            if not educationType:
                                return Response({'error': 'Hemisdan educationType biriktrilmagan!'})
                            educationType = Educationtype.objects.get(code=str(item['educationType']['code']))
                            old.locality_type = locality_type
                            old.educationType = educationType
                            department_check = item['department']
                            if department_check is not None:
                                department = Faculty.objects.filter(hemisid=item['department']['id']).exists()
                                if not department:
                                    return Response({'error': 'Hemisdan department  biriktrilmagan!'})
                                department = Faculty.objects.get(hemisid=item['department']['id'])
                            else:
                                department = None
                            bachelorSpecialty_check = item['bachelorSpecialty']
                            if bachelorSpecialty_check is not None:
                                bachelorSpecialty = Bspeciality.objects.filter(
                                    base_spec_id=item['bachelorSpecialty']['id']).exists()
                                if not bachelorSpecialty:
                                    return Response({'error': 'Hemisdan bachelorSpecialty  biriktrilmagan!'})
                                bachelorSpecialty = Bspeciality.objects.get(base_spec_id=item['bachelorSpecialty']['id'])
                            else:
                                bachelorSpecialty = None
                            masterSpecialty_check = item['masterSpecialty']
                            if masterSpecialty_check is not None:
                                masterSpecialty = Mspeciality.objects.filter(
                                    base_spec_id=item['masterSpecialty']['id']).exists()
                                if not masterSpecialty:
                                    return Response({'error': 'Hemisdan masterSpecialty  biriktrilmagan!'})
                                masterSpecialty = Mspeciality.objects.get(base_spec_id=item['masterSpecialty']['id'])
                            else:
                                masterSpecialty = None
                            ordinatureSpecialty_check = item['ordinatureSpecialty']
                            if ordinatureSpecialty_check is not None:
                                ordinatureSpecialty = Ospeciality.objects.filter(
                                    base_spec_id=item['ordinatureSpecialty']['id']).exists()
                                if not ordinatureSpecialty:
                                    return Response({'error': 'Hemisdan ordinatureSpecialty  biriktrilmagan!'})
                                ordinatureSpecialty = Ospeciality.objects.get(base_spec_id=item['ordinatureSpecialty']['id'])
                            else:
                                ordinatureSpecialty = None
                            doctorateSpecialty_check = item['doctorateSpecialty']
                            if doctorateSpecialty_check is not None:
                                doctorateSpecialty = Dspeciality.objects.filter(
                                    base_spec_id=item['doctorateSpecialty']['id']).exists()
                                if not doctorateSpecialty:
                                    return Response({'error': 'Hemisdan doctorateSpecialty  biriktrilmagan!'})
                                doctorateSpecialty = Dspeciality.objects.get(base_spec_id=item['doctorateSpecialty']['id'])
                            else:
                                doctorateSpecialty = None
                            old.department = department
                            old.bachelorSpecialty = bachelorSpecialty
                            old.masterSpecialty = masterSpecialty
                            old.ordinatureSpecialty = ordinatureSpecialty
                            old.doctorateSpecialty = doctorateSpecialty
                            old.save()
                        except AllSpeciality.DoesNotExist as ex:
                            new = AllSpeciality()
                            new.spec_id = item['id']
                            new.code = item['code']
                            new.name = item['name']
                            locality_type = Faculty_type.objects.filter(code=item['localityType']['code']).exists()
                            if not locality_type:
                                return Response({'error': 'Hemisdan locality type biriktrilmagan!'})
                            locality_type = Faculty_type.objects.get(code=item['localityType']['code'])
                            educationType = Educationtype.objects.filter(Q(code=item['educationType']['code'])).exists()
                            # print(educationType)
                            # print(item['educationType']['code'])
                            if not educationType:
                                return Response({'error': 'Hemisdan educationType biriktrilmagan!'})
                            educationType = Educationtype.objects.get(code=item['educationType']['code'])
                            new.locality_type = locality_type
                            new.educationType = educationType
                            department_check = item['department']
                            if department_check is not None:
                                # print(department_check)
                                department = Faculty.objects.filter(hemisid=item['department']['id']).exists()
                                if not department:
                                    return Response({'error': 'Hemisdan department  biriktrilmagan!'})
                                department = Faculty.objects.get(hemisid=item['department']['id'])
                            else:
                                department = None
                            bachelorSpecialty_check = item['bachelorSpecialty']

                            if bachelorSpecialty_check is not None:
                                bachelorSpecialty = Bspeciality.objects.filter(
                                    base_spec_id=item['bachelorSpecialty']['id']).exists()
                                if not bachelorSpecialty:
                                    return Response({'error': 'Hemisdan bachelorSpecialty  biriktrilmagan!'})
                                bachelorSpecialty = Bspeciality.objects.get(base_spec_id=item['bachelorSpecialty']['id'])
                            else:
                                bachelorSpecialty = None
                            masterSpecialty_check = item['masterSpecialty']
                            if masterSpecialty_check is not None:
                                masterSpecialty = Mspeciality.objects.filter(
                                    base_spec_id=item['masterSpecialty']['id']).exists()
                                if not masterSpecialty:
                                    return Response({'error': 'Hemisdan masterSpecialty  biriktrilmagan!'})
                                masterSpecialty = Mspeciality.objects.get(base_spec_id=item['masterSpecialty']['id'])
                            else:
                                masterSpecialty = None
                            ordinatureSpecialty_check = item['ordinatureSpecialty']
                            if ordinatureSpecialty_check is not None:
                                ordinatureSpecialty = Ospeciality.objects.filter(
                                    base_spec_id=item['ordinatureSpecialty']['id']).exists()
                                if not ordinatureSpecialty:
                                    return Response({'error': 'Hemisdan ordinatureSpecialty  biriktrilmagan!'})
                                ordinatureSpecialty = Ospeciality.objects.get(base_spec_id=item['ordinatureSpecialty']['id'])
                            else:
                                ordinatureSpecialty = None
                            doctorateSpecialty_check = item['doctorateSpecialty']
                            if doctorateSpecialty_check is not None:
                                doctorateSpecialty = Dspeciality.objects.filter(
                                    base_spec_id=item['doctorateSpecialty']['id']).exists()
                                if not doctorateSpecialty:
                                    return Response({'error': 'Hemisdan doctorateSpecialty  biriktrilmagan!'})
                                doctorateSpecialty = Dspeciality.objects.get(base_spec_id=item['doctorateSpecialty']['id'])
                            else:
                                doctorateSpecialty = None
                            new.department = department
                            new.bachelorSpecialty = bachelorSpecialty
                            new.masterSpecialty = masterSpecialty
                            new.ordinatureSpecialty = ordinatureSpecialty
                            new.doctorateSpecialty = doctorateSpecialty
                            new.save()

            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})
