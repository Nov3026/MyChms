from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import ChurchActivity
from .serializers import ChurchActivitySerializer
from accounts.models import ChurchAccount, SecretaryAccount, ChoirMemberAccount, ChoirDirectorAccount
from django.core.exceptions import PermissionDenied
from rest_framework import generics
from rest_framework.exceptions import NotFound
from accounts.views import CustomPagination

    

class ChurchActivityCreateView(APIView):
    """
    View to create a new church activity.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChurchActivitySerializer

    def post(self, request):
        """
        Create a new church activity.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to perform CRUD operations on ChurchActivity.")

        # Retrieve the ChurchAccount based on the logged-in user
        church_account = None
        try:
            # Check if the user is a church admin
            church_account = ChurchAccount.objects.get(church_admin=request.user)
        except ChurchAccount.DoesNotExist:
            # If not a church admin, check if they are a church secretary
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

class ChurchActivityListView(generics.ListAPIView):
    """
    View to retrieve all activities with pagination.
    Church Admin, Secretary, Choir Director, and Choir Members can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChurchActivitySerializer
    pagination_class = CustomPagination  # Use pagination for large datasets

    def get_queryset(self):
        # Determine the church account based on the user role
        church_account = None
        try:
            # Check if the user is a church admin
            church_account = ChurchAccount.objects.get(church_admin=self.request.user)
        except ChurchAccount.DoesNotExist:
            # Check if the user is a secretary
            try:
                secretary_account = SecretaryAccount.objects.get(user=self.request.user)
                church_account = secretary_account.church
            except SecretaryAccount.DoesNotExist:
                # Check if the user is a choir director
                try:
                    choir_director_account = ChoirDirectorAccount.objects.get(user=self.request.user)
                    church_account = choir_director_account.church
                except ChoirDirectorAccount.DoesNotExist:
                    # Check if the user is a choir member
                    try:
                        choir_member_account = ChoirMemberAccount.objects.get(user=self.request.user)
                        church_account = choir_member_account.church
                    except ChoirMemberAccount.DoesNotExist:
                        raise PermissionDenied("You do not have permission to view activities.")

        # Retrieve activities associated with the church
        activities = ChurchActivity.objects.filter(church=church_account)

        # Apply search filters based on query parameters
        name = self.request.query_params.get('name', None)
        if name:
            activities = activities.filter(name__icontains=name)

        return activities
  
class ChurchActivityDetailUpdateDeleteView(APIView):
    """
    View to retrieve, update, and delete a activity.
    Both Church Admin and Secretary can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChurchActivitySerializer

    def get_church(self, user):
        """
        Helper method to get the church account associated with the user.
        """
        try:
            # Check if the user is a church admin
            return ChurchAccount.objects.get(church_admin=user)
        except ChurchAccount.DoesNotExist:
            # Check if the user is a secretary
            try:
                secretary_account = SecretaryAccount.objects.get(user=user)
                return secretary_account.church
            except SecretaryAccount.DoesNotExist:
                raise PermissionDenied("You do not have permission to manage activity.")

    def get_object(self, pk, church):
        """
        Helper method to get the ChurchActivity object and ensure it belongs to the church.
        """
        try:
            return ChurchActivity.objects.get(id=pk, church=church)
        except ChurchActivity.DoesNotExist:
            raise NotFound("Activity not found or you do not have permission to access this record.")

    def get(self, request, pk):
        """
        Retrieve a activity by their ID.
        """
        church = self.get_church(request.user)
        activity = self.get_object(pk, church)
        serializer = ChurchActivitySerializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a activity's information.
        """
        church = self.get_church(request.user)
        activity = self.get_object(pk, church)
        serializer = ChurchActivitySerializer(activity, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a activity.
        """
        church = self.get_church(request.user)
        activity = self.get_object(pk, church)
        activity.delete()
        return Response({"detail": "Activity has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)