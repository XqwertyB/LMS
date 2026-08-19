from django.core.management.base import BaseCommand
from bigbluebutton.models import BigbluebuttonMain, Bigbluebutton_sub
from config.settings import BIGBLUEBUTTON_SECRET,BIGBLUEBUTTON_URL

class Command(BaseCommand):
    help = 'Prints "Hello, World!" to the console'

    def handle(self, *args, **options):
        base_url = BIGBLUEBUTTON_URL+'/bigbluebutton'
        obj_check = BigbluebuttonMain.objects.filter(main_url=base_url).exists()
        if obj_check:
            obj = BigbluebuttonMain.objects.get(main_url=base_url)

            if Bigbluebutton_sub.objects.filter(uniq_id=1).exists():

                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=1)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'Create_Zoom'
                obj_sub.uniq_id = 1
                obj_sub.url = '/api/create'
                obj_sub.url_method = 'create'
                obj_sub.comment = 'Zoom meeting room yartish'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=2).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=2)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'Join as moderator'
                obj_sub.uniq_id = 2
                obj_sub.url = '/api/join'
                obj_sub.url_method = 'join'
                obj_sub.comment = 'Join as Moderator'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=3).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=3)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'End Zoom room'
                obj_sub.uniq_id = 3
                obj_sub.url = '/api/end'
                obj_sub.url_method = 'end'
                obj_sub.comment = 'Zoom xonani yopish'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=4).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=4)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'isMeetingRunning'
                obj_sub.uniq_id = 4
                obj_sub.url = '/api/isMeetingRunning'
                obj_sub.url_method = 'isMeetingRunning'
                obj_sub.comment = 'Meeting  davom etvotgani haqida ma`lumotlarni olish'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=5).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=5)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'getMeetingInfo'
                obj_sub.uniq_id = 5
                obj_sub.url = '/api/getMeetingInfo'
                obj_sub.url_method = 'getMeetingInfo'
                obj_sub.comment = 'Meeting haqida malumot olish'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=6).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=6)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'getMeetings'
                obj_sub.uniq_id = 6
                obj_sub.url = '/api/getMeetings'
                obj_sub.url_method = 'getMeetings'
                obj_sub.comment = 'Meetlaring haqida malumot olish'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=7).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=7)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'EndMeeting'
                obj_sub.uniq_id = 7
                obj_sub.url = '/api/end'
                obj_sub.url_method = 'end'
                obj_sub.comment = 'Meeting yopish'
                obj_sub.save()
        else:
            obj = BigbluebuttonMain()
            obj.main_url = base_url
            obj.sicret_key = BIGBLUEBUTTON_SECRET
            obj.save()

            if Bigbluebutton_sub.objects.filter(uniq_id=1).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=1)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'Create_Zoom'
                obj_sub.uniq_id = 1
                obj_sub.url = '/api/create'
                obj_sub.url_method = 'create'
                obj_sub.comment = 'Zoom meeting room yartish'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=2).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=2)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'Join as moderator'
                obj_sub.uniq_id = 2
                obj_sub.url = '/api/join'
                obj_sub.url_method = 'join'
                obj_sub.comment = 'Join as Moderator'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=3).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=3)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'End Zoom room'
                obj_sub.uniq_id = 3
                obj_sub.url = '/api/end'
                obj_sub.url_method = 'end'
                obj_sub.comment = 'Zoom xonani yopish'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=4).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=4)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'isMeetingRunning'
                obj_sub.uniq_id = 4
                obj_sub.url = '/api/isMeetingRunning'
                obj_sub.url_method = 'isMeetingRunning'
                obj_sub.comment = 'Meeting  davom etvotgani haqida ma`lumotlarni olish'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=5).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=5)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'getMeetingInfo'
                obj_sub.uniq_id = 5
                obj_sub.url = '/api/getMeetingInfo'
                obj_sub.url_method = 'getMeetingInfo'
                obj_sub.comment = 'Meeting haqida malumot olish'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=6).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=6)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'getMeetings'
                obj_sub.uniq_id = 6
                obj_sub.url = '/api/getMeetings'
                obj_sub.url_method = 'getMeetings'
                obj_sub.comment = 'Meetlaring haqida malumot olish'
                obj_sub.save()
            if Bigbluebutton_sub.objects.filter(uniq_id=7).exists():
                obj_sub = Bigbluebutton_sub.objects.get(uniq_id=7)
            else:
                obj_sub = Bigbluebutton_sub()
                obj_sub.name = 'EndMeeting'
                obj_sub.uniq_id = 7
                obj_sub.url = '/api/end'
                obj_sub.url_method = 'end'
                obj_sub.comment = 'Meeting yopish'
                obj_sub.save()

        self.stdout.write('Yangilanish!')
