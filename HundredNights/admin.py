
import models
from django.contrib import admin

admin.site.register(models.Donor)
admin.site.register(models.Donation)

admin.site.register(models.Visitor)
admin.site.register(models.Visit)
admin.site.register(models.VisitType)

admin.site.register(models.Volunteer)
admin.site.register(models.VolunteerParticipation)
admin.site.register(models.ParticipationType)

admin.site.register(models.VisitorQuestion)
admin.site.register(models.VisitorResponse)

admin.site.register(models.VisitQuestion)
admin.site.register(models.VisitResponse)

