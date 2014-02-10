#encoding:utf-8
from django import forms
from .models import Ciudad, Estado

class CiudadManageForm(forms.ModelForm):
    class Meta:
        model = Ciudad