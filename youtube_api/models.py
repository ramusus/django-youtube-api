# -*- coding: utf-8 -*-
import logging
import re
from dateutil import parser

from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.utils import timezone

from .api import api_call

__all__ = ['Video']

log = logging.getLogger('youtube_api')


class YoutubeContentError(Exception):
    pass


class YoutubeManager(models.Manager):
    """
    Youtube Manager for RESTful CRUD operations
    """
    def __init__(self, methods=None, remote_pk=None, *args, **kwargs):
        if methods and len(methods.items()) < 1:
            raise ValueError('Argument methods must contains at least 1 specified method')

        self.methods = methods or {}
        self.remote_pk = remote_pk or ('id',)
        if not isinstance(self.remote_pk, tuple):
            self.remote_pk = (self.remote_pk,)

        super(YoutubeManager, self).__init__(*args, **kwargs)

    def get_or_create_from_instance(self, instance):

        remote_pk_dict = {}
        for field_name in self.remote_pk:
            remote_pk_dict[field_name] = getattr(instance, field_name)

        try:
            old_instance = self.model.objects.get(**remote_pk_dict)
            instance._substitute(old_instance)
            instance.save()
        except self.model.DoesNotExist:
            instance.save()
            log.debug('Fetch and create new object %s with remote pk %s' % (self.model, remote_pk_dict))

        return instance

    def api_call(self, method, *args, **kwargs):
        if method in self.methods:
            method = self.methods[method]
        return api_call(method, *args, **kwargs)

    def fetch(self, *args, **kwargs):
        """
        Retrieve and save object to local DB
        """
        result = self.get(*args, **kwargs)
        if isinstance(result, list):
            return [self.get_or_create_from_instance(instance) for instance in result]
        else:
            return self.get_or_create_from_instance(result)

    def get(self, method='get', *args, **kwargs):
        """
        Retrieve objects from remote server
        """
        response = self.api_call(method, *args, **kwargs)

        extra_fields = kwargs.pop('extra_fields', {})
        extra_fields['fetched_at'] = timezone.now()
        return self.parse_response(response, extra_fields)

    def parse_response(self, response, extra_fields=None):
        if isinstance(response, (list, tuple)):
            return self.parse_response_list(response, extra_fields)
        # elif isinstance(response, ApiModel):
        #     return self.parse_response_object(response, extra_fields)
        else:
            raise YoutubeContentError('Youtube response should be list or ApiModel, not %s' % response)

    def parse_response_object(self, resource, extra_fields=None):

        instance = self.model()
        # important to do it before calling parse method
        if extra_fields:
            instance.__dict__.update(extra_fields)
        instance._resource = resource#.__dict__ if isinstance(resource, ApiModel) else resource
        instance.parse()

        return instance

    def parse_response_list(self, response_list, extra_fields=None):

        instances = []
        for response in response_list:
            instance = self.parse_response_object(response, extra_fields)
            instances += [instance]

        return instances


class YoutubeModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True

    def _substitute(self, old_instance):
        """
        Substitute new user with old one while updating in method Manager.get_or_create_from_instance()
        Can be overrided in child models
        """
        self.pk = old_instance.pk

    def parse(self):
        """
        Parse API response and define fields with values
        """
        for key, value in self._resource.items():
            if key == '_api':
                continue

            key = re.sub(r'([A-Z])', lambda m: '_' + m.group(0).lower(), key)

            try:
                field, model, direct, m2m = self._meta.get_field_by_name(key)
            except FieldDoesNotExist:
                log.debug('Field with name "%s" doesn\'t exist in the model %s' % (key, type(self)))
                continue

            # if isinstance(field, ForeignObjectRel) and value:
            #     # for item in value:
            #     # rel_instance = field.model.remote.parse_response_object(item)
            #     # self._external_links_post_save += [(field.field.name, rel_instance)]
            #     pass
            # else:
            if isinstance(field, models.DateTimeField) and value:
                value = parser.parse(value)

            elif isinstance(field, (models.BooleanField)):
                value = bool(value)

            elif isinstance(field, (models.IntegerField)) and value:
                try:
                    value = int(value)
                except:
                    pass

            # elif isinstance(field, (models.OneToOneField, models.ForeignKey)) and value:
            #     rel_instance = field.rel.to.remote.parse_response_object(value)
            #     value = rel_instance
            #     if isinstance(field, models.ForeignKey):
            #         self._foreignkeys_pre_save += [(key, rel_instance)]
            #
            # elif isinstance(field, (fields.CommaSeparatedCharField,
            #                         models.CommaSeparatedIntegerField)) and isinstance(value, list):
            #     value = ','.join([unicode(v) for v in value])

            elif isinstance(field, (models.CharField, models.TextField)) and value:
                if isinstance(value, (str, unicode)):
                    value = value.strip()

            setattr(self, key, value)


class YoutubeBaseModel(YoutubeModel):

    _resource = None

    fetched_at = models.DateTimeField(u'Fetched', blank=True)

    class Meta:
        abstract = True

    def get_url(self):
        return 'http://www.youtube.com/%s' % self.slug


class VideoManager(YoutubeManager):

    def fetch(self, *args, **kwargs):
        kwargs['part'] = 'snippet'
        if args:
            kwargs['id'] = ','.join(args)
        return super(VideoManager, self).fetch(**kwargs)

    def parse_response(self, response, extra_fields=None):
        response = response['items']
        return super(VideoManager, self).parse_response(response, extra_fields)

    def search(self, q, max_results=50, **kwargs):
        kwargs['part'] = 'snippet'
        kwargs['maxResults'] = max_results
        kwargs['q'] = q
        return self.get('search', **kwargs)


class Video(YoutubeBaseModel):

    video_id = models.CharField(max_length=11, primary_key=True)

    channel_id = models.CharField(max_length=24)
    channel_title = models.CharField(max_length=250)  # denormalization

    category_id = models.PositiveIntegerField(null=True)

    published_at = models.DateTimeField()

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)

    remote = VideoManager(remote_pk='video_id', methods={
        'get': 'videos',
        'search': 'search',
    })

    def __unicode__(self):
        return self.title

    @property
    def thumbnail_urls(self):
        return {
            "default": "https://i.ytimg.com/vi/%s/default.jpg" % self.video_id,
            "medium": "https://i.ytimg.com/vi/%s/mqdefault.jpg" % self.video_id,
            "high": "https://i.ytimg.com/vi/%s/hqdefault.jpg" % self.video_id,
        }

    @property
    def thumbnail_dimensions(self):
        return {
            "default": (120, 90),
            "medium": (320, 180),
            "high": (480, 360),
        }

    @property
    def slug(self):
        return u'watch?v=%s' % self.video_id

    def parse(self):
        if 'id' in self._resource and 'video_id' not in self._resource:
            self._resource['video_id'] = self._resource.pop('id')

        # {u'kind': u'youtube#video', u'videoId': u'eUdM9vrCbow'} -> u'eUdM9vrCbow'
        if 'video_id' in self._resource and isinstance(self._resource['video_id'], dict):
            self._resource['video_id'] = self._resource['video_id']['videoId']

        self._resource.update(self._resource.pop('snippet'))
        super(Video, self).parse()
