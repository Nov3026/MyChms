from rest_framework import serializers
from .models import ChurchServiceAttendance, ChoirAttendance
from accounts.models import ChurchAccount, ChoirDirectorAccount
from rest_framework.exceptions import PermissionDenied
from choice.views import days_of_week_choices, week_choices, month_choices



class ChurchServiceAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchServiceAttendance
        fields = ['id', 'church', 'attendance_type', 'number_of_men', 'number_of_women', 
                 'number_of_male_children', 'number_of_female_children','vistor',
                  'month', 'year', 'total_attendees', 'is_deleted', 'date_recorded', 'updated_at']
        
        read_only_fields = ['total_attendees', 'is_deleted', 'church', 'date_recorded', 'updated_at']

    def create(self, validated_data):
        # Retrieve the church passed in the context
        church_account = self.context.get("church", None)
        if not church_account:
            raise serializers.ValidationError("Church information is missing in the context.")

        # Set the church field for the new member
        validated_data['church'] = church_account
        return super().create(validated_data)
    
class ChoirAttendanceSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='choir.member.full_name', read_only=True)
    day = serializers.ChoiceField(choices=days_of_week_choices)
    week = serializers.ChoiceField(choices=week_choices)
    month = serializers.ChoiceField(choices=month_choices)

    class Meta:
        model = ChoirAttendance
        fields = ['id', 'church', 'choir', 'activities','full_name', 'day', 'week', 'month', 'year', 
                  'is_deleted', 'date_recorded', 'updated_at']
        
        read_only_fields = ['is_deleted', 'church', 'date_recorded', 'updated_at']

    def create(self, validated_data):
        # Retrieve the church passed in the context
        church_account = self.context.get("church", None)
        if not church_account:
            raise serializers.ValidationError("Church information is missing in the context.")

        # Set the church field for the new member
        validated_data['church'] = church_account
        return super().create(validated_data)