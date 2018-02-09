from django.conf.urls import patterns, include, url
from HundredNights.views import *
from django.core.urlresolvers import reverse

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', index, name='index'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {"next_page" : "/"}, name="logout"),

    # report creation functions
    url(r'visitor-report/$', visitor_report, name='visitor-report'),
    url(r'visit-report/$', visit_report, name='visit-report'),
    url(r'donation-report/$', donation_report, name='donation-report'),
    url(r'participation-report/$', participation_report, name='participation-report'),
    url(r'united-way-report/$', united_way_report, name='united-way-report'),

    # ancillary report data functions
    url(r'visitor-filter/$', visitor_filter, name="visitor-filter"),
    url(r'visitor-respondents/$', visitor_respondents, name="visitor-respondents"),
    url(r'visit-respondents/$', visit_respondents, name="visit-respondents"),

    # JSON feeds for charting
    url(r'^visits-by-month/$', visits_by_month, name='visits-by-month'),
    url(r'^volunteer-hours-by-month/$', volunteer_hours_by_month, 
                name='volunteer-hours-by-month'),

    # visitor-related functions
    url(r'^api/visitor-search/$', visitor_search_api, name="visitor-search"),
    url(r'^visitor-lookup/$', visitor_lookup, name="visitor-lookup"),
    url(r'^visitors/(?P<history_years>\d{1,10})?$', visit_log, name="visitors"),
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

    # referral-related functions
    url(r'^referrers/$', referrers, name='referrers'),
    url(r'^add-referrer/$', edit_referrer, name='add-referrer'),
    url(r'^edit-referrer/(?P<referrer_id>\d{1,10})$', edit_referrer, name="edit-referrer"),
    url(r'^delete-referrer', delete_referrer, name="delete-referrer"),

    url(r'^add-referral/(?P<referrer_id>\d{1,10})$', edit_referral, name="add-referral"),
    url(r'^edit-referral/(?P<referrer_id>\d{1,10})/(?P<referral_id>\d{1,10})$', edit_referral, name='edit-referral'),
    url(r'^delete-referral/$', delete_referral, name="delete-referral"),

    # CSV file uploads
    url(r'^upload-donors.*$', upload_donors, name='upload-donors'),
    url(r'^upload-visitors.*$', upload_visitors, name='upload-visitors'),
    url(r'^upload-volunteers.*$', upload_volunteers, name='upload-volunteers'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
