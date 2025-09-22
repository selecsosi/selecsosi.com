from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, CreateView
from gps.models import Trip
from gps.forms import TripUploadForm, TripAttrFormset
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from gps.helpers import CsvFileUploadHelper

# Create your views here.
def index(request):
    return render_to_response("gps/index.html")


class TripCreateView(CreateView):
    template_name = 'gps/trip_add.html'
    model = Trip
    form_class = TripUploadForm
    success_url = '/gps'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TripCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        context = self.get_context_data()
        tripattr_formset = context['tripattr_formset']
        if tripattr_formset.is_valid():
            form.instance.user = self.request.user
            self.object = form.save()
            helper = CsvFileUploadHelper()
            helper.parse_trip_data_into_geopoints(self.object)
            for form in tripattr_formset:
                if form.instance.name != "":
                    form.instance.trip = self.object
                    form.save()
            return HttpResponseRedirect('/gps')
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(TripCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['tripattr_formset'] = TripAttrFormset(self.request.POST)
        else:
            context['tripattr_formset'] = TripAttrFormset()
        return context
