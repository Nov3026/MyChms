from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChoirDue
from .serializers import ChoirDueSerializer
from accounts.models import ChoirMemberAccount
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import Http404
from accounts.permissions import IsChoirDirector
from rest_framework.exceptions import PermissionDenied, NotFound
from accounts.models import ChurchAccount, ChoirDirectorAccount
from rest_framework.generics import ListAPIView
from accounts.views import CustomPagination



class ChoirDueListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChoirDueSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        try:
            church_account = ChurchAccount.objects.get(church_admin=self.request.user)
        except ChurchAccount.DoesNotExist:
            try:
                choir_director = ChoirDirectorAccount.objects.get(user=self.request.user)
                church_account = choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
                raise PermissionDenied("You do not have permission to view choir dues.")
        
        dues = ChoirDue.objects.filter(church=church_account)

        # Apply filters
        full_name = self.request.query_params.get('full_name', None)
        if full_name:
            dues = dues.filter(full_name__icontains=full_name)

        gender = self.request.query_params.get('gender', None)
        if gender:
            dues = dues.filter(gender=gender)

        return dues
    
class ChoirDueCreateAPIView(generics.CreateAPIView):
    serializer_class = ChoirDueSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        choir_director = getattr(user, 'choirdirectoraccount', None)
        
        if choir_director:
            # Automatically associate the due with the director's church
            serializer.save(church=choir_director.church)
        else:
            raise PermissionError("Only choir directors can create dues.")

class ChoirDueDetailUpdateDeleteAPIView(APIView):
    """
    View to retrieve, update, and delete a choir due.
    Both Church Admin and Secretary can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChoirDueSerializer

    def get_church(self, user):
        """
        Helper method to get the church account associated with the user.
        """
        try:
            # Check if the user is a church admin
            return ChurchAccount.objects.get(church_admin=user)
        except ChurchAccount.DoesNotExist:
            # Check if the user is a choir director
            try:
                choir_director = ChoirDirectorAccount.objects.get(user=user)
                return choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
                raise PermissionDenied("You do not have permission to manage choir dues.")

    def get_object(self, pk, church):
        """
        Helper method to get the ChoirDue object and ensure it belongs to the church.
        """
        try:
            return ChoirDue.objects.get(id=pk, church=church)
        except ChoirDue.DoesNotExist:
            raise NotFound("Choir due not found or you do not have permission to access this record.")

    def get(self, request, pk):
        """
        Retrieve a choir due by its ID.
        """
        church = self.get_church(request.user)
        due = self.get_object(pk, church)
        serializer = self.serializer_class(due)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a choir due's information.
        """
        church = self.get_church(request.user)
        due = self.get_object(pk, church)
        serializer = self.serializer_class(due, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a choir due.
        """
        church = self.get_church(request.user)
        due = self.get_object(pk, church)
        due.delete()
        return Response({"detail": "Choir Due has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


   