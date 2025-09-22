from django.forms.widgets import Widget


class ReadonlyWidget(Widget):

    def render(self, value, attrs=None):
        return '<input type="text" readonly="true">%s</input>' % value
