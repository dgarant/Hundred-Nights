# Create your views here.
from django.shortcuts import render, redirect
from HundredNights.models import *
from HundredNights.forms import *
from django.views.decorators.csrf import csrf_protect
from datetime import datetime, timedelta
from dateutil import parser
from django.db.models import Sum, Count
from django.forms.models import modelformset_factory, inlineformset_factory
from django.forms import widgets
from django.core import serializers
from django.utils import simplejson
from django.db import connection
from django.http import HttpResponse
from report_renderer import ReportRenderer
from django.contrib.auth.decorators import login_required
import csv, sys, os

@login_required
def index(request):
    """ Returns a view of the dashboard"""
    return render(request, 'index.html', {})

@login_required
def united_way_report(request):
    """ Creates a report representing responses to 
        per-visit and one-time questions over a time window
    """
    renderer = ReportRenderer()
    start_date = parser.parse(request.GET.get('start-date', 
        datetime.now() - timedelta(days=30)))
    end_date = parser.parse(request.GET.get('end-date', datetime.now()))
    return renderer.create_united_way_report_html(start_date, end_date)

@login_required
def visit_report(request):
    """ Creates a report representing visits over a time period """
    renderer = ReportRenderer()

    output_format = request.GET.get('format', 'html')
    start_date = parser.parse(request.GET.get('start-date', 
        datetime.now() - timedelta(days=30)))
    end_date = parser.parse(request.GET.get('end-date', datetime.now()))
    if output_format == 'html':
        return renderer.create_visit_report_html(start_date, end_date)
    else:
        return renderer.create_visit_report_csv(start_date, end_date)

@login_required
def donation_report(request):
    """ Creates a report representing donations over a time period """
    renderer = ReportRenderer()
    output_format = request.GET.get('format', 'html')
    report_type = request.GET.get('type', 'full')

    start_date = parser.parse(request.GET.get('start-date', 
        datetime.now() - timedelta(days=30)))
    end_date = parser.parse(request.GET.get('end-date', datetime.now()))

    if report_type == "full":
        if output_format == 'html':
            return renderer.create_donation_report_html(start_date, end_date)
        else:
            return renderer.create_donation_report_csv(start_date, end_date)
    else: # mailing labels
        if output_format == "html":
            return renderer.create_mailing_label_report_html()
        else:
            return renderer.create_mailing_label_report_csv()

@login_required
def participation_report(request):
    """ Creates a report representing volunteer time within a date range"""
    renderer = ReportRenderer()
    output_format = request.GET.get('format', 'html')
    start_date = parser.parse(request.GET.get('start-date', 
        datetime.now() - timedelta(days=30)))
    end_date = parser.parse(request.GET.get('end-date', datetime.now()))
    if output_format == 'html':
        return renderer.create_participation_report_html(start_date, end_date)
    else:
        return renderer.create_participation_report_csv(start_date, end_date)

@login_required
def visits_by_month(request):
    """ Creates a JSON result set indicating the 
        number of visits over time
    """
    cursor = connection.cursor()
    cursor.execute("""select 
                        to_char(date, 'YYYY-MM') as MonthName, 
                        count(*) as VisitCount
                      from "HundredNights_visit"
                      group by to_char(date, 'YYYY-MM'), MonthName
                      order by to_char(date, 'YYYY-MM')
                      """)
    results = cursor.fetchall()
    return HttpResponse(simplejson.dumps(results), 
            content_type='application/json')

@login_required
def volunteer_hours_by_month(request):
    """ Creates a JSON result set indicating the number of 
        volunteer hours over time
    """
    cursor = connection.cursor()
    cursor.execute("""select
                    to_char(date, 'YYYY-MM') as MonthName,
                    sum(hours * coalesce(num_participants, 1)) as Hours
                    from "HundredNights_volunteerparticipation"
                    group by to_char(date, 'YYYY-MM'), MonthName
                    order by to_char(date, 'YYYY-MM')
                    """)
    results = cursor.fetchall()
    return HttpResponse(simplejson.dumps(results, use_decimal=True),
                content_type='application/json')

@login_required
def edit_visit(request, visitor_id, visit_id=None):
    """ Create a view used to edit a visit for a particular visitor

        Keyword arguments:
            visitor_id -- The integer ID of the visitor to 
                          add/edit/update the visit for
            visit_id -- Primary key of the visit, 
                        required to edit an existing visit.
        Returns a view of the visitor on POST, 
            or an edit page for the visit on GET
    """
    visitor = Visitor.objects.get(id=visitor_id)
    visit = None
    try:
        visit = Visit.objects.select_related().get(id=visit_id)

        # attach new questions
        new_questions = [q for q in VisitQuestion.objects.all()
                 if not q in [r.question for r in visit.visitresponse_set.all()]]
        for new_question in new_questions:
            resp = VisitResponse.objects.create(visit=visit, question=new_question)

    except Visit.DoesNotExist:
        form = VisitForm(initial={'visitor' : visitor.pk})
        qforms = VisitQuestionForm()

    if request.method == "POST":
        form = VisitForm(request.POST, request.FILES, instance=visit)
        qforms = VisitQuestionForm(request.POST, request.FILES, instance=visit)
        if form.is_valid() and qforms.is_valid():
            new_visit = form.save()
            qforms.save()

            # on adds, re-render the page so visit questions can be assigned
            if visit:
                return redirect("edit-visitor", visitor_id=visitor_id)

            new_questions = [q for q in VisitQuestion.objects.all()
                    if not q in [r.question for r in new_visit.visitresponse_set.all()]]
            for new_question in new_questions:
                resp = VisitResponse.objects.create(visit=new_visit, question=new_question)
            qforms = VisitQuestionForm(instance=new_visit)
    elif visit_id:
        form = VisitForm(instance=visit, 
                    initial={'visitor' : visitor.pk})
        qforms = VisitQuestionForm(instance=visit)

    return render(request, 'edit-visit.html',
        {"form" : form, "visitor" : visitor, "responses" : qforms})

@login_required
def delete_visit(request, visit_id):
    """ Removes a visit from the database

        Keyword arguments:
            visit_id -- The primary key of the visit to delete
        Returns a view of the visitor
    """
    visit = Visit.objects.get(id=visit_id)
    visitor_id = visit.visitor.id
    visit.delete()
    return redirect('edit-visitor', visitor_id=visitor_id)

@login_required
def visitor_check_in_resource(request, visitor_id):
    """ Adds a visit to resource center for the 
        specified visitor on the current date

        Keyword arguments:
            visitor_id -- The primary key of the visitor 
                            to log a new visit for
        Returns a view of the visitor with the newly added visit
    """
    visitor = Visitor.objects.get(id=visitor_id)
    visit = Visit()
    visit.visitor = visitor
    visit.date = datetime.now()
    visit.visit_type = VisitType.objects.get(type="Resource Center")
    visit.save()
    return redirect('edit-visitor', visitor_id=visitor_id)

@login_required
def visitor_check_in_overnight(request, visitor_id):
    """ Adds an overnight visit for the 
        specified visitor on the current date

        Keyword arguments:
            visitor_id -- The primary key of the visitor
                            to log a new visit for
        Returns a view of the visitor with the newly added visit
    """
    visitor = Visitor.objects.get(id=visitor_id)
    visit = Visit()
    visit.visitor = visitor
    visit.date = datetime.now()
    visit.visit_type = VisitType.objects.get(type="Overnight")
    visit.save()
    return redirect('edit-visitor', visitor_id=visitor_id)

@login_required
def visit_log(request):
    """ Presents a view of all visitors """
    return render(request, 'visitor-list.html', 
            {"visitors" : Visitor.objects.all()})

@login_required
def edit_visitor(request, visitor_id=None):
    """ Presents a view used to add or edit a visitor.

        Keyword arguments:
            visitor_id -- The primary key of the visitor to edit,   
                            or None to perform an add
        Returns a view used to edit the visitor on GET, or on POST, 
                returns a rediection to the visitor list
    """
    visitor = None
    try:
        visitor = Visitor.objects.select_related().get(id=visitor_id)
        visits = visitor.visit_set.all()

        # attach new questions
        new_questions = [q for q in VisitorQuestion.objects.all() 
                        if not q in [r.question for r in visitor.visitorresponse_set.all()]]
        for new_question in new_questions:
            resp = VisitorResponse.objects.create(visitor=visitor, question=new_question)
    except Visitor.DoesNotExist:
        form = VisitorForm()
        qforms = VisitorQuestionForm()
        visits = []

    if request.method == "POST":
        form = VisitorForm(request.POST, request.FILES, instance=visitor)
        qforms = VisitorQuestionForm(request.POST, request.FILES, instance=visitor)
        if form.is_valid() and qforms.is_valid():
            new_visitor = form.save()
            qforms.save()

            # on adds, re-render the page so donations can be added
            if visitor:
                return redirect("visitors")

            # attach new questions
            new_questions = [q for q in VisitorQuestion.objects.all() 
                            if not q in [r.question for r in new_visitor.visitorresponse_set.all()]]
            for new_question in new_questions:
                resp = VisitorResponse.objects.create(
                        visitor=new_visitor, question=new_question)
            qforms = VisitorQuestionForm(instance=new_visitor)
    elif visitor_id:
        form = VisitorForm(instance=visitor)
        qforms = VisitorQuestionForm(instance=visitor)

    return render(request, 'edit-visitor.html', 
        {
            "form" : form, 
            "visits" : visits, 
            "question_forms" : qforms,
         })

@login_required
def delete_visitor(request, visitor_id):
    """ Removes a visitor from the database

        Keyword arguments:
            visitor_id -- The ID of the visitor to 
                            remove from the database
        Returns a redirection to a view of the visitor list
    """
    visitor = Visitor.objects.get(id=visitor_id)
    visitor.delete()
    return redirect("visitors")

@login_required
def volunteers(request):
    """ Presents a list of volunteers """
    volunteers = Volunteer.objects.all()
    return render(request, 'volunteer-list.html', 
            {"volunteers" : volunteers})

@login_required
def edit_volunteer(request, volunteer_id=None):
    """ Presents a view used to edit a volunteer

        Keyword arguments:
            volunteer_id -- The primary key of the volunteer 
                        to edit, or None to perform an add
        Returns a view used to edit the volunteer on GET, 
            or a redirection to the volunteer list on POST
    """
    volunteer = None
    try:
        volunteer = Volunteer.objects.get(id=volunteer_id)
        participation = volunteer.volunteerparticipation_set.all()
    except Volunteer.DoesNotExist:
        print("Volunteer with id {0} does not exist".format(volunteer_id))
        form = VolunteerForm()
        participation = []

    if request.method == "POST":
        form = VolunteerForm(request.POST, request.FILES, instance=volunteer)
        if form.is_valid():
            svol = form.save()

            # on adds, re-render the page so participation can be added
            if volunteer != None:
                return redirect("volunteers")
            else: # set up the volunteer as a donor also
                donor = Donor(name=svol.name, street_1=svol.street_1, 
                                street_2=svol.street_2, city=svol.town, 
                                state=svol.state, zip=svol.zip)
                donor.save()

    elif volunteer_id:
        form = VolunteerForm(instance=volunteer)

    return render(request, 'edit-volunteer.html', 
        {"form" : form, "participation" : participation})

@login_required
def delete_volunteer(request, volunteer_id=None):
    """ Deletes a volunteer from the database
        Keyword arguments:
            volunteer_id -- The primary key of the volunteer to delete
        Returns a view of the list of volunteers
    """
    volunteer = Volunteer.objects.get(id=volunteer_id)
    volunteer.delete()
    return redirect("volunteers")

@login_required
def edit_participation(request, volunteer_id, part_id=None):
    """ Presents a view used to edit volunteer participation
        Keyword arguments:
            volunteer_id -- The primary key of the volunteer
                    to add or edit participation for
            part_id -- The primary key of the participation 
                    to edit, or None to perform an add
        Returns a view used to edit the volunteer on GET,
            or a list of volunteers on POST
    """
    volunteer = Volunteer.objects.get(id=volunteer_id)
    participation = None
    try:
        participation = VolunteerParticipation.objects.get(id=part_id)
    except VolunteerParticipation.DoesNotExist:
        form = ParticipationForm(initial={"volunteer" : volunteer.pk})

    if request.method == "POST":
        form = ParticipationForm(request.POST, request.FILES, instance=participation)
        if form.is_valid():
            form.save()
            return redirect("edit-volunteer", volunteer_id=volunteer_id)
    elif part_id:
        form = ParticipationForm(instance=participation, 
                    initial={'volunteer' : volunteer.pk})

    return render(request, 'edit-participation.html',
        {"form" : form, "volunteer" : volunteer})

@login_required
def delete_participation(request, part_id=None):
    """ Deletes a participation record.
        Keyword arguments:
            part_id -- The primary key of the 
                participation record to delete
        Returns a view used to edit the volunteer
    """
    to_delete = VolunteerParticipation.objects.get(id=part_id)
    volunteer_id = to_delete.volunteer.id
    to_delete.delete()
    return redirect("edit-volunteer", volunteer_id=volunteer_id)

@login_required
def donors(request):
    """ Presents a list of donors """
    donors = Donor.objects.all()
    return render(request, 'donor-list.html', {"donors" : donors})

@login_required
def edit_donor(request, donor_id=None):
    """ Presents a view used to edit a donor
        Keyword arguments:
            donor_id -- The primary key of the donor to edit
        Returns an edit template, or on POST, 
            a redirection to the donor list
    """
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

@login_required
def delete_donor(request, donor_id):
    """ Removes a donor from the databse
        Keyword arguments:
            donor_id -- The primary key of the donor to delete
        Returns a redirection to a list of donors
    """
    to_delete = Donor.objects.get(id=donor_id)
    to_delete.delete()
    return redirect("donors")

@login_required
def edit_donation(request, donor_id, donation_id=None):
    """ Presents a page to edit a donation
        Keyword arguments:
            donor_id -- The primary key of the donor 
                    to add or edit a donation for
            donation_id -- The primary key of the donation to 
                    edit, or None to perform an add
        Returns an edit template for a donation on GET, 
            or on POST a redirection to the donor list
    """
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

@login_required
def delete_donation(request, donation_id):
    """ Deletes a donation from the database
        Keyword arguments:
            donation_id -- The primary key of 
                            the donation to delete
        Returns a view of a page used to edit the donor
    """
    to_delete = Donation.objects.get(id=donation_id)
    donor_id = to_delete.donor.id
    to_delete.delete()
    return redirect("edit-donor", donor_id=donor_id)

@login_required
@csrf_protect
def upload_donors(request):
    """ Handles an upload of donors in a CSV format """
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

@login_required
@csrf_protect
def upload_visitors(request):
    """ Handles an upload of visitors in a CSV format """
    gender_path = os.path.join(
        os.path.dirname(__file__), '..', 'Name-Gender-Guesser')
    sys.path.append(gender_path)
    from name_gender import NameGender

    primary_guesser = NameGender(
                    os.path.join(gender_path, "us_census_1990_males"), 
                    os.path.join(gender_path, "us_census_1990_females"))
    secondary_guesser = NameGender(
                    os.path.join(gender_path, "popular_1960_2010_males"),
                    os.path.join(gender_path, "popular_1960_2010_females"))

    def guess_gender(guesser, first_name):
        m,f = guesser.get_gender_scores(first_name)
        #print("Name: {0}, male: {1}, female: {2}".format(first_name, m, f))
        if m > 0.8:
            return "M"
        elif f > 0.8:
            return "F"
        else:
            return None

    for row in csv.DictReader(request.FILES["visitor-csv"]):

        try:
            # try to find the user on their last name
            # if there are multiple users with the same, use the full name
            first_name = None
            try:
                last_name, first_name = row["Name"].split(",")
                first_name = first_name.strip(" ")
                visitor = Visitor.objects.get(name__icontains=last_name)
                if len(row["Name"]) > len(visitor.name):
                    visitor.name = row["Name"]
                    visitor.save()
            except:
                visitor = Visitor.objects.get(name=row["Name"])
        except Visitor.DoesNotExist:
            visitor = Visitor()
            visitor.name = row["Name"]
            #visitor.age = int(row[1])
            if first_name:
                visitor.gender = guess_gender(primary_guesser, first_name)
                if not visitor.gender:
                    visitor.gender = guess_gender(secondary_guesser, first_name)

            visitor.town_of_residence = row["Town"]
            visitor.town_of_id = row["TownOfId"]
            visitor.veteran = False#row[4].lower() == "true"
            visitor.save()
        
        visit = Visit()
        visit.visitor = visitor
        visit.date = parser.parse(row["DateOfVisit"])
        visit.visit_type = VisitType.objects.get(
                    type=request.POST.get("visit-type"))
        #visit.comment = row[7]
        visit.save()
    return render(request, 'index.html', {})

@login_required
@csrf_protect
def upload_volunteers(request):
    """ Handles an upload of volunteers in a CSV format """
    for row in csv.DictReader(request.FILES["volunteer-csv"]):
        try:
            volunteer = Volunteer.objects.get(name=row["Person"])
        except Volunteer.DoesNotExist:
            volunteer = Volunteer()
            volunteer.name = row["Person"]
            volunteer.save()

        part = VolunteerParticipation()
        part.volunteer = volunteer
        part.date = parser.parse(row["Date"])
        part.hours = row["Hours"]
        part.participation_type = ParticipationType.objects.get(
                                        type=row["VolType"])
        part.comment = row["Comment"]
        part.save()

    return render(request, 'index.html', {})

