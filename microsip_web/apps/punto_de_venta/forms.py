#encoding:utf-8
from django import forms

import autocomplete_light
from microsip_web.apps.inventarios.models import *
from microsip_web.apps.ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from models import *
class factura_global_form( forms.Form ):
    TIPOS_GEN_FACTURA = (
        ('C', 'Concentrada'),
        ('D', 'Detallada'),
    )
    fecha_inicio = forms.DateField( widget = forms.TextInput( attrs = { 'class' : 'input-small' } ) )
    fecha_fin = forms.DateField(widget = forms.TextInput( attrs = { 'class' : 'input-small' } ) )
    tipo = forms.ChoiceField(choices=TIPOS_GEN_FACTURA, required=True, widget=forms.Select(attrs={'class':'input-medium',}))
    almacen = forms.ModelChoiceField(queryset= Almacenes.objects.all(), widget=forms.Select(attrs={'class':'input-medium', 'disabled':'disabled',}))

class ArticuloCompatibleArticulo_ManageForm(forms.Form):
    compatible_articulo = forms.ModelChoiceField(queryset=Articulos.objects.all(),
        widget=autocomplete_light.ChoiceWidget('ArticulosAutocomplete'))

class ArticuloManageForm(forms.ModelForm):
    
    class Meta:
        model = Articulos
        exclude= {
            'cuenta_ventas',
            'es_almacenable',
            'seguimiento',
            'carpeta',
            'estatus',
            'costo_ultima_compra',
        }

class ClienteManageForm(forms.ModelForm):
    
    class Meta:
        widgets = autocomplete_light.get_widgets_dict(Cliente)
        model = Cliente

        exclude= {
            'cuenta_xcobrar',
            'estatus',
            'moneda',
            'condicion_de_pago',

        }

class TipoClienteManageForm(forms.ModelForm):
    class Meta:
        model = TipoCliente

class LineaArticulosManageForm(forms.ModelForm):
    class Meta:
        model = LineaArticulos
        exclude= {
            'cuenta_ventas',
        }
        
class GrupoLineasManageForm(forms.ModelForm):
    class Meta:
        model = GrupoLineas
        exclude= {
            'cuenta_ventas',
        }

class InformacioncontableRegManageForm(forms.Form):
    TIPOS_POLIZA = []
    # for tipo_poliza in TipoPoliza.objects.all():
    #     opcion = [tipo_poliza.clave, tipo_poliza.nombre]
    #     TIPOS_POLIZA.append(opcion)

    tipo_poliza_ventas = forms.ChoiceField(choices=TIPOS_POLIZA, required=True)
    tipo_poliza_devol  = forms.ChoiceField(choices=TIPOS_POLIZA, required=True)
    tipo_poliza_cobros_cc = forms.ChoiceField(choices=TIPOS_POLIZA, required =True)    

class InformacionContableManageForm(forms.ModelForm):
    condicion_pago_contado  = forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=True)

    class Meta:
        model = InformacionContable_pv

class GenerarPolizasManageForm(forms.Form):
    fecha_ini                   = forms.DateField()
    fecha_fin                   = forms.DateField()
    ignorar_documentos_cont     = forms.BooleanField(required=False, initial=True)
    CREAR_POR = (
        ('Dia', 'Dia'),
        ('Periodo', 'Periodo'),
    )
    crear_polizas_por           = forms.ChoiceField(choices=CREAR_POR)

    descripcion                 = forms.CharField(max_length=100, required=False)
    TIPOS =(
        ('', '------------------'),
        ('V', 'Ventas de mostrador'),
        ('D', 'Devoluciones'),
        ('P', 'Cobros ctas. por cobrar'),
    )
    crear_polizas_de            = forms.ChoiceField(choices=TIPOS, required=True)

    plantilla_ventas = forms.ModelChoiceField(queryset= PlantillaPolizas_pv.objects.filter(tipo='V'), required=False)
    plantilla_devoluciones = forms.ModelChoiceField(queryset= PlantillaPolizas_pv.objects.filter(tipo='D'), required=False)
    plantilla_cobros_cc = forms.ModelChoiceField(queryset= PlantillaPolizas_pv.objects.filter(tipo='F'), required=False)

class ClienteSearchForm(forms.Form):
    cliente = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'autofocus':''}),required=True)

class PlantillaPolizaManageForm(forms.ModelForm):
    class Meta:
        model = PlantillaPolizas_pv

class DetPlantillaPolVentasManageForm(forms.ModelForm):
    posicion        =  forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
    asiento_ingora  = forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)

    def __init__(self, *args, **kwargs):
        super(DetPlantillaPolVentasManageForm, self).__init__(*args, **kwargs)
        self.fields['impuesto'].widget.attrs['class'] = 'input-medium'
        self.fields['tipo_condicionpago'].widget.attrs['class'] = 'input-small'
        
    class Meta:
        widgets = autocomplete_light.get_widgets_dict(DetallePlantillaPolizas_pv)
        model = DetallePlantillaPolizas_pv
        exclude = ('tipo_valor','tipo_asiento')

    def clean_cuenta_co(self):
        cuenta_co = self.cleaned_data['cuenta_co']
        if CuentaCo.objects.filter(cuenta_padre=cuenta_co.id).count() > 0:
            raise forms.ValidationError(u'la cuenta contable (%s) no es de ultimo nivel, por favor seleciona una cuenta de ultimo nivel' % cuenta_co )
        return cuenta_co

class ConceptoPlantillaPolizaManageForm(forms.ModelForm):
    posicion        =  forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
    asiento_ingora  = forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)

    def __init__(self, *args, **kwargs):
        super(ConceptoPlantillaPolizaManageForm, self).__init__(*args, **kwargs)
        self.fields['tipo_asiento'].widget.attrs['class'] = 'input-small'
        self.fields['tipo_valor'].widget.attrs['class'] = 'input-medium'
        # self.fields['valor_iva'].widget.attrs['class'] = 'input-small'
        self.fields['impuesto'].widget.attrs['class'] = 'input-medium'
        self.fields['tipo_condicionpago'].widget.attrs['class'] = 'input-small'
        
    class Meta:
        widgets = autocomplete_light.get_widgets_dict(DetallePlantillaPolizas_pv)
        model = DetallePlantillaPolizas_pv

    def clean_cuenta_co(self):
        cuenta_co = self.cleaned_data['cuenta_co']
        if CuentaCo.objects.filter(cuenta_padre=cuenta_co.id).count() > 0:
            raise forms.ValidationError(u'la cuenta contable (%s) no es de ultimo nivel, por favor seleciona una cuenta de ultimo nivel' % cuenta_co )
        return cuenta_co
        
def PlantillaPoliza_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(PlantillaPolizas_pv, DetallePlantillaPolizas_pv, form, formset, **kwargs)


class DocumentoPV_ManageForm(forms.ModelForm):
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class':'span12', 'rows':2, 'placeholder': 'Descripcion...',}), required= False )

    def __init__(self, *args, **kwargs):
        super(DocumentoPV_ManageForm, self).__init__(*args, **kwargs)
        self.fields['fecha'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].required = False

    class Meta:
        widgets = autocomplete_light.get_widgets_dict(Docto_PV)
        model = Docto_PV
        exclude = (
            'vendedor',
            'forma_global_emitida',
            'modalidad_facturacion',
            'total_fpgc',
            'email_envio',
            'almacen',
            'cajero',
            'hora',
            'clave_cliente',
            'direccion_cliente',
            'tipo_descuento',
            'porcentaje_descuento',
            'importe_descuento',
            'persona',
            'tipo_cambio',
            'cliente_fac',
            'caja',
            'clave_cliente_fac',
            'clave_global_emitida',
            'unidad_comprom',
            'es_cfd',
            'total_impuestos',
            'estado',
            'cargar_sun',
            'impuesto_incluido',
            'importe_donativo',
            'tipo',
            'enviado',
            'unid_comprom',
            'refer_reting',
            'moneda',
            'importe_neto',
            'ticket_emitido',
            'aplicado',
            'forma_emitida',
            'contabilizado',
            'sistema_origen',
            'usuario_creador',
            'fechahora_creacion',
            'usuario_ult_modif',
            'fechahora_ult_modif',
            'puntos',
            )

class DocumentoPVDet_ManageForm(forms.ModelForm):
    articulo = forms.ModelChoiceField(Articulos.objects.all() , widget=autocomplete_light.ChoiceWidget('ArticulosAutocomplete'))
    unidades = forms.FloatField(max_value=100000, widget=forms.TextInput(attrs={'class':'input-mini', 'placeholder':'unidades'}),required=True)
    precio_unitario = forms.FloatField(max_value=100000, widget=forms.TextInput(attrs={'class':'input-mini', 'placeholder':'costo'}),required=True)

    def __init__(self, *args, **kwargs):
        super(DocumentoPVDet_ManageForm, self).__init__(*args, **kwargs)
        self.fields['clave_articulo'].widget.attrs['class'] = 'input-mini'
        self.fields['clave_articulo'].widget.attrs['placeholder'] = "clave"
        self.fields['clave_articulo'].required = False

    class Meta:
        model = Docto_pv_det
        exclude = (
            'rol',
            'puntos',
            'precio_modificado',
            'notas',
            'precio_unitario_impto',
            'porcentaje_comis',
            'es_tran_elect',
            'porcentaje_descuento',
            'fpgc_unitario',
            'vendedor',
            'posicion',
            'estatus_tran_elect',
            'precio_modificado',
            'unidades_dev',
            )

class Docto_pv_cobro_ManageForm(forms.ModelForm):
    class Meta:
        model = Docto_pv_cobro
        exclude = (
            'importe_mon_doc',
            'tipo',
            'tipo_cambio',
        )

def DocumentoPV_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(Docto_PV, Docto_pv_det, form, formset, **kwargs)

def DocumentoPV_cobro_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(Docto_PV, Docto_pv_cobro, form, formset, **kwargs)