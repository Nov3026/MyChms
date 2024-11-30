from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import ChurchTithe
from .serializers import TitheSerializer
from accounts.models import ChurchAccount, SecretaryAccount
from django.core.exceptions import PermissionDenied
from rest_framework import generics
from accounts.views import CustomPagination

    

class TitheCreateView(APIView):
    """
    Add a new tithe.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TitheSerializer

    def post(self, request):
        """
        Add tithe
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to perform CRUD operations on Tithe.")

        # Retrieve the ChurchAccount based on the logged-in user
        church_account = self.get_church_account(request.user)
        if not church_account:
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
            return None

class TitheListView(generics.ListAPIView):
    """
    Retrieve all tithes for the church associated with the logged-in user with pagination.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TitheSerializer
    pagination_class = CustomPagination  # Enable pagination

    def get_queryset(self):
        """
        Get all tithes for the church the user belongs to.
        """
        church_account = self.get_church_account(self.request.user)
        if not church_account:
            raise PermissionDenied("You are not associated with any church.")

        # Get all tithes related to the church account
        tithes = ChurchTithe.objects.filter(church=church_account)

        return tithes

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
            return None

class TitheDetailUpdateDeleteView(APIView):
    """
    Retrieve, update, or delete a specific tithe record.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TitheSerializer

    def get(self, request, pk):
        """
        Retrieve a specific tithe record.
        """
        tithe = self.get_tithe(pk)
        if not tithe:
            return Response({"detail": "Tithe not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to access this tithe
        church_account = self.get_church_account(request.user)
        if church_account != tithe.church:
            raise PermissionDenied("You do not have permission to access this tithe.")

        # Serialize the tithe and return it
        serializer = TitheSerializer(tithe)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update a specific tithe record.
        """
        tithe = self.get_tithe(pk)
        if not tithe:
            return Response({"detail": "Tithe not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to update this tithe
        church_account = self.get_church_account(request.user)
        if church_account != tithe.church:
            raise PermissionDenied("You do not have permission to update this tithe.")

        # Serialize and update the tithe record
        serializer = TitheSerializer(tithe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a specific tithe record.
        """
        tithe = self.get_tithe(pk)
        if not tithe:
            return Response({"detail": "Tithe not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to delete this tithe
        church_account = self.get_church_account(request.user)
        if church_account != tithe.church:
            raise PermissionDenied("You do not have permission to delete this tithe.")

        # Delete the tithe
        tithe.delete()
        return Response({"detail": "Tithe deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def get_tithe(self, pk):
        """
        Retrieve a tithe record by its ID.
        """
        try:
            return ChurchTithe.objects.get(pk=pk)
        except ChurchTithe.DoesNotExist:
            return None

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
            return None