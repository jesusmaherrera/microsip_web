#encoding:utf-8
from django import forms

import autocomplete_light
from microsip_web.apps.inventarios.models import *
from microsip_web.apps.ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from models import *

class ImpuestoManageForm(forms.ModelForm):
     
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Impuesto.objects.filter(nombre=nombre).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(u'Ya existe un impuesto con este nombre')
        return nombre

    def clean(self):
        cleaned_data = self.cleaned_data
        tipo_iva = cleaned_data.get("tipo_iva")
        porcentaje = cleaned_data.get("porcentaje")
        tipo_impuesto = cleaned_data.get("tipoImpuesto")
        
        if (porcentaje != 0 and (tipo_iva =='4' or tipo_iva =='3')) or ((tipo_iva=='1' or tipo_iva=='2') and porcentaje <= 0):
            raise forms.ValidationError(u'La tasa del impuesto no concuerda con el tipo de IVA')

        if tipo_impuesto.id_interno != 'V' and tipo_iva: 
            raise forms.ValidationError(u'El tipo de iva no se debe indicar para este impuesto')

        return cleaned_data

    class Meta:
        model = Impuesto
