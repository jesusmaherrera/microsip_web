#encoding:utf-8
from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
import datetime, time

import autocomplete_light
autocomplete_light.autodiscover()
from .forms import *
from .models import *

class ComprasManageForm(forms.ModelForm):

    proveedor = forms.ModelChoiceField(Proveedor.objects.all(),
        widget=autocomplete_light.ChoiceWidget('ProveedorAutocomplete'))

    def __init__(self, *args, **kwargs):

        super(ComprasManageForm, self).__init__(*args, **kwargs)
        self.fields['fecha'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].required = False
        self.fields['total_impuestos'].widget = forms.HiddenInput()
        self.fields['proveedor_folio'].required = True
    
    def clean(self):
        cleaned_data = self.cleaned_data
        proveedor_folio = cleaned_data.get("proveedor_folio")
        proveedor = cleaned_data.get("proveedor")
        
        if DoctosCp.objects.filter(folio=proveedor_folio, proveedor=proveedor).exists():
            raise forms.ValidationError(u'El folio de factura del proveedor ya esta capturado en cuentas por pagar')
            
        return cleaned_data

    def clean_folio(self):
        folio = self.cleaned_data['folio']

        if not FolioCompra.objects.filter(tipo_doc = 'C').exists() and folio == '':
            raise forms.ValidationError(u'El campo folio es obligatorio')
            
        return folio

    class Meta:

        model = DocumentoCompras
        exclude = (
            'fecha_entrega',
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

    articulo = forms.ModelChoiceField(Articulos.objects.all() , widget=autocomplete_light.ChoiceWidget('ArticulosAutocomplete'))
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
        
        model = DocumentoComprasDetalle
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

def DocumentoComprasDetalleFormset(form, formset = BaseInlineFormSet, **kwargs):

    return inlineformset_factory(DocumentoCompras, DocumentoComprasDetalle, form, formset, **kwargs)

class DocumentoComprasImpuestosManageForm(forms.Form):

    compras_netas = forms.CharField(widget=forms.HiddenInput(), required=False)
    otros_impuestos = forms.CharField(widget=forms.HiddenInput(), required=False)
    importes_impuesto = forms.CharField(widget=forms.HiddenInput(), required=False)
    porcentajes_impuestos = forms.CharField(widget=forms.HiddenInput(), required=False)
    impuestos_ids = forms.CharField(widget=forms.HiddenInput(), required=False)
        



    
