# Create your views here.
from django.shortcuts import render, redirect
from HundredNights.models import *
from HundredNights.forms import *
from django.views.decorators.csrf import csrf_protect
import csv, sys
from datetime import datetime
from dateutil import parser
from django.db.models import Sum, Count
from django.forms.models import modelformset_factory, inlineformset_factory
from django.forms import widgets

def index(request):
    return render(request, 'index.html', {})

def visit_log(request):
    return render(request, 'visitor-list.html', 
            {"visitors" : Visitor.objects.all()})

def donors(request):
    donors = Donor.objects.all()
    return render(request, 'donor-list.html', {"donors" : donors})

def volunteers(request):
    return render(request, 'volunteer-list.html', {})

def edit_visitor(request):
    return render(request, 'edit-visitor.html', {})

def edit_donor(request, donor_id=None):
    donor = None
    try:
        donor = Donor.objects.get(id=donor_id)
        donations = donor.donation_set.all()
    except Donor.DoesNotExist:
        print("Donor with id {0} does not exist".format(donor_id))
        form = DonorForm()
        donations = []

    if request.method == "POST": 
        form = DonorForm(request.POST, request.FILES, instance=donor)
        if form.is_valid():
            form.save()
            # on adds, re-render the page so donations can be added
            if donor != None:
                return redirect("donors")
    elif donor_id:
        form = DonorForm(instance=donor)

    return render(request, 'edit-donor.html', 
        {"form" : form, "donations" : donations})

def delete_donor(request, donor_id):
    to_delete = Donor.objects.get(id=donor_id)
    to_delete.delete()
    return redirect("donors")

def edit_donation(request, donor_id, donation_id=None):
    donor = Donor.objects.get(id=donor_id)
    donation = None
    try:
        donation = Donation.objects.get(id=donation_id)
    except Donation.DoesNotExist:
        form = DonationForm(initial={'donor' : donor.pk})

    if request.method == "POST":
        form = DonationForm(request.POST, request.FILES, instance=donation)
        if form.is_valid():
            print("Donor: {0}".format(donor_id))
            form.save()
            return redirect("edit-donor", donor_id=donor_id)
    elif donation_id:
        form = DonationForm(instance=donation, 
                    initial={'donor' : donor.pk})

    return render(request, 'edit-donation.html',
        {"form" : form, "donor" : donor})

def delete_donation(request, donation_id):
    to_delete = Donation.objects.get(id=donation_id)
    donor_id = to_delete.donor.id
    to_delete.delete()
    return redirect("edit-donor", donor_id=donor_id)

def edit_volunteer(request):
    return render(request, 'edit-volunteer.html', {})
    
@csrf_protect
def upload_donors(request):
    row_num = 0
    for row in csv.DictReader(request.FILES["donor-csv"]):
        row_num += 1
        try:
            donor = Donor()
            try:
                donor = Donor.objects.get(name=row["name"])
            except Donor.DoesNotExist:
                donor.name = row["name"]
                donor.street_1 = row["street1"]
                donor.street_2 = row["street2"]
                donor.city = row["city"]
                donor.zip = row["zip"]
                donor.state = row["state"]
                donor.is_organization = row["isorganization"].lower() == "true" or row["isorganization"] == "1"
                donor.org_contact = row["contact"]
                donor.phone = row["phone"]
                donor.email = row["email"]
                donor.save()

            # we don't always have a donation, sometimes just a donor
            if row["amount"] != "" or row["description"] != "":

                row["amount"] = row["amount"].replace("&", "+")
                # sometimes we have multiple donations per row
                if "+" in row["amount"] or "&" in row["amount"]:
                    amounts = [a for a in row["amount"].split("+")]
                else:
                    amounts = [row["amount"]]

                if "+" in row["date"]:
                    dates = [parser.parse(p) for p in row["date"].split("+")]
                else:
                    dates = [parser.parse(row["date"])]

                donation_num = 0
                for amount in amounts:
                    amount = amount.translate(None, ", \t$")
                    donation = Donation()
                    donation.donor = donor
                    donation.monetary = row["ismonetary"].lower() == "true" or row["ismonetary"] == "1"
                    donation.description = row["description"]
                    donation.amount = amount if donation.monetary else None
                    donation.date = dates[donation_num % len(dates)]
                    #donation.comment = row["comment"]
                    donation.save()

                    donation_num += 1

        except Exception as ex:
            raise ValueError("{0}\nRow {1}\nRow Values: {2}".format(
                    str(ex), row_num, row)), None, sys.exc_info()[2]

    return render(request, 'index.html', {})

@csrf_protect
def upload_visitors(request):
    for row in csv.DictReader(request.FILES["visitor-csv"]):

        try:
            visitor = Visitor.objects.get(name=row["Name"])
        except Visitor.DoesNotExist:
            visitor = Visitor()
            visitor.name = row["Name"]
            #visitor.age = int(row[1])
            visitor.town_of_residence = row["Town"]
            visitor.town_of_id = row["TownOfId"]
            visitor.veteran = False#row[4].lower() == "true"
            visitor.save()
        
        visit = Visit()
        visit.visitor = visitor
        visit.date = parser.parse(row["DateOfVisit"])
        visit.visit_type = VisitType.objects.get(type="Overnight")
        #visit.comment = row[7]
    return render(request, 'index.html', {})

