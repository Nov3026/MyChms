from rest_framework import serializers
from .models import ChoirDue



class ChoirDueSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='choir_member.member.full_name', read_only=True)

    class Meta:
        model = ChoirDue
        fields = [
            'id', 'church', 'choir_member', 'full_name', 'amount_due',
            'amount_paid', 'date_paid', 'balance', 'month', 'year', 'is_deleted',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['is_deleted', 'church', 'full_name', 'balance', 'created_at', 'updated_at']

    def validate(self, data):
        choir_member = data.get('choir_member')
        church = self.context['request'].user.choirdirectoraccount.church

        # Ensure the choir member belongs to the correct church
        if choir_member.church != church:
            raise serializers.ValidationError("The choir member does not belong to the specified church.")
        return data

