from django.shortcuts import get_object_or_404
from .serializers import ChurchAccountSerializer,MemberRegistrationSerializer, ChoirDirectorAccountSerializer,ChoirMemberAccountSerializer, SecretaryAccountAccountSerializer,DepartmentSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics 
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import ChurchAccount, ChoirDirectorAccount, MemberRegistration,ChoirMemberAccount, SecretaryAccount, ChurchDepartment
from django.core.exceptions import PermissionDenied
from .permissions import IsSuperUser
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.pagination import PageNumberPagination
from announcement.models import ChurchAnnouncement


class CustomPagination(PageNumberPagination):
    page_size = 10  # Default items per page
    page_size_query_param = 'page_size'  # Allow client to specify page size
    max_page_size = 100  # Max items per page

class CreateChurchAccount(generics.CreateAPIView):
    """
    Create a new church account. Only superusers (system admins) can perform this action.
    """
    permission_classes = [IsAuthenticated, IsSuperUser]  # Allow only superusers (system admins)
    serializer_class = ChurchAccountSerializer

    def post(self, request, *args, **kwargs):
        # Check if the authenticated user already has a church account
        if hasattr(request.user, 'church'):
            return Response(
                {"message": "You already have a registered church account. You are not allowed to register another church account. "
                            "Please contact the system administrator"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            church = serializer.save()

            # Create or retrieve a token for the church admin
            token, created = Token.objects.get_or_create(user=church.church_admin)
            return Response({
                "message": "Church registered successfully.",
                "church": ChurchAccountSerializer(church).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChurchAccountList(generics.ListAPIView):
    """
    List all church accounts.
    """
    permission_classes = [IsAuthenticated]
    queryset = ChurchAccount.objects.all()
    serializer_class = ChurchAccountSerializer

    def get_queryset(self):
        user = self.request.user
        # If the user is a superuser or staff, return all church accounts
        if user.is_superuser or user.is_staff:
            return ChurchAccount.objects.all()
        # Otherwise, filter to show only the user's church account
        return ChurchAccount.objects.filter(church_admin=user)
    

class ChurchAccountDetail(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update an individual church account.
    System admin can access any church account, while each church admin can only access and update their own account.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChurchAccountSerializer
    queryset = ChurchAccount.objects.all()

    def get_object(self):
        """
        Override to restrict access based on user role:
        - System admin can access any church account.
        - Regular church admins can only access their own account.
        """
        # Fetch the account based on the provided primary key in the URL
        church_account = super().get_object()
        user = self.request.user
        
        # Allow system admin (superuser or staff) to retrieve any account
        if user.is_superuser or user.is_staff:
            return church_account
        
        # If not a system admin, check if the user is the admin of this church account
        if church_account.church_admin == user:
            return church_account
        
        # If the user is neither the account owner nor an admin, deny access
        raise PermissionDenied("You do not have permission to access this account.")
    

class ChurchAccountDeleteView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    # GET method to view the ChurchAccount details before delete
    def get(self, request, pk):
        # Ensure the user is a superuser or system admin
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to view this record.")

        # Fetch the ChurchAccount object
        church_account = get_object_or_404(ChurchAccount, pk=pk, is_deleted=False)

        # Serialize the ChurchAccount object
        serializer = ChurchAccountSerializer(church_account)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE method to perform the delete action after viewing
    def delete(self, request, pk):
        # Ensure the user is a superuser or system admin
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this record.")

        # Fetch the ChurchAccount object
        church_account = get_object_or_404(ChurchAccount, pk=pk, is_deleted=False)

        # Soft delete the ChurchAccount
        church_account.is_deleted = True
        church_account.save()

        return Response({"detail": "Church account successfully deleted."}, status=status.HTTP_204_NO_CONTENT)

########################################################    

class MemberListView(generics.ListAPIView):
    """
    View to retrieve all members with pagination and filtering.
    Both Church Admin and Secretary can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MemberRegistrationSerializer
    pagination_class = CustomPagination
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['full_name', 'gender', 'email']  # Add filterable fields

    def get_queryset(self):
        # Determine the church account based on the user role
        try:
            church_account = ChurchAccount.objects.get(church_admin=self.request.user)
        except ChurchAccount.DoesNotExist:
            try:
                secretary_account = SecretaryAccount.objects.get(user=self.request.user)
                church_account = secretary_account.church
            except SecretaryAccount.DoesNotExist:
                raise PermissionDenied("You do not have permission to view members.")

        # Query members associated with the church
        return MemberRegistration.objects.filter(church=church_account)

class MemberCreateView(APIView):
    """
    View to create a new choir member account.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MemberRegistrationSerializer

    def post(self, request):
        """
        Create a new choir member account.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to perform CRUD operations on ChoirMemberAccount.")

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

class MemberDetailView(APIView):
    """
    View to retrieve, update, and delete a member.
    Both Church Admin and Secretary can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MemberRegistrationSerializer

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
                raise PermissionDenied("You do not have permission to manage members.")

    def get_object(self, pk, church):
        """
        Helper method to get the MemberRegistration object and ensure it belongs to the church.
        """
        try:
            return MemberRegistration.objects.get(id=pk, church=church)
        except MemberRegistration.DoesNotExist:
            raise NotFound("Member not found or you do not have permission to access this record.")

    def get(self, request, pk):
        """
        Retrieve a member by their ID.
        """
        church = self.get_church(request.user)
        member = self.get_object(pk, church)
        serializer = MemberRegistrationSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a member's information.
        """
        church = self.get_church(request.user)
        member = self.get_object(pk, church)
        serializer = MemberRegistrationSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a member.
        """
        church = self.get_church(request.user)
        member = self.get_object(pk, church)
        member.delete()
        return Response({"detail": "Member has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

#####################################################  

class ChoirMemberAccountCreateAPIView(APIView):
    """
    View to create a new choir member account.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChoirMemberAccountSerializer

    def post(self, request):
        """
        Create a new choir member account.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to perform CRUD operations on ChoirMemberAccount.")

        # Retrieve the ChurchAccount based on the logged-in user
        try:
            # If the user is a church admin, fetch the church they manage
            church_account = ChurchAccount.objects.get(church_admin=request.user)
        except ChurchAccount.DoesNotExist:
            # If not a church admin, check if they are a choir director
            try:
                choir_director = ChoirDirectorAccount.objects.get(user=request.user)
                church_account = choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
                return Response({"detail": "You do not belong to any church."}, status=status.HTTP_403_FORBIDDEN)

        # Pass the ChurchAccount instance to the serializer
        serializer = self.serializer_class(data=request.data, context={"church": church_account})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChoirMemberAccountListAPIView(generics.ListAPIView):
    """
    View to retrieve all choir members with pagination and search filters.
    Both Church Admin and Choir Director can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChoirMemberAccountSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Determine the church account based on the user role
        try:
            church_account = ChurchAccount.objects.get(church_admin=self.request.user)
        except ChurchAccount.DoesNotExist:
            try:
                choir_director = ChoirDirectorAccount.objects.get(user=self.request.user)
                church_account = choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
                raise PermissionDenied("You do not have permission to view choir members.")

        # Query choir members associated with the church
        choirs = ChoirMemberAccount.objects.filter(church=church_account)

        # Apply search filters based on query parameters
        full_name = self.request.query_params.get('full_name', None)
        if full_name:
            choirs = choirs.filter(full_name__icontains=full_name)

        gender = self.request.query_params.get('gender', None)
        if gender:
            choirs = choirs.filter(gender=gender)

        return choirs

class ChoirMemberAccountDetailAPIView(APIView):
    """
    View to retrieve, update, and delete a choir.
    Both Church Admin and Secretary can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChoirMemberAccountSerializer

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
                choir_directory = ChoirDirectorAccount.objects.get(user=user)
                return choir_directory.church
            except ChoirDirectorAccount.DoesNotExist:
                raise PermissionDenied("You do not have permission to manage choir.")

    def get_object(self, pk, church):
        """
        Helper method to get the ChoirMemberAccount object and ensure it belongs to the church.
        """
        try:
            return ChoirMemberAccount.objects.get(id=pk, church=church)
        except ChoirMemberAccount.DoesNotExist:
            raise NotFound("Choir not found or you do not have permission to access this record.")

    def get(self, request, pk):
        """
        Retrieve a choir by their ID.
        """
        church = self.get_church(request.user)
        choir = self.get_object(pk, church)
        serializer = ChoirMemberAccountSerializer(choir)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a choir's information.
        """
        church = self.get_church(request.user)
        choir = self.get_object(pk, church)
        serializer = ChoirMemberAccountSerializer(choir, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a choir.
        """
        church = self.get_church(request.user)
        choir = self.get_object(pk, church)
        choir.delete()
        return Response({"detail": "choir has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
##############################################################

class ChoirDirectorAccountCreateAPIView(APIView):
    """
    View to create a new choir member account.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChoirDirectorAccountSerializer

    def post(self, request):
        """
        Create a new choir member account.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to perform CRUD operations on ChoirMemberAccount.")

        # Adjust this line to use the correct field (likely 'church_admin')
        church = get_object_or_404(ChurchAccount, church_admin=request.user)

        # Pass the ChurchAccount instance to the serializer
        serializer = self.serializer_class(data=request.data, context={"church": church})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChoirDirectorAccountListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get all choir director records.
        Restrict choir directors from viewing other choir directors' records.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to view ChoirDirectorAccount records.")

        # Get the church account for the logged-in user (whether admin or director)
        church_account = self.get_church_account(request.user)
        if not church_account:
            return Response({"detail": "You do not belong to any church."}, status=status.HTTP_403_FORBIDDEN)

        # Restrict choir directors from viewing other choir directors' records
        if hasattr(request.user, 'choirdirectoraccount'):
            return Response({"detail": "You are not authorized to view other choir directors' records."}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve all choir director records associated with the same church
        choir_directors = ChoirDirectorAccount.objects.filter(church=church_account)

        # Serialize and return the records
        serializer = ChoirDirectorAccountSerializer(choir_directors, many=True)
        return Response(serializer.data)

    def get_church_account(self, user):
        """
        Try to fetch the church account for the given user. This handles both church admins and choir directors.
        """
        # First, check if the user is a church admin
        try:
            return ChurchAccount.objects.get(church_admin=user)
        except ChurchAccount.DoesNotExist:
            # If the user is not a church admin, check if they are a choir director
            try:
                choir_director = ChoirDirectorAccount.objects.get(user=user)
                return choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
                return None

class ChoirDirectorAccountDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Get the logged-in choir director's account details by pk.
        """
        try:
            # Ensure the logged-in user is trying to access their own account
            choir_director = ChoirDirectorAccount.objects.get(id=pk, user=request.user)
        except ChoirDirectorAccount.DoesNotExist:
            return Response({"detail": "You do not have permission to view this record."}, status=status.HTTP_403_FORBIDDEN)

        # Serialize the choir director's record
        serializer = ChoirDirectorAccountSerializer(choir_director)

        return Response(serializer.data)


class ChoirDirectorAccountUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Retrieve the choir director's record by pk.
        Only the logged-in choir director can view their record.
        """
        try:
            # Ensure the logged-in user is the owner of the record
            choir_director = ChoirDirectorAccount.objects.get(id=pk, user=request.user)
        except ChoirDirectorAccount.DoesNotExist:
            return Response({"detail": "You do not have permission to view this record."}, status=status.HTTP_403_FORBIDDEN)

        # Serialize the choir director data
        serializer = ChoirDirectorAccountSerializer(choir_director)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Prevent the logged-in choir director from updating their own account.
        Only superusers or other authorized users can update a choir director's account.
        """
        try:
            # Ensure the logged-in user is the owner of the record
            choir_director = ChoirDirectorAccount.objects.get(id=pk, user=request.user)
        except ChoirDirectorAccount.DoesNotExist:
            return Response({"detail": "You do not have permission to update this record."}, status=status.HTTP_403_FORBIDDEN)

        # Deny access to PUT method for the logged-in choir director
        raise PermissionDenied("You are not allowed to update your own record.")

    def delete(self, request, pk):
        """
        Prevent the logged-in choir director from deleting their own account.
        Only superusers or other authorized users can delete a choir director's account.
        """
        try:
            # Ensure the logged-in user is the owner of the record
            choir_director = ChoirDirectorAccount.objects.get(id=pk, user=request.user)
        except ChoirDirectorAccount.DoesNotExist:
            return Response({"detail": "You do not have permission to delete this record."}, status=status.HTTP_403_FORBIDDEN)

        # Deny access to DELETE method for the logged-in choir director
        raise PermissionDenied("You are not allowed to delete your own record.")
###################################################


class SecretaryAccountCreateAPIView(APIView):
    """
    View to create a new choir member account.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SecretaryAccountAccountSerializer

    def post(self, request):
        """
        Create a new choir member account.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to perform CRUD operations on ChoirMemberAccount.")

        # Adjust this line to use the correct field (likely 'church_admin')
        church = get_object_or_404(ChurchAccount, church_admin=request.user)

        # Pass the ChurchAccount instance to the serializer
        serializer = self.serializer_class(data=request.data, context={"church": church})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SecretaryAccountDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update an individual member.
    System admin (superuser) cannot perform CRUD operations on members,
    but can access member data. Church admin can access and update their own church members.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SecretaryAccountAccountSerializer
    queryset = SecretaryAccount.objects.all()

    def get_object(self):
        """
        Override to restrict access based on user role:
        - System admin (superuser) can view members but cannot perform updates.
        - Regular church admins can only access and update their own church members.
        """
        # Fetch the member object based on the provided primary key (pk) in the URL
        secretary = super().get_object()
        user = self.request.user

        # Allow system admins (superuser) to view the member data, but they cannot update
        if user.is_superuser:
            return secretary

        # If not a system admin, check if the user is the admin of this member's church
        if secretary.church.church_admin == user:
            return secretary

        # If the user is neither the account owner nor an admin, deny access
        raise PermissionDenied("You do not have permission to access this member.")

    def update(self, request, *args, **kwargs):
        """
        Override the update method to ensure the system admin cannot update members.
        """
        secretary = self.get_object()  # Get the member object
        user = request.user

        # Prevent system admin (superuser) from performing the update
        if user.is_superuser:
            raise PermissionDenied("System admins are not allowed to update members.")

        # If not a superuser, check if the user is allowed to update the member
        if secretary.church.church_admin == user:
            # Proceed with the update as the user has permission
            serializer = self.get_serializer(secretary, data=request.data, partial=True)
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If the user does not have permission, deny access
        raise PermissionDenied("You do not have permission to update this member.")

    def perform_update(self, serializer):
        """
        Override the default update method to save the church field correctly.
        """
        user = self.request.user
        church_account = ChurchAccount.objects.get(church_admin=user)
        serializer.validated_data['church'] = church_account  # Ensure the correct church is associated

        # Save the updated member instance
        serializer.save()

class SecretaryAccountListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get all choir director records.
        Restrict choir directors from viewing other choir directors' records.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to view ChoirDirectorAccount records.")

        # Get the church account for the logged-in user (whether admin or director)
        church_account = self.get_church_account(request.user)
        if not church_account:
            return Response({"detail": "You do not belong to any church."}, status=status.HTTP_403_FORBIDDEN)

        # Restrict choir directors from viewing other choir directors' records
        if hasattr(request.user, 'choirdirectoraccount'):
            return Response({"detail": "You are not authorized to view other choir directors' records."}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve all choir director records associated with the same church
        secretary = SecretaryAccount.objects.filter(church=church_account)

        # Serialize and return the records
        serializer = SecretaryAccountAccountSerializer(secretary, many=True)
        return Response(serializer.data)

    def get_church_account(self, user):
        """
        Try to fetch the church account for the given user. This handles both church admins and choir directors.
        """
        # First, check if the user is a church admin
        try:
            return ChurchAccount.objects.get(church_admin=user)
        except ChurchAccount.DoesNotExist:
            # If the user is not a church admin, check if they are a choir director
            try:
                secretary = SecretaryAccount.objects.get(user=user)
                return secretary.church
            except SecretaryAccount.DoesNotExist:
                return None

class SecretaryAccountDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Get the logged-in choir director's account details by pk.
        """
        try:
            # Ensure the logged-in user is trying to access their own account
            secretary = SecretaryAccount.objects.get(id=pk, user=request.user)
        except SecretaryAccount.DoesNotExist:
            return Response({"detail": "You do not have permission to view this record."}, status=status.HTTP_403_FORBIDDEN)

        # Serialize the choir director's record
        serializer = SecretaryAccountAccountSerializer(secretary)

        return Response(serializer.data)

class SecretaryAccountDeleteView(APIView):
    """
    Handle the deletion of a member.
    - System admin (superuser) cannot delete members.
    - Church admin can delete members of their own church.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Retrieve secretary details before deletion.
        - Display the secretary details before confirming deletion.
        """
        try:
            secretary = SecretaryAccount.objects.get(id=pk)
        except SecretaryAccount.DoesNotExist:
            return Response({"detail": "secretary not found."}, status=status.HTTP_404_NOT_FOUND)

        # Prevent system admins (superusers) from accessing secretary details
        if request.user.is_superuser:
            raise PermissionDenied("System admins are not allowed to view secretary details.")

        # Allow church admin to view the secretary if they belong to the same church
        if secretary.church.church_admin == request.user:
            serializer = SecretaryAccountAccountSerializer(secretary)
            return Response(serializer.data)

        # Deny access if the user is not authorized
        raise PermissionDenied("You do not have permission to view this secretary.")

    def delete(self, request, pk):
        """
        Delete a secretary.
        - System admin (superuser) cannot delete secretary.
        - Church admin can delete secretary of their own church.
        """
        user = request.user

        try:
            secretary = SecretaryAccount.objects.get(id=pk)
        except SecretaryAccount.DoesNotExist:
            return Response({"detail": "secretary not found."}, status=status.HTTP_404_NOT_FOUND)

        # Prevent system admins (superusers) from deleting secretary
        if user.is_superuser:
            raise PermissionDenied("System admins are not allowed to delete secretary.")

        # Allow church admin to delete secretary from their own church
        if secretary.church.church_admin == user:
            secretary.delete()  # Perform the deletion
            return Response({"detail": "secretary deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        # If the user is not the church admin, deny access
        raise PermissionDenied("You do not have permission to delete this secretary.")

###############################################

class DepartmentCreateView(APIView):
    """
    View to create a new announcement.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer

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

class DepartmentListView(APIView):
    """
    View to create and retrieve announcements.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer

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
                    try:
                    # Check if the user is a choir member
                        choir = ChoirMemberAccount.objects.get(user=user)
                        return choir.church
                    except ChoirMemberAccount.DoesNotExist:
                        raise PermissionDenied("You are not associated with any church.")

    def get(self, request):
        """
        Retrieve all departments associated with the user's church.
        """
        # Get the church account associated with the user
        church = self.get_church(request.user)

        # Filter announcements by the church
        departments = ChurchDepartment.objects.filter(church=church, is_deleted=False).order_by('-created_at')

        
        # Serialize the announcements
        serializer = self.serializer_class(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DepartmentDetailUpdateDeleteView(APIView):
    """
    View to create, retrieve, update, and delete department.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer

    def get_church(self, user):
        """
        Helper method to get the church account associated with the user.
        """
        try:
            # Check if the user is a church admin
            return ChurchAccount.objects.get(church_admin=user)
        except ChurchAccount.DoesNotExist:
            try:
                # Check if the user is a secretary
                secretary_account = SecretaryAccount.objects.get(user=user)
                return secretary_account.church
            except SecretaryAccount.DoesNotExist:
                raise PermissionDenied("You are not associated with any church.")

    def get_department(self, pk, church):
        """
        Helper method to get a specific department and ensure it belongs to the church.
        """
        try:
            return ChurchDepartment.objects.get(id=pk, church=church, is_deleted=False)
        except ChurchDepartment.DoesNotExist:
            raise NotFound("Department not found or you do not have permission to access it.")

    def get(self, request, pk):
        """
        Retrieve a single department by its ID.
        """
        church = self.get_church(request.user)
        department = self.get_department(pk, church)
        serializer = self.serializer_class(department)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update an department's information.
        """
        church = self.get_church(request.user)
        department = self.get_department(pk, church)
        serializer = self.serializer_class(
            department, data=request.data, partial=True, context={"church": church, "request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Soft delete an department.
        """
        church = self.get_church(request.user)
        department = self.get_department(pk, church)

        # Perform a soft delete by marking `is_deleted` as True
        department.is_deleted = True
        department.save()
        return Response({"detail": "Department deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# statistics view
class GeneralStatisticsView(APIView):
    """
    View to retrieve total members, total female members, and total male members, total choirs, total announcements.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get the total number of members, total females, and total males.
        """
        # Get the total number of choirs
        total_choirs = ChoirMemberAccount.objects.filter(is_deleted=False).count()
        # Get the total number of members
        total_members = MemberRegistration.objects.filter(is_deleted=False).count()
        # Get the total number of announcements
        total_announcements = ChurchAnnouncement.objects.filter(is_deleted=False).count()

        # Get the total number of female members
        total_female = MemberRegistration.objects.filter(gender='Female', is_deleted=False).count()

        # Get the total number of male members
        total_male = MemberRegistration.objects.filter(gender='Male', is_deleted=False).count()

        

        # Return the response
        return Response({
            "total_members": total_members,
            "total_female": total_female,
            "total_male": total_male,
            'total_choirs': total_choirs,
            'total_announcements': total_announcements,
        }, status=200)

class ChoirStatsView(APIView):
    """
    View to retrieve total choirs, total female choirs, and total male choirs.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get the total number of choirs, total females, and total males.
        """
        # Get the total number of choirs
        total_choirs = ChoirMemberAccount.objects.filter(is_deleted=False).count()
        
        # Get the total number of female choirs
        total_female = ChoirMemberAccount.objects.filter(member__gender='Female', is_deleted=False).count()
        
        # Get the total number of male choirs
        total_male = ChoirMemberAccount.objects.filter(member__gender='Male', is_deleted=False).count()
        
        # Return the response
        return Response({
            "total_choirs": total_choirs,
            "total_female": total_female,
            "total_male": total_male
        }, status=200)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)

        if user is not None:
            # Create a token for the user if it doesn’t already exist
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": "Email or password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

         



