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
		
class GrupoLineasManageForm(forms.ModelForm):
	class Meta:
		model = GrupoLineas
		exclude= {
			'cuenta_ventas',
		}