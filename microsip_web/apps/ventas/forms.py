#encoding:utf-8
from django import forms
from django.forms.models import modelformset_factory
from models import *

class clientes_config_cuentaManageForm(forms.ModelForm):
    class Meta:
        model = clientes_config_cuenta

clientes_config_cuenta_formset = modelformset_factory(clientes_config_cuenta)

class InformacionContableManageForm(forms.ModelForm):
    tipo_poliza_ve          = forms.ModelChoiceField(queryset= TipoPoliza.objects.all(), required=True)
    condicion_pago_contado  = forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=True)
    
    class Meta:
        model = InformacionContable_V
