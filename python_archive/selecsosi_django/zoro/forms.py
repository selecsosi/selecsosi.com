from django import forms


class FibForm(forms.Form):
    input = forms.IntegerField(label="Input", min_value=0)
