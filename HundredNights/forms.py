from django import forms
from HundredNights.models import *
from django.forms.models import modelformset_factory, inlineformset_factory

class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = "__all__"

class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = "__all__"

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        widgets = {
            'donor' : forms.HiddenInput()
        }
        fields = "__all__"

class ParticipationForm(forms.ModelForm):
    class Meta:
        model = VolunteerParticipation
        widgets = {
            'volunteer' : forms.HiddenInput()
        }
        fields = "__all__"

class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = "__all__"

VisitorQuestionForm = inlineformset_factory(Visitor, VisitorResponse, 
                    extra=0, can_delete=False, fields = "__all__")

class VisitForm(forms.ModelForm):
    visit_type = forms.ModelChoiceField(queryset=VisitType.objects.filter(is_selectable=True))
    
    class Meta:
        model = Visit
        widgets = {
            'visit' : forms.HiddenInput(),
            'visitor' : forms.Select(attrs={"style" : "max-width: 220px"})
        }
        fields = "__all__"

VisitQuestionForm = inlineformset_factory(Visit, VisitResponse,
                    extra=0, can_delete=False, fields = "__all__")

class ReferrerForm(forms.ModelForm):
    class Meta:
        model = Referrer
        fields = "__all__"

class ReferralForm(forms.ModelForm):
    class Meta:
        model = Referral
        widgets = {
            'referrer' : forms.HiddenInput() 
        }
        fields = "__all__"

ReferralVisitorForm = inlineformset_factory(
    Referral, ReferralVisitor, extra=0, can_delete=False, fields = "__all__")
        
