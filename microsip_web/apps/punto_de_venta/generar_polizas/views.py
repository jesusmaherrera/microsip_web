#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from models import *
from forms import *
from django.db.models import Sum, Max
# user autentication
from django.contrib.auth.decorators import login_required, permission_required
