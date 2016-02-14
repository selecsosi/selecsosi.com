from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic import TemplateView


class JsAppView(TemplateView):
    template_name = None
    app_name = None

    def get_context_data(self, **kwargs):
        return {
            "app_name": self.get_app_name(),
            "app_main": self.get_app_main(),
            "js_context": self.get_javascript_context()
        }

    def get_app_name(self):
        return self.app_name

    def get_javascript_context(self):
        return {}

    def get_app_main(self):
        return "".join(["js/main.", self.get_app_name(), ".js"])


class IndexView(JsAppView):
    template_name = "web/index.html"
    app_name = "index"


class JSXPlayground(JsAppView):
    template_name = "web/index.html"
    app_name = "jsx_playground"


class TypeScriptView(JsAppView):
    template_name = "web/index.html"
    app_name = "ts_playground"
