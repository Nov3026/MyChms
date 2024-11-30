from rest_framework import serializers
from .models import ChurchActivity
from accounts.models import ChurchAccount, SecretaryAccount
from rest_framework.exceptions import PermissionDenied



class ChurchActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchActivity
        fields = ['id', 'church', 'name', 'start_time', 'end_time', 'day', 'is_deleted', 'created_at', 'updated_at']
        
        read_only_fields = ['is_deleted', 'church', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        Override the create method to set the church field when creating a church activity.
        """
        user = self.context['request'].user  # Accessing the request object to get the logged-in user
        
        # Try to get the church account for the logged-in user (either church admin or secretary)
        church_account = None
        try:
            church_account = ChurchAccount.objects.get(church_admin=user)
        except ChurchAccount.DoesNotExist:
            try:
                secretary_account = SecretaryAccount.objects.get(user=user)
                church_account = secretary_account.church
            except SecretaryAccount.DoesNotExist:
                raise PermissionDenied("You are not associated with any church.")
                
        
        # Set the church for the activity
        validated_data['church'] = church_account

        # Call the parent class's create method to save the instance
        return super().create(validated_data)


