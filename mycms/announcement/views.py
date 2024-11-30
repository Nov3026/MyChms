from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import ChurchAnnouncement
from .serializers import ChurchAnnouncementSerializer
from accounts.models import ChurchAccount,SecretaryAccount,ChoirDirectorAccount, ChoirMemberAccount
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework import generics
from accounts.views import CustomPagination
from datetime import datetime



class AnnouncementCreateView(APIView):
    """
    View to create a new announcement.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChurchAnnouncementSerializer

    def post(self, request):
        """
        Create a new announcement.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to perform CRUD operations on announcements.")

        # Retrieve the ChurchAccount based on the logged-in user
        church_account = None
        try:
            # Check if the user is a church admin
            church_account = ChurchAccount.objects.get(church_admin=request.user)
        except ChurchAccount.DoesNotExist:
            # Check if they are a choir director or secretary
            try:
                choir_director = ChoirDirectorAccount.objects.get(user=request.user)
                church_account = choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
                try:
                    secretary_account = SecretaryAccount.objects.get(user=request.user)
                    church_account = secretary_account.church
                except SecretaryAccount.DoesNotExist:
                    return Response(
                        {"detail": "You are not associated with any church."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

        # Pass both the request and ChurchAccount instance to the serializer
        serializer = self.serializer_class(
            data=request.data,
            context={"church": church_account, "request": request},
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnnouncementListView(generics.ListAPIView):
    """
    View to create and retrieve announcements with pagination.
    """
    serializer_class = ChurchAnnouncementSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Retrieve announcements for the user's church.
        """
        user = self.request.user
        try:
            # Check if the user is a church admin
            church = ChurchAccount.objects.get(church_admin=user)
        except ChurchAccount.DoesNotExist:
            try:
                # Check if the user is a choir director
                choir_director = ChoirDirectorAccount.objects.get(user=user)
                church = choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
                try:
                    # Check if the user is a secretary
                    secretary_account = SecretaryAccount.objects.get(user=user)
                    church = secretary_account.church
                except SecretaryAccount.DoesNotExist:
                    try:
                        # Check if the user is a choir member
                        choir = ChoirMemberAccount.objects.get(user=user)
                        church = choir.church
                    except ChoirMemberAccount.DoesNotExist:
                        raise PermissionDenied("You are not associated with any church.")

        # Return announcements filtered by the user's church
        return ChurchAnnouncement.objects.filter(church=church, is_deleted=False).order_by('-created_at')

class AnnouncementDetailUpdateDeleteView(APIView):
    """
    View to create, retrieve, update, and delete announcements.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChurchAnnouncementSerializer

    def get_church(self, user):
        """
        Helper method to get the church account associated with the user.
        """
        try:
            # Check if the user is a church admin
            return ChurchAccount.objects.get(church_admin=user)
        except ChurchAccount.DoesNotExist:
            try:
                # Check if the user is a choir director
                choir_director = ChoirDirectorAccount.objects.get(user=user)
                return choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
                try:
                    # Check if the user is a secretary
                    secretary_account = SecretaryAccount.objects.get(user=user)
                    return secretary_account.church
                except SecretaryAccount.DoesNotExist:
                    raise PermissionDenied("You are not associated with any church.")

    def get_announcement(self, pk, church):
        """
        Helper method to get a specific announcement and ensure it belongs to the church.
        """
        try:
            return ChurchAnnouncement.objects.get(id=pk, church=church, is_deleted=False)
        except ChurchAnnouncement.DoesNotExist:
            raise NotFound("Announcement not found or you do not have permission to access it.")

    def get(self, request, pk):
        """
        Retrieve a single announcement by its ID.
        """
        church = self.get_church(request.user)
        announcement = self.get_announcement(pk, church)
        serializer = self.serializer_class(announcement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update an announcement's information.
        """
        church = self.get_church(request.user)
        announcement = self.get_announcement(pk, church)
        serializer = self.serializer_class(
            announcement, data=request.data, partial=True, context={"church": church, "request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Soft delete an announcement.
        """
        church = self.get_church(request.user)
        announcement = self.get_announcement(pk, church)

        # Perform a soft delete by marking `is_deleted` as True
        announcement.is_deleted = True
        announcement.save()
        return Response({"detail": "Announcement deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

# Announcement statistics view
class AnnounceStatsView(APIView):
     """
        Get the total number of members, total females, and total males.
        """
     def get(self, request):
        # Get the total number of announcements

        announcements = ChurchAnnouncement.objects.filter(is_deleted=False).count()

        return Response({
            "announcements": announcements,
        }, status=200)
