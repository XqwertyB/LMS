from django.core.exceptions import ValidationError
from django.db import models
from shared.models import BaseModel
import uuid
import random
import string
from content.models import Topic, LessonRoom


def generate_random_password():
    length = 8  # You can adjust the length of the password as needed
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


# Create your models here.
class BigbluebuttonMain(BaseModel, models.Model):
    main_url = models.CharField(max_length=250, unique=True)
    sicret_key = models.CharField(max_length=250)
    status_name = [
        (True, 'Faol'),
        (False, 'Faol emas')
    ]
    status = models.BooleanField(status_name, default=True)


class Bigbluebutton_sub(BaseModel, models.Model):
    name = models.CharField(max_length=250)
    uniq_id = models.IntegerField(unique=True, null=True, blank=True)
    method_name = [
        (True, 'GET'),
        (False, 'POST')
    ]
    method = models.BooleanField(choices=method_name, default=True)
    url = models.CharField(max_length=250)
    url_method = models.CharField(max_length=250, null=True)
    auth_name = [
        (True, 'Mavjud'),
        (False, 'Mavjud emas')
    ]
    auth_is = models.BooleanField(choices=auth_name, default=False)
    comment = models.TextField(null=True, blank=True)


class Bigbluebutton_Model(BaseModel, models.Model):
    name = models.CharField(max_length=250)
    meetingID = models.UUIDField(primary_key=False, editable=True, default=uuid.uuid4,
                                 unique=True)  # unikal bo`lishi shart
    recordID = models.UUIDField(primary_key=False, editable=True)
    attendeePW = models.CharField(max_length=250, null=True, blank=True)  # ishtrokchi paroli
    moderatorPW = models.CharField(max_length=250, null=True, blank=True)  # moderator parol
    welcome = models.TextField(null=True, blank=True)
    # fullName = models.CharField(max_length=250, null=True, blank=True)
    # dialNumber
    voiceBridge = models.IntegerField(null=True, blank=True)  # in the range 10000 to 99999
    maxParticipants = models.IntegerField(null=True,
                                          blank=True)  # bir vaqtda qoshilish mumkin bo`lgan foydalanuvchi maxium soni
    logoutURL = models.CharField(max_length=250, null=True, blank=True)
    record = models.BooleanField(null=True, blank=True)
    redirect = models.BooleanField(null=True, blank=True)
    logoutURL = models.CharField(max_length=250, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True, default=86400)  # minutda
    # isBreakout = models.BooleanField(default=True)
    status_name = [
        (True, 'Zoom xona ochildi'),
        (False, 'Zoom xonasi yopiq')
    ]
    status = models.BooleanField(default=False, choices=status_name)
    allowStartStopRecording = models.BooleanField(default=True)
    autoStartRecording = models.BooleanField(default=True)
    meetingExpireIfNoUserJoinedInMinutes = models.IntegerField(null=True, blank=True, default=86400)
    meetingExpireWhenLastUserLeftInMinutes = models.IntegerField(null=True, blank=True, default=86400)
    topic_id = models.OneToOneField(Topic, on_delete=models.SET_NULL, related_name='topic_bigbluebutton', null=True,
                                    blank=True)
    team_id = models.OneToOneField(LessonRoom, on_delete=models.SET_NULL, related_name='team_bigbluebutton', null=True,
                                   blank=True)

    def add_random_field(self, name, count_user):
        self.recordID = self.meetingID
        self.moderatorPW = generate_random_password()
        while True:
            genpasswrod = generate_random_password()
            if self.moderatorPW != genpasswrod:
                break
        self.attendeePW = genpasswrod
        while True:
            random_voiceBridge = random.randint(10000, 99999)
            if not Bigbluebutton_Model.objects.filter(voiceBridge=random_voiceBridge).exists():
                self.voiceBridge = random_voiceBridge
                break
        self.welcome = 'Xush kelibsiz!'
        if count_user > 230:
            raise ValidationError({
                'error': True,
                'message': 'Talabalar soni chegaradan oshib ketdi(max=230)'
            })
        self.maxParticipants = count_user+5
        self.record = False
        self.duration = 0
        self.meetingExpireWhenLastUserLeftInMinutes = 0
        self.meetingExpireIfNoUserJoinedInMinutes = 5
        self.redirect = False
        if name is None:
            name = 'Dars'+str(random_voiceBridge)
        self.name = name

    def add_restart_field(self, name, count_user):

        while True:
            random_voiceBridge = random.randint(10000, 99999)
            if not Bigbluebutton_Model.objects.filter(voiceBridge=random_voiceBridge).exists():
                self.voiceBridge = random_voiceBridge
                break
        self.welcome = 'Xush kelibsiz!'
        if count_user > 230:
            raise ValidationError({
                'error': True,
                'message': 'Talabalar soni chegaradan oshib ketdi(max=230)'
            })
        self.maxParticipants = count_user + 5
        self.record = False
        self.duration = 0
        self.meetingExpireWhenLastUserLeftInMinutes = 0
        self.meetingExpireIfNoUserJoinedInMinutes = 5
        self.redirect = False
        if name is None:
            name = 'Dars' + str(random_voiceBridge)
        self.name = name
