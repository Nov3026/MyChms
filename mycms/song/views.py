from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import ChoirSong
from .serializers import SongSerializer
from accounts.models import ChurchAccount, ChoirMemberAccount, ChoirDirectorAccount, SecretaryAccount
from django.core.exceptions import PermissionDenied
from rest_framework import generics
from rest_framework.exceptions import NotFound
from accounts.views import CustomPagination

    

class SongCreateView(APIView):
    """
    View to create a new choir member account.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SongSerializer

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

class SongListView(generics.ListAPIView):
    """
    View to retrieve all songs with pagination.
    Church Admin, Secretary, Choir Director, and Choir Members can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SongSerializer
    pagination_class = CustomPagination  

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
                        raise PermissionDenied("You do not have permission to view songs.")

        # Retrieve all songs associated with the church
        songs = ChoirSong.objects.filter(church=church_account)

        # Apply search filters based on query parameters
        title = self.request.query_params.get('title', None)
        if title:
            songs = songs.filter(title__icontains=title)
        
        author = self.request.query_params.get('author', None)
        if author:
            songs = songs.filter(author__icontains=author)

        return songs


class SongDetailUpdateDeleteView(APIView):
    """
    View to retrieve, update, and delete a song.
    Both Church Admin and Secretary can access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SongSerializer

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
                raise PermissionDenied("You do not have permission to manage songs.")

    def get_object(self, pk, church):
        """
        Helper method to get the ChoirSong object and ensure it belongs to the church.
        """
        try:
            return ChoirSong.objects.get(id=pk, church=church)
        except ChoirSong.DoesNotExist:
            raise NotFound("Song not found or you do not have permission to access this record.")

    def get(self, request, pk):
        """
        Retrieve a song by their ID.
        """
        church = self.get_church(request.user)
        song = self.get_object(pk, church)
        serializer = SongSerializer(song)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a song's information.
        """
        church = self.get_church(request.user)
        song = self.get_object(pk, church)
        serializer = SongSerializer(song, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a song.
        """
        church = self.get_church(request.user)
        song = self.get_object(pk, church)
        song.delete()
        return Response({"detail": "Song has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
