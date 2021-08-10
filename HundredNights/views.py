# Create your views here.
from django.shortcuts import render, redirect
from HundredNights.models import *
from HundredNights.forms import *
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.db import DatabaseError
from django.db.models import Sum, Count
from django.forms.models import modelformset_factory, inlineformset_factory
from django.forms import widgets
from django.core import serializers
from django.db import connection
from django.http import HttpResponse
import django
from HundredNights.report_renderer import ReportRenderer
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.serializers.json import DjangoJSONEncoder
import csv, sys, os
import decimal
import json

class HNEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(HNEncoder, self).default(o)

@login_required
def index(request):
    """ Returns a view of the dashboard"""
    return render(request, 'index.html', {"visit_types" : VisitType.objects.all()})

@login_required
@csrf_protect
@require_POST
def united_way_report(request):
    """ Creates a report representing responses to 
        per-visit and one-time questions over a time window
    """
    renderer = ReportRenderer()
    if "start-date" in request.POST:
        start_date = parser.parse(request.POST.get('start-date'))
    else:
        start_date = datetime.now() - timedelta(days=30)

    if "end-date" in request.POST:
        end_date = parser.parse(request.POST.get('end-date'))
    else:
        end_date = datetime.now()

    visit_types = VisitType.objects.filter(id__in=request.POST.getlist("visit-type"))
    return renderer.create_united_way_report_html(
                request, start_date, end_date, visit_types)

@login_required
def visitor_report(request):
    """ Creates a report rendering information about visitors """
    renderer = ReportRenderer()
    return renderer.create_visitor_report_csv()

@login_required
def visit_report(request):
    """ Creates a report representing visits over a time period """
    renderer = ReportRenderer()

    output_format = request.GET.get('format', 'html')
    start_date = parser.parse(request.GET.get('start-date', 
        datetime.now() - timedelta(days=30)))
    end_date = parser.parse(request.GET.get('end-date', datetime.now()))
    if output_format == 'html':
        return renderer.create_visit_report_html(request, start_date, end_date)
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
            return renderer.create_donation_report_html(request, start_date, end_date)
        else:
            return renderer.create_donation_report_csv(start_date, end_date)
    else: # mailing labels
        if output_format == "html":
            return renderer.create_mailing_label_report_html(request)
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
        return renderer.create_participation_report_html(request, start_date, end_date)
    else:
        return renderer.create_participation_report_csv(start_date, end_date)

@login_required
@csrf_protect
def visitor_filter(request):
    ethnicity_filter = request.POST.get("ethnicity_filter", None)
    town_of_id_filter = request.POST.get("town_of_id_filter", None)
    town_of_resid_filter = request.POST.get("town_of_resid_filter", None)
    age_filter = request.POST.get("age_filter", None)
    income_filter = request.POST.get("income_filter", None)
    start_date = request.POST.get("start_date", None)
    end_date = request.POST.get("end_date", None)
    visit_type_ids = request.POST.getlist("visit_types", None)
    if not start_date or not end_date or not visit_type_ids:
        return HttpResponse(json.dumps(
                {"result" : "error", 
                 "message" : "Missing one or more required parameters. " + 
                    "Expected question_id, start_date, end_date, and visit_type"}), 
                    content_type="application/json")
    try:
        start_date = parser.parse(start_date)
        end_date = parser.parse(end_date)
    except Exception as ex:
        return HttpResponse(json.dumps(
                {"result" : "error", 
                 "message" : "Failed to parse a supplied date. " + 
                             "Message was {0}.".format(ex)}),
                    content_type="application/json")
    
    visit_query = Visit.objects.select_related("visitor").filter(
            date__gte = start_date, date__lte = end_date, 
            visit_type__id__in = visit_type_ids)

    def income_match(income):
        if income_filter:
            if income_filter == "Unknown":
                return (income is None or income < 0)
            elif income is None or income < 0:
                return False
            elif "+" in income_filter:
                return income >= float(income_filter.replace("+", ""))
            else:
                lower, upper = income_filter.split("-")
                return float(lower) <= income and float(upper) >= income
        else:
            return True

    def ethnicity_match(ethnicity):
        if ethnicity_filter:
            return (ethnicity_filter == "Unknown" and ethnicity is None) or (ethnicity == ethnicity_filter)
        else:
            return True

    today = datetime.now()
    def age_match(date_of_birth):
        if age_filter:
            if age_filter == "Unknown":
                return date_of_birth is None
            elif date_of_birth is None:
                return False
            else: # age is  known
                age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
                if "+" in age_filter and float(age_filter.replace("+", "")) <= age:
                    return True
                else:
                    lower, upper = age_filter.split("-")
                    return float(lower) <= age and float(upper) >= age
        else:
            return True

    def town_match(town, town_filter):
        return (town_filter is None or 
                town.upper().strip() == town_filter.upper().strip())

    visitors = []
    saw_visitor_ids = set()
    for v in visit_query:
        if not v.visitor.id in saw_visitor_ids:
            saw_visitor_ids.add(v.visitor.id)
            if (income_match(v.visitor.income_val) and 
                    ethnicity_match(v.visitor.get_ethnicity_display()) and 
                    age_match(v.visitor.date_of_birth) and
                    town_match(v.visitor.town_of_id, town_of_id_filter) and
                    town_match(v.visitor.town_of_residence, town_of_resid_filter)):
                visitors.append({"name" : v.visitor.name, "id" : v.visitor.id})

    return HttpResponse(json.dumps(
                {
                    "result" : "success", 
                    "respondents" : sorted(visitors, key=lambda x: x["name"])
                 }), content_type="application/json")

@login_required
@csrf_protect
def visitor_respondents(request):
    question_id = request.POST.get("question_id", None)
    start_date = request.POST.get("start_date", None)
    end_date = request.POST.get("end_date", None)
    affirmative_resp = request.POST.get("response_type", "true").lower()[0] == "t"
    visit_type_ids = request.POST.getlist("visit_types", None)
    if not question_id or not start_date or not end_date or not visit_type_ids:
        return HttpResponse(json.dumps(
                {"result" : "error", 
                 "message" : "Missing one or more required parameters. " + 
                    "Expected question_id, start_date, end_date, and visit_type"}), 
                    content_type="application/json")
    try:
        start_date = parser.parse(start_date)
        end_date = parser.parse(end_date)
    except Exception as ex:
        return HttpResponse(json.dumps(
                {"result" : "error", 
                 "message" : "Failed to parse a supplied date. " + 
                             "Message was {0}.".format(ex)}),
                    content_type="application/json")
    
    responses = VisitorResponse.objects.select_related("visitor").filter(
        question__id=question_id, bool_response=affirmative_resp)
    visitors_in_window = set([v.visitor.id for v in Visit.objects.filter(
            date__gte = start_date, date__lte = end_date, 
            visit_type__id__in = visit_type_ids).only("visitor__id")])

    respondents = []
    for response in responses:
        if response.visitor.id in visitors_in_window:
            respondents.append({"name" : response.visitor.name, 
                                "id" : response.visitor.id })
    return HttpResponse(json.dumps(
                {
                    "result" : "success", 
                    "respondents" : respondents
                 }, cls=HNEncoder),
            content_type="application/json")

@login_required
@csrf_protect
def visit_respondents(request):
    question_id = request.POST.get("question_id", None)
    start_date = request.POST.get("start_date", None)
    end_date = request.POST.get("end_date", None)
    affirmative_resp = request.POST.get("response_type", "true").lower()[0] == "t"
    visit_types = request.POST.getlist("visit_types", None)
    if not question_id or not start_date or not end_date or not visit_types:
        return HttpResponse(json.dumps(
                {"result" : "error", 
                 "message" : "Missing one or more required parameters. " + 
                    "Expected question_id, start_date, end_date, and visit_type"}), 
                    content_type="application/json")
    try:
        start_date = parser.parse(start_date)
        end_date = parser.parse(end_date)
    except ex:
        return HttpResponse(json.dumps(
                {"result" : "error", 
                 "message" : "Failed to parse a supplied date. " + 
                             "Message was {0}.".format(ex)}),
                    content_type="application/json")
    
    responses = VisitResponse.objects.select_related("visit__visitor").filter(
        question__id=question_id, bool_response=affirmative_resp, visit__date__gte = start_date,
        visit__date__lte = end_date, visit__visit_type__id__in = visit_types)

    respondents = []
    already_recorded = set()
    for response in responses:
        visitor_id = response.visit.visitor.id
        if not visitor_id in already_recorded:
            already_recorded.add(visitor_id)
            respondents.append({"name" : response.visit.visitor.name, 
                                "visitorid" : response.visit.visitor.id,
                                "id" : response.visit.id })
    return HttpResponse(json.dumps(
                {
                    "result" : "success", 
                    "respondents" : respondents
                }, cls=HNEncoder), content_type="application/json")

@login_required
def visits_by_month(request):
    """ Creates a JSON result set indicating the 
        number of visits over time
    """
    cursor = connection.cursor()
    try:
        cursor.execute("""select 
                            to_char(date, 'YYYY-MM') as MonthName, 
                            count(*) as VisitCount
                          from "HundredNights_visit"
                          group by to_char(date, 'YYYY-MM'), MonthName
                          order by to_char(date, 'YYYY-MM')
                          """)
    except DatabaseError:
        cursor.execute("""
            select 
                strftime('%Y-%m', date) as MonthName,
                count(*) as VisitCount
              from "HundredNights_visit"
                group by strftime('%Y-%m', date), MonthName
                order by strftime('%Y-%m', date)
              """)
    results = cursor.fetchall()
    return HttpResponse(json.dumps(results, cls=HNEncoder), 
            content_type='application/json')

@login_required
def volunteer_hours_by_month(request):
    """ Creates a JSON result set indicating the number of 
        volunteer hours over time
    """
    cursor = connection.cursor()
    try:
        cursor.execute("""
                    select
                        to_char(date, 'YYYY-MM') as MonthName,
                        sum(hours * coalesce(num_participants, 1)) as Hours
                    from "HundredNights_volunteerparticipation"
                    group by to_char(date, 'YYYY-MM'), MonthName
                    order by to_char(date, 'YYYY-MM')
                    """)
    except DatabaseError: #support either postgres or sqlite with raw SQL
        cursor.execute("""
                    select
                        strftime('%Y-%m', date) as MonthName,
                        sum(hours * coalesce(num_participants, 1)) as Hours
                    from "HundredNights_volunteerparticipation"
                    group by strftime('%Y-%m', date), MonthName
                    order by strftime('%Y-%m', date)
                    """)
    results = cursor.fetchall()
    return HttpResponse(json.dumps(results, cls=HNEncoder),
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
                 if not q in [r.question for r in visit.visitresponse_set.all()] and q.active]
        for new_question in new_questions:
            resp = VisitResponse.objects.create(visit=visit, question=new_question, bool_response=False)

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
                    if not q in [r.question for r in new_visit.visitresponse_set.all()] and q.active]
            for new_question in new_questions:
                resp = VisitResponse.objects.create(visit=new_visit, question=new_question, bool_response=False)
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
    return redirect('edit-visit', visitor_id=visitor_id, visit_id=visit.id)

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
    return redirect('edit-visit', visitor_id=visitor_id, visit_id=visit.id)

@login_required
def visitor_lookup(request):
    return render(request, 'bs_template.html')

@login_required
def visitor_search_api(request):
    name_filter = request.GET.get('name', None)
    vobjs = Visitor.objects.annotate(django.db.models.Max("visit__date"))
    if name_filter:
        results = vobjs.filter(name__icontains = name_filter)
    else:
        results = vobjs.objects.all()

    return HttpResponse(json.dumps([{
                "name" : v.name, "town_of_residence" : v.town_of_residence, 
                "town_of_id" : v.town_of_id, "id" : v.id, 
                "latest_check_in" : v.visit__date__max.isoformat() if v.visit__date__max else None} 
                    for v in results], cls=HNEncoder),
                 content_type="application/json")

@login_required
def visit_log(request, history_years=None):
    """ Presents a view of all visitors """
    if history_years:
        visitor_ids = Visit.objects.filter(date__gte = datetime.now() - relativedelta(years=2)).values_list("visitor__id", flat=True).distinct()
        visitors = Visitor.objects.filter(id__in = visitor_ids)
    else:
        visitors = Visitor.objects.all()

    return render(request, 'visitor-list.html', 
            {"visitors" : visitors, "year_filter" : history_years})

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
    alert = None
    try:
        visitor = Visitor.objects.select_related().get(id=visitor_id)
        visits = visitor.visit_set.select_related().all()
        last_check_in = max([v.date for v in visits]) if visits else None
        if not last_check_in is None and last_check_in < (datetime.now()- relativedelta(years=2)).date():
            alert = "It has been over two years since the last check-in. Consider collecting new information."
        
        # attach new questions
        new_questions = [q for q in VisitorQuestion.objects.all() 
                        if not q in [r.question for r in visitor.visitorresponse_set.all()]]
        for new_question in new_questions:
            resp = VisitorResponse.objects.create(visitor=visitor, question=new_question, bool_response=False)
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
            "alert" : alert,
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
    elif donor_id:
        form = DonorForm(instance=donor)

    return render(request, 'edit-donor.html', 
        {"form" : form, "donations" : donations})

@login_required
@require_POST
def delete_referral(request):
    """ Removes a referral from the database """
    to_delete = Referral.objects.get(id=request.POST.get("id"))
    to_delete.delete()
    return redirect("referrers")

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
def referrers(request):
    """ Presents a list of referrers """
    referrers = Referrer.objects.all()
    return render(request, "referrer-list.html", {"referrers" : referrers})

@login_required
def edit_referrer(request, referrer_id=None):
    """ Presents a page to edit a referrer
        Keyword arguments:
            referrer_id -- The primary key of the referrer, 
                           or None to perform an add
        Returns an edit template for the referrer
    """
    referrer = None
    try:
        referrer = Referrer.objects.get(id=referrer_id)
        referrals= referrer.referral_set.all()
    except Referrer.DoesNotExist:
        print("Referrer with id {0} does not exist".format(referrer_id))
        form = ReferrerForm()
        referrals = []

    if request.method == "POST": 
        form = ReferrerForm(request.POST, request.FILES, instance=referrer)
        if form.is_valid():
            form.save()
    elif referrer_id:
        form = ReferrerForm(instance=referrer)

    return render(request, 'edit-referrer.html', 
        {"form" : form, "referrals" : referrals})

@login_required
def edit_referral(request, referrer_id, referral_id=None):
    """ Presents a page to edit a referral  
        Keyword arguments:
            referrer_id -- The primary key of the referrer 
                    to add or edit a referral for
            referral_id -- The primary key of the referral to 
                    edit, or None to perform an add
        Returns an edit template for a donation on GET, 
            or on POST a redirection to the donor list
    """
    referrer = Referrer.objects.get(id=referrer_id)
    referral = None
    try:
        referral = Referral.objects.get(id=referral_id)
    except Referral.DoesNotExist:
        form = ReferralForm(initial={'referrer' : referrer.pk})

    if request.method == "POST":
        form = ReferralForm(request.POST, request.FILES, instance=referral)
        if form.is_valid():
            form.save()
            return redirect("edit-referrer", referrer_id=referrer_id)
    elif referral_id:
        form = ReferralForm(instance=referral, 
                    initial={'referrer' : referrer.pk})

    return render(request, 'edit-referral.html',
        {"form" : form, "referrer" : referrer})

@login_required
@require_POST
def delete_referrer(request):
    """ Removes a referrer from the databse.
        Returns a redirection to a list of referrers
    """
    to_delete = Referrer.objects.get(id=request.POST.get("id"))
    to_delete.delete()
    return redirect("referrers")
    
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
                    str(ex), row_num, row)) from e

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

