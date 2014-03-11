#encoding:utf-8
from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
import datetime, time

import autocomplete_light
autocomplete_light.autodiscover()
from .forms import *
from .models import *

class OrdenManageForm(forms.ModelForm):
    proveedor = forms.ModelChoiceField(Proveedor.objects.all(),
        widget=autocomplete_light.ChoiceWidget('ProveedorAutocomplete'))

    def __init__(self, *args, **kwargs):
        super(OrdenManageForm, self).__init__(*args, **kwargs)
        self.fields['fecha'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].required = False
        self.fields['total_impuestos'].widget = forms.HiddenInput()

    class Meta:
        model = ComprasDocumento
        exclude = (
            'aplicado',
            'usuario_creador',
            'fletes',
            'tiene_cfd',
            'otros_cargos',
            'enviado',
            'importe_neto',
            'importe_descuento',
            'tipo',
            'estado',
            'tipo_descuento',
            'porcentaje_descuento',
            'total_fpgc',
            'cargar_sun',
            'porcentaje_dscto_ppag',
            'tipo_cambio',
            'total_retenciones',
            'sistema_origen',
            'gastos_aduanales',
            'otros_gastos',
             )


class DocumentoComprasDetalleManageForm(forms.ModelForm):
    articulo = forms.ModelChoiceField(Articulo.objects.all() , widget=autocomplete_light.ChoiceWidget('ArticuloAutocomplete'))
    unidades = forms.FloatField(max_value=100000, widget=forms.TextInput(attrs={'class':'input-mini text-right', 'placeholder':'unidades'}),required=True)
    precio_unitario = forms.FloatField(widget=forms.TextInput(attrs={'class':'input-small text-right', 'placeholder':'costo'}),required=True)
    detalles_liga = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(DocumentoComprasDetalleManageForm, self).__init__(*args, **kwargs)
        self.fields['clave_articulo'].widget.attrs['class'] = 'input-mini'
        self.fields['umed'].widget.attrs['class'] = 'input-mini'
        self.fields['clave_articulo'].widget.attrs['placeholder'] = "clave"
        self.fields['clave_articulo'].required = False

    class Meta:
        model = ComprasDocumentoDetalle
        exclude = (
            'porcentaje_descuento_vol',
            'contenido_umed',
            'porcentaje_arancel',
            'porcentaje_descuento_promo',
            'porcentaje_descuento_pro',
            'fpgc_unitario',
            'porcentaje_descuento',
            'posicion',
            'unidades_rec_dev',
            'unidades_a_rec',    
            )

class DocumentoComprasImpuestosManageForm(forms.Form):
    compras_netas = forms.CharField(widget=forms.HiddenInput(), required=False)
    otros_impuestos = forms.CharField(widget=forms.HiddenInput(), required=False)
    importes_impuesto = forms.CharField(widget=forms.HiddenInput(), required=False)
    porcentajes_impuestos = forms.CharField(widget=forms.HiddenInput(), required=False)
    impuestos_ids = forms.CharField(widget=forms.HiddenInput(), required=False)
        
def DocumentoComprasDetalleFormset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(ComprasDocumento, ComprasDocumentoDetalle, form, formset, **kwargs)



    
