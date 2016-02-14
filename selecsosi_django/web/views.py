from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic import TemplateView


class JsAppView(TemplateView):
    template_name = None
    app_name = None

    def get_context_data(self, **kwargs):
        return {
            "app_name": self.get_app_name(),
            "js_context": {}
        }

    def get_app_name(self):
        return self.app_name


class IndexView(JsAppView):
    template_name = "web/index.html"
    app_name = "index"
