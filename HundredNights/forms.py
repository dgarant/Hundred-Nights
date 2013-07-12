from django import forms
from HundredNights.models import *


class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        widgets = {
            'donor' : forms.HiddenInput()
        }

