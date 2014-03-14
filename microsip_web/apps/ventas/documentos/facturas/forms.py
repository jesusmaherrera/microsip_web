#encoding:utf-8
from django import forms
import autocomplete_light
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from models import *

class VentasDocumentoForm(forms.ModelForm):
    MODALIDADES_FATURACION = (
        ('CFDI', 'Factura electrónica CFDI'),   
    )
    modalidad_facturacion = forms.ChoiceField(choices= MODALIDADES_FATURACION, required=True)
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class':'span12', 'rows':2, 'placeholder': 'Descripcion...',}), required= False )

    def __init__(self, *args, **kwargs):
        super(VentasDocumentoForm, self).__init__(*args, **kwargs)
        self.fields['fecha'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].required = False
        self.fields['impuestos_total'].widget = forms.HiddenInput()
        self.fields['importe_neto'].widget = forms.HiddenInput()
        self.fields['fpgc_total'].widget = forms.HiddenInput()
        self.fields['descuento_importe'].widget = forms.HiddenInput()

    class Meta:
        widgets = autocomplete_light.get_widgets_dict(VentasDocumento)
        model = VentasDocumento
        exclude = (
            'vendedor',
            'email_envio',
            'almacen',
            'cliente_clave',
            'cliente_direccion',
            'descuento_tipo',
            'descuento_porcentaje',
            'tipo_cambio',
            'es_cfd',
            'estado',
            'cargar_sun',
            'tipo',
            'envio_enviado',
            'refer_reting',
            'moneda',
            'aplicado',
            'forma_emitida',
            'contabilizado',
            'sistema_origen',
            'creacion_usuario',
            'creacion_fechahora',
            'creacion_usuario_aut',
            'modificacion_usuario',
            'modificacion_fechahora',
            'modificacion_usuario_aut',
            )

class VentasDocumentoDetalleForm(forms.ModelForm):
    articulo = forms.ModelChoiceField(Articulo.objects.all() , widget=autocomplete_light.ChoiceWidget('ArticuloAutocomplete'))
    unidades = forms.FloatField(max_value=100000, widget=forms.TextInput(attrs={'class':'input-mini text-right', 'placeholder':'unidades'}),required=True)
    precio_unitario = forms.FloatField(widget=forms.TextInput(attrs={'class':'input-small text-right', 'placeholder':'costo'}),required=True)
    
    def __init__(self, *args, **kwargs):
        super(VentasDocumentoDetalleForm, self).__init__(*args, **kwargs)
        self.fields['articulo_clave'].widget.attrs['class'] = 'input-mini'
        self.fields['articulo_clave'].widget.attrs['placeholder'] = "clave"
        self.fields['articulo_clave'].required = False

        self.fields['decuento_porcentaje'].widget.attrs['class'] = 'input-mini text-right'
        self.fields['precio_total_neto'].widget.attrs['class'] = 'input-small text-right'

    class Meta:
        model = VentasDocumentoDetalle
        exclude = (
            'rol',
            'notas',
            'precio_unitario',
            'comisiones_porcentaje',
            'fpgc_unitario',
            'posicion',
            'unidades_surtidas_devueltas',
            )

def VentasDocumentoDetalleFormSet(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(VentasDocumento, VentasDocumentoDetalle, form, formset, **kwargs)