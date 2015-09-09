Django youtube API
==================


[![Build Status](https://travis-ci.org/ramusus/django-youtube-api.png?branch=master)](https://travis-ci.org/ramusus/django-youtube-api) [![Coverage Status](https://coveralls.io/repos/ramusus/django-youtube-api/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-youtube-api)

Application for interacting with youtube API objects using Django model interface

Installation
------------

    pip install django-youtube-api

Add into `settings.py` lines:

    INSTALLED_APPS = (
        ...
        'youtube_api',
    )

Usage examples
--------------

### Get video by ID

    >>> from youtube_api.models import Video
    
    >>> video = Video.remote.fetch('BJ80RsAQKqE')[0]
    >>> video.title
    u'(Officiele Videocl\xedp) Django Wagner - Mooie Blauwe Ogen'

### Search videos by title

    >>> videos = Video.remote.search('Django Unchaned Trailer')
    >>> len(videos)
    50

    >>> videos[0]
    <Video: Django Unchained - Official Trailer (HD)>

    >>> videos[0].video_id
    u'eUdM9vrCbow'
