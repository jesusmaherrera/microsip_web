#encoding:utf-8
from django import forms

import autocomplete_light

from microsip_web.apps.inventarios.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory


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
    modo_rapido = forms.BooleanField()

class DoctosInvfisDetManageForm(forms.ModelForm):
    clave = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'clave ...'}),required=False)
    unidades = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-mini', 'placeholder':'unidades ...'}),required=True)

    class Meta:
        widgets = autocomplete_light.get_widgets_dict(DoctosInvfisDet)
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

    def clean(self):
        cleaned_data = self.cleaned_data
        clave = cleaned_data.get("clave")
        articulo = cleaned_data.get("articulo")
        art_disc = ArticulosDiscretos.objects.filter(articulo=articulo, clave=clave, fecha=None) 

        #if DesgloseEnDiscretosInvfis.objects.filter(art_discreto=art_disc).exists():
        #     raise forms.ValidationError(u'El articulo con este numero de serie ya se registro en el inventario')
        if not ArticulosDiscretos.objects.filter(articulo=articulo, clave=clave, fecha=None).exists() and clave != None:
            raise forms.ValidationError(u'Numero de serie, no registrado en los articulos')

        return cleaned_data

    class Meta:
        model = ArticulosDiscretos
        exclude = (
            'tipo',
            'fecha',
            )

# class NumeroSerie_ManageForm(forms.Form):
#     articulo   =  forms.ModelChoiceField(queryset= Articulos.objects.filter(es_almacenable='S'), required=True, widget=forms.HiddenInput())
#     clave = forms.CharField(max_length=100, required=True)

#     exclude = ('articulo',)
    
