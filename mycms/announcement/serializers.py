# from rest_framework import serializers
# from .models import ChurchAnnouncement
# from accounts.models import ChurchAccount

# # class ChurchAnnouncementSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = ChurchAnnouncement
# #         fields = ['id', 'church', 'author', 'title', 'content', 'is_deleted', 'created_at', 'updated_at']
        
# #         read_only_fields = ['is_deleted', 'church', 'created_at', 'updated_at']

# #     def create(self, validated_data):
# #         # Ensure that the church is set here when creating a member
# #         user = self.context['request'].user  # Accessing the request object to get the logged-in user
# #         church_account = ChurchAccount.objects.get(church_admin=user)  # Get the church associated with the user
# #         validated_data['church'] = church_account  # Set the church field programmatically
# #         return super().create(validated_data)

# ############################Testing


# # class ChurchAnnouncementSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = ChurchAnnouncement
# #         fields = ['id', 'church', 'author', 'title', 'content', 'is_deleted', 'created_at', 'updated_at']
# #         read_only_fields = ['is_deleted', 'church', 'created_at', 'updated_at']

# #     def create(self, validated_data):
# #         # Church field is already set by the view; no need to fetch it here
# #         return super().create(validated_data)


# from rest_framework import serializers
# from .models import ChurchAnnouncement

# class ChurchAnnouncementSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ChurchAnnouncement
#         fields = ['id', 'church', 'author', 'title', 'content', 'is_deleted', 'created_at', 'updated_at']
#         read_only_fields = ['church', 'is_deleted', 'created_at', 'updated_at']

#     def create(self, validated_data):
#         # The church field is already set by the view; no need to fetch it here
#         return super().create(validated_data)

from rest_framework import serializers
from .models import ChurchAnnouncement


# class ChurchAnnouncementSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ChurchAnnouncement
#         fields = ['id', 'church', 'author', 'title', 'content', 'is_deleted', 'created_at', 'updated_at']
#         read_only_fields = ['church', 'is_deleted', 'created_at', 'updated_at']

#         def create(self, validated_data):
#             # Retrieve the church passed in the context
#             church_account = self.context.get("church", None)
#             if not church_account:
#                 raise serializers.ValidationError("Church information is missing in the context.")

#             # Set the church field for the new member
#             validated_data['church'] = church_account
#             return super().create(validated_data)



class ChurchAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchAnnouncement
        fields = ['id', 'church', 'author', 'title', 'content', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['church', 'is_deleted', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Retrieve the church passed in the context
        church_account = self.context.get("church", None)
        if not church_account:
            raise serializers.ValidationError("Church information is missing in the context.")

        # Set the church field for the new member
        validated_data['church'] = church_account
        return super().create(validated_data)
