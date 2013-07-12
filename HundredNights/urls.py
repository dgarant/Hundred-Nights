from django.conf.urls import patterns, include, url
from HundredNights.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', index, name='index'),
    url(r'^visit-log/$', visit_log, name='visit-log'),
    url(r'^donors/$', donors, name='donors'),
    url(r'^volunteers/$', volunteers, name='volunteers'),
    url(r'^edit-visitor.*$', edit_visitor, name='edit-visitor'),
    url(r'^edit-volunteer.*$', edit_volunteer, name='edit-volunteer'),
    url(r'^add-donor/$', edit_donor, name='add-donor'),
    url(r'^edit-donor/(?P<donor_id>\d{1,10})$', edit_donor, name='edit-donor'),
    url(r'^delete-donor/(?P<donor_id>\d{1,10})$', delete_donor, name='delete-donor'),
    url(r'^edit-donation/(?P<donor_id>\d{1,10})/(?P<donation_id>\d{1,10})$', edit_donation, name='edit-donation'),
    url(r'^delete-donation/(?P<donation_id>\d{1,10})$', delete_donation, name='delete-donation'),
    url(r'^add-donation/(?P<donor_id>\d{1,10})$', edit_donation, name='add-donation'),
    url(r'^upload-donors.*$', upload_donors, name='upload-donors'),
    url(r'^upload-visitors.*$', upload_visitors, name='upload-visitors'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
