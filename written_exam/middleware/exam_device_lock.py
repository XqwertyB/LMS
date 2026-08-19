from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse

from written_exam.models import ExamSession, WrittenExamAttempt


class ExamDeviceLockMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not request.path.startswith("/api/exam/"):
            return self.get_response(request)

        attempt_id = request.headers.get("X-Attempt-ID")
        device_hash = request.headers.get("X-Device-Hash")

        if not attempt_id or not device_hash:
            return self.get_response(request)

        try:
            with transaction.atomic():

                attempt = (
                    WrittenExamAttempt.objects
                    .select_for_update()
                    .select_related("session", "exam", "student__user")
                    .get(id=attempt_id)
                )

                if attempt.student.user != request.user:
                    return JsonResponse(
                        {"error": "Ushbu urinish sizga tegishli emas"},
                        status=403
                    )

                if attempt.status != "in_progress":
                    return self.get_response(request)

                session = attempt.session

                if not session.status:
                    return JsonResponse(
                        {"error": "Sessiya yopilgan"},
                        status=403
                    )

                now = timezone.now()
                timeout = timedelta(minutes=attempt.exam.inactivity_timeout_minutes)

                if now - session.last_activity > timeout:
                    session.device_hash = device_hash
                else:
                    if session.device_hash and session.device_hash != device_hash:
                        return JsonResponse(
                            {"error": "Imtihon boshqa qurilmada ochilgan"},
                            status=403
                        )

                session.last_activity = now
                session.locked = True
                session.save(update_fields=["device_hash", "last_activity", "locked"])

        except (WrittenExamAttempt.DoesNotExist, ExamSession.DoesNotExist):
            return JsonResponse(
                {"error": "Sessiya topilmadi"},
                status=403
            )

        return self.get_response(request)
