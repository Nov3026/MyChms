from rest_framework import serializers
from accounts.models import ChurchAccount, ChoirDirectorAccount, MemberRegistration,ChoirMemberAccount, SecretaryAccount, ChurchDepartment
from django.contrib.auth.models import User
from choice.views import gender_choices
from django_countries.serializer_fields import CountryField as CountrySerializerField
from .models import ChoirDirectorAccount
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError


class ChurchAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)  # Optional for update
    confirm_password = serializers.CharField(write_only=True, required=False)  # Optional for update

    class Meta:
        model = ChurchAccount
        fields = [
            'id',
            'church_name',
            'address',
            'phone_number',
            'email',
            'logo',
            'status',
            'password',
            'confirm_password',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['status', 'is_deleted', 'created_at', 'updated_at']

        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }
    
    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Validate password match only if both are provided
        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Validate password length if provided
        if password and len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        return data
    
    def create(self, validated_data):
        # Ensure both password and confirm_password are provided during creation
        password = validated_data.pop('password')
        validated_data.pop('confirm_password', None)  # Ignore confirm_password during creation

        # Create the user with password
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=password
        )

        # Create church instance
        church = ChurchAccount.objects.create(church_admin=user, **validated_data)
        return church
    
    def update(self, instance, validated_data):
        # Update password only if it's provided
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)  # Ignore confirm_password during update

        if password:
            instance.church_admin.set_password(password)
            instance.church_admin.save()

        # Update other fields in the church instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

# member serializer
class MemberRegistrationSerializer(serializers.ModelSerializer):
    
    gender = serializers.ChoiceField(choices=gender_choices)
    nationality = CountrySerializerField()

    class Meta:
        model = MemberRegistration
        fields =['id', 'church', 'full_name', 'email', 'gender', 'date_of_birth', 'nationality', 'address', 'profile_image',
                 'department','status','is_deleted','created_at','updated_at'
                 ]
        read_only_fields = ['church', 'is_deleted', 'created_at', 'updated_at', 'status']
    
    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        # Override the country field to display the full name
        representation['nationality'] = instance.nationality.name if instance.nationality else None
        return representation
    
    def create(self, validated_data):
        # Retrieve the church passed in the context
        church_account = self.context.get("church", None)
        if not church_account:
            raise serializers.ValidationError("Church information is missing in the context.")

        # Set the church field for the new member
        validated_data['church'] = church_account
        return super().create(validated_data)


#############################################################

class ChoirDirectorAccountSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='member.full_name', read_only=True)
    email = serializers.EmailField(source='member.email', read_only=True)  # Automatically retrieve email
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = ChoirDirectorAccount
        fields = ['member', 'full_name', 'email','church', 'password', 'confirm_password']
        read_only_fields = ['full_name', 'church','email']  # Keep full_name and email read-only

    def validate(self, data):
        """
        Validate passwords and check for existing user email.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        # Check if a user with this email already exists
        if User.objects.filter(username=data['member'].email).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        return data

    def create(self, validated_data):
        """
        Create a new choir director account and associated user.
        """
        validated_data.pop('confirm_password')  # Remove confirm_password from validated data

        # Extract the member object from validated data
        member = validated_data['member']

        # Create the user account
        user = User.objects.create_user(
            username=member.email,  # Use member's email as username
            email=member.email,
            password=validated_data['password']
        )

        # Create the choir director account
        choir_director_account = ChoirDirectorAccount.objects.create(
            user=user,
            church=self.context['church'],  # Pass church from context
            member=member
        )

        return choir_director_account

############################################################

class ChoirMemberAccountSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='member.full_name', read_only=True)
    email = serializers.EmailField(source='member.email', read_only=True)  # Use member's existing email
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = ChoirMemberAccount
        fields = ['id', 'member', 'full_name', 'church', 'email', 'password', 'confirm_password']
        read_only_fields = ['id', 'full_name', 'church', 'email']

    # def validate(self, data):
    #     """
    #     Validate passwords and ensure the email belongs to an existing member.
    #     """
    #     if data['password'] != data['confirm_password']:
    #         raise serializers.ValidationError("Passwords do not match.")
        
    #     # Ensure the member exists and has an email
    #     member = data.get('member')
    #     if not member.email:
    #         raise serializers.ValidationError({"member": "The selected member does not have an email address."})

    #     return data

    # def create(self, validated_data):
    #     """
    #     Create a new choir member account and associate it with the existing member's email.
    #     """
    #     validated_data.pop('confirm_password')  # Remove confirm_password from validated data

    #     member = validated_data['member']

    #     # Create or retrieve the user account associated with the member's email
    #     user, created = User.objects.get_or_create(
    #         username=member.email,
    #         defaults={'email': member.email, 'password': validated_data['password']}
    #     )

    #     if not created:
    #         # Update the password if the user already exists
    #         user.set_password(validated_data['password'])
    #         user.save()

    #     # Ensure the context includes the church
    #     church = self.context.get('church')
    #     if not church:
    #         raise serializers.ValidationError("Church information is missing.")

    #     # Create the choir member account
    #     choir_member_account = ChoirMemberAccount.objects.create(
    #         user=user,
    #         member=member,
    #         church=church,
    #     )
    #     return choir_member_account
    def validate(self, data):
        """
        Validate passwords and check for existing user email.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        # Check if a user with this email already exists
        if User.objects.filter(username=data['member'].email).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        return data

    def create(self, validated_data):
        """
        Create a new choir director account and associated user.
        """
        validated_data.pop('confirm_password')  # Remove confirm_password from validated data

        # Extract the member object from validated data
        member = validated_data['member']

        # Create the user account
        user = User.objects.create_user(
            username=member.email,  # Use member's email as username
            email=member.email,
            password=validated_data['password']
        )

        # Create the choir director account
        choir_member_account = ChoirMemberAccount.objects.create(
            user=user,
            church=self.context['church'],  # Pass church from context
            member=member
        )

        return choir_member_account

class SecretaryAccountAccountSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='member.full_name', read_only=True)
    email = serializers.EmailField(source='member.email', read_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = SecretaryAccount
        fields = ['member', 'full_name', 'church', 'email', 'password', 'confirm_password']
        read_only_fields = ['full_name', 'church', 'email']

    def validate(self, data):
        """
        Validate passwords and check for existing user email.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Check if a user with this email already exists
        if User.objects.filter(username=data['member'].email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})

        return data

    def create(self, validated_data):
        """
        Create a new secretary account and associated user.
        """
        validated_data.pop('confirm_password')  # Remove confirm_password from validated data

        # Create the user account
        user = User.objects.create_user(
            username=validated_data['member'].email,  # Use email as the username
            email=validated_data['member'].email,
            password=validated_data['password']
        )

        # Create the secretary account
        secretary_account = SecretaryAccount.objects.create(
            user=user,
            member=validated_data['member'],
            church=self.context['church'],  # Pass church from context
        )
        return secretary_account

    def update(self, instance, validated_data):
        """
        Update an existing secretary account.
        """
        if 'password' in validated_data:
            instance.user.set_password(validated_data['password'])  # Update password
            instance.user.save()

        # No updates to 'member' or 'church' allowed via this serializer
        return instance

#####################################

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchDepartment
        fields = ['id', 'church', 'name', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['is_deleted', 'church', 'created_at', 'updated_at']

    def validate_name(self, value):
        """
        Ensure that the department name is unique within the same church.
        """
        church_account = self.context.get("church", None)
        if not church_account:
            raise serializers.ValidationError("Church information is missing in the context.")

        # Check for duplicate name within the same church
        if ChurchDepartment.objects.filter(church=church_account, name=value, is_deleted=False).exists():
            raise serializers.ValidationError("A department with this name already exists in your church.")

        return value

    def create(self, validated_data):
        # Retrieve the church passed in the context
        church_account = self.context.get("church", None)
        if not church_account:
            raise serializers.ValidationError("Church information is missing in the context.")

        # Set the church field for the new department
        validated_data['church'] = church_account
        return super().create(validated_data)



