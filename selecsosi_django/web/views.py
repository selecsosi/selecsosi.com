from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template.context import RequestContext
# Create your views here.
def index(request):
    return render_to_response('bootstrap_base.html', {}, context_instance=RequestContext(request))
