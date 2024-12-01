from django.contrib import admin
from .models import ChurchServiceAttendance, ChoirAttendance

# Register your models here.
@admin.register(ChurchServiceAttendance)
class ChurchServiceAttendanceAdmin(admin.ModelAdmin):
    list_display = ('church','attendance_type','number_of_men','number_of_women','number_of_male_children',
                    'number_of_female_children','vistor','month','year','date')
    search_fields = ('date',)
    list_filter = ('month', 'year')


@admin.register(ChoirAttendance)
class ChoirAttendanceAdmin(admin.ModelAdmin):
    list_display = ('church','activities','choir',
                    'month','year','date')
    search_fields = ('date', 'activities__name', 'choir__member__full_name')
    list_filter = ('month', 'year')

