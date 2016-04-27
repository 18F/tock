# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

  dependencies = [('hours', '0002_auto_20150405_0317'),]

  operations = [
      migrations.AddField(model_name='timecard',
                          name='created_at',
                          field=models.DateTimeField(default=datetime.datetime(
                              2015, 4, 8, 19, 34, 17, 307448,
                              tzinfo=utc),
                                                     auto_now_add=True),
                          preserve_default=False,),
      migrations.AddField(model_name='timecard',
                          name='updated_at',
                          field=models.DateTimeField(default=datetime.datetime(
                              2015, 4, 8, 19, 34, 21, 857017,
                              tzinfo=utc),
                                                     auto_now=True),
                          preserve_default=False,),
  ]
