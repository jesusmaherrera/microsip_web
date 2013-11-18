#encoding:utf-8
from django import forms
from microsip_web.apps.main.models import *
from models import *
import autocomplete_light

class generartarjetas_form( forms.Form ):
    prefijo = forms.CharField( max_length = 3, widget = forms.TextInput( attrs = { 'class' : 'input-mini' } ) )
    iniciar_en = forms.IntegerField( widget = forms.TextInput( attrs = { 'class' : 'input-mini' } ),)
    cantidad = forms.IntegerField( max_value = 6000 , widget = forms.TextInput( attrs = { 'class' : 'input-mini' } ),)
    TIPOS_TARJETA = ( ( 'N', 'No Aplica' ), ( 'P', 'Puntos' ), ( 'D', 'Dinero Electronico' ), )
    tipo_tarjeta = forms.ChoiceField( choices = TIPOS_TARJETA )
    puntos = forms.IntegerField( initial = 0, widget = forms.TextInput( attrs = { 'class' : 'input-mini' } ) )
    dinero_electronico = forms.DecimalField( initial = 0, max_value = 2000, decimal_places = 2, widget = forms.TextInput( attrs = { 'class' : 'input-mini' } ) )
    hereda_valorpuntos = forms.BooleanField( initial = True, required = False )
    valor_puntos = forms.DecimalField( initial = 0, max_digits = 15, decimal_places = 2, widget = forms.TextInput( attrs = { 'class' : 'input-mini' } ) )
    hereda_puntos_a = forms.ModelChoiceField( queryset = Cliente.objects.all(), widget=autocomplete_light.ChoiceWidget('ClienteAutocomplete'), required = False )
    
    def clean_iniciar_en(self):
        iniciar_en = self.cleaned_data['iniciar_en']
        if not iniciar_en:
            raise forms.ValidationError(u'Campo obligatorio.')
        return iniciar_en

    def clean(self):
        cleaned_data = self.cleaned_data
        prefijo = cleaned_data.get("prefijo")
        iniciar_en = cleaned_data.get("iniciar_en")
        cantidad = cleaned_data.get("cantidad")
        
        if iniciar_en != None and cantidad != None:
            claves = []
            for numero in range( iniciar_en, iniciar_en + cantidad ):
                claves.append( '%s' % '%s%s'% ( prefijo, ( "%09d" % numero ) ) )

            if ClavesClientes.objects.filter( clave__in = claves ).exists():
                raise forms.ValidationError(u'Ya Existe una o mas claves en este rango')

        return cleaned_data

