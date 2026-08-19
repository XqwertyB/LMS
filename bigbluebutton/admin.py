from django.contrib import admin

from .models import BigbluebuttonMain, Bigbluebutton_sub, Bigbluebutton_Model


@admin.register(BigbluebuttonMain)
class BigbluebuttonMainAdmin(admin.ModelAdmin):
    pass


@admin.register(Bigbluebutton_sub)
class Bigbluebutton_subMainAdmin(admin.ModelAdmin):
    list_display = ['uniq_id', 'name']
    pass


@admin.register(Bigbluebutton_Model)
class Bigbluebutton_ModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'status', 'meetingID', 'attendeePW', 'moderatorPW', 'voiceBridge', 'maxParticipants', 'topic_id',
        'team_id')
    list_filter = ['status', 'topic_id', 'team_id']
    search_fields = ['name', 'meetingID', 'attendeePW', ]
