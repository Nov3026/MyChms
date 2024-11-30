from rest_framework import serializers
from .models import ChurchTithe
from datetime import date
from choice.views import month_choices
from accounts.models import ChurchAccount, SecretaryAccount


class TitheSerializer(serializers.ModelSerializer):
    month = serializers.ChoiceField(choices=month_choices)

    class Meta:
        model = ChurchTithe
        fields = ['id', 'church', 'member', 'usd_amount', 'lrd_amount', 'payment_date',
                  'month', 'year', 'is_deleted', 'created_at', 'updated_at']
        
        read_only_fields = ['is_deleted', 'church', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Ensure that the church is set here when creating a tithe
        user = self.context['request'].user  # Access the logged-in user
        church_account = self.get_church_account(user)  # Get the church account
        validated_data['church'] = church_account  # Set the church field programmatically
        return super().create(validated_data)

    def validate_payment_date(self, value):
        # Check if the payment date is in the future
        if value > date.today():
            raise serializers.ValidationError("The payment date cannot be in the future.")
        return value

    def get_church_account(self, user):
        """
        Retrieve the ChurchAccount for the user, whether they are a church admin or secretary.
        """
        # Check if the user is a church admin
        try:
            return ChurchAccount.objects.get(church_admin=user)
        except ChurchAccount.DoesNotExist:
            pass  # Continue to check if the user is a secretary

        # Check if the user is a church secretary
        try:
            secretary_account = SecretaryAccount.objects.get(user=user)
            return secretary_account.church
        except SecretaryAccount.DoesNotExist:
            raise serializers.ValidationError("You are not associated with any church.")