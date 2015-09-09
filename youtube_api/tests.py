# -*- coding: utf-8 -*-
from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Video

VIDEO_ID = 'BJ80RsAQKqE'


class VideoTest(TestCase):
    def setUp(self):
        self.time = timezone.now()

    def test_fetch_video(self):
        v = Video.remote.fetch(VIDEO_ID)[0]

        self.assertEqual(v.video_id, VIDEO_ID)
        self.assertGreater(len(v.title), 0)
        self.assertGreater(len(v.description), 0)
        self.assertGreater(v.fetched_at, self.time)
        self.assertIsInstance(v.published_at, datetime)
        self.assertTrue(v.channel_id)

    def test_search_videos(self):

        videos = Video.remote.search('Django Unchaned Trailer')
        video = videos[0]

        self.assertEqual(len(videos), 50)
        self.assertIsInstance(video, Video)
        with self.assertRaises(Video.DoesNotExist):
            Video.objects.get(pk=video.pk)

        video.save()
        self.assertEqual(video, Video.objects.get(pk=video.pk))

class YoutubeApiTest(VideoTest):
    pass
