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
        return self.__render_to_html('visitor_report.html', data)

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
        part = data_dict['overnight_part'] | data_dict['resource_part'] | data_dict['other_part']
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
        overnight_type = VisitType.objects.get(type='Overnight')
        resource_type = VisitType.objects.get(type='Resource Center')
        other_type = VisitType.objects.get(type='Other')

        overnight_part = VolunteerParticipation.objects.filter(date__gte=start_date, 
                                             date__lte=end_date, 
                                             participation_type__exact=overnight_type)
        resource_part = VolunteerParticipation.objects.filter(date__gte=start_date, 
                                             date__lte=end_date, 
                                             participation_type__exact=resource_type)
        other_part = VolunteerParticipation.objects.filter(date__gte=start_date, 
                                             date__lte=end_date, 
                                             participation_type__exact=other_type)
        overnight_hours = sum([p.hours * (p.num_participants if p.num_participants else 1) 
                                for p in overnight_part])
        resource_hours = sum([p.hours * (p.num_participants if p.num_participants else 1) 
                                for p in resource_part])
        other_hours = sum([p.hours * (p.num_participants if p.num_participants else 1) 
                                for p in other_part])
        return {
                "overnight_part" : overnight_part, 
                "resource_part" : resource_part, 
                "other_part" : other_part,
                "total_overnight_hours" : overnight_hours,
                "total_resource_hours" : resource_hours,
                "total_other_hours" : other_hours,
                "total_volunteer_hours" : overnight_hours + resource_hours + other_hours,
                "start_date" : datetime.strftime(start_date, '%Y-%m-%d'),
                "end_date" : datetime.strftime(end_date, '%Y-%m-%d')
               }

