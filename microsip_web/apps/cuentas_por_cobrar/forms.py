#encoding:utf-8
from django import forms

import autocomplete_light

from microsip_web.apps.ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from microsip_web.apps.cuentas_por_cobrar.models import *

class InformacionContableManageForm(forms.ModelForm):
    condicion_pago_contado  = forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=True)

    class Meta:
        model = InformacionContable_CC

class GenerarPolizasManageForm(forms.Form):
    fecha_ini                   = forms.DateField()
    fecha_fin                   = forms.DateField()
    ignorar_documentos_cont     = forms.BooleanField(required=False, initial=True)
    CREAR_POR = (
        ('Documento', 'Documento'),
        ('Dia', 'Dia'),
        ('Periodo', 'Periodo'),
    )
    crear_polizas_por           = forms.ChoiceField(choices=CREAR_POR)

    descripcion                 = forms.CharField(max_length=100, required=False)
    
    plantilla = forms.ModelChoiceField(queryset= PlantillaPolizas_CC.objects.all(), required=True)
    crear_polizas_de = forms.ModelChoiceField(queryset= CuentasXCobrarConcepto.objects.filter(crear_polizas='S'), required=True)

class PlantillaPolizaManageForm(forms.ModelForm):
    tipo = forms.ModelChoiceField(queryset= CuentasXCobrarConcepto.objects.filter(crear_polizas='S'), required=True)
    
    class Meta:
        model = PlantillaPolizas_CC

class ConceptoPlantillaPolizaManageForm(forms.ModelForm):
    posicion =  forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
    asiento_ingora = forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
    cuenta_co = forms.ModelChoiceField(queryset=CuentaCo.objects.all(), widget=autocomplete_light.ChoiceWidget('CuentaCoAutocomplete'))

    def __init__(self, *args, **kwargs):
        super(ConceptoPlantillaPolizaManageForm, self).__init__(*args, **kwargs)
        self.fields['tipo'].widget.attrs['class'] = 'input-small'
        self.fields['valor_tipo'].widget.attrs['class'] = 'input-medium'
        self.fields['valor_iva'].widget.attrs['class'] = 'input-small'
        self.fields['valor_contado_credito'].widget.attrs['class'] = 'input-small'
        
    class Meta:
        model = DetallePlantillaPolizas_CC

    def clean_cuenta_co(self):
        cuenta_co = self.cleaned_data['cuenta_co']
        if CuentaCo.objects.filter(cuenta_padre=cuenta_co.id).count() > 1:
            raise forms.ValidationError(u'la cuenta contable (%s) no es de ultimo nivel, por favor seleciona una cuenta de ultimo nivel' % cuenta_co )
        return cuenta_co

    def clean(self):
        cleaned_data = self.cleaned_data
        valor_tipo = cleaned_data.get("valor_tipo")
        asiento_ingora = cleaned_data.get("asiento_ingora")
        
        if ('+' in asiento_ingora or '-' in asiento_ingora) and 'Segmento' in valor_tipo:
            raise forms.ValidationError(u'los Aisetntos tipo segmentno no pueden agregar ni eliminar otros solo sustiturilos')
        return cleaned_data
        
def PlantillaPoliza_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(PlantillaPolizas_CC, DetallePlantillaPolizas_CC, form, formset, **kwargs)
