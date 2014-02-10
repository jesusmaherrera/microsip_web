#encoding:utf-8
from django import forms
from .models import *

class PaisManageForm(forms.ModelForm):
    class Meta:
        model = Pais