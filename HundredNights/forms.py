from django import forms
from HundredNights.models import *
from django.forms.models import modelformset_factory, inlineformset_factory

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

VisitorQuestionForm = inlineformset_factory(Visitor, VisitorResponse, 
                    extra=0, can_delete=False)

class VisitForm(forms.ModelForm):     
    def __init__(self, *args, **kwargs):
        super(VisitForm, self).__init__(*args, **kwargs)
        self.fields["visit_type"].queryset = VisitType.objects.filter(is_selectable=True)
    
    class Meta:
        model = Visit
        widgets = {
            'visit' : forms.HiddenInput()
        }

VisitQuestionForm = inlineformset_factory(Visit, VisitResponse,
                    extra=0, can_delete=False)

class ReferrerForm(forms.ModelForm):
    class Meta:
        model = Referrer

class ReferralForm(forms.ModelForm):
    class Meta:
        model = Referral
        widgets = {
            'referrer' : forms.HiddenInput() 
        }

ReferralVisitorForm = inlineformset_factory(
    Referral, ReferralVisitor, extra=0, can_delete=False)
        
