import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from config.permissions import AllowOnlyTrustedOrigins
from hemis.models import Hemis_sub, Hemis_Base, HemisToken
from shared.permissions import IsAdmin
from universty.models import Otm, Otmtype, Otmshape, City, OtmSection, Faculty_type, Faculty, Department
from .serializers import OtmSerializer


class GetCheckUniversity(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=1)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'}, status=status.HTTP_400_BAD_REQUEST)

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        if checkapi:
            try:
                respon = requests.get(baseurl + pathurl, timeout=30)
                respon.raise_for_status()
                data = respon.json()
            except requests.exceptions.Timeout:
                return Response({'error': 'HEMIS API javob bermadi (timeout).'},
                                status=status.HTTP_504_GATEWAY_TIMEOUT)
            except requests.exceptions.RequestException as ex:
                return Response({'error': 'HEMIS API bilan ulanishda xatolik', 'message': str(ex)},
                                status=status.HTTP_502_BAD_GATEWAY)
            except ValueError:
                return Response({'error': 'HEMIS API noto`g`ri javob qaytardi (JSON emas).'},
                                status=status.HTTP_502_BAD_GATEWAY)

            if 'data' in data:
                data = data['data']
            if not isinstance(data, dict) or 'code' not in data:
                return Response({'error': 'HEMIS javobida kutilgan maydonlar yo`q.'},
                                status=status.HTTP_502_BAD_GATEWAY)
            kod = data['code']
            if Otm.objects.filter(kod=kod).exists():
                obj = Otm.objects.get(kod=kod)
                sdate = OtmSerializer(obj, many=False)
                return Response({'succes': True, 'data': sdate.data})
            else:
                # Otm turi bazada tekshrish
                otmtype = None
                try:
                    if Otmtype.objects.filter(code=data['ownership']['code']).exists():
                        otmtype = Otmtype.objects.get(code=data['ownership']['code'])
                    else:
                        return Response({'error': False, 'data': 'Otm turi bazadan topilmadi'},
                                        status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({'error': False, 'data': 'Tizim hatolik mavjud'},
                                    status=status.HTTP_400_BAD_REQUEST)
                otmshape = None
                try:
                    if Otmshape.objects.filter(code=data['universityForm']['code']).exists():
                        otmshape = Otmshape.objects.get(code=data['universityForm']['code'])
                    else:
                        return Response({'error': False, 'data': 'Otm Shakli bazadan topilmadi'},
                                        status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({'error': False, 'data': 'Tizim hatolik mavjud'},
                                    status=status.HTTP_400_BAD_REQUEST)
                cityhemis = None
                try:
                    if City.objects.filter(code=data['soato']['code']).exists():
                        cityhemis = City.objects.get(code=data['soato']['code'])
                    else:
                        return Response({'error': False, 'data': 'Otm Shakli bazadan topilmadi'})
                except:
                    return Response({'error': False, 'data': 'Tizim hatolik mavjud'},
                                    status=status.HTTP_400_BAD_REQUEST)

                try:
                    mobj = Otm()
                    mobj.kod = data['code']
                    mobj.name = data['name']
                    mobj.area_located = data['address']
                    mobj.phone = data['contact']
                    mobj.stir = data['tin']
                    mobj.address = data['mailing_address']
                    mobj.bank_info = data['bank_details']
                    mobj.ownership = otmtype
                    mobj.universityForm = otmshape
                    mobj.city = cityhemis
                    mobj.save()
                    sdate = OtmSerializer(mobj, many=False)
                    return Response({'success': 'Hemisdan olindi va bazaga yuklandi.', 'data': sdate.data},
                                    status=status.HTTP_200_OK)
                except Exception as ex:
                    return Response({'error': 'Bazaga yuklanishda hatolik bor.','sad':str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Tokensiz murojaat qilish imkoni mavjud!'}, status=status.HTTP_400_BAD_REQUEST)


class GetOtmtype(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]# Otm turini Hemisdan yangiliash
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'}, status=status.HTTP_400_BAD_REQUEST)
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'}, status=status.HTTP_400_BAD_REQUEST)

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_ownership',
                'page': '1',
                'limit': '200',
            }
            try:
                respon = requests.get(baseurl + pathurl, headers=headers, params=params, timeout=30)
                respon.raise_for_status()
                payload = respon.json()
            except requests.exceptions.Timeout:
                return Response({'error': 'HEMIS API javob bermadi (timeout).'},
                                status=status.HTTP_504_GATEWAY_TIMEOUT)
            except requests.exceptions.RequestException as ex:
                return Response({'error': 'HEMIS API bilan ulanishda xatolik', 'message': str(ex)},
                                status=status.HTTP_502_BAD_GATEWAY)
            except ValueError:
                return Response({'error': 'HEMIS API noto`g`ri javob qaytardi (JSON emas).'},
                                status=status.HTTP_502_BAD_GATEWAY)
            try:
                data = payload['data']['items'][0]['options']
            except (KeyError, IndexError, TypeError):
                return Response({'error': 'HEMIS javobida kutilgan maydonlar yo`q.'},
                                status=status.HTTP_502_BAD_GATEWAY)
            for i in data:
                obj = Otmtype.objects.filter(code=i['code']).exists()
                if not obj:
                    new_obj = Otmtype()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Otmtype.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
        return Response({'succes': 'Baza qo`shildi va yangilandi!'}, status=status.HTTP_200_OK)


class GetOtmshape(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]# Otm shakli Hemisdan yangiliash
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'}, status=status.HTTP_400_BAD_REQUEST)
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'}, status=status.HTTP_400_BAD_REQUEST)

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_university_form',
                'page': '1',
                'limit': '200',
            }
            try:
                respon = requests.get(baseurl + pathurl, headers=headers, params=params, timeout=30)
                respon.raise_for_status()
                payload = respon.json()
            except requests.exceptions.Timeout:
                return Response({'error': 'HEMIS API javob bermadi (timeout).'},
                                status=status.HTTP_504_GATEWAY_TIMEOUT)
            except requests.exceptions.RequestException as ex:
                return Response({'error': 'HEMIS API bilan ulanishda xatolik', 'message': str(ex)},
                                status=status.HTTP_502_BAD_GATEWAY)
            except ValueError:
                return Response({'error': 'HEMIS API noto`g`ri javob qaytardi (JSON emas).'},
                                status=status.HTTP_502_BAD_GATEWAY)
            try:
                data = payload['data']['items'][0]['options']
            except (KeyError, IndexError, TypeError):
                return Response({'error': 'HEMIS javobida kutilgan maydonlar yo`q.'},
                                status=status.HTTP_502_BAD_GATEWAY)
            for i in data:
                obj = Otmshape.objects.filter(code=i['code']).exists()
                if not obj:
                    new_obj = Otmshape()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Otmshape.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
        return Response({'succes': 'Baza qo`shildi va yangilandi!'}, status=status.HTTP_200_OK)


class GetCity(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]# Otm uchun shahar Hemisdan yangiliash
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'}, status=status.HTTP_400_BAD_REQUEST)
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'}, status=status.HTTP_400_BAD_REQUEST)

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_soato',
                'page': '1',
                'limit': '200',
            }
            try:
                respon = requests.get(baseurl + pathurl, headers=headers, params=params, timeout=30)
                respon.raise_for_status()
                payload = respon.json()
            except requests.exceptions.Timeout:
                return Response({'error': 'HEMIS API javob bermadi (timeout).'},
                                status=status.HTTP_504_GATEWAY_TIMEOUT)
            except requests.exceptions.RequestException as ex:
                return Response({'error': 'HEMIS API bilan ulanishda xatolik', 'message': str(ex)},
                                status=status.HTTP_502_BAD_GATEWAY)
            except ValueError:
                return Response({'error': 'HEMIS API noto`g`ri javob qaytardi (JSON emas).'},
                                status=status.HTTP_502_BAD_GATEWAY)
            try:
                data = payload['data']['items'][0]['options']
            except (KeyError, IndexError, TypeError):
                return Response({'error': 'HEMIS javobida kutilgan maydonlar yo`q.'},
                                status=status.HTTP_502_BAD_GATEWAY)
            for i in data:
                obj = City.objects.filter(code=i['code']).exists()
                if not obj:
                    new_obj = City()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.parent = i['_parent']
                    new_obj.save()
                else:
                    update_obj = City.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.parent = i['_parent']
                    update_obj.save()
        return Response({'succes': 'Baza qo`shildi va yangilandi!'}, status=status.HTTP_200_OK)


class GetOtmSection(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]# Otm bolimlar Hemisdan yangiliash
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'}, status=status.HTTP_400_BAD_REQUEST)
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'}, status=status.HTTP_400_BAD_REQUEST)

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_structure_type',
                'page': '1',
                'limit': '200',
            }
            try:
                respon = requests.get(baseurl + pathurl, headers=headers, params=params, timeout=30)
                respon.raise_for_status()
                payload = respon.json()
            except requests.exceptions.Timeout:
                return Response({'error': 'HEMIS API javob bermadi (timeout).'},
                                status=status.HTTP_504_GATEWAY_TIMEOUT)
            except requests.exceptions.RequestException as ex:
                return Response({'error': 'HEMIS API bilan ulanishda xatolik', 'message': str(ex)},
                                status=status.HTTP_502_BAD_GATEWAY)
            except ValueError:
                return Response({'error': 'HEMIS API noto`g`ri javob qaytardi (JSON emas).'},
                                status=status.HTTP_502_BAD_GATEWAY)
            try:
                data = payload['data']['items'][0]['options']
            except (KeyError, IndexError, TypeError):
                return Response({'error': 'HEMIS javobida kutilgan maydonlar yo`q.'},
                                status=status.HTTP_502_BAD_GATEWAY)
            for i in data:
                obj = OtmSection.objects.filter(code=i['code']).exists()
                if not obj:
                    new_obj = OtmSection()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = OtmSection.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
        return Response({'succes': 'Baza qo`shildi va yangilandi!'}, status=status.HTTP_200_OK)


class GetOtmFacultytype(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]# Otm bolimlar Hemisdan yangiliash
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=2)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'}, status=status.HTTP_400_BAD_REQUEST)
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'}, status=status.HTTP_400_BAD_REQUEST)

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                'classifier': 'h_locality_type',
                'page': '1',
                'limit': '200',
            }
            try:
                respon = requests.get(baseurl + pathurl, headers=headers, params=params, timeout=30)
                respon.raise_for_status()
                payload = respon.json()
            except requests.exceptions.Timeout:
                return Response({'error': 'HEMIS API javob bermadi (timeout).'},
                                status=status.HTTP_504_GATEWAY_TIMEOUT)
            except requests.exceptions.RequestException as ex:
                return Response({'error': 'HEMIS API bilan ulanishda xatolik', 'message': str(ex)},
                                status=status.HTTP_502_BAD_GATEWAY)
            except ValueError:
                return Response({'error': 'HEMIS API noto`g`ri javob qaytardi (JSON emas).'},
                                status=status.HTTP_502_BAD_GATEWAY)
            try:
                data = payload['data']['items'][0]['options']
            except (KeyError, IndexError, TypeError):
                return Response({'error': 'HEMIS javobida kutilgan maydonlar yo`q.'},
                                status=status.HTTP_502_BAD_GATEWAY)
            for i in data:
                obj = Faculty_type.objects.filter(code=i['code']).exists()
                if not obj:
                    new_obj = Faculty_type()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Faculty_type.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
        return Response({'succes': 'Baza qo`shildi va yangilandi!'}, status=status.HTTP_200_OK)


class GetOtmFaculty(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin]

    def get(self, request, format=None):

        try:
            hemis = Hemis_Base.objects.get(own_uniq=3)
        except Hemis_Base.DoesNotExist:
            return Response(
                {'error': 'Hemis modulida biriktirilmagan'},
                status=status.HTTP_400_BAD_REQUEST
            )

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi

        try:
            token = HemisToken.objects.filter(
                status=True,
                hemis_user=hemis.hemis_user
            ).first()

            if not token:
                return Response(
                    {'error': 'Faol token mavjud emas!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception:
            return Response(
                {'error': 'Token olishda xatolik!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if checkapi:
            return Response(
                {'error': 'Tokensiz murojaat qilib bo‘lmaydi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
        }

        params = {
            '_structure_type': '11',
            'active': 'all',
            'page': '1',
            'limit': '200',
        }

        try:
            respon = requests.get(baseurl + pathurl, headers=headers, params=params, timeout=30)
            respon.raise_for_status()
            payload = respon.json()
        except requests.exceptions.Timeout:
            return Response({'error': 'HEMIS API javob bermadi (timeout).'},
                            status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.RequestException as e:
            return Response({'error': 'HEMIS API bilan ulanishda xatolik', 'message': str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)
        except ValueError:
            return Response({'error': 'HEMIS API noto`g`ri javob qaytardi (JSON emas).'},
                            status=status.HTTP_502_BAD_GATEWAY)
        try:
            data = payload['data']['items']
        except (KeyError, TypeError):
            return Response({'error': 'HEMIS javobida kutilgan maydonlar yo`q.'},
                            status=status.HTTP_502_BAD_GATEWAY)

        created = 0
        updated = 0

        for i in data:

            try:
                ftype = Faculty_type.objects.get(code=i['localityType']['code'])
            except Faculty_type.DoesNotExist:
                return Response(
                    {'error': 'Fakultet turi mavjud emas !'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            obj, created_flag = Faculty.objects.update_or_create(
                hemisid=i['id'],
                defaults={
                    "name": i['name'],
                    "kod": i['code'],
                    "faculty_type": ftype
                }
            )

            if created_flag:
                created += 1
            else:
                updated += 1

        return Response(
            {
                'success': 'Baza yangilandi',
                'created': created,
                'updated': updated
            },
            status=status.HTTP_200_OK
        )


class GetOtmDepartment(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]# Otm Kafedra Hemisdan yangiliash
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=3)
        except:
            return Response({'error': 'Hemis modulida birktrilmagan'}, status=status.HTTP_400_BAD_REQUEST)
        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user)[0]
        except:
            return Response({'error': 'Faol token mavjud emas!'}, status=status.HTTP_400_BAD_REQUEST)

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.hemis_token_type + ' ' + token.hemis_token
            }
            params = {
                '_structure_type': '12',
                'active':'all',
                'page': '1',
                'limit': '200',
            }
            try:
                respon = requests.get(baseurl + pathurl, headers=headers, params=params, timeout=30)
                respon.raise_for_status()
                payload = respon.json()
            except requests.exceptions.Timeout:
                return Response({'error': 'HEMIS API javob bermadi (timeout).'},
                                status=status.HTTP_504_GATEWAY_TIMEOUT)
            except requests.exceptions.RequestException as ex:
                return Response({'error': 'HEMIS API bilan ulanishda xatolik', 'message': str(ex)},
                                status=status.HTTP_502_BAD_GATEWAY)
            except ValueError:
                return Response({'error': 'HEMIS API noto`g`ri javob qaytardi (JSON emas).'},
                                status=status.HTTP_502_BAD_GATEWAY)
            try:
                data = payload['data']['items']
            except (KeyError, TypeError):
                return Response({'error': 'HEMIS javobida kutilgan maydonlar yo`q.'},
                                status=status.HTTP_502_BAD_GATEWAY)
            for i in data:
                if Faculty_type.objects.filter(code=i['localityType']['code']).exists():
                    try:
                        ftype = Faculty_type.objects.get(code=i['localityType']['code'])
                        if Faculty.objects.filter(hemisid=i['parent']).exists():
                            if not Department.objects.filter(hemisid=i['id']).exists():
                                try:
                                    fakul = Faculty.objects.get(hemisid=i['parent'])
                                    obj = Department()
                                    obj.hemisid = i['id']
                                    obj.name = i['name']
                                    obj.kod = i['code']
                                    obj.faculty = fakul
                                    obj.save()
                                except Exception as ex :
                                    # print("1:", str(ex))
                                    return Response({'error': 'Kafedra saqlashda muammo bor !'},
                                                    status=status.HTTP_400_BAD_REQUEST)
                            else:
                                try:
                                    fakul = Faculty.objects.get(hemisid=i['parent'])
                                    obj = Department.objects.get(hemisid=i['id'])
                                    obj.name = i['name']
                                    obj.kod = i['code']
                                    obj.faculty = fakul
                                    obj.save()
                                except Exception as ex:
                                    #print(str(ex))
                                    return Response({'error': 'Kafedra yangilashda muammo bor !'},
                                                    status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({'error': 'Kafidra yangilashdan oldin Fakultet olish kere hemisdan !'},
                                            status=status.HTTP_400_BAD_REQUEST)
                    except Exception as ex:
                        print(str(ex))
                        return Response({'error': 'Kafedra saqlashda muamo bor !'}, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({'error': 'Kafedra turi mavjud emas !'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'succes': 'Baza qo`shildi va yangilandi!'}, status=status.HTTP_200_OK)
