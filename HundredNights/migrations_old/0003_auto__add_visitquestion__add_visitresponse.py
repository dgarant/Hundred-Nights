# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VisitQuestion'
        db.create_table('HundredNights_visitquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('prompt', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('details_prompt', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('HundredNights', ['VisitQuestion'])

        # Adding model 'VisitResponse'
        db.create_table('HundredNights_visitresponse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('visit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['HundredNights.Visit'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['HundredNights.VisitQuestion'])),
            ('bool_response', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal('HundredNights', ['VisitResponse'])


    def backwards(self, orm):
        # Deleting model 'VisitQuestion'
        db.delete_table('HundredNights_visitquestion')

        # Deleting model 'VisitResponse'
        db.delete_table('HundredNights_visitresponse')


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
        'HundredNights.visitorquestion': {
            'Meta': {'object_name': 'VisitorQuestion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prompt': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'HundredNights.visitorresponse': {
            'Meta': {'object_name': 'VisitorResponse'},
            'bool_response': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['HundredNights.VisitorQuestion']"}),
            'visitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['HundredNights.Visitor']"})
        },
        'HundredNights.visitquestion': {
            'Meta': {'object_name': 'VisitQuestion'},
            'details_prompt': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prompt': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'HundredNights.visitresponse': {
            'Meta': {'object_name': 'VisitResponse'},
            'bool_response': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['HundredNights.VisitQuestion']"}),
            'visit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['HundredNights.Visit']"})
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