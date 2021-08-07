
import HundredNights.models as models
from django.contrib import admin

class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', )
admin.site.register(models.Donor, DonorAdmin)

class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth')
admin.site.register(models.Visitor, VisitorAdmin)

class VisitTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'is_selectable')
admin.site.register(models.VisitType, VisitTypeAdmin)

class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth')
admin.site.register(models.Volunteer, VolunteerAdmin)

class ParticipationTypeAdmin(admin.ModelAdmin):
    list_display = ('type', )
admin.site.register(models.ParticipationType, ParticipationTypeAdmin)

class VisitorQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'prompt', 'type')
admin.site.register(models.VisitorQuestion, VisitorQuestionAdmin)

class VisitQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'prompt', 'type', 'active')
admin.site.register(models.VisitQuestion, VisitQuestionAdmin)

