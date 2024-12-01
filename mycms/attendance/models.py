from django.db import models
from accounts.models import ChurchAccount, ChoirMemberAccount
from choice.views import month_choices, days_of_week_choices, week_choices
from church_activity.models import ChurchActivity
from datetime import datetime


# Create your models here.
class ChurchServiceAttendance(models.Model):
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE, related_name="church_attendance")
    attendance_type = models.CharField(max_length=200)
    number_of_men = models.IntegerField(null=True, blank=True)
    number_of_women = models.IntegerField(null=True, blank=True)
    number_of_male_children = models.IntegerField(null=True, blank=True)
    number_of_female_children = models.IntegerField(null=True, blank=True)
    vistor = models.IntegerField(null=True, blank=True)
    date = models.DateField(null=True, blank=True, default=datetime.today)
    total_attendees = models.IntegerField(null=True, blank=True)
    month = models.CharField(max_length=20, choices=month_choices, default='Select')
    year = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    date_recorded = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        # Return a string representation of the object
        return f"{self.church} - {self.attendance_type} ({self.year}, {self.month})"
    
    def save(self, *args, **kwargs):
        self.total_attendees = self.number_of_men + self.number_of_women + self.number_of_male_children + self.number_of_female_children + self.vistor
        super().save(*args, **kwargs)
 

class ChoirAttendance(models.Model):
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE, related_name='church_choir_attendance')
    activities = models.ForeignKey(ChurchActivity, on_delete=models.CASCADE, related_name='activity')
    choir = models.ForeignKey(ChoirMemberAccount, on_delete=models.CASCADE, related_name='choir_practice')
    day = models.CharField(max_length=20, choices=days_of_week_choices, default='Select Day')
    week = models.CharField(max_length=5, choices=week_choices, default='Select')
    date = models.DateField(default=datetime.today, blank=True, null=True)
    month = models.CharField(max_length=20, choices=month_choices)
    year = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    date_recorded = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.choir.member.full_name
    
    class Meta:
        ordering = ['-date_recorded']
    
    