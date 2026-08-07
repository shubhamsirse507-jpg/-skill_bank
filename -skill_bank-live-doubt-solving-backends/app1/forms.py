from django import forms
from .models import Doubt, Booking

class DoubtForm(forms.ModelForm):
    class Meta:
        model = Doubt
        fields = '__all__'

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'


