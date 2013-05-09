#encoding:utf-8
from django import forms
from microsip_web.apps.inventarios.models import *
from models import *

class ArticuloManageForm(forms.ModelForm):
	class Meta:
		model = Articulos
		exclude= {
			'cuenta_ventas',
			'linea',
			'es_almacenable',
		}

class ClienteManageForm(forms.ModelForm):
	class Meta:
		model = Cliente
		exclude= {
			'cuenta_xcobrar',
		}

class LineaArticulosManageForm(forms.ModelForm):
	class Meta:
		model = LineaArticulos
		exclude= {
			'grupo',
			'cuenta_ventas',
		}
		
class GrupoLineasManageForm(forms.ModelForm):
	class Meta:
		model = GrupoLineas
		exclude= {
			'cuenta_ventas',
		}