 #encoding:utf-8
import json
from models import *
from dajaxice.decorators import dajaxice_register
from django.shortcuts import render_to_response, get_object_or_404

@dajaxice_register( method = 'GET' )
def aplicar_docto( request, **kwargs ):
    docto_id = kwargs.get( 'docto_id', None )
    documento = ComprasDocumento.objects.get(pk=docto_id)
    documento.aplicado ='S'
    documento.save()
    return json.dumps( { 'msg' : 'ya'} )