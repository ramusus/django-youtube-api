import random
import string

import factory
from django.utils import timezone

from . import models


class VideoFactory(factory.DjangoModelFactory):

    video_id = factory.Sequence(lambda n: "".join([random.choice(string.letters) for i in xrange(11)]))
    published_at = factory.LazyAttribute(lambda o: timezone.now())

    class Meta:
        model = models.Video
