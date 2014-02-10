#encoding:utf-8
from django import forms
from .models import Estado, Pais

class EstadoManageForm(forms.ModelForm):
    class Meta:
        model = Estado