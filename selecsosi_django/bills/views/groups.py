from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import ListView, DetailView
from ..models import Group


class GroupListView(ListView):
    queryset = Group.objects.all()
    template_name = "bill/groups/group_list.html"


class GroupDetailView(DetailView):
    model = Group
    template_name = "bill/groups/group_detail.html"
    slug = "id"
    slug_url_kwarg = "id"
    slug_field = "id"
