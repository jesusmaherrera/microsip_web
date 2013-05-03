#encoding:utf-8
from django import forms
from microsip_web.apps.inventarios.models import *
from models import *

class LineaArticulosManageForm(forms.ModelForm):
	class Meta:
		model = LineaArticulos
		exclude= {
			'grupo',
			'cuenta_ventas',
		}

class Libres_LineaArticulosManageForm(forms.ModelForm):
	class Meta:
		model = Libres_linea_articulos
		exclude={
			'linea',
		}

class GrupoLineasManageForm(forms.ModelForm):
	class Meta:
		model = GrupoLineas
		exclude= {
			'cuenta_ventas',
		}

class Libres_GrupoLineasManageForm(forms.ModelForm):
	class Meta:
		model = Libres_grupo_lineas
		exclude={
			'grupo',
		}