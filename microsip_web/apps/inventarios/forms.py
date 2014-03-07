#encoding:utf-8
from django import forms

import autocomplete_light
from django.core.exceptions import ObjectDoesNotExist
from microsip_web.apps.inventarios.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from microsip_web.settings.common import RUTA_PROYECTO
from django.contrib.auth.forms import AuthenticationForm
from microsip_web.apps.config.models import *
import fdb
import autocomplete_light

class impuestos_articulos_form(forms.ModelForm):
    class Meta:
        model = ImpuestosArticulo
        exclude = ('articulo',)
        
class precios_articulos_form(forms.ModelForm):
    class Meta:
        model = PrecioArticulo
        exclude = ('articulo',)

class articulos_form(forms.ModelForm):
    class Meta:
        model = Articulo
        exclude = ('seguimiento', 'estatus', 'puntos','es_almacenable',)

    def __init__(self, *args, **kwargs):
        super(articulos_form, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'span12'

class claves_articulos_form(forms.ModelForm):
    class Meta:
        model = ClavesArticulos
        exclude = ('articulo',)
    
    def clean_clave(self):
        cleaned_data = self.cleaned_data
        clave = cleaned_data.get("clave")
        
        clave_id  = self.instance.pk
        
        if clave_id != None:
            old_clave = ClavesArticulos.objects.get(pk=clave_id).clave
        else:
            old_clave = None

        if ClavesArticulos.objects.exclude(clave = old_clave).filter(clave= clave).exists():
            raise forms.ValidationError(u'La clave [%s] ya se encuentra registrada'% clave)
        return clave
    
    def __init__(self, *args, **kwargs):
        super(claves_articulos_form, self).__init__(*args, **kwargs)
        self.fields['rol'].widget.attrs['class'] = 'input-medium'
        self.fields['clave'].widget.attrs['class'] = 'input-small'

class PreferneciasEmpresaInv( forms.Form ):
    ajustesprimerconteo = forms.BooleanField( required = False )
    
class CustomAuthenticationForm(forms.Form):
    conexion_db = forms.ModelChoiceField(ConexionDB.objects.all(), required= False)
    username = forms.CharField( max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())
    
    def clean(self):
        cleaned_data = self.cleaned_data
        conexion_db = cleaned_data.get("conexion_db")
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if conexion_db == None and username != 'SYSDBA':
            raise forms.ValidationError(u'Por favor selecciona una conexion')
        #Si se seleciona una conexion comprueba usuario y password de firebird
        else:
            try:
                db = fdb.connect(host='localhost', user=username ,password=str(password) , database= RUTA_PROYECTO + "data\LOGIN.FDB")
            except fdb.DatabaseError:
               raise forms.ValidationError(u'nombre de usuario o password invalidos')

            if conexion_db:
                try:
                    db = fdb.connect(host=conexion_db.servidor ,user=conexion_db.usuario ,password=conexion_db.password , database="%s\System\CONFIG.FDB"% conexion_db.carpeta_datos)
                except fdb.DatabaseError:
                   raise forms.ValidationError(u'Error en la conexion selecionada')
                
            #Crea o modifica usuario                   
            try:
                usuario = User.objects.get(username__exact=username)
            except ObjectDoesNotExist:
                usuario = User.objects.create_user(username = username, password=str(password))
                if username == 'SYSDBA':
                    User.objects.filter(username = 'SYSDBA').update(is_superuser=True, is_staff=True)
            else:
                usuario.set_password(str(password))
                usuario.save()
            
            #Se crea o se modifica perfil de usuario con conexion                
            # user_profile = UserProfile.objects.filter(usuario = usuario)
            # if conexion_db:
            #     if user_profile.exists():
            #         user_profile.update(conexion_activa = conexion_db, basedatos_activa='')
            #     else:
            #         UserProfile.objects.create(usuario= usuario, basedatos_activa='', conexion_activa= conexion_db)
            # elif usuario.username == 'SYSDBA' and not user_profile.exists():
            #     UserProfile.objects.create(usuario= usuario, basedatos_activa='', conexion_activa=None)


        return cleaned_data

class SelectDBForm(forms.Form):    
     def __init__(self,*args,**kwargs):
        usuario = kwargs.pop('usuario')
        conexion_activa = kwargs.pop('conexion_activa')
        empresas = []
        if conexion_activa != '':
            conexion_activa = ConexionDB.objects.get(pk=conexion_activa)
        else:
            conexion_activa = None

        if conexion_activa:
            acceso_empresas = ''
            try:
                acceso_empresas = Usuario.objects.get(nombre__exact=usuario.username).acceso_empresas
            except ObjectDoesNotExist:
                if usuario.username == 'SYSDBA':
                    acceso_empresas = 'T'            
            consulta = ''

            # T: Acceso total L: Acceso solo a determinadas empresas
            if acceso_empresas == 'T':
                consulta = u"SELECT EMPRESAS.nombre_corto FROM EMPRESAS"
            elif acceso_empresas == 'L':
                consulta = u"SELECT EMPRESAS.nombre_corto FROM EMPRESAS_USUARIOS, EMPRESAS, USUARIOS WHERE USUARIOS.usuario_id = empresas_usuarios.usuario_id AND EMPRESAS.empresa_id = empresas_usuarios.empresa_id AND usuarios.nombre = '%s'"% usuario
            
            db= fdb.connect(host=conexion_activa.servidor, user= conexion_activa.usuario, password=conexion_activa.password, database="%s\System\CONFIG.FDB"%conexion_activa.carpeta_datos)
            cur = db.cursor()
            cur.execute(consulta)
            empresas_rows = cur.fetchall()
            for empresa in empresas_rows:
                try:
                    empresa = u'%s'%empresa[0]
                except UnicodeDecodeError:
                    pass
                else:
                    empresa_option = [empresa, empresa]
                    empresas.append(empresa_option)
                    
        super(SelectDBForm,self).__init__(*args,**kwargs)
        self.fields['conexion'] = forms.ChoiceField(choices= empresas)

class linea_articulos_form(forms.Form):
    linea = forms.ModelChoiceField(queryset= LineaArticulos.objects.all())

class UbicacionArticulosForm(forms.Form):
    ubicacion = forms.CharField(widget=forms.TextInput(attrs={'class':'input-small',}))

class EntradaManageForm(forms.ModelForm):
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class':'span12', 'rows':2, 'placeholder': 'Descripcion...',}), required= False )
    concepto = forms.ModelChoiceField( ConceptosIn.objects.filter( naturaleza= 'E', nombre_abrev='Compra'))

    def __init__(self, *args, **kwargs):
        super(EntradaManageForm, self).__init__(*args, **kwargs)
        self.fields['fecha'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].widget.attrs['class'] = 'input-small'
        self.fields['folio'].required = False


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


class DoctoInDetManageForm(forms.ModelForm):
    articulo = forms.ModelChoiceField(Articulo.objects.all() , widget=autocomplete_light.ChoiceWidget('ArticuloAutocomplete'))
    unidades = forms.FloatField(max_value=100000, widget=forms.TextInput(attrs={'class':'input-mini', 'placeholder':'unidades'}),required=True)
    costo_unitario = forms.FloatField(max_value=100000, widget=forms.TextInput(attrs={'class':'input-mini', 'placeholder':'costo'}),required=True)

    class Meta:
        model   = InventariosDocumentoDetalle
        exclude = (
                'doctosIn',
                'tipo_movto',
                'almacen',
                'concepto',
                'metodo_costeo',
                'rol',
                'cancelado',
                'aplicado',
                'costeo_pend',
                'pedimento_pend',
                'fecha',
            )

    def __init__(self, *args, **kwargs):
        super(DoctoInDetManageForm, self).__init__(*args, **kwargs)
        self.fields['claveArticulo'].widget.attrs['class'] = 'input-mini'
        self.fields['claveArticulo'].widget.attrs['placeholder'] = "clave"
        

class DoctosInDetManageForm(forms.ModelForm):    
    claveArticulo = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={"class":"input-small", "placeholder":"Clave",}),
        required=False
        )

    articulo = forms.ModelChoiceField(Articulo.objects.all() , widget=autocomplete_light.ChoiceWidget('ArticuloAutocomplete'))
    unidades = forms.FloatField(max_value=100000, widget=forms.TextInput(attrs={'class':'input-mini', 'placeholder':'unidades ...'}),required=True)

    def __init__(self, *args, **kwargs):
        super(DoctosInDetManageForm, self).__init__(*args, **kwargs)
        self.fields['costo_unitario'].widget.attrs['class'] = 'input-mini'
        # self.fields['costo_total'].widget.attrs['disabled'] = ''
        self.fields['costo_total'].widget.attrs['class'] = 'input-small'

    class Meta:
        model = InventariosDocumentoDetalle
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

class DoctoIn_CreateForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.TextInput(attrs={'class':'input-small'}))
    almacen = forms.ModelChoiceField(queryset= Almacen.objects.all(), widget=forms.Select(attrs={'class':'input-medium'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'rows':'3', 'cols':'20',}))
    
    class Meta:
        model = DoctosInvfis
        exclude = (
            'cancelado',
            'aplicado',
            'folio',
            'usuario_creador',
            'concepto',
            'fechahora_creacion',
            'forma_emitida',
            'naturaleza_concepto',
            'contabilizado',
            'usuario_aut_creacion',
            'usuario_ult_modif',
            'fechahora_ult_modif',
            'usuario_aut_modif',
            )
    def clean(self):
        cleaned_data = self.cleaned_data
        almacen = cleaned_data.get( "almacen" )
        
        if DoctosIn.objects.filter( descripcion = 'ES INVENTARIO', almacen = almacen, cancelado = 'N' ).exists():
            raise forms.ValidationError(u'Ya existe un almenos un documento para el almacen [%s], porfavor crea uno que no sea de ese almacen.'% almacen)
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
    clave = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={"class":"input-medium", "placeholder":"clave ...",}),
        required=False
        )
    articulo = forms.ModelChoiceField(Articulo.objects.all() , widget=autocomplete_light.ChoiceWidget('ArticuloAutocomplete'))
    unidades = forms.FloatField(max_value=100000, widget=forms.TextInput(attrs={'class':'input-mini', 'placeholder':'unidades ...'}),required=True)
    
    def __init__(self, *args, **kwargs):
        super(DoctosInvfisDetManageForm, self).__init__(*args, **kwargs)
        self.fields['articulo'].widget.attrs['class'] = 'input-medium'

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

# attrs={'class':'input-medium'}
def doctoIn_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(DoctosIn, InventariosDocumentoDetalle, form, formset, **kwargs)

def inventarioFisico_items_formset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(DoctosInvfis, DoctosInvfisDet, form, formset, **kwargs)


class almacen_inventariando_form(forms.ModelForm):
    class Meta:
        model = Almacen
        exclude = (
            'nombre',
            'inventariando',
            )

class ArticulosDiscretos_ManageForm(forms.ModelForm):
    id = forms.IntegerField(required=False)
    articulo   =  forms.ModelChoiceField(queryset= Articulo.objects.filter(es_almacenable='S'), required=True, widget=forms.HiddenInput())
    clave = forms.CharField(max_length=100, required=True)

    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     clave = cleaned_data.get("clave")
    #     articulo = cleaned_data.get("articulo")
    #     art_disc = ArticuloDiscreto.objects.filter(articulo=articulo, clave=clave, fecha=None) 

    #     #if DesgloseEnDiscretosInvfis.objects.filter(art_discreto=art_disc).exists():
    #     #     raise forms.ValidationError(u'El articulo con este numero de serie ya se registro en el inventario')
    #     if not ArticuloDiscreto.objects.filter(articulo=articulo, clave=clave, fecha=None).exists() and clave != None:
    #         raise forms.ValidationError(u'Numero de serie, no registrado en los articulos')

    #     return cleaned_data

    class Meta:
        model = ArticuloDiscreto
        exclude = (
            'tipo',
            'fecha',
            )

class LotesArticulo_ManageForm(forms.Form):
    lote  = forms.ModelChoiceField(queryset= ArticuloDiscreto.objects.filter(tipo='L'))

    
