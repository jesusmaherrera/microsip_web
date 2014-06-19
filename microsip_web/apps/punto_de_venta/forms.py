#encoding:utf-8
from django import forms

import autocomplete_light
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from models import *

class articulo_byclave_form( forms.Form ):
    clave = forms.CharField(max_length=100)

class factura_global_form( forms.Form ):
    TIPOS_GEN_FACTURA = (
        ('P', 'Una partida'),
        ('C', 'Concentrada'),
    )
    fecha_inicio = forms.DateField( widget = forms.TextInput( attrs = { 'class' : 'input-small' } ), required= True )
    fecha_fin = forms.DateField(widget = forms.TextInput( attrs = { 'class' : 'input-small' } ) , required= True)
    tipo = forms.ChoiceField(choices=TIPOS_GEN_FACTURA, required=True, widget=forms.Select(attrs={'class':'input-medium',}))
    almacen = forms.ModelChoiceField(queryset= Almacen.objects.all(), widget=forms.Select(attrs={'class':'input-medium', 'disabled':'disabled',}), required=False)

class ArticuloCompatibleArticulo_ManageForm(forms.Form):
    compatible_articulo = forms.ModelChoiceField(queryset=Articulo.objects.all(),
        widget=autocomplete_light.ChoiceWidget('ArticuloAutocomplete'))

class ArticuloManageForm(forms.ModelForm):
    
    class Meta:
        model = Articulo
        exclude= {
            'cuenta_ventas',
            'es_almacenable',
            'seguimiento',
            'carpeta',
            'estatus',
            'costo_ultima_compra',
        }


class TipoClienteManageForm(forms.ModelForm):
    class Meta:
        model = ClienteTipo

class PreferenciasPuntosManageForm(forms.Form):
    MESES = (
        ('', '--------'),
        ('1', 'Enero'),
        ('2', 'Febrero'),
        ('3', 'Marzo'),
        ('4', 'Abril'),
        ('5', 'Mayo'),
        ('6', 'Junio'),
        ('7', 'Julio'),
        ('8', 'Agosto'),
        ('9', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),

    )

    DIAS = []
    for dia in range(1,32):
        DIAS.append((str(dia),str(dia)))

    corte_dia = forms.ChoiceField(choices=DIAS)
    corte_mes = forms.ChoiceField(choices=MESES, required= False)
    corte_anio = forms.IntegerField(required= False)

    articulo_puntos = forms.IntegerField(min_value=0)
    articulo_dinero_electronico = forms.DecimalField(min_value=0)

    def save(self, *args, **kwargs):
        corte_dia_obj = Registry.objects.get( nombre = 'SIC_PUNTOS_CORTE_DIA')
        corte_mes_obj = Registry.objects.get( nombre = 'SIC_PUNTOS_CORTE_MES')
        corte_anio_obj = Registry.objects.get( nombre = 'SIC_PUNTOS_CORTE_ANIO')

        corte_dia = self.cleaned_data['corte_dia'] or 0
        corte_mes = self.cleaned_data['corte_mes'] or 0
        corte_anio = self.cleaned_data['corte_anio'] or 0

        if corte_dia_obj.valor != corte_dia:
            corte_dia_obj.valor = corte_dia
            corte_dia_obj.save()
        
        if corte_mes_obj.valor != corte_mes:
            corte_mes_obj.valor = corte_mes
            corte_mes_obj.save()
      
        if corte_anio_obj.valor != corte_anio:
            corte_anio_obj.valor = corte_anio
            corte_anio_obj.save()

        articulo_puntos_obj = Registry.objects.get( nombre = 'SIC_PUNTOS_ARTICULO_PUNTOS_PREDET')
        articulo_dinero_electronico_obj = Registry.objects.get( nombre = 'SIC_PUNTOS_ARTICULO_DINERO_ELECT_PREDET')

        articulo_puntos_obj.valor = self.cleaned_data['articulo_puntos']
        articulo_dinero_electronico_obj.valor = self.cleaned_data['articulo_dinero_electronico']

        articulo_puntos_obj.save()
        articulo_dinero_electronico_obj.save()



class PreferenciasGeneralManageForm(forms.Form):
    articulo_general= forms.ModelChoiceField(Articulo.objects.filter( es_almacenable= 'N' ), 
            widget= autocomplete_light.ChoiceWidget('Articulos_noalm_Autocomplete')
        )

    def save(self, *args, **kwargs):
        articulo_general_obj = Registry.objects.get( nombre = 'ARTICULO_VENTAS_FG_PV_ID')
        if articulo_general_obj.valor != self.cleaned_data['articulo_general']:
            articulo_general_obj.valor = self.cleaned_data['articulo_general']
            articulo_general_obj.save()

class InformacioncontableRegManageForm(forms.Form):
    tipo_poliza_ventas = forms.ModelChoiceField(queryset= TipoPoliza.objects.all())
    tipo_poliza_devol  = forms.ModelChoiceField(queryset= TipoPoliza.objects.all())
    tipo_poliza_cobros_cc = forms.ModelChoiceField(queryset= TipoPoliza.objects.all())
    
    def save(self, *args, **kwargs):
        tipo_poliza_ventas_obj = Registry.objects.get( nombre = 'TIPO_POLIZA_VENTAS_PV')
        if tipo_poliza_ventas_obj.valor != self.cleaned_data['tipo_poliza_ventas']:
            tipo_poliza_ventas_obj.valor = self.cleaned_data['tipo_poliza_ventas']
            tipo_poliza_ventas_obj.save()

        tipo_poliza_devol_obj = Registry.objects.get( nombre = 'TIPO_POLIZA_DEVOL_PV')
        if tipo_poliza_devol_obj.valor != self.cleaned_data['tipo_poliza_devol']:
            tipo_poliza_devol_obj.valor = self.cleaned_data['tipo_poliza_devol']
            tipo_poliza_devol_obj.save()

        tipo_poliza_cobros_cc_obj = Registry.objects.get( nombre = 'TIPO_POLIZA_COBROS_CXC_PV')
        if tipo_poliza_cobros_cc_obj.valor != self.cleaned_data['tipo_poliza_cobros_cc']:
            tipo_poliza_cobros_cc_obj.valor = self.cleaned_data['tipo_poliza_cobros_cc']
            tipo_poliza_cobros_cc_obj.save()

class InformacionContableManageForm(forms.ModelForm):
    condicion_pago_contado  = forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=False)

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
    cuenta_co = forms.ModelChoiceField(queryset=ContabilidadCuentaContable.objects.all(), widget=autocomplete_light.ChoiceWidget('ContabilidadCuentaContableAutocomplete'))

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
        if ContabilidadCuentaContable.objects.filter(cuenta_padre=cuenta_co.id).count() > 0:
            raise forms.ValidationError(u'la cuenta contable (%s) no es de ultimo nivel, por favor seleciona una cuenta de ultimo nivel' % cuenta_co )
        return cuenta_co

class ConceptoPlantillaPolizaManageForm(forms.ModelForm):
    posicion        =  forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
    asiento_ingora  = forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
    cuenta_co = forms.ModelChoiceField(queryset=ContabilidadCuentaContable.objects.all(), widget=autocomplete_light.ChoiceWidget('ContabilidadCuentaContableAutocomplete'))

    def __init__(self, *args, **kwargs):
        super(ConceptoPlantillaPolizaManageForm, self).__init__(*args, **kwargs)
        self.fields['tipo_asiento'].widget.attrs['class'] = 'input-small'
        self.fields['tipo_valor'].widget.attrs['class'] = 'input-medium'
        # self.fields['valor_iva'].widget.attrs['class'] = 'input-small'
        self.fields['impuesto'].widget.attrs['class'] = 'input-medium'
        self.fields['tipo_condicionpago'].widget.attrs['class'] = 'input-small'
        
    class Meta:
        model = DetallePlantillaPolizas_pv

    def clean_cuenta_co(self):
        cuenta_co = self.cleaned_data['cuenta_co']
        if ContabilidadCuentaContable.objects.filter(cuenta_padre=cuenta_co.id).count() > 0:
            raise forms.ValidationError(u'la cuenta contable (%s) no es de ultimo nivel, por favor seleciona una cuenta de ultimo nivel' % cuenta_co )
        return cuenta_co
        
def PlantillaPoliza_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(PlantillaPolizas_pv, DetallePlantillaPolizas_pv, form, formset, **kwargs)

class FacturaManageForm(forms.ModelForm):
    MODALIDADES_FATURACION = (
        ('CFDI', 'Factura electrónica CFDI'),   
    )
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class':'span12', 'rows':2, 'placeholder': 'Descripcion...',}), required= False )
    modalidad_facturacion = forms.ChoiceField(choices= MODALIDADES_FATURACION, required=True)
    ventas_en_factura = forms.CharField(widget=forms.HiddenInput(), required=False)
    impuestos_venta_neta = forms.CharField(widget=forms.HiddenInput(), required=False)
    impuestos_otros_impuestos = forms.CharField(widget=forms.HiddenInput(), required=False)
    impuestos_importe_impuesto = forms.CharField(widget=forms.HiddenInput(), required=False)
    impuestos_ids = forms.CharField(widget=forms.HiddenInput(), required=False)
    impuestos_porcentaje_impuestos = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(FacturaManageForm, self).__init__(*args, **kwargs)
        self.fields['fecha'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].required = False
        self.fields['total_impuestos'].widget = forms.HiddenInput()
        self.fields['importe_neto'].widget = forms.HiddenInput()
        self.fields['importe_donativo'].widget = forms.HiddenInput()
        self.fields['total_fpgc'].widget = forms.HiddenInput()
        self.fields['importe_descuento'].widget = forms.HiddenInput()

    class Meta:
        widgets = autocomplete_light.get_widgets_dict(PuntoVentaDocumento)
        model = PuntoVentaDocumento
        
        exclude = (
            'tipo_gen_fac',
            'es_fac_global',
            'vendedor',
            'forma_global_emitida',
            'email_envio',
            'almacen',
            'cajero',
            'hora',
            'clave_cliente',
            'direccion_cliente',
            'tipo_descuento',
            'porcentaje_descuento',
            'persona',
            'tipo_cambio',
            'cliente_fac',
            'caja',
            'clave_cliente_fac',
            'clave_global_emitida',
            'unidad_comprom',
            'es_cfd',
            'estado',
            'cargar_sun',
            'impuesto_incluido',
            'tipo',
            'enviado',
            'unid_comprom',
            'refer_reting',
            'moneda',
            'ticket_emitido',
            'aplicado',
            'forma_emitida',
            'contabilizado',
            'sistema_origen',
            'usuario_creador',
            'fechahora_creacion',
            'usuario_aut_creacion',
            'usuario_aut_modif',
            'usuario_cancelacion',
            'usuario_ult_modif',
            'fechahora_ult_modif',
            'puntos',
            )


class DocumentoPV_ManageForm(forms.ModelForm):
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class':'span12', 'rows':2, 'placeholder': 'Descripcion...',}), required= False )

    def __init__(self, *args, **kwargs):
        super(DocumentoPV_ManageForm, self).__init__(*args, **kwargs)
        self.fields['fecha'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].required = False

    class Meta:
        widgets = autocomplete_light.get_widgets_dict(PuntoVentaDocumento)
        model = PuntoVentaDocumento
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
    articulo = forms.ModelChoiceField(Articulo.objects.all() , widget=autocomplete_light.ChoiceWidget('ArticuloAutocomplete'))
    unidades = forms.FloatField(max_value=100000, widget=forms.TextInput(attrs={'class':'input-mini text-right', 'placeholder':'unidades'}),required=True)
    precio_unitario = forms.FloatField(widget=forms.TextInput(attrs={'class':'input-small text-right', 'placeholder':'costo'}),required=True)
    detalles_liga = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(DocumentoPVDet_ManageForm, self).__init__(*args, **kwargs)
        self.fields['clave_articulo'].widget.attrs['class'] = 'input-mini'
        self.fields['porcentaje_descuento'].widget.attrs['class'] = 'input-mini text-right'
        self.fields['precio_total_neto'].widget.attrs['class'] = 'input-small text-right'
        self.fields['clave_articulo'].widget.attrs['placeholder'] = "clave"
        self.fields['clave_articulo'].required = False

    class Meta:
        model = PuntoVentaDocumentoDetalle
        exclude = (
            'rol',
            'puntos',
            'precio_modificado',
            'notas',
            'precio_unitario_impto',
            'porcentaje_comis',
            'es_tran_elect',
            'fpgc_unitario',
            'vendedor',
            'posicion',
            'estatus_tran_elect',
            'precio_modificado',
            'unidades_dev',
            )

class Docto_pv_cobro_ManageForm(forms.ModelForm):
    class Meta:
        model = PuntoVentaCobro
        exclude = (
            'importe_mon_doc',
            'tipo',
            'tipo_cambio',
        )

def DocumentoPV_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(PuntoVentaDocumento, PuntoVentaDocumentoDetalle, form, formset, **kwargs)

# def DoctoPVLigas_formset(form, formset = BaseInlineFormSet, **kwargs):
#     return inlineformset_factory(PuntoVentaDocumento, PuntoVentaDocumentoLiga, form, formset, **kwargs)

def DocumentoPV_cobro_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(PuntoVentaDocumento, PuntoVentaCobro, form, formset, **kwargs)