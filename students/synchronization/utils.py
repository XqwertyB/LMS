import requests
from django.db import transaction

from group.models import Group
from hemis.models import HemisToken
from hemis.models import Hemis_Base
from learning_process.models import Educationform
from learning_process.models import Educationlang
from learning_process.models import Educationtype
from learning_process.models import Educationyear
from semestr.models import HCourse
from semestr.models import Hsemester_action
from shared.models import FormOfPayment
from shared.models import Gender
from shared.models import H_Accommodation
from shared.models import H_Citizenship_type
from shared.models import H_Social_Category
from shared.models import H_Student_Status
from shared.models import State
from speciality.models import AllSpeciality
from students.models import Student
from universty.models import City
from universty.models import Faculty
from user.models import User


def fetch_hemis_students(education_form, page=1, limit=50, group_id=None):
    try:
        hemis = Hemis_Base.objects.get(own_uniq=8)
    except Hemis_Base.DoesNotExist:
        return None, {'error': 'Hemis modulida biriktirilmagan'}

    if hemis.openapi:
        return None, {'error': 'Tokensiz murojaat qilib bo‘lmaydi'}

    token = HemisToken.objects.filter(
        status=True,
        hemis_user=hemis.hemis_user
    ).first()

    if not token:
        return None, {'error': 'Faol token mavjud emas!'}

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"{token.hemis_token_type} {token.hemis_token}"
    }

    params = {
        'page': page,
        'limit': limit,
        '_education_form': education_form
    }

    if group_id is not None:
        params['_group'] = group_id

    url = hemis.base_url + hemis.path_url

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)

        if response.status_code == 401:
            return None, {'error': 'Hemis token muddati tugagan'}

        if response.status_code >= 500:
            return None, {'error': 'Hemis serverida xatolik yuz berdi'}

        response.raise_for_status()

        return response.json(), None

    except requests.Timeout:
        return None, {'error': 'Hemis server javobi juda sekin (timeout)'}

    except requests.RequestException as e:
        return None, {'error': f'Hemisga so‘rov yuborishda xatolik: {str(e)}'}


# ---------------- FK CACHE ---------------- #

def load_fk_cache():

    return {
        "gender": {g.code: g for g in Gender.objects.all()},
        "education_form": {e.code: e for e in Educationform.objects.all()},
        "educationLang": {e.code: e for e in Educationlang.objects.all()},
        "education_type": {e.code: e for e in Educationtype.objects.all()},
        "education_year": {e.code: e for e in Educationyear.objects.all()},
        "paymentForm": {e.code: e for e in FormOfPayment.objects.all()},

        "faculty": {f.hemisid: f for f in Faculty.objects.all()},
        "group": {g.h_id: g for g in Group.objects.all()},
        "new_specialty": {s.spec_id: s for s in AllSpeciality.objects.all()},

        "level": {l.code: l for l in HCourse.objects.all()},
        "semester": {s.h_id: s for s in Hsemester_action.objects.all()},

        "country": {c.code: c for c in State.objects.all()},
        "city": {c.code: c for c in City.objects.all()},

        "citizenship": {c.code: c for c in H_Citizenship_type.objects.all()},
        "status": {s.code: s for s in H_Student_Status.objects.all()},
        "social": {s.code: s for s in H_Social_Category.objects.all()},
        "accommodation": {a.code: a for a in H_Accommodation.objects.all()},
    }


# ---------------- MAIN BULK SYNC ---------------- #

def bulk_sync_students(items):
    import time
    start = time.perf_counter()

    cache = load_fk_cache()
    print(f"[CACHE LOAD] {round(time.perf_counter() - start, 3)}s")
    student_numbers = [i['student_id_number'] for i in items]

    existing_students = {
        s.student_id_number: s
        for s in Student.objects.filter(
            student_id_number__in=student_numbers
        ).select_related("user")
    }

    existing_users = {
        u.username: u
        for u in User.objects.filter(username__in=student_numbers)
    }

    users_to_create = []
    students_to_create = []
    students_to_update = []

    skipped = 0

    for item in items:

        try:
            gender = cache['gender'][item['gender']['code']]
            education_form = cache['education_form'][item['educationForm']['code']]
            education_type = cache['education_type'][item['educationType']['code']]
            education_year = cache['education_year'][item['educationYear']['code']]
            edu_lang = cache['educationLang'][item['group']['educationLang']['code']]
            payment_form = cache['paymentForm'][item['paymentForm']['code']]

            faculty = cache['faculty'][item['department']['id']]
            group = cache['group'][item['group']['id']]
            new_specialty = cache['new_specialty'][item['specialty']['id']]

            level = cache['level'][item['level']['code']]
            semester = cache['semester'][item['semester']['id']]

            country = cache['country'][item['country']['code']]
            province = cache['city'][item['province']['code']]
            district = cache['city'][item['district']['code']]

            citizenship = cache['citizenship'][item['citizenship']['code']]
            status = cache['status'][item['studentStatus']['code']]
            social = cache['social'][item['socialCategory']['code']]
            accommodation = cache['accommodation'][item['accommodation']['code']]

        except KeyError:
            skipped += 1
            continue

        username = item['student_id_number']

        # -------- USER -------- #

        user = existing_users.get(username)

        if not user:
            user = User(
                username=username,
                first_name=item['first_name'],
                last_name=item['second_name'],
                email=item['email'] or "",
                role="student",
                password="!"  # unusable password (xavfsiz)
            )
            users_to_create.append(user)
            existing_users[username] = user

        # -------- STUDENT DATA -------- #

        student_data = {
            'user': user,
            'first_name': item['first_name'],
            'second_name': item['second_name'],
            'third_name': item['third_name'],
            'full_name': item['full_name'],
            'birth_date': item['birth_date'],
            'email': item['email'],
            'image': item['image_full'],
            'gender': gender,
            'new_specialty': new_specialty,
            'studentStatus': status,
            'educationForm': education_form,
            'educationType': education_type,
            'educationYear': education_year,
            'educationLang': edu_lang,
            'paymentForm': payment_form,
            'group': group,
            'faculty': faculty,
            'level': level,
            'semester': semester,
            'country': country,
            'province': province,
            'district': district,
            'citizenship': citizenship,
            'socialCategory': social,
            'accommodation': accommodation,
            'university': item['university']['name'],
            'validateUrl': item['validateUrl'],
            'year_of_enter': item['year_of_enter'],
            'avg_gpa': item['avg_gpa'],
            'total_credit': item['total_credit'],
        }

        existing_student = existing_students.get(username)

        if existing_student:
            for k, v in student_data.items():
                setattr(existing_student, k, v)
            students_to_update.append(existing_student)
        else:
            students_to_create.append(
                Student(
                    student_id_number=username,
                    **student_data
                )
            )

    # ---------------- SAVE ---------------- #

    with transaction.atomic():

        if users_to_create:
            User.objects.bulk_create(users_to_create, batch_size=100)

        if students_to_create:
            Student.objects.bulk_create(students_to_create, batch_size=100)

        if students_to_update:
            Student.objects.bulk_update(
                students_to_update,
                fields=list(student_data.keys()),
                batch_size=100
            )
    spent = round(time.perf_counter() - start, 3)
    print(
        f"[SYNC] create={len(students_to_create)} "
        f"update={len(students_to_update)} "
        f"time={spent}s"
    )
    return {
        "users_created": len(users_to_create),
        "students_created": len(students_to_create),
        "students_updated": len(students_to_update),
        "skipped": skipped
    }
