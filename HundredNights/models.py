from django.db import models
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from HundredNights.models import *
from datetime import datetime

class Donor(models.Model):
    name = models.CharField(max_length=75, 
        verbose_name="Donor Name", help_text="Enter the full name of the individual or organization")
    street_1 = models.CharField(max_length=50, 
        verbose_name="Street Address Line 1", null=True, blank=True)
    street_2 = models.CharField(max_length=50,
        verbose_name="Street Address Line 2", null=True, blank=True)
    city = models.CharField(max_length=50,
        verbose_name="City", null=True, blank=True)
    zip = models.CharField(max_length=10,
        verbose_name="Zip", null=True, blank=True,
        help_text="Enter a zip code in the format 00000 or 00000-0000")
    state = models.CharField(max_length=2, 
        choices=STATE_CHOICES, null=True, blank=True,
        verbose_name="State", default="NH")
    is_organization = models.BooleanField(
        verbose_name="Is this an organization?")
    email = models.CharField(max_length=100,
        verbose_name = "Email", null=True, blank=True)
    organization_contact = models.CharField(max_length=100,
        verbose_name="Organization Contact", null=True, blank=True)
    title = models.CharField(max_length=10,
        verbose_name="Title", null=True, blank=True)

    class Meta:
        verbose_name = "Donor"

    def __unicode__(self):
        return unicode(self.name)
    
class Donation(models.Model):
    donor = models.ForeignKey(Donor, verbose_name="Donor")
    amount = models.DecimalField(max_digits=15, 
        decimal_places=2, verbose_name="Amount (if monetary)",
        null=True, blank=True)
    monetary = models.BooleanField(
        verbose_name="Is this donation monetary?")
    description = models.CharField(max_length=100,
        verbose_name="Item Description (if not monetary)", 
        null=True, blank=True)
    date = models.DateField(
        verbose_name="Date of donation", default=datetime.now)
    comment = models.TextField(
        verbose_name="Comments", null=True, blank=True)

    class Meta:
        verbose_name = "Donation"

    def __unicode__(self):
        return u"{0} - {1}".format(self.donor.name, self.date)
    
class Visitor(models.Model):
    name = models.CharField(max_length=75,
        verbose_name="Visitor Name")
    date_of_birth = models.DateField(verbose_name="Date of Birth", null=True, blank=True)
    gender = models.CharField(max_length=1, choices = (('M', 'Male'), ('F', 'Female')), 
                            null=True, blank=True)
    town_of_residence = models.CharField(max_length=50,
        verbose_name="Town of Residence", null=True, blank=True)
    town_of_id = models.CharField(max_length=50,
        verbose_name="Town of ID", null=True, blank=True)
    veteran = models.BooleanField(
        verbose_name="Is this visitor a veteran?")

    class Meta:
        verbose_name = "Visitor"

    def __unicode__(self):
        return unicode(self.name)

class VisitorQuestion(models.Model):
    title = models.CharField(max_length=75,
            verbose_name="Title")
    prompt = models.CharField(max_length=200,
            verbose_name="Prompt")
    type = models.CharField(max_length=50, choices=(("CHECKBOX", "Check Box"), ))

    class Meta:
        verbose_name = "Visitor Question"

    def __unicode__(self):
        return unicode(self.title)

class VisitorResponse(models.Model):
    visitor = models.ForeignKey(Visitor, verbose_name="Visitor")
    question = models.ForeignKey(VisitorQuestion, verbose_name="Question")
    bool_response = models.BooleanField(verbose_name="Did the visitor respond affirmatively?")

    class Meta:
        verbose_name = "Visitor Response"

    def __unicode__(self):
        return unicode(self.visitor) + u" - " + unicode(self.question)

    
class VisitType(models.Model):
    type = models.CharField(max_length=50, unique=True, 
        verbose_name="Visit Type")

    class Meta:
        verbose_name = "Visit Type"

    def __unicode__(self):
        return unicode(self.type)

class ParticipationType(models.Model):
    type = models.CharField(max_length=50, unique=True,
        verbose_name="Participation Type")

    class Meta:
        verbose_name = "Participation Type"

    def __unicode__(self):
        return unicode(self.type)

class Visit(models.Model):
    visitor = models.ForeignKey(Visitor, verbose_name="Visitor")
    date = models.DateField(verbose_name="Visit Date", default=datetime.now)
    visit_type = models.ForeignKey(VisitType, verbose_name="Visit Type")
    comment = models.TextField(verbose_name="Comments", null=True, blank=True)

    class Meta:
        verbose_name = "Visit"

    def __unicode__(self):
        return unicode(self.visitor)
    
class Volunteer(models.Model):
    name = models.CharField(max_length=75, 
        verbose_name="Volunteer Name",
        help_text="Enter the full name of the volunteer or volunteer group")
    date_of_birth = models.DateField(verbose_name="Date of Birth", null=True, blank=True)
    street_1 = models.CharField(max_length=50,
        verbose_name="Street Address 1", null=True, blank=True)
    street_2 = models.CharField(max_length=50,
        verbose_name="Street Address 2", null=True, blank=True)
    town = models.CharField(max_length=50,
        verbose_name="Town", null=True, blank=True)
    zip = models.CharField(max_length=9,
        verbose_name="Zip", null=True, blank=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, 
        null=True, blank=True, verbose_name="State", default="NH")
    is_group = models.BooleanField(verbose_name="Is this a group?")
    contact_name = models.CharField(max_length=50, null=True, blank=True, 
                verbose_name="Contact Name (for group)")
    phone = models.CharField(max_length=20, null=True, blank=True,
                verbose_name="Phone")
    email = models.CharField(max_length=50, null=True, blank=True,
                verbose_name="Email")


    class Meta:
        verbose_name = "Volunteer"

    def __unicode__(self):
        return unicode(self.name)
    
class VolunteerParticipation(models.Model):
    date = models.DateField(verbose_name="Participation date")
    volunteer = models.ForeignKey(Volunteer, verbose_name="Volunteer")
    hours = models.DecimalField(max_digits=4, 
        decimal_places=2, verbose_name="Number of hours")
    num_participants = models.IntegerField(
        verbose_name="Number of participants (if group)", null=True, blank=True)
    participation_type = models.ForeignKey(ParticipationType, 
        verbose_name="Participation Type")
    comment = models.TextField(verbose_name="Comments", null=True, blank=True)

    class Meta:
        verbose_name = "Volunteer Participation"

    def __unicode__(self):
        return u"{0} - {1}".format(volunteer.name, date)
