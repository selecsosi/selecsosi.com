# Create your views here.
from math import sqrt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from .forms import FibForm

def index(request):
    return render_to_response("zoro/boilerplate.html", {}, context_instance=RequestContext(request))

@login_required
def fib(request):
    if request.method == "POST":
        form = FibForm(request.POST)
        if form.is_valid():
            request.session["fib_result"] = F(form.cleaned_data["input"])
            return HttpResponseRedirect("/zoro/fib_result/")
    else:
        request.session["fib_result"] = None
    form = FibForm()
    return render_to_response("zoro/fib.html", {"form": form}, context_instance=RequestContext(request))


def fib_result(request):
    if request.session.get("fib_result", None):
        return render_to_response(
            "zoro/fib_result.html",
            {"fib_result": request.session["fib_result"]},
            context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/zoro/fib/")


def F(n):
    return ((1+sqrt(5))**n-(1-sqrt(5))**n)/(2**n*sqrt(5))
