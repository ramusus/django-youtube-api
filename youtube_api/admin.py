# -*- coding: utf-8 -*-
from django.contrib import admin
from models import Video


class AllFieldsReadOnly(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in obj._meta.fields]
        return []


class VideoAdmin(AllFieldsReadOnly):
    def youtube_link(self, obj):
        return u'<a href="%s">link</a>' % (obj.get_url())

    youtube_link.allow_tags = True

    list_display = ['video_id', 'title', 'youtube_link']
    list_display_links = ['video_id', 'title',]
    search_fields = ('title', 'description')


admin.site.register(Video, VideoAdmin)
