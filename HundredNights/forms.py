from django import forms
from HundredNights.models import *


class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor

class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        widgets = {
            'donor' : forms.HiddenInput()
        }

class ParticipationForm(forms.ModelForm):
    class Meta:
        model = VolunteerParticipation
        widgets = {
            'volunteer' : forms.HiddenInput()
        }

class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        widgets = {
            'visit' : forms.HiddenInput()
        }


        
