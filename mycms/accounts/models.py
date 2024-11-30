from django.db import models
from django_countries.fields import CountryField
from choice.views import gender_choices, status_choices
from validator.views import valid_phone_number, validate_file_size
from django.contrib.auth.models import User
from django.core.validators import EmailValidator



# Create your models here.
class ActiveChurchAccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class ChurchAccount(models.Model):
    church_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, validators=[valid_phone_number], verbose_name='church phone number')
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    logo = models.ImageField(upload_to='church_logos/%Y/%m/%d/', max_length=256, validators=[validate_file_size], blank=True, null=True)
    status = models.CharField(max_length=10, choices=status_choices, default='active')
    church_admin = models.ForeignKey(User, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveChurchAccountManager()  # Default manager excludes soft-deleted records
    all_objects = models.Manager()  # Includes soft-deleted records if needed

    def __str__(self):
        return self.church_name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['church_name', 'email'], name='unique_church_account')
        ]
        verbose_name_plural = 'Church Accounts'

class ChurchDepartment(models.Model):
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE, related_name='dept_church')
    name = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ('church', 'name')
        verbose_name_plural = 'Church Departments'
    
class MemberRegistration(models.Model):
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE, related_name='church')
    full_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=gender_choices, default='select gender')
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15, validators=[valid_phone_number], verbose_name='church phone number')
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    nationality = CountryField(blank=('selected country'), default='Select Country')
    address = models.CharField(max_length=200)
    profile_image = models.ImageField(upload_to='profile_photos/%Y/%m/%d/', max_length=256, validators=[validate_file_size], blank=True, null=True)
    department = models.ForeignKey(ChurchDepartment, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=status_choices, default='active')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    
    def __str__(self):
        return f"{self.full_name}"

class ChoirDirectorAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE, related_name='church_members')
    member = models.ForeignKey(MemberRegistration, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.member.full_name
    
class ChoirMemberAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member = models.ForeignKey(MemberRegistration, on_delete=models.CASCADE, related_name='member')
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE, related_name='church_choir')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.member.full_name
    
class SecretaryAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member = models.ForeignKey(MemberRegistration, on_delete=models.CASCADE, related_name='member_secretary')
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE, related_name='church_secretary')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.member.full_name
    

