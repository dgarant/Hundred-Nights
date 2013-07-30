import locale # for formatting

import os
from xhtml2pdf import pisa
from io import BytesIO
from io import StringIO
import csv
import datetime
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
import tempfile
from HundredNights.models import *
from weasyprint import HTML

class ReportRenderer(object):

    def __init__(self):
        pass

    """
    def link_callback(uri, rel):
        sUrl = settings.STATIC_URL      # Typically /static/
        sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL       # Typically /static/media/
        mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))

        # make sure that file exists
        if not os.path.isfile(path):
                raise Exception(
                        'media URI must start with %s or %s' % \
                        (sUrl, mUrl))
        return path
        """

    def __render_to_pdf(self, template_path, data_dict):
         # Render html content through html template with context
        template = get_template(template_path)
        html  = template.render(Context(data_dict))

        # Write PDF to file
        with tempfile.TemporaryFile() as handle:
            HTML(html).write_pdf(handle)

            # Return PDF document through a Django HTTP response
            handle.seek(0)
            pdf = handle.read()
            handle.close()
            return HttpResponse(pdf, mimetype='application/pdf')

    def create_visit_report_csv(self, start_date, end_date):
        pass

    def create_visit_report_pdf(self, start_date, end_date):
        data = self.__create_visit_report_data(start_date, end_date)
        return self.__render_to_pdf('visitor_report.html', data)

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
        pass

    def create_donation_report_pdf(self, start_date, end_date):
        pass

    def __create_donation_report_data(self, start_date, end_date):
        pass

    def create_volunteer_report_csv(self, start_date, end_date):
        pass

    def create_volunteer_report_pdf(self, start_date, end_date):
        pass

    def __create_donation_report_data(self, start_date, end_date):
        pass

