from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import ChurchAccount

# class IsChurchAdmin(permissions.BasePermission):
#     """
#     Custom permission to only allow the church admin to create or update choir director accounts.
#     """
#     def has_permission(self, request, view):
#         # Ensure the user is logged in
#         if not request.user.is_authenticated:
#             return False

#         # Extract the church_id from the request data
#         church_id = request.data.get('church')
        
#         # Ensure the church_id exists in the request
#         if not church_id:
#             return False

#         try:
#             # Fetch the ChurchAccount based on the given church_id
#             church = ChurchAccount.objects.get(id=church_id)
#         except ChurchAccount.DoesNotExist:
#             return False
        
#         # Check if the logged-in user is the church admin for this church
#         if church.church_admin != request.user:
#             return False
        
#         return True

class IsChurchAdmin(BasePermission):
    """
    Custom permission to allow only church admins (non-superusers) to register members.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and is a church admin (not superuser/system admin)
        return request.user.is_authenticated and not request.user.is_superuser and hasattr(request.user, 'churchaccount')
    
class IsSuperUser(BasePermission):
    """
    Custom permission to allow only superusers (system admins) to create church accounts.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and is a superuser
        return request.user.is_authenticated and request.user.is_superuser
    
class IsSameChurch(BasePermission):
    """
    Custom permission to allow access to members that belong to the same church
    as the authenticated user.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access if the member belongs to the same church as the authenticated user
        return obj.church == request.user.church
    
    
# class IsChoirDirector(BasePermission):
#     """
#     Allows access only to users who are choir directors.
#     """
#     def has_permission(self, request, view):
#         # Ensure the user is authenticated and is a choir director
#         return request.user.is_authenticated and hasattr(request.user, 'choirdirectoraccount')

# class IsChurchAdminOrChoirDirector(BasePermission):
#     """
#     Custom permission to allow only church admins or choir directors to create choir member accounts.
#     """
#     def has_permission(self, request, view):
#         # Check if the user is a church admin (staff) or choir director
#         return request.user.is_authenticated and (
#             request.user.is_staff or hasattr(request.user, 'choir_directoraccount')
#         )

class IsChurchAdminOrChoirDirector(BasePermission):
    """
    Custom permission to allow only church admins or choir directors to create choir member accounts.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False  # Ensure the user is authenticated
        # Allow church admins (is_staff) or choir directors
        return user.is_staff or hasattr(user, 'choir_directoraccount')
    

from rest_framework.permissions import BasePermission
from .models import ChoirDirectorAccount

class IsChoirDirector(BasePermission):
    """
    Custom permission to check if the user has a Choir Director account.
    """

    def has_permission(self, request, view):
        try:
            # Check if the user has an associated ChoirDirectorAccount
            return ChoirDirectorAccount.objects.filter(user=request.user, is_deleted=False).exists()
        except ChoirDirectorAccount.DoesNotExist:
            return False
