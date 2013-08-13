from django.conf.urls import patterns, include, url
from HundredNights.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', index, name='index'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # report creation functions
    url(r'visit-report/$', visit_report, name='visit-report'),
    url(r'donation-report/$', donation_report, name='donation-report'),
    url(r'participation-report/$', participation_report, name='participation-report'),

    # JSON feeds for charting
    url(r'^visits-by-month/$', visits_by_month, name='visits-by-month'),
    url(r'^volunteer-hours-by-month/$', volunteer_hours_by_month, 
                name='volunteer-hours-by-month'),

    # visitor-related functions
    url(r'^visitors/$', visit_log, name='visitors'),
    url(r'^edit-visitor/(?P<visitor_id>\d{1,10})$', edit_visitor, name='edit-visitor'),
    url(r'^add-visitor/$', edit_visitor, name='add-visitor'),
    url(r'^delete-visitor/(?P<visitor_id>\d{1,10})$', delete_visitor, name='delete-visitor'),

    # visit-related functions
    url(r'^add-visit/(?P<visitor_id>\d{1,10})$', edit_visit, name='add-visit'),
    url(r'^edit-visit/(?P<visitor_id>\d{1,10})/(?P<visit_id>\d{1,10})$', 
                edit_visit, name='edit-visit'),
    url(r'^delete-visit/(?P<visit_id>\d{1,10})$', delete_visit, name='delete-visit'),

    url(r'^resource-check-in/(?P<visitor_id>\d{1,10})$', visitor_check_in_resource, name='resource-check-in'),
    url(r'^overnight-check-in/(?P<visitor_id>\d{1,10})$', visitor_check_in_overnight, name='overnight-check-in'),

    # volunteer-related functions
    url(r'^volunteers/$', volunteers, name='volunteers'),
    url(r'^add-volunteer/$', edit_volunteer, name='add-volunteer'),
    url(r'^edit-volunteer/(?P<volunteer_id>\d{1,10})$', edit_volunteer, name='edit-volunteer'),
    url(r'^delete-volunteer/(?P<volunteer_id>\d{1,10})$', delete_volunteer, name='delete-volunteer'),

    # participation-related functions
    url(r'^add-participation/(?P<volunteer_id>\d{1,10})$', edit_participation, name='add-participation'),
    url(r'^edit-participation/(?P<volunteer_id>\d{1,10})/(?P<part_id>\d{1,10})$', edit_participation, name='edit-participation'),
    url(r'^delete-participation/(?P<part_id>\d{1,10})$', delete_participation, name='delete-participation'),

    # donor-related functions
    url(r'^donors/$', donors, name='donors'),
    url(r'^add-donor/$', edit_donor, name='add-donor'),
    url(r'^edit-donor/(?P<donor_id>\d{1,10})$', edit_donor, name='edit-donor'),
    url(r'^delete-donor/(?P<donor_id>\d{1,10})$', delete_donor, name='delete-donor'),

    # donation-related functions
    url(r'^edit-donation/(?P<donor_id>\d{1,10})/(?P<donation_id>\d{1,10})$', edit_donation, name='edit-donation'),
    url(r'^delete-donation/(?P<donation_id>\d{1,10})$', delete_donation, name='delete-donation'),
    url(r'^add-donation/(?P<donor_id>\d{1,10})$', edit_donation, name='add-donation'),

    # CSV file uploads
    url(r'^upload-donors.*$', upload_donors, name='upload-donors'),
    url(r'^upload-visitors.*$', upload_visitors, name='upload-visitors'),
    url(r'^upload-volunteers.*$', upload_volunteers, name='upload-volunteers'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
