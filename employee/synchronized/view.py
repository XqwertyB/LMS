import logging
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import RLock

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from django.contrib.auth.hashers import make_password
from django.db import connections, transaction

from employee.models import Employee
from shared.models import Gender, EmployeeStatus
from universty.models import Department
from user.models import User

logger = logging.getLogger(__name__)

# Module-level job registry (per-process). Status endpoint shu jarayon ichida ishlaydi —
# bir nechta gunicorn worker bo'lsa, status faqat sync boshlangan workerda ko'rinadi,
# lekin sync har holda backgroundda davom etadi va to'liq yakunlanadi.
_sync_jobs = {}
_sync_jobs_lock = RLock()
_MAX_KEEP_JOBS = 20


def _build_session(token, pool_size: int = 20, retries: int = 3) -> requests.Session:
    """Connection-pooling va retry'li sessiya."""
    sess = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=pool_size,
        pool_maxsize=pool_size,
    )
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    sess.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"{token.hemis_token_type} {token.hemis_token}",
    })
    return sess


class EmployeeClient:
    def __init__(self, hemis, token, session: requests.Session = None):
        self.hemis = hemis
        self.token = token
        self.base_url = hemis.base_url + hemis.path_url
        self.session = session or _build_session(token)
        self.params = {'limit': '200', 'type': 'teacher'}

    def _fetch_page(self, page: int):
        resp = self.session.get(
            self.base_url,
            params={**self.params, "page": page},
            timeout=(10, 30),
        )
        resp.raise_for_status()
        return resp.json()["data"]["items"]

    def sync_teachers(self, max_workers: int = 10, progress_cb=None):
        resp = self.session.get(self.base_url, params=self.params, timeout=(10, 30))
        resp.raise_for_status()
        total_pages = int(resp.json()["data"]["pagination"]["pageCount"])

        if progress_cb:
            progress_cb({"phase": "fetching", "total_pages": total_pages, "fetched_pages": 0})

        # reference tables
        departments = {d.hemisid: d for d in Department.objects.all()}
        genders = {g.code: g for g in Gender.objects.all()}
        statuses = {s.code: s for s in EmployeeStatus.objects.all()}

        all_teachers = []
        fetched = 0
        errors = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._fetch_page, page): page for page in range(1, total_pages + 1)}
            for future in as_completed(futures):
                page = futures[future]
                try:
                    items = future.result()
                    all_teachers.extend(items)
                except Exception as e:
                    errors.append({"page": page, "error": str(e)})
                    logger.warning("HEMIS teacher page %s error: %s", page, e)
                fetched += 1
                if progress_cb:
                    progress_cb({
                        "phase": "fetching",
                        "total_pages": total_pages,
                        "fetched_pages": fetched,
                    })

        if progress_cb:
            progress_cb({"phase": "processing", "total_items": len(all_teachers)})

        existing_employees = {e.employee_id_number: e for e in Employee.objects.all()}

        new_users, new_employees, update_employees = [], [], []

        for t in all_teachers:
            employee_id = t.get("employee_id_number")
            if not employee_id:
                continue

            if employee_id not in existing_employees:
                new_users.append(User(
                    username=employee_id,
                    role='teacher',
                    first_name=t.get("first_name") or "",
                    last_name=t.get("second_name") or "",
                    password=make_password(employee_id),
                ))
                new_employees.append(Employee(
                    employee_id_number=employee_id,
                    department=departments.get(t.get("department", {}).get("id")),
                    e_status=statuses.get(t.get("employeeStatus", {}).get("code")),
                    gender=genders.get(t.get("gender", {}).get("code")),
                    first_name=t.get("first_name") or "",
                    second_name=t.get("second_name") or "",
                    full_name=t.get("full_name") or "",
                    father_name=t.get("father_name") or "",
                    birth_date=t.get("birth_date") or "",
                    user=None,
                ))
            else:
                emp = existing_employees[employee_id]
                emp.department = departments.get(t.get("department", {}).get("id"))
                emp.e_status = statuses.get(t.get("employeeStatus", {}).get("code"))
                emp.gender = genders.get(t.get("gender", {}).get("code"))
                emp.first_name = t.get("first_name") or ""
                emp.second_name = t.get("second_name") or ""
                emp.full_name = t.get("full_name") or ""
                emp.father_name = t.get("father_name") or ""
                emp.birth_date = t.get("birth_date") or ""
                update_employees.append(emp)

        with transaction.atomic():
            if new_users:
                User.objects.bulk_create(new_users, ignore_conflicts=True, batch_size=500)
                saved_users = User.objects.filter(username__in=[u.username for u in new_users])
                users_dict = {u.username: u for u in saved_users}
                for emp in new_employees:
                    emp.user = users_dict.get(emp.employee_id_number)

            if new_employees:
                Employee.objects.bulk_create(new_employees, ignore_conflicts=True, batch_size=500)
            if update_employees:
                Employee.objects.bulk_update(
                    update_employees,
                    [
                        "department", "e_status", "gender",
                        "first_name", "second_name", "full_name",
                        "father_name", "birth_date",
                    ],
                    batch_size=500,
                )

        return {
            "synced": len(new_employees) + len(update_employees),
            "created": len(new_employees),
            "updated": len(update_employees),
            "skipped": len(all_teachers) - (len(new_employees) + len(update_employees)),
            "fetch_errors": errors,
        }


def _trim_jobs():
    if len(_sync_jobs) <= _MAX_KEEP_JOBS:
        return
    finished = [
        (jid, info) for jid, info in _sync_jobs.items()
        if info.get("status") in ("completed", "failed")
    ]
    finished.sort(key=lambda x: x[1].get("finished_at") or "")
    while len(_sync_jobs) > _MAX_KEEP_JOBS and finished:
        jid, _ = finished.pop(0)
        _sync_jobs.pop(jid, None)


def start_sync_teachers_job(hemis, token, max_workers: int = 10):
    """Sinxronlashni background threadda ishga tushiradi, job_id qaytaradi.

    Agar shu paytda boshqa sync ishlayotgan bo'lsa, mavjud job ma'lumotini qaytaradi.
    """
    with _sync_jobs_lock:
        for jid, info in _sync_jobs.items():
            if info.get("status") in ("pending", "running"):
                return {
                    "job_id": jid,
                    "status": info["status"],
                    "started_at": info.get("started_at"),
                    "progress": info.get("progress", {}),
                    "already_running": True,
                }

        job_id = str(uuid.uuid4())
        _sync_jobs[job_id] = {
            "status": "pending",
            "started_at": datetime.utcnow().isoformat() + "Z",
            "progress": {},
            "result": None,
            "error": None,
            "finished_at": None,
        }
        _trim_jobs()

    def _progress(p):
        with _sync_jobs_lock:
            job = _sync_jobs.get(job_id)
            if job is not None:
                job["progress"] = p

    def _run():
        with _sync_jobs_lock:
            _sync_jobs[job_id]["status"] = "running"
        t0 = time.time()
        try:
            client = EmployeeClient(hemis, token)
            result = client.sync_teachers(max_workers=max_workers, progress_cb=_progress)
            result["elapsed_time"] = round(time.time() - t0, 2)
            with _sync_jobs_lock:
                _sync_jobs[job_id]["status"] = "completed"
                _sync_jobs[job_id]["result"] = result
                _sync_jobs[job_id]["finished_at"] = datetime.utcnow().isoformat() + "Z"
        except Exception as e:
            logger.exception("HEMIS teachers sync failed: %s", e)
            with _sync_jobs_lock:
                _sync_jobs[job_id]["status"] = "failed"
                _sync_jobs[job_id]["error"] = str(e)
                _sync_jobs[job_id]["finished_at"] = datetime.utcnow().isoformat() + "Z"
        finally:
            # Thread tugagach Django DB connectionlarni bo'shatish kerak,
            # aks holda ular tashlab ketiladi (resource leak).
            connections.close_all()

    threading.Thread(
        target=_run,
        name=f"hemis-sync-teachers-{job_id}",
        daemon=True,
    ).start()

    return {
        "job_id": job_id,
        "status": "pending",
        "started_at": _sync_jobs[job_id]["started_at"],
        "progress": {},
        "already_running": False,
    }


def get_sync_teachers_job(job_id):
    with _sync_jobs_lock:
        job = _sync_jobs.get(job_id)
        if job is None:
            return None
        return dict(job)
