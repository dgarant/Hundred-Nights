import locale # for formatting

import django
import os
import datetime
from datetime import date
from io import BytesIO
from io import StringIO
import csv
import datetime
from django.conf import settings
from django.http import HttpResponse
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.shortcuts import render_to_response
from HundredNights.models import *
from itertools import chain
from collections import defaultdict
import collections
from dateutil.relativedelta import relativedelta

class TwoWayCountTable(object):
    """ Tracks counts of two discrete variables """

    def __init__(self, states_var1, states_var2):
        self.states_var1 = states_var1
        self.states_var2 = states_var2
        self.counts = dict()
        for s1 in self.states_var1:
            for s2 in self.states_var2:
                self.counts[(s1, s2)] = 0

    def add(self, val1, val2):
        """ Incorporates the two variables into the table """
        self.counts[(val1, val2)] += 1

    def row_names(self):
        return self.states_var1

    def col_names(self):
        return self.states_var2

    def rows(self):
        for s1 in self.states_var1:
            row = []
            for s2 in self.states_var2:
                row.append(self.counts[(s1, s2)])
            yield [s1] + row

    def rows_with_total(self):
        for row in self.rows():
            yield [row[0]] + row[1:] + [sum(row[1:])]

class ReportRenderer(object):

    def __init__(self):
        pass

    def __render_to_html(self, template_path, request, data_dict):
        return render_to_response(template_path, data_dict, 
                        context_instance=RequestContext(request))

    def __render_to_csv(self, field_names, data, filename):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)

        writer = csv.writer(response)
        writer.writerow(field_names)
        for row in data:
            writer.writerow([unicode(s).encode("ascii", "ignore") if s else "" for s in row])
        
        return response

    def create_united_way_report_html(self, request, start_date, end_date, visit_types):
        """ Builds a page from an HTML template """
        visit_type_ids = [v.id for v in visit_types]
        visit_questions = [] # contianing tuples (prompt, count, distinct users)
        for question in VisitQuestion.objects.all():
            responses = question.visitresponse_set. \
                select_related("visit").filter(
                visit__date__gte=start_date,
                visit__date__lte=end_date,
                visit__visit_type_id__in=visit_type_ids,
                bool_response=True).all()
            visitor_ids = set()
            for resp in responses:
                visitor_ids.add(resp.visit.visitor_id)

            if responses.count() > 0:
                visit_questions.append(
                    (question, responses.count(), len(visitor_ids)))

        questions = VisitorQuestion.objects.all()
        question_ids = set(questions.values_list('id', flat=True).distinct())

        visitor_questions = dict([(q, 0) for q in questions])
        # maps from town to [num. unique visitors, total visits]
        visitors_by_id_town = defaultdict(lambda: [0, 0])
        visitors_by_resid_town = defaultdict(lambda: [0, 0])

        overall_total_visits = 0
        num_unique_visitors = 0
        num_veteran_visits = 0
        num_visiting_veterans = 0

        gender_choices = ["Female", "Male"]

        # create age bins for fast lookup
        age_map = dict()
        distinct_age_vals = set()
        age_vals = []
        end_points = [-1, 5, 12, 17, 24, 35, 45, 55, 65, 75, 200]
        for i in range(1, len(end_points)):
            prev_val = end_points[i-1] + 1
            val = end_points[i]
            for age in range(prev_val, val+1):
                if end_points[i] == 200:
                    age_map[age] = "{0}+".format(end_points[i-1]+1)
                else:
                    age_map[age] = "{0}-{1}".format(prev_val, val)
                if not age_map[age] in distinct_age_vals:
                    distinct_age_vals.add(age_map[age])
                    age_vals.append(age_map[age])

        # setup income bins
        #income_bin_end_points = [-1, 11880, 17820, 23760, 29700]
        income_bin_end_points = [-1, 12140, 16753, 18210, 24280]
        income_options = [
                "{0}+".format(income_bin_end_points[i]+1) 
                    if (i == len(income_bin_end_points) - 1) 
                    else "{0}-{1}".format(income_bin_end_points[i]+1, income_bin_end_points[i+1])
                for i in range(len(income_bin_end_points))] + ["Unknown", ]

        def get_income_category(income_val):
            if income_val is None or income_val < 0:
                return "Unknown"
            for i, v in enumerate(income_bin_end_points):
                if income_val < v:
                    return "{0}-{1}".format(income_bin_end_points[i-1]+1, v)

            if i == len(income_bin_end_points) - 1:
                return "{0}+".format(v+1)

                

        ethnicity_choices = Visitor._meta.get_field_by_name("ethnicity")[0].choices
        ethnicity_vals = [e[1] for e in ethnicity_choices]
        ethnicity_table = TwoWayCountTable(ethnicity_vals, gender_choices)
        ethnicity_map = dict(ethnicity_choices)
        ethnicity_map[None] = "Unknown"

        income_table = TwoWayCountTable(income_options, gender_choices)

        num_male = 0 
        age_table = TwoWayCountTable(age_vals, gender_choices)

        unique_visitor_names = []
        for visitor in Visitor.objects \
                        .prefetch_related("visit_set", "visitorresponse_set"):
            num_visits = visitor.visit_set.filter(
                 date__gte = start_date, 
                 date__lte = end_date,
                 visit_type__id__in = visit_type_ids).count()
            if num_visits == 0:
                 continue
            num_unique_visitors += 1
            unique_visitor_names.append(visitor.name)
            overall_total_visits += num_visits
            num_visiting_veterans += 1 if visitor.veteran else 0
            num_veteran_visits += num_visits if visitor.veteran else 0
            if visitor.gender == "M":
                num_male += 1
                gender_label = "Male"
            else:
                gender_label = "Female"

            ethnicity_table.add(ethnicity_map[visitor.ethnicity], gender_label)
            income_table.add(get_income_category(visitor.income_val), gender_label)

            if visitor.date_of_birth:
                curr_age = self.calculate_age(visitor.date_of_birth)
                if curr_age in age_map:
                    age_table.add(age_map[curr_age], gender_label)

            unique_visits, total_visits = visitors_by_id_town[visitor.town_of_id.upper().strip()]
            visitors_by_id_town[visitor.town_of_id.upper().strip()] = [unique_visits+1, total_visits+num_visits]

            unique_visits, total_visits = visitors_by_resid_town[visitor.town_of_residence.upper().strip()]
            visitors_by_resid_town[visitor.town_of_residence.upper().strip()] = [unique_visits+1, total_visits+num_visits]

            for response in visitor.visitorresponse_set.filter(
                            question__id__in = question_ids, 
                            bool_response=True).all():
                visitor_questions[response.question] += 1
            
        return self.__render_to_html("united_way_report.html", request,
                {"num_unique_visitors" : num_unique_visitors,
                "total_visits" : overall_total_visits,
                 "visit_questions" : sorted(visit_questions), 
                 "start_date" : datetime.date(start_date), 
                 "end_date" : datetime.date(end_date),
                 "visitor_questions" : sorted(visitor_questions.iteritems()),
                 "visitors_by_id_town" : sorted([(k, c[0], c[1]) for k, c in visitors_by_id_town.iteritems()]),
                 "visitors_by_resid_town" : sorted([(k, c[0], c[1]) for k, c in visitors_by_resid_town.iteritems()]),
                 "report_header" : ", ".join([v.type for v in visit_types]),
                 "num_veteran_visits" : num_veteran_visits,
                 "num_visiting_veterans" : num_visiting_veterans,
                 "visit_types" : visit_types,
                 "ethnicity_distr" : ethnicity_table,
                 "income_distr" : income_table,
                 "age_distr" : age_table,
                 "num_male" : num_male,
                 "num_female" : num_unique_visitors - num_male,
                 "unique_visitor_names" : sorted(unique_visitor_names)
                 })

    def calculate_age(self, born):
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def __initialize_dict(self, allowable_entries):
        d = collections.OrderedDict()
        for entry in allowable_entries:
            d[entry] = 0
        return d

    def create_visitor_report_csv(self):
        all_visitors = (Visitor.objects
            .annotate(num_visits=django.db.models.Count("visit"),
                      last_visit_date=django.db.models.Max("visit__date"))
            .prefetch_related("visitorresponse_set", "visitorresponse_set__question")).all()

        unique_questions = set()
        for v in all_visitors:
            v.indexed_responses = dict()
            for r in v.visitorresponse_set.all():
                unique_questions.add(r.question)
                v.indexed_responses[r.question.title] = "Y" if r.bool_response else "N"

        visitor_questions = sorted([q for q in unique_questions], key=lambda x: x.title)
        question_cols = [q.title for q in visitor_questions]


        filename = 'HundredNightsVisitors-{0}.csv'.format(datetime.now().strftime("%Y-%m-%d"))

        data = [[v.name, v.date_of_birth, v.gender, v.town_of_residence, 
                 v.town_of_id, v.veteran, v.income_val, v.ethnicity, v.last_visit_date, 
                 (v.last_visit_date.year - v.date_of_birth.year) - ((v.last_visit_date.month, v.last_visit_date.day) < (v.date_of_birth.month, v.date_of_birth.day)) if v.last_visit_date and v.date_of_birth else None
                ]
                 + [v.indexed_responses.get(col) for col in question_cols]
                 for v in all_visitors]

        headers = ["Name", "Birth Date", "Gender", "Town of Residence", "Town of ID", 
                   "Veteran?", "Income", "Ethnicity", "Last Visit Date", "Age at Last Visit"] + question_cols
        return self.__render_to_csv(headers, data, filename)

    def create_visit_report_csv(self, start_date, end_date):
        visit_info = self.__create_visit_report_data(start_date, end_date)
        visits = visit_info["visits"]

        unique_questions = set()
        for v in visits:
            v.indexed_responses = dict()
            for r in v.visitresponse_set.all():
                unique_questions.add(r.question)
                v.indexed_responses[r.question.title] = "Y" if r.bool_response else "N"

        visit_questions = sorted([q for q in unique_questions], key=lambda x: x.title)
        question_cols = [q.title for q in visit_questions]

        filename = 'HundredNightsVisits-{0}-thru-{1}.csv'.format(visit_info['start_date'], visit_info['end_date'])
        data = [[v.visitor.name, v.visitor.date_of_birth, v.visitor.town_of_residence, 
                 v.visitor.town_of_id, v.visitor.veteran, v.visit_type, v.date, v.comment] + [v.indexed_responses.get(col) for col in question_cols]
                for v in visits]

        return self.__render_to_csv(['Name', 'Birth Date', 'Town of Residence', 
                                     'Town of ID', 'Veteran?', 'Visit Type', 
                                     'Date', 'Comment'] + question_cols, data, filename)

    def create_visit_report_html(self, request, start_date, end_date):
        visit_info = self.__create_visit_report_data(start_date, end_date)
        overnight_visits = [v for v in visit_info["visits"] if v.visit_type.type == "Overnight"]
        resource_visits = [v for v in visit_info["visits"] if v.visit_type.type == "Resource Center"]
        other_visits = [v for v in visit_info["visits"] if not v.visit_type.type in ["Overnight", "Resource Center"]]

        # more terse format for HTML - create a table of counts on a per-visitor basis
        visitors = defaultdict(lambda: [0, 0, 0]) # to map visitor to list of counts [overnight, resource, other]
        for visit in overnight_visits:
            visitors[visit.visitor][0] += 1
        for visit in resource_visits:
            visitors[visit.visitor][1] += 1
        for visit in other_visits:
            visitors[visit.visitor][2] += 1

        return self.__render_to_html('visitor_report.html', request, {"visit_dict" : dict(visitors), 
                    "start_date" : visit_info["start_date"], "end_date" : visit_info["end_date"]})

    def __create_visit_report_data(self, start_date, end_date):
        all_visits = (Visit.objects.filter(date__gte=start_date, date__lte=end_date)
            .prefetch_related("visitresponse_set", "visitresponse_set__question", "visit_type")).all()

        return {
                "visits" : all_visits, 
                "start_date" : datetime.strftime(start_date, '%Y-%m-%d'),
                "end_date" : datetime.strftime(end_date, '%Y-%m-%d')
               }

    def create_mailing_label_report_csv(self):
        """ Returns a CSV formatted report with all donors' contact info"""
        filename = "HundredNights-Donors-{0}.csv".format(datetime.now().strftime("%Y-%m-%d"))
        donors = self.__create_mailing_label_report_data()
        data = [[d.name, d.street_1, d.street_2, d.city, d.zip, d.state, 
                 d.is_organization, d.email, d.organization_contact, d.title]
                for d in donors]
        return self.__render_to_csv(['Name', 'Street 1', 'Street 2', 'City', 'Zip', 
                                     'State', 'Is Org?', 'Email', 'Org. Contact', 'Title'], 
                                     data, filename)

    def create_mailing_label_report_html(self, request):
        """ Returns an HTML formatted report with all donors' contact info"""
        data = self.__create_mailing_label_report_data()
        return self.__render_to_html('mailing_labels.html', request,
            {"donors" : data, "created_date" : datetime.now().strftime("%Y-%m-%d")})
        

    def __create_mailing_label_report_data(self):
        """ Creates data a report that lists all donors and contact info """
        return Donor.objects.all()

    def create_donation_report_csv(self, start_date, end_date):
        data_dict = self.__create_donation_report_data(start_date, end_date)
        filename = 'HundredNightsDonations-{0}-thru-{1}.csv'.format(
                    data_dict['start_date'], data_dict['end_date'])
        data = [[d.donor.name, d.donor.street_1, d.donor.street_2, d.donor.city, d.donor.zip, d.donor.state, 
                 d.donor.is_organization, d.donor.email, d.donor.organization_contact, d.donor.title,
                 d.amount, d.monetary, d.description, d.date, d.comment ]
                for d in data_dict['donations']]
        return self.__render_to_csv(['Name', 'Street 1', 'Street 2', 'City', 'Zip', 
                                     'State', 'Is Org?', 'Email', 'Org. Contact', 
                                     'Title', 'Amount', 'Monetary', 
                                     'Description', 'Date', 'Comment'], data, filename)

    def create_donation_report_html(self, request, start_date, end_date):
        data = self.__create_donation_report_data(start_date, end_date)
        return self.__render_to_html('donation_report.html', request, data)

    def __create_donation_report_data(self, start_date, end_date):
        donations = Donation.objects.filter(
            date__gte=start_date, date__lte=end_date).order_by('date', 'donor__name')
        return {
                "donations" : donations,
                "total_donated" : sum([d.amount for d in donations if d.amount]),
                "start_date" : datetime.strftime(start_date, '%Y-%m-%d'),
                "end_date" : datetime.strftime(end_date, '%Y-%m-%d')
               }

    def create_participation_report_csv(self, start_date, end_date):
        data_dict = self.__create_participation_report_data(start_date, end_date)
        part = VolunteerParticipation.objects.none()
        for q in [p[1] for p in data_dict["part_info"]]:
            part = part | q
        filename = 'HundredNightsParticipation-{0}-thru-{1}.csv'.format(data_dict['start_date'], data_dict['end_date'])
        data = [[p.volunteer.name, p.volunteer.date_of_birth, p.volunteer.street_1, p.volunteer.street_2,
                 p.volunteer.zip, p.volunteer.state, p.volunteer.is_group, 
                 p.date, p.hours, p.num_participants, p.participation_type, p.comment]
                for p in part]
        return self.__render_to_csv(['Name', 'Birth Date', 'Street 1', 'Street 2', 'Zip', 'State', 'Group?',
                                     'Date', 'Hours', '# Participants', 'Type', 'Comment'],
                                     data, filename)

    def create_participation_report_html(self, request, start_date, end_date):
        data = self.__create_participation_report_data(start_date, end_date)
        return self.__render_to_html('participation_report.html', request, data)

    def __create_participation_report_data(self, start_date, end_date):
        part_by_type = [( 
                          v.type, 
                          v.volunteerparticipation_set
                                .filter(date__gte=start_date, date__lte=end_date)
                        )
                    for v in ParticipationType.objects.all()]
                        
        # append hours for each type
        part_info = []
        for part_tuple in part_by_type:
            part_info.append((
                            part_tuple[0], # part type
                            part_tuple[1], # participation records
                            sum([p.hours * (p.num_participants if p.num_participants else 1) 
                                for p in part_tuple[1]]) # hours for this type
                            ))
        return {
                "part_info" : part_info, 
                "total_volunteer_hours" : sum([p[2] for p in part_info]),
                "start_date" : datetime.strftime(start_date, '%Y-%m-%d'),
                "end_date" : datetime.strftime(end_date, '%Y-%m-%d')
               }

