#encoding:utf-8
from django.db import models
from datetime import datetime

class BancoBase(models.Model):
    BANCO_ID = models.AutoField(primary_key=True)

    class Meta:
        db_table = u'bancos'
        abstract = True