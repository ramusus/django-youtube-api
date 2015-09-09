# -*- coding: utf-8 -*-
from django.contrib import admin
from models import Video


class AllFieldsReadOnly(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in obj._meta.fields]
        return []


class VideoAdmin(AllFieldsReadOnly):
    pass
    # def instagram_link(self, obj):
    #     return u'<a href="%s">%s</a>' % (obj.link, obj.link)
    #
    # instagram_link.allow_tags = True
    #
    # list_display = ['id', 'user', 'caption', 'created_time', 'instagram_link']
    # search_fields = ('caption',)


admin.site.register(Video, VideoAdmin)
