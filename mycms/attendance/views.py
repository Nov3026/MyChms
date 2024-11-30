from .serializers import ChurchServiceAttendanceSerializer, ChoirAttendanceSerializer
from .models import ChurchServiceAttendance, ChoirAttendance
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from accounts.models import ChurchAccount, SecretaryAccount, ChoirDirectorAccount, ChoirMemberAccount
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import PermissionDenied, NotFound
from accounts.views import CustomPagination
from rest_framework import generics


# Create your views here.
class ChurchserviceAttendanceCreateView(APIView):
    """
    View to create a new attendance.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChurchServiceAttendanceSerializer

    def post(self, request):
        """
        Create a new attendance.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to perform CRUD operations on Church Attendance.")

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


class ChurchserviceAttendanceListView(generics.ListAPIView):
    """
    View to retrieve all attendance with pagination.
    Both Church Admin and Secretary can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChurchServiceAttendanceSerializer
    pagination_class = CustomPagination  # Use pagination for large datasets

    def get_queryset(self):
        # Determine the church account based on the user role
        try:
            church_account = ChurchAccount.objects.get(church_admin=self.request.user)
        except ChurchAccount.DoesNotExist:
            try:
                secretary_account = SecretaryAccount.objects.get(user=self.request.user)
                church_account = secretary_account.church
            except SecretaryAccount.DoesNotExist:
                try:
                    choir_director = ChoirDirectorAccount.objects.get(user=self.request.user)
                    church_account = choir_director.church
                except ChoirDirectorAccount.DoesNotExist:
                    try:
                        choir = ChoirMemberAccount.objects.get(user=self.request.user)
                        church_account = choir.church
                    except ChoirMemberAccount.DoesNotExist:
                        raise PermissionDenied("You do not have permission to view attendance.")

        # Query attendance records associated with the church
        church_attendance = ChurchServiceAttendance.objects.filter(church=church_account)

        # You can add any additional filtering here if required

        return church_attendance


class ChurchserviceAttendanceDetailUpdateDeleteView(APIView):
    """
    View to retrieve, update, and delete a member.
    Both Church Admin and Secretary can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChurchServiceAttendanceSerializer

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
                raise PermissionDenied("You do not have permission to manage attendance.")

    def get_object(self, pk, church):
        """
        Helper method to get the ChurchServiceAttendance object and ensure it belongs to the church.
        """
        try:
            return ChurchServiceAttendance.objects.get(id=pk, church=church)
        except ChurchServiceAttendance.DoesNotExist:
            raise NotFound("Attendance not found or you do not have permission to access this record.")

    def get(self, request, pk):
        """
        Retrieve a attendance by their ID.
        """
        church = self.get_church(request.user)
        church_attendance = self.get_object(pk, church)
        serializer = ChurchServiceAttendanceSerializer(church_attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a attendance's information.
        """
        church = self.get_church(request.user)
        church_attendance = self.get_object(pk, church)
        serializer = ChurchServiceAttendanceSerializer(church_attendance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a attendance.
        """
        church = self.get_church(request.user)
        church_attendance = self.get_object(pk, church)
        church_attendance.delete()
        return Response({"detail": "Attendance has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

# church attendance view ends here

class ChoirAttendanceCreateView(APIView):
    """
    View to create a new attendance.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChoirAttendanceSerializer

    def post(self, request):
        """
        Create a new attendance.
        """
        if request.user.is_superuser:
            raise PermissionDenied("Superusers are not allowed to perform CRUD operations on Church Attendance.")

        # Retrieve the ChurchAccount based on the logged-in user
        church_account = None
        try:
            # Check if the user is a church admin
            church_account = ChurchAccount.objects.get(church_admin=request.user)
        except ChurchAccount.DoesNotExist:
            # If not a church admin, check if they are a church secretary
            try:
                choir_director = ChoirDirectorAccount.objects.get(user=request.user)
                church_account = choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
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


class ChoirAttendanceListView(generics.ListAPIView):
    """
    View to retrieve all attendance with pagination.
    Both Church Admin and Choir Director can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChurchServiceAttendanceSerializer
    pagination_class = CustomPagination  # Use pagination for large datasets

    def get_queryset(self):
        # Determine the church account based on the user role
        try:
            church_account = ChurchAccount.objects.get(church_admin=self.request.user)
        except ChurchAccount.DoesNotExist:
            try:
                choir_director = ChoirDirectorAccount.objects.get(user=self.request.user)
                church_account = choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
                try:
                    choir = ChoirMemberAccount.objects.get(user=self.request.user)
                    church_account = choir.church
                except ChoirMemberAccount.DoesNotExist:
                    raise PermissionDenied("You do not have permission to view attendance.")

        # Query attendance records associated with the church
        church_attendance = ChurchServiceAttendance.objects.filter(church=church_account)

        # You can add any additional filtering here if required

        return church_attendance

class ChoirAttendanceDetailUpdateDeleteView(APIView):
    """
    View to retrieve, update, and delete a member.
    Both Church Admin and choir director can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChoirAttendanceSerializer

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
                choir_director = ChoirDirectorAccount.objects.get(user=user)
                return choir_director.church
            except ChoirDirectorAccount.DoesNotExist:
                raise PermissionDenied("You do not have permission to manage attendance.")

    def get_object(self, pk, church):
        """
        Helper method to get the ChoirAttendance object and ensure it belongs to the church.
        """
        try:
            return ChoirAttendance.objects.get(id=pk, church=church)
        except ChoirAttendance.DoesNotExist:
            raise NotFound("Attendance not found or you do not have permission to access this record.")

    def get(self, request, pk):
        """
        Retrieve a attendance by their ID.
        """
        church = self.get_church(request.user)
        choir_attendance = self.get_object(pk, church)
        serializer = ChoirAttendanceSerializer(choir_attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a attendance's information.
        """
        church = self.get_church(request.user)
        choir_attendance = self.get_object(pk, church)
        serializer = ChoirAttendanceSerializer(choir_attendance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a attendance.
        """
        church = self.get_church(request.user)
        church_attendance = self.get_object(pk, church)
        church_attendance.delete()
        return Response({"detail": "Attendance has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)