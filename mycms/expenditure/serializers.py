from rest_framework import serializers
from .models import ChurchExpenditure
from accounts.models import ChurchAccount
from rest_framework import serializers
from choice.views import expense_types_choices



class ExpenditureSerializer(serializers.ModelSerializer):
    expenses_type = serializers.ChoiceField(choices=expense_types_choices)
    class Meta:
        model = ChurchExpenditure
        fields = ['id', 'church', 'expenses_type', 'item', 'lrd_amount', 'usd_amount', 'descriptions', 'month', 'year', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = [ 'church', 'is_deleted', 'created_at', 'updated_at']


    def create(self, validated_data):
        # Retrieve the church passed in the context
        church_account = self.context.get("church", None)
        if not church_account:
            raise serializers.ValidationError("Church information is missing in the context.")

        # Set the church field for the new department
        validated_data['church'] = church_account
        return super().create(validated_data)
