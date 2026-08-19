from django.contrib import admin
from .models import HemisToken,HemisModel,Hemis_Base,Hemis_sub

# Register your models here.


class HemisTokenAdmin(admin.TabularInline):
    model = HemisToken



@admin.register(HemisModel)
class HemisModelAdmin(admin.ModelAdmin):
    inlines = [HemisTokenAdmin,]

    pass

@admin.register(Hemis_Base)
class Hemis_BaseModelAdmin(admin.ModelAdmin):
    list_display = ['name','own_uniq']

    pass


@admin.register(Hemis_sub)
class Hemis_subModelAdmin(admin.ModelAdmin):


    pass
