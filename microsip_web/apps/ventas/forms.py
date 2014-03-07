#encoding:utf-8
from django import forms
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.forms.models import modelformset_factory
import autocomplete_light

from models import *

class DoctoVe_ManageForm(forms.ModelForm): 
    fecha = forms.DateField(widget=forms.TextInput(attrs={'class':'input-small'}), required= False)
    folio = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'input-small'}))
    class Meta:
        model = VentasDocumento

class DoctoVeDet_ManageForm(forms.ModelForm): 
    unidades = forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'input-small'}))
    precio_unitario = forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'input-small'}))
    class Meta:
        widgets = autocomplete_light.get_widgets_dict(DoctoVeDet)
        model = DoctoVeDet

def DoctoVeDet_inlineformset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(VentasDocumento, DoctoVeDet, form, formset, **kwargs)

class clientes_config_cuentaManageForm(forms.ModelForm):
    class Meta:
        model = clientes_config_cuenta

clientes_config_cuenta_formset = modelformset_factory(clientes_config_cuenta)

class InformacionContableManageForm(forms.ModelForm):
    tipo_poliza_ve          = forms.ModelChoiceField(queryset= TipoPoliza.objects.all(), required=True)
    condicion_pago_contado  = forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=True)
    
    class Meta:
        model = InformacionContable_V

class GenerarPolizasManageForm(forms.Form):
    fecha_ini               = forms.DateField()
    fecha_fin               = forms.DateField()
    ignorar_documentos_cont     = forms.BooleanField(required=False, initial=True)
    CREAR_POR = (
        ('Documento', 'Documento'),
        ('Dia', 'Dia'),
        ('Periodo', 'Periodo'),
    )
    crear_polizas_por       = forms.ChoiceField(choices=CREAR_POR)

    descripcion = forms.CharField(max_length=100, required=False)

    CREAR_DE = (
        ('', '---------------'),
        ('F', 'Facturas'),
        ('D', 'Devoluciones'),
        ('FD', 'Facturas y Devoluciones'),
    )
    crear_polizas_de        = forms.ChoiceField(choices=CREAR_DE)

    plantilla = forms.ModelChoiceField(queryset= PlantillaPolizas_V.objects.filter(tipo='F'), required=False)
    plantilla_2 = forms.ModelChoiceField(queryset= PlantillaPolizas_V.objects.filter(tipo='D'), required=False)
    
class PlantillaPolizaManageForm(forms.ModelForm):
    class Meta:
        model = PlantillaPolizas_V

class ConceptoPlantillaPolizaManageForm(forms.ModelForm):
    posicion        =  forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
    asiento_ingora  = forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)

    def __init__(self, *args, **kwargs):
        super(ConceptoPlantillaPolizaManageForm, self).__init__(*args, **kwargs)
        self.fields['tipo'].widget.attrs['class'] = 'input-small'
        self.fields['valor_tipo'].widget.attrs['class'] = 'input-medium'
        self.fields['valor_iva'].widget.attrs['class'] = 'input-small'
        self.fields['valor_contado_credito'].widget.attrs['class'] = 'input-small'
        
    class Meta:
        widgets = autocomplete_light.get_widgets_dict(DetallePlantillaPolizas_V)
        model = DetallePlantillaPolizas_V
    
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
    return inlineformset_factory(PlantillaPolizas_V, DetallePlantillaPolizas_V, form, formset, **kwargs)
