#encoding:utf-8
from django import forms

import autocomplete_light

from microsip_web.apps.ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from models import *

class ProveedorManageForm(forms.ModelForm):
    class Meta:
        widgets = autocomplete_light.get_widgets_dict(Proveedor)
        model = Proveedor
