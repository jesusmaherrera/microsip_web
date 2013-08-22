#encoding:utf-8
from django import forms

import autocomplete_light

from microsip_web.apps.inventarios.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from microsip_web.settings.common import MICROSIP_DATABASES
from django.contrib.auth.forms import AuthenticationForm
from microsip_web.apps.config.models import *
import fdb

class SelectDBForm(forms.Form):    
     def __init__(self,*args,**kwargs):
        usuario = kwargs.pop('usuario')
        db= fdb.connect(host="localhost",user="SYSDBA",password="masterkey",database="C:\Microsip datos\System\CONFIG.FDB")
        cur = db.cursor()
        if Usuario.objects.filter(nombre=usuario)[0].acceso_empresas != 'T':
            consulta = u"SELECT EMPRESAS.nombre_corto FROM EMPRESAS_USUARIOS, EMPRESAS, USUARIOS WHERE USUARIOS.usuario_id = empresas_usuarios.usuario_id AND EMPRESAS.empresa_id = empresas_usuarios.empresa_id AND usuarios.nombre = '%s'"% usuario
        else:
            consulta = u"SELECT EMPRESAS.nombre_corto FROM EMPRESAS"
        cur.execute(consulta)

        empresas_rows = cur.fetchall()
        empresas = []
        for empresa_str in empresas_rows:
            empresa_option = [empresa_str[0], empresa_str[0]]
            empresas.append(empresa_option)

        super(SelectDBForm,self).__init__(*args,**kwargs)
        self.fields['conexion'] = forms.ChoiceField(choices= empresas)

class linea_articulos_form(forms.Form):
    def __init__(self,*args,**kwargs):
        self.database = kwargs.pop('database')
        super(linea_articulos_form,self).__init__(*args,**kwargs)
        self.fields['linea'] = forms.ModelChoiceField(queryset= LineaArticulos.objects.using(self.database).all())

class UbicacionArticulosForm(forms.Form):
    ubicacion = forms.CharField(widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Ubicacion..'}))

class DoctosInManageForm(forms.ModelForm):
    file_inventario = forms.CharField(widget=forms.FileInput, required = False)
    
    class Meta:
        model = DoctosIn
        exclude = (
            'cancelado',
            'aplicado',
            'forma_emitida',
            'contabilizado',
            'sistema_origen',
            'naturaleza_concepto',
            'usuario_creador',
            'fechahora_creacion',
            'usuario_ult_modif',
            'fechahora_ult_modif',
            )

class DoctosInDetManageForm(forms.ModelForm):
    class Meta:
        widgets = autocomplete_light.get_widgets_dict(DoctosInDet)
        model = DoctosInDet
        exclude = (
            'tipo_movto',
            'almacen',
            'concepto',
            'metodo_costeo',
            'rol',
            'cancelado',
            'aplicado',
            'costeo_pend',
            'pedimento_pend',
            'fecha',)

class DoctoInvfis_CreateForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.TextInput(attrs={'class':'input-small'}))
    # almacen = forms.ModelChoiceField(queryset= Almacenes.objects.all(), widget=forms.Select(attrs={'class':'input-medium'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'rows':'3', 'cols':'20',}))
    
    def __init__(self,*args,**kwargs):
        self.database = kwargs.pop('database')
        super(DoctoInvfis_CreateForm,self).__init__(*args,**kwargs)
        self.fields['almacen'] = forms.ModelChoiceField(queryset= Almacenes.objects.using(self.database).all(), widget=forms.Select(attrs={'class':'input-medium'}))

    class Meta:
        model = DoctosInvfis
        exclude = (
            'cancelado',
            'aplicado',
            'folio',
            'usuario_creador',
            'fechahora_creacion',
            'usuario_aut_creacion',
            'usuario_ult_modif',
            'fechahora_ult_modif',
            'usuario_aut_modif',
            )

    def clean(self):
        cleaned_data = self.cleaned_data
        almacen = cleaned_data.get("almacen")
        if DoctosInvfis.objects.using(self.database).filter(aplicado='N', almacen = almacen).exists():
            raise forms.ValidationError(u'Ya existe un inventario fisico abierto para el almacen [%s], porfavor crea uno que no sea de ese almacen.'% almacen)
        return cleaned_data

class DoctosInvfisManageForm(forms.ModelForm):
    file_inventario = forms.CharField(widget=forms.FileInput, required = False)
    
    class Meta:
        model = DoctosInvfis
        exclude = (
            'cancelado',
            'aplicado',
            'usuario_creador',
            'fecha',
            'fechahora_creacion',
            'usuario_aut_creacion',
            'usuario_ult_modif',
            'fechahora_ult_modif',
            'usuario_aut_modif',
            )

    def clean(self):
        cleaned_data = self.cleaned_data
        almacen = cleaned_data.get("almacen")
        if DoctosInvfis.objects.filter(aplicado='N', almacen = almacen).exists():
            raise forms.ValidationError(u'Ya existe un inventario fisico abierto para el almacen [%s], porfavor crea uno que no sea de ese almacen.'% almacen)
        return cleaned_data

class inventario_pa_form(forms.Form):
    modo_rapido = forms.BooleanField(required=False)

class DoctosInvfisDetManageForm(forms.ModelForm):
    clave = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'clave ...'}),required=False)
    unidades = forms.FloatField(max_value=100000, widget=forms.TextInput(attrs={'class':'input-mini', 'placeholder':'unidades ...'}),required=True)
    
    def __init__(self,*args,**kwargs):
        self.database = kwargs.pop('database')
        super(DoctosInvfisDetManageForm,self).__init__(*args,**kwargs)
        self.fields['articulo'] = forms.ModelChoiceField(queryset= Articulos.objects.using(self.database).all())

    class Meta:
        model   = DoctosInvfisDet
        exclude = (
            'docto_invfis',
            )

    def clean_articulo(self):
        cleaned_data = self.cleaned_data
        articulo = cleaned_data.get("articulo")
        if articulo.es_almacenable == 'N':
            raise forms.ValidationError(u'Este articulo no es almacenable')
        return articulo

def doctoIn_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(DoctosIn, DoctosInDet, form, formset, **kwargs)

def inventarioFisico_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(DoctosInvfis, DoctosInvfisDet, form, formset, **kwargs)


class ArticulosDiscretos_ManageForm(forms.ModelForm):
    id = forms.IntegerField(required=False)
    articulo   =  forms.ModelChoiceField(queryset= Articulos.objects.filter(es_almacenable='S'), required=True, widget=forms.HiddenInput())
    clave = forms.CharField(max_length=100, required=True)

    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     clave = cleaned_data.get("clave")
    #     articulo = cleaned_data.get("articulo")
    #     art_disc = ArticulosDiscretos.objects.filter(articulo=articulo, clave=clave, fecha=None) 

    #     #if DesgloseEnDiscretosInvfis.objects.filter(art_discreto=art_disc).exists():
    #     #     raise forms.ValidationError(u'El articulo con este numero de serie ya se registro en el inventario')
    #     if not ArticulosDiscretos.objects.filter(articulo=articulo, clave=clave, fecha=None).exists() and clave != None:
    #         raise forms.ValidationError(u'Numero de serie, no registrado en los articulos')

    #     return cleaned_data

    class Meta:
        model = ArticulosDiscretos
        exclude = (
            'tipo',
            'fecha',
            )

class LotesArticulo_ManageForm(forms.Form):
    lote  = forms.ModelChoiceField(queryset= ArticulosDiscretos.objects.filter(tipo='L'))

    
