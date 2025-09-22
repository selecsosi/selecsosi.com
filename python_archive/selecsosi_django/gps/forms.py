from django.forms import ModelForm
from .models import Trip, TripAttr
from django.forms.models import inlineformset_factory


class TripUploadForm(ModelForm):
    class Meta:
        model = Trip
        exclude = ('user',)

'''
Additional Attribute Formset when a trip is added
'''
TripAttrFormset = inlineformset_factory(Trip, TripAttr, extra=3)



        
    