# -*- coding: utf-8 -*-

import factory
from factory.django import DjangoModelFactory

from django.contrib.auth.models import User

from employees import models


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


class UserDataFactory(DjangoModelFactory):
    class Meta:
        model = models.UserData

    user = factory.SubFactory(UserFactory)
