import datetime
import requests
from django.db import transaction
from django.utils import timezone

from shared.permissions import IsAdmin
from .models import Hsemester, HCourse, Hsemester_action, CurriculumWeeks
from learning_process.models import Curriculum, Educationyear


EDUCATION_FORM_DISTANCE = 16  # Masofaviy


class HemisSemesterSyncService:

    def __init__(self, hemis, token):
        self.hemis = hemis
        self.token = token
        self.errors = []
        self.created = 0
        self.updated = 0

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"{self.token.hemis_token_type} {self.token.hemis_token}"
        }

    def _parse_date(self, value):
        if not value:
            return None
        try:
            return datetime.datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            return None

    def sync(self):
        start_time = timezone.now()

        # 🔥 FAQAT MASOFAVIY CURRICULUM
        curriculums = Curriculum.objects.filter(
            educationform__code=EDUCATION_FORM_DISTANCE
        )

        for curriculum in curriculums:
            self._sync_curriculum(curriculum)

        return {
            "created": self.created,
            "updated": self.updated,
            "errors": self.errors,
            "time": timezone.now() - start_time
        }

    def _sync_curriculum(self, curriculum):
        page = 1

        while True:
            try:
                response = requests.get(
                    self.hemis.base_url + self.hemis.path_url,
                    headers=self._headers(),
                    params={
                        "page": page,
                        "limit": 100,
                        "_curriculum": curriculum.cur_id
                    },
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()["data"]
            except Exception as e:
                self.errors.append(
                    f"API error | curriculum={curriculum.id} | {str(e)}"
                )
                return

            for item in data.get("items", []):
                self._save_semester(curriculum, item)

            if page >= data["pagination"]["pageCount"]:
                break
            page += 1

    @transaction.atomic
    def _save_semester(self, curriculum, rx):
        edy = Educationyear.objects.filter(code=rx["_education_year"]).first()
        if not edy:
            self.errors.append(
                f"Education year topilmadi: {rx['_education_year']}"
            )
            return

        course = None
        if rx.get("level"):
            course = HCourse.objects.filter(
                code=rx["level"]["code"]
            ).first()
            if not course:
                self.errors.append(
                    f"Course topilmadi: {rx['level']['code']}"
                )
                return

        semester = Hsemester.objects.filter(code=rx["code"]).first()
        if not semester:
            self.errors.append(
                f"Semester topilmadi: {rx['code']}"
            )
            return

        hac, created = Hsemester_action.objects.update_or_create(
            h_id=rx["id"],
            defaults={
                "curriculum": curriculum,
                "education_year": edy,
                "level": course,
                "semester": semester,
                "current": rx["current"]
            }
        )

        if created:
            self.created += 1
        else:
            self.updated += 1

        self._sync_weeks(hac, rx.get("curriculumWeeks", []))

    def _sync_weeks(self, hac, weeks):
        for cw in weeks:
            CurriculumWeeks.objects.update_or_create(
                h_id=cw["id"],
                defaults={
                    "msemester": hac,
                    "current": cw["current"],
                    "start_date": cw["start_date"],
                    "end_date": cw["end_date"],
                    "start_date_f": self._parse_date(cw.get("start_date_f")),
                    "end_date_f": self._parse_date(cw.get("end_date_f")),
                }
            )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from hemis.models import Hemis_Base, HemisToken



class GetZeroHsemesterAction(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        hemis = Hemis_Base.objects.filter(own_uniq=6).first()
        if not hemis:
            return Response(
                {"error": "Hemis modul biriktirilmagan"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = HemisToken.objects.filter(
            status=True,
            hemis_user=hemis.hemis_user
        ).first()

        if not token:
            return Response(
                {"error": "Faol token mavjud emas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if hemis.openapi:
            return Response(
                {"error": "Tokensiz murojaat qilish mumkin emas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = HemisSemesterSyncService(hemis, token)
        result = service.sync()

        return Response(result, status=status.HTTP_200_OK)