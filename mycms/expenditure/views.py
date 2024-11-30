from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import ChurchExpenditure
from .serializers import ExpenditureSerializer
from accounts.models import ChurchAccount, SecretaryAccount, ChoirDirectorAccount
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework import generics
from accounts.views import CustomPagination

        
    

class ExpenditureCreateView(APIView):
    """
    View to create a new expenditure.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenditureSerializer

    def post(self, request):
        """
        Create a new expenditure.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to perform CRUD operations on expenditure.")

        # Retrieve the ChurchAccount based on the logged-in user
        church_account = None
        try:
            # Check if the user is a church admin
            church_account = ChurchAccount.objects.get(church_admin=request.user)
        except ChurchAccount.DoesNotExist:
            # Check if they are a choir director or secretary
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

class ExpenditureListView(generics.ListAPIView):
    """
    View to retrieve all expenditures with pagination.
    Both Church Admin and Secretary can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenditureSerializer
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
                raise PermissionDenied("You do not have permission to view expenditures.")

        # Retrieve all expenditures associated with the church
        expenditures = ChurchExpenditure.objects.filter(church=church_account)

        # Apply search filters based on query parameters
        expenses_type = self.request.query_params.get('expenses_type', None)
        if expenses_type:
            expenditures = expenditures.filter(expenses_type__icontains=expenses_type)
        
        month = self.request.query_params.get('month', None)
        if month:
            expenditures = expenditures.filter(month__icontains=month)

        return expenditures
    
class ExpenditureDetailUpdateDeleteView(APIView):
    """
    View to retrieve, update, and delete a expenditure.
    Both Church Admin and Secretary can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenditureSerializer

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
                raise PermissionDenied("You do not have permission to manage expenditure.")

    def get_object(self, pk, church):
        """
        Helper method to get the ChurchExpenditure object and ensure it belongs to the church.
        """
        try:
            return ChurchExpenditure.objects.get(id=pk, church=church)
        except ChurchExpenditure.DoesNotExist:
            raise NotFound("Expenditure not found or you do not have permission to access this record.")

    def get(self, request, pk):
        """
        Retrieve a expenditure by their ID.
        """
        church = self.get_church(request.user)
        expenditure = self.get_object(pk, church)
        serializer = ExpenditureSerializer(expenditure)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a expenditure's information.
        """
        church = self.get_church(request.user)
        expenditure = self.get_object(pk, church)
        serializer = ExpenditureSerializer(expenditure, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a member.
        """
        church = self.get_church(request.user)
        expenditure = self.get_object(pk, church)
        expenditure.delete()
        return Response({"detail": "Expenditure has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
