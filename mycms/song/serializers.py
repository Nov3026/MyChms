from rest_framework import serializers
from .models import ChoirSong
from accounts.models import ChurchAccount, ChoirDirectorAccount
from rest_framework.exceptions import PermissionDenied



class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoirSong
        fields = ['id', 'church', 'author', 'title', 'song_content', 'is_deleted', 'created_at', 'updated_at']
        
        read_only_fields = ['is_deleted', 'church', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Retrieve the church passed in the context
        church_account = self.context.get("church", None)
        if not church_account:
            raise serializers.ValidationError("Church information is missing in the context.")

        # Set the church field for the new member
        validated_data['church'] = church_account
        return super().create(validated_data)