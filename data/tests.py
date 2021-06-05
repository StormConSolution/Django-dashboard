# -*- encoding: utf-8 -*-

from django.test import TestCase

from data.models import *

class TestAlertRule(TestCase):
    
    def setUp(self):
        self.project = Project.objects.create(name='Test')


    def test_should_notify(self):
        rule = AlertRule.objects.create(
            project=self.project,
            name='Test Alert',
            aspect='',
            frequency=1,
            period='daily',
            keywords='hello',
            emails='noreply@repustate.com',
            sms='',
        )
        
        alert = Alert.objects.create(project=self.project, rule=rule, title='Test', description='Test')

        self.assertEquals(rule.should_notify(), True)

        # Changing the frequency/period should mean this rule doesn't notify.
        rule.period = 'weekly'
        rule.frequency = 10
        rule.save()
        
        self.assertEquals(rule.should_notify(), False)
        
        # Changing the frequency/period back should notify.
        rule.period = 'weekly'
        rule.frequency = 1
        rule.save()
        
        self.assertEquals(rule.should_notify(), True)
        
        rule.period = 'monthly'
        rule.frequency = 1
        rule.save()
        
        self.assertEquals(rule.should_notify(), True)
