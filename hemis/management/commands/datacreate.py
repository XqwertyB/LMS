from django.core.management.base import BaseCommand
from hemis.models import HemisModel, HemisToken, Hemis_Base
from config.settings import HEMIS_URL,HEMIS_SECRET

class Command(BaseCommand):
    help = 'Prints "Hello, World!" to the console'

    def handle(self, *args, **options):

        obj_check = HemisModel.objects.filter(fio='LMS').exists()
        #base_url = "https://student.tfi.uz"
        base_url = HEMIS_URL
        if obj_check:
            obj = HemisModel.objects.get(fio='LMS')
            token = HemisToken.objects.filter(hemis_user=obj, status=True).last()
            if token.status:
                print('Mavjud hemis model')
            else:
                hemis_token = HemisToken()
                hemis_token.hemis_user = obj
                hemis_token.hemis_token = HEMIS_SECRET
                hemis_token.hemis_token_type = 'Bearer'
                hemis_token.save()
        else:
            obj = HemisModel()
            obj.fio = 'LMS'
            obj.hemis_login = 'LMS'
            obj.hemis_password = '123'
            obj.save()
            hemis_token = HemisToken()
            hemis_token.hemis_user = obj
            hemis_token.hemis_token = HEMIS_SECRET
            hemis_token.hemis_token_type = 'Bearer'
            hemis_token.save()
        if Hemis_Base.objects.filter(own_uniq=1).exists():
            print("Mavjud Unver hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/public/university-profile"
            hemis_base.name = "Universitet malumotlari"
            hemis_base.comment = "Ochiq ma`lumotlar"
            hemis_base.openapi = True
            hemis_base.own_uniq = 1
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=2).exists():
            print("Mavjud Klasifatorlar ro`yhati hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/classifier-list"
            hemis_base.name = "Klasifatorlar ro`yhati"
            hemis_base.comment = "Talim shakli,Talim turi va boshqalar"
            hemis_base.openapi = False
            hemis_base.own_uniq = 2
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=3).exists():
            print("Mavjud Klasifatorlar ro`yhati hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/department-list"
            hemis_base.name = "Fakulltet va bo`limlar"
            hemis_base.comment = "Bo`limlar olish"
            hemis_base.openapi = False
            hemis_base.own_uniq = 3
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=4).exists():
            print("Mavjud O`quv reja ro`yhati hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/curriculum-list"
            hemis_base.name = "O`quv reja ro`yhati"
            hemis_base.comment = "O`quv reja ro`yhati"
            hemis_base.openapi = False
            hemis_base.own_uniq = 4
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=5).exists():
            print("Mavjud Fakultet va Yonalishlar  boglash api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/specialty-list"
            hemis_base.name = "Fakultet va Yonalishlar  boglash"
            hemis_base.comment = "Fakultet va Yonalishlar  boglash"
            hemis_base.openapi = False
            hemis_base.own_uniq = 5
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=6).exists():
            print("Mavjud O`quv semestr va haftalarni birktrish hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/semester-list"
            hemis_base.name = "O`quv semestr va haftalarni birktrish"
            hemis_base.comment = "O`quv semestr va haftalarni birktrish"
            hemis_base.openapi = False
            hemis_base.own_uniq = 6
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=7).exists():
            print("Mavjud Gruhlarni qo`shish  hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/group-list"
            hemis_base.name = "Gruhlarni qo`shish "
            hemis_base.comment = "Gruhlarni qo`shish "
            hemis_base.openapi = False
            hemis_base.own_uniq = 7
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=8).exists():
            print("Mavjud Gruhlarni qo`shish  hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/student-list"
            hemis_base.name = "Talabalarni tortish "
            hemis_base.comment = "Talabalarni tortish "
            hemis_base.openapi = False
            hemis_base.own_uniq = 8
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=9).exists():
            print("Mavjud Hodimlarni qo`shish  hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/employee-list"
            hemis_base.name = "Hodimlarni tortib kelish "
            hemis_base.comment = "Hodimlarni tortib kelish "
            hemis_base.openapi = False
            hemis_base.own_uniq = 9
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=10).exists():
            print("Mavjud Gruhlarni qo`shish  hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/subject-meta-list"
            hemis_base.name = "Fanlarni ro`yhatini qo`shish "
            hemis_base.comment = "Fanlar ozinin ro`yhati "
            hemis_base.openapi = False
            hemis_base.own_uniq = 10
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=11).exists():
            print("Mavjud Gruhlarni qo`shish  hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/curriculum-subject-list"
            hemis_base.name = "o`quv reja va Fanlar boglash "
            hemis_base.comment = "o`quv rejadagi fanlar boglash "
            hemis_base.openapi = False
            hemis_base.own_uniq = 11
            hemis_base.save()
        if Hemis_Base.objects.filter(own_uniq=12).exists():
            print("Mavjud Yo`nalishlarni qo`shish  hemis api path")
        else:
            hemis_base = Hemis_Base()
            hemis_base.hemis_user = obj
            hemis_base.base_url = base_url
            hemis_base.path_url = "/rest/v1/data/specialty-list"
            hemis_base.name = "Yo`nalishlarni tortib kelish "
            hemis_base.comment = "Yo`nalishlarni tortib kelish "
            hemis_base.openapi = False
            hemis_base.own_uniq = 12
            hemis_base.save()

        self.stdout.write('Yangilanish!')
