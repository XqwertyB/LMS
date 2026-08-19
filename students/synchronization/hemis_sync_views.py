import time

from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import AllowOnlyTrustedOrigins
from semestr.models import Hsemester_action
from shared.permissions import IsAdmin
from students.synchronization.utils import bulk_sync_students
from students.synchronization.utils import fetch_hemis_students


class HemisBaseStudentsAPIView(APIView):
    education_form = None
    success_message = "Talabalar sinxronlash yakunlandi"

    def get(self, request, *args, **kwargs):

        start_time = time.perf_counter()

        groups = list(
            Hsemester_action.objects.filter(
                current=True,
                curriculum__educationform__code=self.education_form
            ).values_list(
                'curriculum__group_curriculum__h_id',
                flat=True
            )
        )

        if not groups:
            return Response({
                "error": "Hsemester_action modelda current=True bo‘lgan ma’lumot topilmadi",
                "education_form": self.education_form,
                "hint": "Avval semestr_action sync qilinganini tekshiring"
            }, status=400)

        total_created = 0
        total_updated = 0
        total_skipped = 0
        request_counter = 0
        sync_errors = []

        for group_id in groups:

            page = 1
            page_count = 1

            while page <= page_count:
                print(f"[PAGE] group={group_id} page={page}/{page_count}")
                res_data, error = fetch_hemis_students(
                    education_form=self.education_form,
                    group_id=group_id,
                    limit=50,
                    page=page
                )

                if res_data is None:
                    sync_errors.append({
                        "group_id": group_id,
                        "page": page,
                        "error": "Hemisdan response kelmadi"
                    })
                    break

                data = res_data.get("data")

                if error:
                    sync_errors.append({
                        "group_id": group_id,
                        "page": page,
                        "error": error
                    })
                    break

                if not data:
                    sync_errors.append({
                        "group_id": group_id,
                        "page": page,
                        "error": "Hemisdan data bo‘sh qaytdi",
                        "raw": res_data
                    })
                    break

                students = data.get("items", [])
                pagination = data.get("pagination", {})

                if not students:
                    break

                result = bulk_sync_students(students)

                total_created += result['students_created']
                total_updated += result['students_updated']
                total_skipped += result['skipped']

                page_count = pagination.get("pageCount", 1)
                page += 1

                request_counter += 1
                if request_counter >= 5:
                    time.sleep(1)
                    request_counter = 0

        spent_time = round(time.perf_counter() - start_time, 2)

        return Response({
            "message": self.success_message,
            "education_form": self.education_form,
            "groups_count": len(groups),
            "created": total_created,
            "updated": total_updated,
            "skipped": total_skipped,
            "time_spent_seconds": spent_time,
            "errors": sync_errors[:20]
        })


# ------------------ Asosiy ta'lim shakllari ------------------


class HemisExternalStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    education_form = 13
    success_message = "Sirtqi ta'lim talabalarni sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Sirtqi ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan sirtqi ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HemisDaytimeStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Kunduzgi ta'lim shaklidagi talabalar"""
    education_form = 11
    success_message = "Kunduzgi talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Kunduzgi ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan kunduzgi ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HemisEveningStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Kechki ta'lim shaklidagi talabalar"""
    education_form = 12
    success_message = "Kechki ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Kechki ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan kechki ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HemisDistanceStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Masofaviy ta'lim shaklidagi talabalar"""
    education_form = 16
    success_message = "Masofaviy ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Masofaviy ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan masofaviy ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ------------------ Ikkinchi oliy ------------------

class HemisSecondDegreeDaytimeStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Ikkinchi oliy (kunduzgi) talabalar"""
    education_form = 18
    success_message = "Ikkinchi oliy (kunduzgi) ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Ikkinchi oliy (kunduzgi) ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan ikkinchi oliy (kunduzgi) ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HemisSecondDegreeEveningStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Ikkinchi oliy (kechki) talabalar"""
    education_form = 19
    success_message = "Ikkinchi oliy (kechki) ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Ikkinchi oliy (kechki) ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan ikkinchi oliy (kechki) ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HemisSecondDegreeExternalStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Ikkinchi oliy (sirtqi) talabalar"""
    education_form = 15
    success_message = "Ikkinchi oliy (sirtqi) ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Ikkinchi oliy (sirtqi) ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan ikkinchi oliy (sirtqi) ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HemisSecondDegreeDistanceStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Ikkinchi oliy (masofaviy) talabalar"""
    education_form = 22
    success_message = "Ikkinchi oliy (masofaviy) ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Ikkinchi oliy (masofaviy) ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan ikkinchi oliy (masofaviy) ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ------------------ Qo‘shma ta'lim ------------------

class HemisJointDaytimeStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Qo‘shma ta'lim (kunduzgi) talabalar"""
    education_form = 20
    success_message = "Qo‘shma ta'lim (kunduzgi) ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Qo‘shma ta'lim (kunduzgi) ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan qo‘shma ta'lim (kunduzgi) ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HemisJointEveningStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Qo‘shma ta'lim (kechki) talabalar"""
    education_form = 21
    success_message = "Qo‘shma ta'lim (kechki) ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Qo‘shma ta'lim (kechki) ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan qo‘shma ta'lim (kechki) ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HemisJointExternalStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Qo‘shma ta'lim (sirtqi) talabalar"""
    education_form = 17
    success_message = "Qo‘shma ta'lim (sirtqi) ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Qo‘shma ta'lim (sirtqi) ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan qo‘shma ta'lim (sirtqi) ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HemisJointDistanceStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Qo‘shma ta'lim (masofaviy) talabalar"""
    education_form = 23
    success_message = "Qo‘shma ta'lim (masofaviy) ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Qo‘shma ta'lim (masofaviy) ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan qo‘shma ta'lim (masofaviy) ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ------------------ Maxsus ------------------

class HemisSpecialExternalStudentsAPIView(HemisBaseStudentsAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    """Maxsus sirtqi ta'lim shaklidagi talabalar"""
    education_form = 14
    success_message = "Maxsus sirtqi ta'lim talabalar sinxronlash yakunlandi"

    @swagger_auto_schema(
        operation_summary="Maxsus sirtqi ta'lim talabalarni sinxronlash",
        operation_description="Hemisdan maxsus sirtqi  ta'lim shaklidagi talabalarni olib LMS tizimiga yozadi",
        tags=["Hemis Talabalar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
