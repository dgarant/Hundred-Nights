# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Donor'
        db.create_table('HundredNights_donor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('street_1', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('street_2', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='NH', max_length=2, null=True, blank=True)),
            ('is_organization', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('organization_contact', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal('HundredNights', ['Donor'])

        # Adding model 'Donation'
        db.create_table('HundredNights_donation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['HundredNights.Donor'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=2, blank=True)),
            ('monetary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('HundredNights', ['Donation'])

        # Adding model 'Visitor'
        db.create_table('HundredNights_visitor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('town_of_residence', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('town_of_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('veteran', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('HundredNights', ['Visitor'])

        # Adding model 'VisitType'
        db.create_table('HundredNights_visittype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('HundredNights', ['VisitType'])

        # Adding model 'ParticipationType'
        db.create_table('HundredNights_participationtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('HundredNights', ['ParticipationType'])

        # Adding model 'Visit'
        db.create_table('HundredNights_visit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('visitor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['HundredNights.Visitor'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('visit_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['HundredNights.VisitType'])),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('HundredNights', ['Visit'])

        # Adding model 'Volunteer'
        db.create_table('HundredNights_volunteer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('street_1', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('street_2', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('town', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='NH', max_length=2, null=True, blank=True)),
            ('is_group', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('HundredNights', ['Volunteer'])

        # Adding model 'VolunteerParticipation'
        db.create_table('HundredNights_volunteerparticipation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('volunteer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['HundredNights.Volunteer'])),
            ('hours', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('num_participants', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('participation_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['HundredNights.ParticipationType'])),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('HundredNights', ['VolunteerParticipation'])


    def backwards(self, orm):
        # Deleting model 'Donor'
        db.delete_table('HundredNights_donor')

        # Deleting model 'Donation'
        db.delete_table('HundredNights_donation')

        # Deleting model 'Visitor'
        db.delete_table('HundredNights_visitor')

        # Deleting model 'VisitType'
        db.delete_table('HundredNights_visittype')

        # Deleting model 'ParticipationType'
        db.delete_table('HundredNights_participationtype')

        # Deleting model 'Visit'
        db.delete_table('HundredNights_visit')

        # Deleting model 'Volunteer'
        db.delete_table('HundredNights_volunteer')

        # Deleting model 'VolunteerParticipation'
        db.delete_table('HundredNights_volunteerparticipation')


    models = {
        'HundredNights.donation': {
            'Meta': {'object_name': 'Donation'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'donor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['HundredNights.Donor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monetary': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'HundredNights.donor': {
            'Meta': {'object_name': 'Donor'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_organization': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'organization_contact': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'NH'", 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street_1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'street_2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'HundredNights.participationtype': {
            'Meta': {'object_name': 'ParticipationType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'HundredNights.visit': {
            'Meta': {'object_name': 'Visit'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'visit_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['HundredNights.VisitType']"}),
            'visitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['HundredNights.Visitor']"})
        },
        'HundredNights.visitor': {
            'Meta': {'object_name': 'Visitor'},
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'town_of_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'town_of_residence': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'veteran': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'HundredNights.visittype': {
            'Meta': {'object_name': 'VisitType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'HundredNights.volunteer': {
            'Meta': {'object_name': 'Volunteer'},
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'NH'", 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street_1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'street_2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'})
        },
        'HundredNights.volunteerparticipation': {
            'Meta': {'object_name': 'VolunteerParticipation'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'hours': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_participants': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'participation_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['HundredNights.ParticipationType']"}),
            'volunteer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['HundredNights.Volunteer']"})
        }
    }

    complete_apps = ['HundredNights']