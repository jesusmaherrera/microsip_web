#encoding:utf-8
from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from .models import *
import autocomplete_light
from microsip_web.apps.main.forms import filtroarticulos_form

class impuestos_articulos_form(forms.ModelForm):
    class Meta:
        model = ImpuestosArticulo
        exclude = ('articulo',)
        
class precios_articulos_form(forms.ModelForm):
    class Meta:
        model = ArticuloPrecio
        exclude = ('articulo',)

class articulos_form(forms.ModelForm):
    class Meta:
        model = Articulo
        exclude = ('seguimiento', 'estatus','es_almacenable',)

    def __init__(self, *args, **kwargs):
        super(articulos_form, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'span12'

class claves_articulos_form(forms.ModelForm):
    class Meta:
        model = ArticuloClave
        exclude = ('articulo',)
    
    def clean_clave(self):
        cleaned_data = self.cleaned_data
        clave = cleaned_data.get("clave")
        
        clave_id  = self.instance.pk
        
        if clave_id != None:
            old_clave = ArticuloClave.objects.get(pk=clave_id).clave
        else:
            old_clave = None

        if ArticuloClave.objects.exclude(clave = old_clave).filter(clave= clave).exists():
            raise forms.ValidationError(u'La clave [%s] ya se encuentra registrada'% clave)
        return clave
    
    def __init__(self, *args, **kwargs):
        super(claves_articulos_form, self).__init__(*args, **kwargs)
        self.fields['rol'].widget.attrs['class'] = 'input-medium'
        self.fields['clave'].widget.attrs['class'] = 'input-small'