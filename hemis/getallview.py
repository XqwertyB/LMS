from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from config.permissions import AllowOnlyTrustedOrigins
from shared.permissions import IsAdmin


class GetAll(APIView):
    permission_classes = [IsAdmin, ]
    def get(self, request):

        try:
            data = {}

            main_url = 'http://127.0.0.1:8000'
            """
            Otm uchun yuklangan shaharlarni yuklash
            http://api.fastlms.uz/api/otmcity/hemis/get/
            """
            url = main_url + "/api/otmcity/hemis/get/"
            reqcity = requests.get(url)
            data['reqcity'] = {
                'status_kod': reqcity.status_code,
                'content': reqcity.content
            }
            """
                Otm uchun yuklangan Otm turlari yuklash
                http://api.fastlms.uz/api/otmtype/hemis/get/
                    """
            url = main_url + "/api/otmtype/hemis/get/"
            reqotmtype = requests.get(url)
            data['reqotmtype'] = {
                'status_kod': reqotmtype.status_code,
                'content': reqotmtype.content
            }
            """
            -----------------------------------------------------------------------------------------------------------
            Otm uchun yuklangan Otm Shaki yuklash
            http://api.fastlms.uz/api/otmshape/hemis/get/
                            """
            url = main_url + "/api/otmshape/hemis/get/"
            reqotmshape = requests.get(url)
            data['reqotmshape'] = {
                'status_kod': reqotmshape.status_code,
                'content': reqotmshape.content
            }
            """
            -----------------------------------------------------------------------------------------------------------
            Otm uchun yuklangan Otmni yuklash
            http://api.fastlms.uz/api/otm/hemis/get/
                                    """
            url = main_url + "/api/otm/hemis/get/"
            reqotm = requests.get(url)
            data['reqotm'] = {
                'status_kod': reqotm.status_code,
                'content': reqotm.content
            }
            """
                -----------------------------------------------------------------------------------------------------------
                Otm uchun yuklangan Otm bo`limlar kodni yuklash
                http://api.fastlms.uz/api/otmsection/hemis/get/
                                            """
            url = main_url + "/api/otmsection/hemis/get/"
            reqotmsection = requests.get(url)
            data['reqotmsection'] = {
                'status_kod': reqotmsection.status_code,
                'content': reqotmsection.content
            }
            """
                -----------------------------------------------------------------------------------------------------------
                Otm uchun yuklangan Otm Fakultet turlari yuklash
                http://api.fastlms.uz/api/faculty_type/hemis/get/
                                                    """
            url = main_url + "/api/faculty_type/hemis/get/"
            req_faculty_type = requests.get(url)
            data['reqfacultytype'] = {
                'status_kod': req_faculty_type.status_code,
                'content': req_faculty_type.content
            }

            """
                -----------------------------------------------------------------------------------------------------------
                Otm uchun yuklangan Otm Fakultetlarni  yuklash
                http://api.fastlms.uz/api/otmfaculty/hemis/get/
                                                            """
            url = main_url + "/api/otmfaculty/hemis/get/"
            req_faculty = requests.get(url)
            data['req_faculty'] = {
                'status_kod': req_faculty.status_code,
                'content': req_faculty.content
            }
            """
                -----------------------------------------------------------------------------------------------------------
                Otm uchun yuklangan Otm Fakultetga birktrilgan kafedralar  yuklash
                http://api.fastlms.uz/api/otmdepartment/hemis/get/
                                                                    """
            url = main_url + "/api/otmdepartment/hemis/get/"
            req_faculty_department = requests.get(url)
            data['req_faculty_department'] = {
                'status_kod': req_faculty_department.status_code,
                'content': req_faculty_department.content
            }
            """
               -----------------------------------------------------------------------------------------------------------
               Otm uchun yuklangan Oquv tili
               http://api.fastlms.uz/api/science_branch/hemis/get/
                                                                                                                       """
            url = main_url + "/api/science_branch/hemis/get/"
            science_branch = requests.get(url)
            data['science_branch'] = {
                'status_kod': science_branch.status_code,
                'content': science_branch.content
            }
            """
                -----------------------------------------------------------------------------------------------------------
                Otm uchun yuklangan Yonalishlarni yuklab olish Bakalavr
                http://api.fastlms.uz/api/bspeciality/hemis/get/
                                                                            """
            url = main_url + "/api/bspeciality/hemis/get/"
            bspeciality = requests.get(url)
            data['bspeciality'] = {
                'status_kod': bspeciality.status_code,
                'content': bspeciality.content
            }
            """
               -----------------------------------------------------------------------------------------------------------
               Otm uchun yuklangan Yonalishlarni yuklab olish Magistratur
               http://api.fastlms.uz/api/mspeciality/hemis/get/
                                                                                   """
            url = main_url + "/api/mspeciality/hemis/get/"
            mspeciality = requests.get(url)
            data['mspeciality'] = {
                'status_kod': mspeciality.status_code,
                'content': mspeciality.content
            }
            """
               -----------------------------------------------------------------------------------------------------------
               Otm uchun yuklangan Yonalishlarni yuklab olish Ordenatura
               http://api.fastlms.uz/api/ospeciality/hemis/get/
                                                                                           """
            url = main_url + "/api/ospeciality/hemis/get/"
            ospeciality = requests.get(url)
            data['ospeciality'] = {
                'status_kod': ospeciality.status_code,
                'content': ospeciality.content
            }
            """
               -----------------------------------------------------------------------------------------------------------
               Otm uchun yuklangan Oquv yillar to`plami yuklash
               http://api.fastlms.uz/api/educationyear/hemis/get/
                                                                                                   """
            url = main_url + "/api/educationyear/hemis/get/"
            educationyear = requests.get(url)
            data['educationyear'] = {
                'status_kod': educationyear.status_code,
                'content': educationyear.content
            }
            """
               -----------------------------------------------------------------------------------------------------------
               Otm uchun yuklangan Oquv yil turlari to`plami yuklash
               http://api.fastlms.uz/api/educationtype/hemis/get/
                                                               """
            url = main_url + "/api/educationtype/hemis/get/"
            educationtype = requests.get(url)
            data['educationtype'] = {
                'status_kod': educationtype.status_code,
                'content': educationtype.content
            }
            """
               -----------------------------------------------------------------------------------------------------------
               Otm uchun yuklangan Oquv yil  format turlari to`plami yuklash
               http://api.fastlms.uz/api/educationform/hemis/get/
                                                                       """
            url = main_url + "/api/educationform/hemis/get/"
            educationform = requests.get(url)
            data['educationform'] = {
                'status_kod': educationform.status_code,
                'content': educationform.content
            }
            """
                       -----------------------------------------------------------------------------------------------------------
                       Otm uchun yuklangan Oquv rejani yuklash
                       http://api.fastlms.uz/api/curriculum/hemis/get/
                                                                               """
            url = main_url + "/api/curriculum/hemis/get/"
            curriculum = requests.get(url)
            data['curriculum'] = {
                'status_kod': curriculum.status_code,
                'content': curriculum.content
            }
            """
                   -----------------------------------------------------------------------------------------------------------
                   Otm uchun yuklangan Oquv reja fakultet va yonalishlarni birlashtrish
                   http://api.fastlms.uz/api/speciality/hemis/get/all/
                                                                                       """
            url = main_url + "/api/speciality/hemis/get/all/"
            connectspeciality = requests.get(url)
            data['curriculum'] = {
                'status_kod': connectspeciality.status_code,
                'content': connectspeciality.content
            }
            """
                   -----------------------------------------------------------------------------------------------------------
                   Otm uchun yuklangan Semestr kursini turlari
                   http://api.fastlms.uz/api/hcourse/hemis/get/
                                                                                               """
            url = main_url + "/api/hcourse/hemis/get/"
            hcourse = requests.get(url)
            data['hcourse'] = {
                'status_kod': hcourse.status_code,
                'content': hcourse.content
            }
            """
                           -----------------------------------------------------------------------------------------------------------
                           Otm uchun yuklangan Semestr  turlari yuklash
                           http://api.fastlms.uz/api/hsemester/hemis/get/
                                                                                                       """
            url = main_url + "/api/hsemester/hemis/get/"
            hsemester = requests.get(url)
            data['hsemester'] = {
                'status_kod': hsemester.status_code,
                'content': hsemester.content
            }
            """
               -----------------------------------------------------------------------------------------------------------
               Otm uchun yuklangan Semestrga birktrilgan haftalar harkatini yuklavolish
               http://api.fastlms.uz/api/hsemesteraction/hemis/get/
                                                                                                       """
            url = main_url + "/api/hsemesteraction/hemis/get/"
            hsemesteraction = requests.get(url)
            data['hsemesteraction'] = {
                'status_kod': hsemesteraction.status_code,
                'content': hsemesteraction.content
            }
            """
               -----------------------------------------------------------------------------------------------------------
               Otm uchun yuklangan Oquv tili
               http://api.fastlms.uz/api/educationlang/hemis/get/
                                                                                                               """
            url = main_url + "/api/educationlang/hemis/get/"
            educationlang = requests.get(url)
            data['educationlang'] = {
                'status_kod': educationlang.status_code,
                'content': educationlang.content
            }
            """
                       -----------------------------------------------------------------------------------------------------------
                       Otm uchun yuklangan guruhlarni qoshish
                       http://api.fastlms.uz/api/group/hemis/get/
                                                                                                                       """
            url = main_url + "/api/group/hemis/get/"
            group = requests.get(url)
            data['group'] = {
                'status_kod': group.status_code,
                'content': group.content
            }

            return Response(data)
        except Exception as ex:
            return Response({'error':str(ex)})
