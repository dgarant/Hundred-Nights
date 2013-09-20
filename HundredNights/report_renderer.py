import locale # for formatting

import os
from io import BytesIO
from io import StringIO
import csv
import datetime
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from HundredNights.models import *
from itertools import chain
from collections import defaultdict

class ReportRenderer(object):

    def __init__(self):
        pass

    def __render_to_html(self, template_path, data_dict):
        template = get_template(template_path)
        html  = template.render(Context(data_dict))
        return HttpResponse(html)

    def __render_to_csv(self, field_names, data, filename):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)

        writer = csv.writer(response)
        writer.writerow(field_names)
        for row in data:
            writer.writerow([str(s) if s else "" for s in row])
        
        return response

    def create_visit_report_csv(self, start_date, end_date):
        data_dict = self.__create_visit_report_data(start_date, end_date)
        visits = data_dict['overnight_visits'] | data_dict['resource_visits'] | data_dict['other_visits']
        filename = 'HundredNightsVisits-{0}-thru-{1}.csv'.format(data_dict['start_date'], data_dict['end_date'])
        data = [[v.visitor.name, v.visitor.age, v.visitor.town_of_residence, 
                 v.visitor.town_of_id, v.visitor.veteran, v.visit_type, v.date, v.comment]
                for v in visits]
        return self.__render_to_csv(['Name', 'Age', 'Town of Residence', 
                                     'Town of ID', 'Veteran?', 'Visit Type', 
                                     'Date', 'Comment'], data, filename)

    def create_visit_report_html(self, start_date, end_date):
        data = self.__create_visit_report_data(start_date, end_date)

        # more terse format for HTML - create a table of counts on a per-visitor basis
        visitors = defaultdict(lambda: [0, 0, 0]) # to map visitor to list of counts [overnight, resource, other]
        for visit in data["overnight_visits"]:
            visitors[visit.visitor][0] += 1
        for visit in data["resource_visits"]:
            visitors[visit.visitor][1] += 1
        for visit in data["other_visits"]:
            visitors[visit.visitor][2] += 1

        print(visitors.items())
        return self.__render_to_html('visitor_report.html', {"visit_dict" : dict(visitors), 
                    "start_date" : data["start_date"], "end_date" : data["end_date"]})

    def __create_visit_report_data(self, start_date, end_date):
        overnight_type = VisitType.objects.get(type='Overnight')
        resource_type = VisitType.objects.get(type='Resource Center')
        other_type = VisitType.objects.get(type='Other')

        overnight_visits = Visit.objects.filter(date__gte=start_date, 
                                             date__lte=end_date, 
                                             visit_type__exact=overnight_type)
        resource_visits = Visit.objects.filter(date__gte=start_date, 
                                             date__lte=end_date, 
                                             visit_type__exact=resource_type)
        other_visits = Visit.objects.filter(date__gte=start_date, 
                                             date__lte=end_date, 
                                             visit_type__exact=other_type)
        return {
                "overnight_visits" : overnight_visits, 
                "resource_visits" : resource_visits, 
                "other_visits" : other_visits,
                "unique_resource_visitor_count" : len(set([v.visitor.id for v in resource_visits])),
                "unique_overnight_visitor_count" : len(set([v.visitor.id for v in overnight_visits])),
                "unique_other_visitor_count" : len(set([v.visitor.id for v in other_visits])),
                "start_date" : datetime.strftime(start_date, '%Y-%m-%d'),
                "end_date" : datetime.strftime(end_date, '%Y-%m-%d')
               }

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

    def create_donation_report_html(self, start_date, end_date):
        data = self.__create_donation_report_data(start_date, end_date)
        return self.__render_to_html('donation_report.html', data)

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
        data = [[p.volunteer.name, p.volunteer.age, p.volunteer.street_1, p.volunteer.street_2,
                 p.volunteer.zip, p.volunteer.state, p.volunteer.is_group, 
                 p.date, p.hours, p.num_participants, p.participation_type, p.comment]
                for p in part]
        return self.__render_to_csv(['Name', 'Age', 'Street 1', 'Street 2', 'Zip', 'State', 'Group?',
                                     'Date', 'Hours', '# Participants', 'Type', 'Comment'],
                                     data, filename)

    def create_participation_report_html(self, start_date, end_date):
        data = self.__create_participation_report_data(start_date, end_date)
        return self.__render_to_html('participation_report.html', data)

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

