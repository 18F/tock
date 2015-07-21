# -*- coding: utf-8 -*-

import factory
from factory.django import DjangoModelFactory

from projects import models


class AgencyFactory(DjangoModelFactory):
    class Meta:
        model = models.Agency
    name = 'GSA'


class AccountingCodeFactory(DjangoModelFactory):
    class Meta:
        model = models.AccountingCode
    agency = factory.SubFactory(AgencyFactory)


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = models.Project
    name = 'Tock'
    accounting_code = factory.SubFactory(AccountingCodeFactory)
