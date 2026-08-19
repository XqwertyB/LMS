from django.db import transaction
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from config.permissions import AllowOnlyTrustedOrigins
from hemis.models import Hemis_sub, Hemis_Base, HemisToken
from shared.permissions import IsAdmin
# h_bachelor_speciality
from .models import Subject, Subjectgroup, Subject_block, Subject_type, Subject_exam_finish, Subject_Curriculum, \
    RatingGrade, SubjectDetails, SubjectExamTypes
from learning_process.models import Educationtype, Curriculum
from semestr.models import Hsemester, Hsemester_action
import datetime
from universty.models import Department, Faculty
from shared.models import ExamTypes, TrainingType
from collections import Counter

import logging



logger = logging.getLogger(__name__)


class GetSubject(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=10)
        except Hemis_Base.DoesNotExist:
            return Response({'error': 'Hemis modulida birktrilmagan'})

        baseurl = hemis.base_url
        pathurl = hemis.path_url
        checkapi = hemis.openapi
        try:
            token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        except HemisToken.DoesNotExist:
            return Response({'error': 'Faol token mavjud emas!'})

        if checkapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'})
        else:
            start_time = datetime.datetime.now()

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
            }
            params = {
                'page': '1',
                'limit': '100',
            }
            print(baseurl + pathurl)
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()
            page = data['data']['pagination']['page']
            pagecount = data['data']['pagination']['pageCount'] + 1

            for i in range(page, pagecount):
                params['page'] = str(i)
                prespon = requests.get(baseurl + pathurl, headers=headers, params=params)
                rdata = prespon.json()['data']['items']

                for obj in rdata:
                    check = Subject.objects.filter(hemis_id=obj['id']).exists()

                    if check:
                        subject = Subject.objects.get(hemis_id=obj['id'])
                    else:
                        subject = Subject()
                        subject.hemis_id = obj['id']

                    subjectgroup, created = Subjectgroup.objects.get_or_create(
                        code=obj['subjectGroup']['code'],
                        defaults={'name': obj['subjectGroup']['name']}
                    )

                    educationtype, created = Educationtype.objects.get_or_create(
                        code=obj['educationType']['code'],
                        defaults={'name': obj['educationType']['name']}
                    )

                    subject.code = obj['code']
                    subject.name = obj['name']
                    subject.subjectgroup = subjectgroup
                    subject.sub_educationtype = educationtype
                    subject.save()

            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time

        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetSubjectblock(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
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
                'classifier': 'h_subject_block',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = Subject_block.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = Subject_block()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Subject_block.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetSubjecttype(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
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
                'classifier': 'h_subject_type',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = Subject_type.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = Subject_type()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Subject_type.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class GetSubject_exam_finish(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
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
                'classifier': 'h_exam_finish',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items'][0]['options']
            start_time = datetime.datetime.now()
            for i in data:
                obj = Subject_exam_finish.objects.filter(code__iexact=i['code']).exists()
                if not obj:
                    new_obj = Subject_exam_finish()
                    new_obj.code = i['code']
                    new_obj.name = i['name']
                    new_obj.save()
                else:
                    update_obj = Subject_exam_finish.objects.get(code=i['code'])
                    update_obj.name = i['name']
                    update_obj.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})


class Getsubject_list(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request, format=None):
        try:
            hemis = Hemis_Base.objects.get(own_uniq=11)
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
                'classifier': 'h_exam_finish',
                'page': '1',
                'limit': '200',
            }
            respon = requests.get(baseurl + pathurl, headers=headers, params=params)
            data = respon.json()['data']['items']
            start_time = datetime.datetime.now()
            curricm = Curriculum.objects.all()
            for j in curricm:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': token.hemis_token_type + ' ' + token.hemis_token
                }
                params = {
                    'page': '1',
                    'limit': '100',
                    '_curriculum': j.cur_id
                }
                respon = requests.get(baseurl + pathurl, headers=headers, params=params)
                data = respon.json()
                page = data['data']['pagination']['page']
                pagecount = data['data']['pagination']['pageCount'] + 1
                for i in range(int(page), int(pagecount), 1):
                    # print(i)
                    params = {
                        'page': str(i),
                        'limit': '100',
                        '_curriculum': j.cur_id
                    }
                    prespon = requests.get(baseurl + pathurl, headers=headers, params=params)
                    rdata = prespon.json()['data']['items']
                    # print(rdata)
                    for rx in rdata:
                        check = Subject_Curriculum.objects.filter(hemis_id=rx['id']).exists()
                        if check:
                            print(rx['subject'])
                            semests_status = Hsemester_action.objects.filter(semester__code=rx['semester']['code'],
                                                                             curriculum__cur_id=j.cur_id).exists()
                            if semests_status:
                                semester_active = Hsemester_action.objects.get(semester__code=rx['semester']['code'],
                                                                               curriculum__cur_id=j.cur_id)
                                semester_is = Hsemester.objects.filter(code=rx['semester']['code']).exists()
                                if semester_is:
                                    semester = Hsemester.objects.get(code=rx['semester']['code'])
                                else:
                                    return Response({'error': 'Semester hemis bazadan biriktrilmagan!'})
                                # qoshiladi
                                obj = Subject_Curriculum.objects.get(hemis_id=rx['id'])
                                subject_is = Subject.objects.filter(hemis_id=rx['subject']['id']).exists()
                                if subject_is:
                                    subject = Subject.objects.get(hemis_id=rx['subject']['id'])
                                else:
                                    print(rx['subject'])
                                    return Response({'error': 'Fan hemis bazadan biriktrilmagan!'})
                                print(rx)
                                subject_type_is = Subject_type.objects.filter(code=rx['subjectType']['code']).exists()
                                if subject_type_is:
                                    subject_type = Subject_type.objects.get(code=rx['subjectType']['code'])
                                else:
                                    return Response({'error': 'Fan turi hemis bazadan biriktrilmagan!'})
                                subject_block_is = Subject_block.objects.filter(
                                    code=rx['subjectBlock']['code']).exists()
                                if subject_block_is:
                                    subject_block = Subject_block.objects.get(code=rx['subjectBlock']['code'])
                                else:
                                    return Response({'error': 'Fan block hemis bazadan biriktrilmagan!'})
                                subject_exam_finish_is = Subject_exam_finish.objects.filter(
                                    code=rx['examFinish']['code']).exists()
                                if subject_exam_finish_is:
                                    subject_exam_finish = Subject_exam_finish.objects.get(code=rx['examFinish']['code'])
                                else:
                                    return Response({'error': 'Fan exam hemis bazadan biriktrilmagan!'})

                                department_is = Department.objects.filter(hemisid=rx['department']['id']).exists()
                                if department_is:
                                    department = Department.objects.get(hemisid=rx['department']['id'])
                                else:
                                    print(rx['department'])
                                    return Response({'error': 'Bo`lim va kafedra hemis bazadan biriktrilmagan!'})
                                rating_grade_is = RatingGrade.objects.filter(code=rx['ratingGrade']['code']).exists()
                                if rating_grade_is:
                                    rating_grade = RatingGrade.objects.get(code=rx['ratingGrade']['code'])
                                else:
                                    rating_grade = RatingGrade()
                                    rating_grade.code = rx['ratingGrade']['code']
                                    rating_grade.name = rx['ratingGrade']['name']
                                    rating_grade.save()

                                for subdetail in rx['subjectDetails']:
                                    try:
                                        trainingtype = TrainingType.objects.get(code=subdetail['trainingType']['code'])
                                    except:
                                        return Response(
                                            {'error': True,
                                             'message': 'Training Turini malumotlarni qo`ishish kerak'},
                                            status=status.HTTP_400_BAD_REQUEST
                                        )

                                    try:
                                        subdet = SubjectDetails.objects.get(hemis_id=subdetail['id'])
                                        subdet.academic_load = subdetail['academic_load']
                                        subdet.subject_details = obj
                                        subdet.trainingType = trainingtype
                                        subdet.save()
                                    except SubjectDetails.DoesNotExist:
                                        subdet = SubjectDetails()
                                        subdet.hemis_id = subdetail['id']
                                        subdet.academic_load = subdetail['academic_load']
                                        subdet.subject_details = obj
                                        subdet.trainingType = trainingtype
                                        subdet.save()

                                for subexam in rx['subjectExamTypes']:
                                    try:
                                        examtype = ExamTypes.objects.get(code=subexam['examType']['code'])
                                    except:
                                        return Response(
                                            {'error': True,
                                             'message': 'Exam Turini malumotlarni qo`ishish kerak'},
                                            status=status.HTTP_400_BAD_REQUEST
                                        )

                                    try:
                                        subtexam = SubjectExamTypes.objects.get(hemis_id=subexam['id'])
                                        subtexam.max_ball = subexam['max_ball']
                                        subtexam.sub_exam_type = obj
                                        subtexam.examType = examtype
                                        subtexam.save()
                                    except SubjectExamTypes.DoesNotExist:
                                        subtexam = SubjectExamTypes()
                                        subtexam.hemis_id = subexam['id']
                                        subtexam.max_ball = subexam['max_ball']
                                        subtexam.sub_exam_type = obj
                                        subtexam.examType = examtype
                                        subtexam.save()

                                obj.subject_departmant = department
                                obj.exam_finish = subject_exam_finish
                                obj.subject = subject
                                obj.subject_type = subject_type
                                obj.subject_block = subject_block
                                obj.subject_curriculum = j
                                obj.ratingGrade = rating_grade
                                obj.subject_semestr = semester
                                obj.total_acload = rx['total_acload']
                                obj.resource_count = rx['resource_count']
                                obj.credit = rx['credit']
                                obj.save()
                        else:

                            semests_status = Hsemester_action.objects.filter(semester__code=rx['semester']['code'],
                                                                             curriculum__cur_id=j.cur_id).exists()
                            if semests_status:
                                semester_active = Hsemester_action.objects.get(semester__code=rx['semester']['code'],
                                                                               curriculum__cur_id=j.cur_id)
                                if semester_active.current == True:
                                    subject_is = Subject.objects.filter(hemis_id=rx['subject']['id']).exists()
                                    if subject_is:
                                        subject = Subject.objects.get(hemis_id=rx['subject']['id'])
                                    else:
                                        print(rx)
                                        print(rx['subject'],"2")
                                        return Response({'error': 'Fan hemis bazadan biriktrilmagan!'})
                                    print(rx)
                                    subject_type_is = Subject_type.objects.filter(code=rx['subjectType']['code']).exists()
                                    if subject_type_is:
                                        subject_type = Subject_type.objects.get(code=rx['subjectType']['code'])
                                    else:
                                        return Response({'error': 'Fan turi hemis bazadan biriktrilmagan!'})
                                    subject_block_is = Subject_block.objects.filter(
                                        code=rx['subjectBlock']['code']).exists()
                                    if subject_block_is:
                                        subject_block = Subject_block.objects.get(code=rx['subjectBlock']['code'])
                                    else:
                                        return Response({'error': 'Fan block hemis bazadan biriktrilmagan!'})
                                    subject_exam_finish_is = Subject_exam_finish.objects.filter(
                                        code=rx['examFinish']['code']).exists()
                                    if subject_exam_finish_is:
                                        subject_exam_finish = Subject_exam_finish.objects.get(code=rx['examFinish']['code'])
                                    else:
                                        return Response({'error': 'Fan exam hemis bazadan biriktrilmagan!'})
                                    semester_is = Hsemester.objects.filter(code=rx['semester']['code']).exists()
                                    if semester_is:
                                        semester = Hsemester.objects.get(code=rx['semester']['code'])
                                    else:
                                        return Response({'error': 'Semester hemis bazadan biriktrilmagan!'})
                                    department_is = Department.objects.filter(hemisid=rx['department']['id']).exists()
                                    if department_is:
                                        department = Department.objects.get(hemisid=rx['department']['id'])
                                    else:
                                        if Faculty.objects.filter(hemisid=rx['department']['parent']).exists():
                                            fakul = Faculty.objects.get(hemisid=rx['department']['parent'])
                                        else:
                                            return Response({'error': 'Bo`lim va kafedra hemis bazadan biriktrilmagan!'})
                                        if rx['department']['active'] == False:
                                            department = Department()
                                            department.hemisid = rx['department']['id']
                                            department.name = rx['department']['name']
                                            department.kod = rx['department']['code']
                                            department.faculty = fakul
                                            department.save()

                                    rating_grade_is = RatingGrade.objects.filter(code=rx['ratingGrade']['code']).exists()
                                    if rating_grade_is:
                                        rating_grade = RatingGrade.objects.get(code=rx['ratingGrade']['code'])
                                    else:
                                        rating_grade = RatingGrade()
                                        rating_grade.code = rx['ratingGrade']['code']
                                        rating_grade.name = rx['ratingGrade']['name']
                                        rating_grade.save()
                                    obj = Subject_Curriculum()
                                    obj.hemis_id = rx['id']
                                    obj.subject_departmant = department
                                    obj.exam_finish = subject_exam_finish
                                    obj.subject = subject
                                    obj.subject_type = subject_type
                                    obj.subject_block = subject_block
                                    obj.subject_curriculum = j
                                    obj.ratingGrade = rating_grade
                                    obj.subject_semestr = semester
                                    obj.total_acload = rx['total_acload']
                                    obj.resource_count = rx['resource_count']
                                    obj.credit = rx['credit']
                                    obj.save()
                                    for subdetail in rx['subjectDetails']:
                                        try:
                                            trainingtype = TrainingType.objects.get(code=subdetail['trainingType']['code'])
                                        except:
                                            return Response(
                                                {'error': True,
                                                 'message': 'Training Turini malumotlarni qo`ishish kerak'},
                                                status=status.HTTP_400_BAD_REQUEST
                                            )

                                        try:
                                            subdet = SubjectDetails.objects.get(hemis_id=subdetail['id'])
                                            subdet.academic_load = subdetail['academic_load']
                                            subdet.subject_details = obj
                                            subdet.trainingType = trainingtype
                                            subdet.save()
                                        except SubjectDetails.DoesNotExist:
                                            subdet = SubjectDetails()
                                            subdet.hemis_id = subdetail['id']
                                            subdet.academic_load = subdetail['academic_load']
                                            subdet.subject_details = obj
                                            subdet.trainingType = trainingtype
                                            subdet.save()

                                    for subexam in rx['subjectExamTypes']:
                                        try:
                                            examtype = ExamTypes.objects.get(code=subexam['examType']['code'])
                                        except:
                                            return Response(
                                                {'error': True,
                                                 'message': 'Exam Turini malumotlarni qo`ishish kerak'},
                                                status=status.HTTP_400_BAD_REQUEST
                                            )

                                        try:
                                            subtexam = SubjectExamTypes.objects.get(hemis_id=subexam['id'])
                                            subtexam.max_ball = subexam['max_ball']
                                            subtexam.sub_exam_type = obj
                                            subtexam.examType = examtype
                                            subtexam.save()
                                        except SubjectExamTypes.DoesNotExist:
                                            subtexam = SubjectExamTypes()
                                            subtexam.hemis_id = subexam['id']
                                            subtexam.max_ball = subexam['max_ball']
                                            subtexam.sub_exam_type = obj
                                            subtexam.examType = examtype
                                            subtexam.save()
            time = respon.elapsed.total_seconds()
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
        return Response({'succes': 'Baza qo`shildi va yangilandi!', 'time': elapsed_time})

class Getsubject_listNew(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    REQUIRED_FIELDS = [
        "subjectType",
        "subjectBlock",
        "examFinish",
        "department",
        "ratingGrade"
    ]

    # ---------------------------------------------------------------------------------------
    # YAMLASH: HEMIS API dan JSON olish
    # ---------------------------------------------------------------------------------------
    def fetch_json(self, url, headers, params):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
        except Exception as e:
            return None, f"REQUEST_ERROR: {str(e)}"

        try:
            data = r.json()
        except:
            return None, "INVALID_JSON"

        if isinstance(data, list):
            return None, f"LIST_RESPONSE: {str(data)[:200]}"

        if not isinstance(data, dict):
            return None, "NOT_DICT_RESPONSE"

        if "data" not in data:
            return None, f"MISSING_DATA_KEY: {str(data)[:200]}"

        return data, None

    # ---------------------------------------------------------------------------------------
    # MAJBURIY MAYDONLARNI TEKSHIRISH
    # ---------------------------------------------------------------------------------------
    def check_missing_fields(self, rx, stats):
        missing = []
        for field in self.REQUIRED_FIELDS:
            if rx.get(field) in (None, ""):
                missing.append(field)
                stats["empty_fields"][field] += 1
        return missing

    # =======================================================================================
    # GET METHOD
    # =======================================================================================
    def get(self, request, format=None):

        # ---------------------------
        # STATISTICS
        # ---------------------------
        stats = {
            "total_items": 0,
            "saved_items": 0,
            "failed_items": 0,
            "empty_fields": {
                "subjectType": 0,
                "subjectBlock": 0,
                "examFinish": 0,
                "department": 0,
                "ratingGrade": 0
            },
            "errors": []
        }

        start_time = datetime.datetime.now()

        # ---------------------------
        # HEMIS BOSHLANG‘ICH CHECKLAR
        # ---------------------------
        try:
            hemis = Hemis_Base.objects.get(own_uniq=11)
        except:
            return Response({"error": "Hemis modulida biriktirilmagan!"})

        token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        if not token:
            return Response({"error": "Faol token mavjud emas!"})

        if hemis.openapi:
            return Response({"error": "Tokensiz murojaat qilib bo‘lmaydi!"})

        baseurl = hemis.base_url.rstrip("/") + "/" + hemis.path_url.lstrip("/")

        headers = {
            "Content-Type": "application/json",
            "Authorization": token.hemis_token_type + " " + token.hemis_token
        }

        # ---------------------------
        # CURRICULUMLAR LOOP
        # ---------------------------
        for cur in Curriculum.objects.filter(hcurriculum__current=True):

            params = {
                "page": "1",
                "limit": "100",
                "_curriculum": cur.cur_id
            }

            data, err = self.fetch_json(baseurl, headers, params)
            if err:
                stats["errors"].append({"curriculum": cur.cur_id, "error": err})
                continue

            pagination = data["data"].get("pagination")
            if not pagination:
                stats["errors"].append({
                    "curriculum": cur.cur_id,
                    "error": "NO_PAGINATION",
                    "sample": str(data)[:300]
                })
                continue

            try:
                pagecount = int(pagination.get("pageCount", 1))
            except:
                stats["errors"].append({
                    "curriculum": cur.cur_id,
                    "error": "INVALID_PAGECOUNT",
                    "sample": str(pagination)[:200]
                })
                continue

            # ---------------------------
            # PAGINATION LOOP
            # ---------------------------
            for page in range(1, pagecount + 1):
                params["page"] = page
                pdata, perr = self.fetch_json(baseurl, headers, params)
                if perr:
                    stats["errors"].append({"curriculum": cur.cur_id, "page": page, "error": perr})
                    continue

                items = pdata["data"].get("items", [])
                if not isinstance(items, list):
                    stats["errors"].append({"curriculum": cur.cur_id, "page": page, "error": "ITEMS_NOT_LIST"})
                    continue

                # ---------------------------
                # ITEMS LOOP
                # ---------------------------
                for rx in items:
                    stats["total_items"] += 1

                    # Missing fields
                    missing = self.check_missing_fields(rx, stats)
                    if missing:
                        stats["failed_items"] += 1
                        stats["errors"].append({
                            "hemis_id": rx.get("id"),
                            "missing_fields": missing
                        })
                        continue

                    # Semester action check
                    sem_ok = Hsemester_action.objects.filter(
                        semester__code=rx["semester"]["code"],
                        curriculum__cur_id=cur.cur_id
                    ).exists()

                    if not sem_ok:
                        stats["failed_items"] += 1
                        stats["errors"].append({
                            "hemis_id": rx.get("id"),
                            "error": "SEMESTER_ACTION_NOT_FOUND"
                        })
                        continue

                    # ===========================
                    # SAVE BLOCK
                    # ===========================
                    try:
                        with transaction.atomic():
                            semester = Hsemester.objects.get(code=rx["semester"]["code"])
                            subject = Subject.objects.get(hemis_id=rx["subject"]["id"])
                            subject_type = Subject_type.objects.get(code=rx["subjectType"]["code"])
                            subject_block = Subject_block.objects.get(code=rx["subjectBlock"]["code"])

                            # exam finish
                            subject_exam_finish = Subject_exam_finish.objects.get(
                                code=rx["examFinish"]["code"]
                            )

                            # department
                            dep_data = rx["department"]
                            dep_id = dep_data["id"]

                            if Department.objects.filter(hemisid=dep_id).exists():
                                department = Department.objects.get(hemisid=dep_id)
                            else:
                                parent_id = dep_data["parent"]
                                if Faculty.objects.filter(hemisid=parent_id).exists():
                                    fakul = Faculty.objects.get(hemisid=parent_id)
                                    department = Department.objects.create(
                                        hemisid=dep_id,
                                        name=dep_data["name"],
                                        kod=dep_data["code"],
                                        faculty=fakul
                                    )
                                else:
                                    raise Exception("DEPARTMENT_OR_FACULTY_NOT_FOUND")

                            # rating grade
                            grade_code = rx["ratingGrade"]["code"]
                            rating_grade, _ = RatingGrade.objects.get_or_create(
                                code=grade_code,
                                defaults={"name": rx["ratingGrade"]["name"]}
                            )

                            sc_obj, created = Subject_Curriculum.objects.get_or_create(
                                hemis_id=rx["id"],
                                defaults={"subject_curriculum": cur}
                            )

                            sc_obj.subject = subject
                            sc_obj.subject_type = subject_type
                            sc_obj.subject_block = subject_block
                            sc_obj.exam_finish = subject_exam_finish
                            sc_obj.subject_departmant = department
                            sc_obj.subject_curriculum = cur
                            sc_obj.ratingGrade = rating_grade
                            sc_obj.subject_semestr = semester
                            sc_obj.total_acload = rx["total_acload"]
                            sc_obj.resource_count = rx["resource_count"]
                            sc_obj.credit = rx["credit"]
                            sc_obj.save()

                            # subject details
                            for d in rx.get("subjectDetails", []):
                                tt = TrainingType.objects.get(code=d["trainingType"]["code"])
                                SubjectDetails.objects.update_or_create(
                                    hemis_id=d["id"],
                                    defaults={
                                        "academic_load": d["academic_load"],
                                        "subject_details": sc_obj,
                                        "trainingType": tt
                                    }
                                )

                            # exam types
                            for e in rx.get("subjectExamTypes", []):
                                etype = ExamTypes.objects.get(code=e["examType"]["code"])
                                SubjectExamTypes.objects.update_or_create(
                                    hemis_id=e["id"],
                                    defaults={
                                        "max_ball": e["max_ball"],
                                        "sub_exam_type": sc_obj,
                                        "examType": etype
                                    }
                                )

                            stats["saved_items"] += 1

                    except Exception as e:
                        stats["failed_items"] += 1
                        stats["errors"].append({
                            "hemis_id": rx.get("id"),
                            "error": str(e),
                            "raw_json": rx  # ⭐⭐ ENDI JSON ham chiqadi ⭐⭐
                        })
                        continue

        # ---------------------------
        # HISOBOT BLOKINI QO‘SHISH
        # ---------------------------
        report = {
            "summary": {
                "total_items": stats["total_items"],
                "saved_items": stats["saved_items"],
                "failed_items": stats["failed_items"],
            },
            "errors_by_type": {},
            "missing_fields_details": [],
            "exam_finish_errors": [],
            "other_errors": []
        }

        for err in stats["errors"]:

            # missing_fields error
            if "missing_fields" in err:
                report["errors_by_type"].setdefault("missing_fields", 0)
                report["errors_by_type"]["missing_fields"] += 1

                report["missing_fields_details"].append({
                    "hemis_id": err["hemis_id"],
                    "missing": err["missing_fields"]
                })
                continue

            # exam_finish null
            if "exam_finish_id" in str(err.get("error", "")):
                report["errors_by_type"].setdefault("exam_finish_null", 0)
                report["errors_by_type"]["exam_finish_null"] += 1

                report["exam_finish_errors"].append({
                    "hemis_id": err["hemis_id"],
                    "reason": "examFinish bo‘sh yoki DB dagi code topilmadi"
                })
                continue

            # Other errors
            report["errors_by_type"].setdefault("other", 0)
            report["errors_by_type"]["other"] += 1
            report["other_errors"].append(err)

        # ---------------------------
        # FINISH
        # ---------------------------
        elapsed = datetime.datetime.now() - start_time

        return Response({
            "success": True,
            "message": "Baza qo‘shildi va yangilandi!",
            "stats": stats,
            "report": report,
            "time": str(elapsed)
        })

class Getzerosubject_listNew(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    REQUIRED_FIELDS = [
        "subjectType",
        "subjectBlock",
        "examFinish",
        "department",
        "ratingGrade"
    ]

    # ---------------------------------------------------------------------------------------
    # YAMLASH: HEMIS API dan JSON olish
    # ---------------------------------------------------------------------------------------
    def fetch_json(self, url, headers, params):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
        except Exception as e:
            return None, f"REQUEST_ERROR: {str(e)}"

        try:
            data = r.json()
        except:
            return None, "INVALID_JSON"

        if isinstance(data, list):
            return None, f"LIST_RESPONSE: {str(data)[:200]}"

        if not isinstance(data, dict):
            return None, "NOT_DICT_RESPONSE"

        if "data" not in data:
            return None, f"MISSING_DATA_KEY: {str(data)[:200]}"

        return data, None

    # ---------------------------------------------------------------------------------------
    # MAJBURIY MAYDONLARNI TEKSHIRISH
    # ---------------------------------------------------------------------------------------
    def check_missing_fields(self, rx, stats):
        missing = []
        for field in self.REQUIRED_FIELDS:
            if rx.get(field) in (None, ""):
                missing.append(field)
                stats["empty_fields"][field] += 1
        return missing

    # =======================================================================================
    # GET METHOD
    # =======================================================================================
    def get(self, request, format=None):

        # ---------------------------
        # STATISTICS
        # ---------------------------
        stats = {
            "total_items": 0,
            "saved_items": 0,
            "failed_items": 0,
            "empty_fields": {
                "subjectType": 0,
                "subjectBlock": 0,
                "examFinish": 0,
                "department": 0,
                "ratingGrade": 0
            },
            "errors": []
        }

        start_time = datetime.datetime.now()

        # ---------------------------
        # HEMIS BOSHLANG‘ICH CHECKLAR
        # ---------------------------
        try:
            hemis = Hemis_Base.objects.get(own_uniq=11)
        except:
            return Response({"error": "Hemis modulida biriktirilmagan!"})

        token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        if not token:
            return Response({"error": "Faol token mavjud emas!"})

        if hemis.openapi:
            return Response({"error": "Tokensiz murojaat qilib bo‘lmaydi!"})

        baseurl = hemis.base_url.rstrip("/") + "/" + hemis.path_url.lstrip("/")

        headers = {
            "Content-Type": "application/json",
            "Authorization": token.hemis_token_type + " " + token.hemis_token
        }

        # ---------------------------
        # CURRICULUMLAR LOOP
        # ---------------------------
        for cur in Curriculum.objects.filter(hcurriculum__current=True, educationform__code=16):

            params = {
                "page": "1",
                "limit": "100",
                "_curriculum": cur.cur_id
            }

            data, err = self.fetch_json(baseurl, headers, params)
            if err:
                stats["errors"].append({"curriculum": cur.cur_id, "error": err})
                continue

            pagination = data["data"].get("pagination")
            if not pagination:
                stats["errors"].append({
                    "curriculum": cur.cur_id,
                    "error": "NO_PAGINATION",
                    "sample": str(data)[:300]
                })
                continue

            try:
                pagecount = int(pagination.get("pageCount", 1))
            except:
                stats["errors"].append({
                    "curriculum": cur.cur_id,
                    "error": "INVALID_PAGECOUNT",
                    "sample": str(pagination)[:200]
                })
                continue

            # ---------------------------
            # PAGINATION LOOP
            # ---------------------------
            for page in range(1, pagecount + 1):
                params["page"] = page
                pdata, perr = self.fetch_json(baseurl, headers, params)
                if perr:
                    stats["errors"].append({"curriculum": cur.cur_id, "page": page, "error": perr})
                    continue

                items = pdata["data"].get("items", [])
                if not isinstance(items, list):
                    stats["errors"].append({"curriculum": cur.cur_id, "page": page, "error": "ITEMS_NOT_LIST"})
                    continue

                # ---------------------------
                # ITEMS LOOP
                # ---------------------------
                for rx in items:
                    stats["total_items"] += 1

                    # Missing fields
                    missing = self.check_missing_fields(rx, stats)
                    if missing:
                        stats["failed_items"] += 1
                        stats["errors"].append({
                            "hemis_id": rx.get("id"),
                            "missing_fields": missing
                        })
                        continue

                    # Semester action check
                    sem_ok = Hsemester_action.objects.filter(
                        semester__code=rx["semester"]["code"],
                        curriculum__cur_id=cur.cur_id
                    ).exists()

                    if not sem_ok:
                        stats["failed_items"] += 1
                        stats["errors"].append({
                            "hemis_id": rx.get("id"),
                            "error": "SEMESTER_ACTION_NOT_FOUND"
                        })
                        continue

                    # ===========================
                    # SAVE BLOCK
                    # ===========================
                    try:
                        with transaction.atomic():
                            semester = Hsemester.objects.get(code=rx["semester"]["code"])
                            subject = Subject.objects.get(hemis_id=rx["subject"]["id"])
                            subject_type = Subject_type.objects.get(code=rx["subjectType"]["code"])
                            subject_block = Subject_block.objects.get(code=rx["subjectBlock"]["code"])

                            # exam finish
                            subject_exam_finish = Subject_exam_finish.objects.get(
                                code=rx["examFinish"]["code"]
                            )

                            # department
                            dep_data = rx["department"]
                            dep_id = dep_data["id"]

                            if Department.objects.filter(hemisid=dep_id).exists():
                                department = Department.objects.get(hemisid=dep_id)
                            else:
                                parent_id = dep_data["parent"]
                                if Faculty.objects.filter(hemisid=parent_id).exists():
                                    fakul = Faculty.objects.get(hemisid=parent_id)
                                    department = Department.objects.create(
                                        hemisid=dep_id,
                                        name=dep_data["name"],
                                        kod=dep_data["code"],
                                        faculty=fakul
                                    )
                                else:
                                    raise Exception("DEPARTMENT_OR_FACULTY_NOT_FOUND")

                            # rating grade
                            grade_code = rx["ratingGrade"]["code"]
                            rating_grade, _ = RatingGrade.objects.get_or_create(
                                code=grade_code,
                                defaults={"name": rx["ratingGrade"]["name"]}
                            )

                            sc_obj, created = Subject_Curriculum.objects.get_or_create(
                                hemis_id=rx["id"],
                                defaults={"subject_curriculum": cur}
                            )

                            sc_obj.subject = subject
                            sc_obj.subject_type = subject_type
                            sc_obj.subject_block = subject_block
                            sc_obj.exam_finish = subject_exam_finish
                            sc_obj.subject_departmant = department
                            sc_obj.subject_curriculum = cur
                            sc_obj.ratingGrade = rating_grade
                            sc_obj.subject_semestr = semester
                            sc_obj.total_acload = rx["total_acload"]
                            sc_obj.resource_count = rx["resource_count"]
                            sc_obj.credit = rx["credit"]
                            sc_obj.save()

                            # subject details
                            for d in rx.get("subjectDetails", []):
                                tt = TrainingType.objects.get(code=d["trainingType"]["code"])
                                SubjectDetails.objects.update_or_create(
                                    hemis_id=d["id"],
                                    defaults={
                                        "academic_load": d["academic_load"],
                                        "subject_details": sc_obj,
                                        "trainingType": tt
                                    }
                                )

                            # exam types
                            for e in rx.get("subjectExamTypes", []):
                                etype = ExamTypes.objects.get(code=e["examType"]["code"])
                                SubjectExamTypes.objects.update_or_create(
                                    hemis_id=e["id"],
                                    defaults={
                                        "max_ball": e["max_ball"],
                                        "sub_exam_type": sc_obj,
                                        "examType": etype
                                    }
                                )

                            stats["saved_items"] += 1

                    except Exception as e:
                        stats["failed_items"] += 1
                        stats["errors"].append({
                            "hemis_id": rx.get("id"),
                            "error": str(e),
                            "raw_json": rx  # ⭐⭐ ENDI JSON ham chiqadi ⭐⭐
                        })
                        continue

        # ---------------------------
        # HISOBOT BLOKINI QO‘SHISH
        # ---------------------------
        report = {
            "summary": {
                "total_items": stats["total_items"],
                "saved_items": stats["saved_items"],
                "failed_items": stats["failed_items"],
            },
            "errors_by_type": {},
            "missing_fields_details": [],
            "exam_finish_errors": [],
            "other_errors": []
        }

        for err in stats["errors"]:

            # missing_fields error
            if "missing_fields" in err:
                report["errors_by_type"].setdefault("missing_fields", 0)
                report["errors_by_type"]["missing_fields"] += 1

                report["missing_fields_details"].append({
                    "hemis_id": err["hemis_id"],
                    "missing": err["missing_fields"]
                })
                continue

            # exam_finish null
            if "exam_finish_id" in str(err.get("error", "")):
                report["errors_by_type"].setdefault("exam_finish_null", 0)
                report["errors_by_type"]["exam_finish_null"] += 1

                report["exam_finish_errors"].append({
                    "hemis_id": err["hemis_id"],
                    "reason": "examFinish bo‘sh yoki DB dagi code topilmadi"
                })
                continue

            # Other errors
            report["errors_by_type"].setdefault("other", 0)
            report["errors_by_type"]["other"] += 1
            report["other_errors"].append(err)

        # ---------------------------
        # FINISH
        # ---------------------------
        elapsed = datetime.datetime.now() - start_time

        return Response({
            "success": True,
            "message": "Baza qo‘shildi va yangilandi!",
            "stats": stats,
            "report": report,
            "time": str(elapsed)
        })


class GetSubjectNew_versionList(APIView):
    # permission_classes = [AllowOnlyTrustedOrigins, IsAdmin]

    def get(self, request, format=None):

        hemis = Hemis_Base.objects.filter(own_uniq=11).first()
        if not hemis:
            return Response({'error': 'Hemis modulida birktrilmagan'}, status=status.HTTP_400_BAD_REQUEST)

        if hemis.openapi:
            return Response({'error': 'Tokensiz murojaat qilib bo`lmidi'}, status=status.HTTP_400_BAD_REQUEST)

        token = HemisToken.objects.filter(status=True, hemis_user=hemis.hemis_user).first()
        if not token:
            return Response({'error': 'Faol token mavjud emas!'}, status=status.HTTP_400_BAD_REQUEST)

        baseurl = hemis.base_url
        pathurl = hemis.path_url

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'{token.hemis_token_type} {token.hemis_token}'
        }

        start_time = datetime.datetime.now()

        session = requests.Session()
        session.headers.update(headers)

        curriculums = list(Curriculum.objects.all())

        # ---------- ANALITIKA ----------
        total_curriculums = len(curriculums)
        curriculum_success = 0
        curriculum_api_error = 0

        total_subjects_api = 0
        total_subjects_processed = 0
        total_subjects_skipped = 0
        total_subjects_failed = 0

        errors = []

        # ---------- ASOSIY CIKL ----------
        for curriculum in curriculums:
            try:
                items = self._fetch_all_subjects_for_curriculum(
                    session, baseurl, pathurl, curriculum.cur_id
                )
                curriculum_success += 1
                total_subjects_api += len(items)
            except Exception as exc:
                logger.exception("Curriculum %s uchun ma'lumot olishda xatolik: %s",
                                 curriculum.cur_id, exc)
                curriculum_api_error += 1
                errors.append({
                    'scope': 'curriculum_api',
                    'curriculum_id': curriculum.cur_id,
                    'message': 'API xatolik',
                    'detail': str(exc),
                })
                continue

            for rx in items:
                try:
                    processed = self._sync_single_subject(curriculum, rx)

                    if processed:
                        total_subjects_processed += 1
                    else:
                        total_subjects_skipped += 1

                except Exception as exc:
                    logger.exception(
                        "Subject sync xatolik (curriculum=%s, subject_id=%s): %s",
                        curriculum.cur_id, rx.get('id'), exc
                    )
                    total_subjects_failed += 1

                    errors.append({
                        'scope': 'subject_sync',
                        'curriculum_id': curriculum.cur_id,
                        'subject_id': rx.get('id'),
                        'message': str(exc),
                    })
                    continue

        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time

        # ---------- ERROR STATISTIKA ----------
        error_messages_stats = dict(Counter(e['message'] for e in errors))
        error_scope_stats = dict(Counter(e['scope'] for e in errors))

        # ---------- JAVOB ----------
        return Response(
            {
                'success': True,
                'message': 'Baza qo`shildi va yangilandi!',
                'time': str(elapsed_time),

                # Curriculum statistikasi
                'total_curriculums': total_curriculums,
                'curriculum_success': curriculum_success,
                'curriculum_api_error': curriculum_api_error,

                # Subject statistikasi
                'total_subjects_api': total_subjects_api,
                'total_subjects_processed': total_subjects_processed,
                'total_subjects_skipped': total_subjects_skipped,
                'total_subjects_failed': total_subjects_failed,

                # Error statistikasi
                'errors_count': len(errors),
                'error_scope_stats': error_scope_stats,
                'error_messages_stats': error_messages_stats,

                # Xohlasang to‘liq error logni ham chiqaramiz:
                # 'errors': errors,
            },
            status=status.HTTP_200_OK
        )

    # ============================================
    #   API-dan barcha sahifalarni yuklash
    # ============================================
    def _fetch_all_subjects_for_curriculum(self, session, baseurl, pathurl, cur_id):
        params = {
            'page': '1',
            'limit': '100',
            '_curriculum': cur_id
        }
        resp = session.get(baseurl + pathurl, params=params, verify=False)
        resp.raise_for_status()
        data = resp.json()

        pagination = data.get('data', {}).get('pagination', {})
        first_page = int(pagination.get('page', 1))
        page_count = int(pagination.get('pageCount', 1))

        all_items = data.get('data', {}).get('items', []) or []

        for page in range(first_page + 1, page_count + 1):
            params['page'] = str(page)
            presp = session.get(baseurl + pathurl, params=params, verify=False)
            presp.raise_for_status()
            pdata = presp.json()
            items = pdata.get('data', {}).get('items', []) or []
            all_items.extend(items)

        return all_items

    # ============================================
    #   Bitta subjectni bazaga sync qilish
    # ============================================
    def _sync_single_subject(self, curriculum, rx: dict) -> bool:

        semester_code = rx['semester']['code']
        has_sem_act = Hsemester_action.objects.filter(
            semester__code=semester_code,
            curriculum__cur_id=curriculum.cur_id
        ).exists()

        if not has_sem_act:
            return False

        obj = Subject_Curriculum.objects.filter(hemis_id=rx['id']).first()
        is_new = obj is None

        if is_new:
            semester_active = Hsemester_action.objects.filter(
                semester__code=semester_code,
                curriculum__cur_id=curriculum.cur_id,
                current=True
            ).first()
            if not semester_active:
                return False
            obj = Subject_Curriculum(hemis_id=rx['id'])

        subject = self._get_subject(rx)
        if not subject:
            raise ValueError("Fan hemis bazadan biriktrilmagan!")

        subject_type = self._get_subject_type(rx)
        if not subject_type:
            raise ValueError("Fan turi hemis bazadan biriktrilmagan!")

        subject_block = self._get_subject_block(rx)
        if not subject_block:
            raise ValueError("Fan block hemis bazadan biriktrilmagan!")

        subject_exam_finish = self._get_subject_exam_finish(rx)
        if not subject_exam_finish:
            raise ValueError("Fan exam hemis bazadan biriktrilmagan!")

        semester = self._get_semester(semester_code)
        if not semester:
            raise ValueError("Semester hemis bazadan biriktrilmagan!")

        department = self._get_department(rx)
        if not department:
            raise ValueError("Bo`lim va kafedra hemis bazadan biriktrilmagan!")

        rating_grade = self._get_or_create_rating_grade(rx)

        obj.subject_departmant = department
        obj.exam_finish = subject_exam_finish
        obj.subject = subject
        obj.subject_type = subject_type
        obj.subject_block = subject_block
        obj.subject_curriculum = curriculum
        obj.ratingGrade = rating_grade
        obj.subject_semestr = semester
        obj.total_acload = rx['total_acload']
        obj.resource_count = rx['resource_count']
        obj.credit = rx['credit']
        obj.save()

        self._sync_subject_details(obj, rx.get('subjectDetails', []))
        self._sync_subject_exam_types(obj, rx.get('subjectExamTypes', []))

        return True

    # ============================================
    #   RELATED OBJECT HELPERS
    # ============================================

    def _get_subject(self, rx):
        subject_id = rx['subject']['id']
        subject = Subject.objects.filter(hemis_id=subject_id).first()
        return subject

    def _get_subject_type(self, rx):
        return Subject_type.objects.filter(code=rx['subjectType']['code']).first()

    def _get_subject_block(self, rx):
        return Subject_block.objects.filter(code=rx['subjectBlock']['code']).first()

    def _get_subject_exam_finish(self, rx):
        return Subject_exam_finish.objects.filter(code=rx['examFinish']['code']).first()

    def _get_semester(self, semester_code):
        return Hsemester.objects.filter(code=semester_code).first()

    def _get_department(self, rx):
        dep_id = rx['department']['id']
        department = Department.objects.filter(hemisid=dep_id).first()
        if department:
            return department

        parent_id = rx['department'].get('parent')
        if not parent_id:
            return None

        faculty = Faculty.objects.filter(hemisid=parent_id).first()
        if not faculty:
            return None

        department = Department(
            hemisid=dep_id,
            name=rx['department']['name'],
            kod=rx['department']['code'],
            faculty=faculty
        )
        department.save()
        return department

    def _get_or_create_rating_grade(self, rx):
        code = rx['ratingGrade']['code']
        rating = RatingGrade.objects.filter(code=code).first()
        if rating:
            return rating

        rating = RatingGrade(
            code=code,
            name=rx['ratingGrade']['name']
        )
        rating.save()
        return rating

    # ============================================
    #   DETAILS VA EXAM TYPES SYNC
    # ============================================

    def _sync_subject_details(self, subject_curriculum_obj, details_list):
        for subdetail in details_list:
            training_code = subdetail['trainingType']['code']
            trainingtype = TrainingType.objects.filter(code=training_code).first()
            if not trainingtype:
                continue

            subdet, created = SubjectDetails.objects.get_or_create(
                hemis_id=subdetail['id'],
                defaults={
                    'academic_load': subdetail['academic_load'],
                    'subject_details': subject_curriculum_obj,
                    'trainingType': trainingtype,
                }
            )
            if not created:
                subdet.academic_load = subdetail['academic_load']
                subdet.subject_details = subject_curriculum_obj
                subdet.trainingType = trainingtype
                subdet.save()

    def _sync_subject_exam_types(self, subject_curriculum_obj, exam_types_list):
        for subexam in exam_types_list:
            examtype = ExamTypes.objects.filter(code=subexam['examType']['code']).first()
            if not examtype:
                continue

            subtexam, created = SubjectExamTypes.objects.get_or_create(
                hemis_id=subexam['id'],
                defaults={
                    'max_ball': subexam['max_ball'],
                    'sub_exam_type': subject_curriculum_obj,
                    'examType': examtype,
                }
            )
            if not created:
                subtexam.max_ball = subexam['max_ball']
                subtexam.sub_exam_type = subject_curriculum_obj
                subtexam.examType = examtype
                subtexam.save()

class OneCurriclumGetHemis(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin]

    def get(self, request, cur_id, format=None):

        # 1. HEMIS base
        try:
            hemis = Hemis_Base.objects.get(own_uniq=11)
        except Hemis_Base.DoesNotExist:
            return Response({'error': 'Hemis modulida biriktirilmagan'})

        # 2. Token
        try:
            token = HemisToken.objects.filter(
                status=True,
                hemis_user=hemis.hemis_user
            ).first()
            if not token:
                raise Exception
        except:
            return Response({'error': 'Faol token mavjud emas!'})

        if hemis.openapi:
            return Response({'error': 'Tokensiz murojaat qilib bo‘lmaydi'})

        # 3. Curriculum (BITTA)
        try:
            curriculum = Curriculum.objects.get(cur_id=cur_id)
        except Curriculum.DoesNotExist:
            return Response({'error': 'O‘quv reja topilmadi'})

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
        }

        start_time = datetime.datetime.now()

        # 4. Birinchi request (pagination olish uchun)
        params = {
            'page': '1',
            'limit': '100',
            '_curriculum': curriculum.cur_id
        }

        respon = requests.get(
            hemis.base_url + hemis.path_url,
            headers=headers,
            params=params
        )

        data = respon.json()
        page = int(data['data']['pagination']['page'])
        pagecount = int(data['data']['pagination']['pageCount']) + 1

        # 5. Sahifalar bo‘yicha aylanish
        for i in range(page, pagecount):
            params['page'] = str(i)

            prespon = requests.get(
                hemis.base_url + hemis.path_url,
                headers=headers,
                params=params
            )

            items = prespon.json()['data']['items']

            for rx in items:

                # Semester active tekshirish
                sem_act = Hsemester_action.objects.filter(
                    semester__code=rx['semester']['code'],
                    curriculum__cur_id=curriculum.cur_id
                ).first()

                if not sem_act:
                    continue

                # Semester
                semester = Hsemester.objects.filter(
                    code=rx['semester']['code']
                ).first()
                if not semester:
                    return Response({'error': 'Semester bazada yo‘q'})

                # Subject
                subject = Subject.objects.filter(
                    hemis_id=rx['subject']['id']
                ).first()
                if not subject:
                    return Response({'error': 'Fan bazada yo‘q'})

                # Subject type
                subject_type = Subject_type.objects.filter(
                    code=rx['subjectType']['code']
                ).first()
                if not subject_type:
                    return Response({'error': 'Fan turi yo‘q'})

                # Subject block
                subject_block = Subject_block.objects.filter(
                    code=rx['subjectBlock']['code']
                ).first()
                if not subject_block:
                    return Response({'error': 'Fan block yo‘q'})

                # Exam finish
                exam_finish = Subject_exam_finish.objects.filter(
                    code=rx['examFinish']['code']
                ).first()
                if not exam_finish:
                    return Response({'error': 'Exam finish yo‘q'})

                # Department
                department = Department.objects.filter(
                    hemisid=rx['department']['id']
                ).first()
                if not department:
                    return Response({'error': 'Kafedra topilmadi'})

                # Rating grade
                rating_grade, _ = RatingGrade.objects.get_or_create(
                    code=rx['ratingGrade']['code'],
                    defaults={'name': rx['ratingGrade']['name']}
                )

                # 6. Subject Curriculum (create / update)
                obj, created = Subject_Curriculum.objects.update_or_create(
                    hemis_id=rx['id'],
                    defaults={
                        'subject_departmant': department,
                        'exam_finish': exam_finish,
                        'subject': subject,
                        'subject_type': subject_type,
                        'subject_block': subject_block,
                        'subject_curriculum': curriculum,
                        'ratingGrade': rating_grade,
                        'subject_semestr': semester,
                        'total_acload': rx['total_acload'],
                        'resource_count': rx['resource_count'],
                        'credit': rx['credit'],
                    }
                )

                # 7. Subject details
                for subdetail in rx['subjectDetails']:
                    trainingtype = TrainingType.objects.filter(
                        code=subdetail['trainingType']['code']
                    ).first()
                    if not trainingtype:
                        return Response({'error': 'TrainingType yo‘q'})

                    SubjectDetails.objects.update_or_create(
                        hemis_id=subdetail['id'],
                        defaults={
                            'academic_load': subdetail['academic_load'],
                            'subject_details': obj,
                            'trainingType': trainingtype
                        }
                    )

                # 8. Exam types
                for subexam in rx['subjectExamTypes']:
                    examtype = ExamTypes.objects.filter(
                        code=subexam['examType']['code']
                    ).first()
                    if not examtype:
                        return Response({'error': 'ExamType yo‘q'})

                    SubjectExamTypes.objects.update_or_create(
                        hemis_id=subexam['id'],
                        defaults={
                            'max_ball': subexam['max_ball'],
                            'sub_exam_type': obj,
                            'examType': examtype
                        }
                    )

        elapsed_time = datetime.datetime.now() - start_time

        return Response({
            'success': 'Bitta o‘quv reja bo‘yicha fanlar yuklandi',
            'curriculum': cur_id,
            'time': str(elapsed_time)
        })