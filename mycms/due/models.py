from django.db import models
from accounts.models import ChurchAccount, ChoirMemberAccount
from django.core.validators import MinValueValidator
from django.db.models import Sum
from choice.views import month_choices
from django.core.exceptions import ValidationError


# Create your models here.
class ChoirDue(models.Model):
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE, related_name='church_member_dues')
    choir_member = models.ForeignKey(ChoirMemberAccount, on_delete=models.CASCADE,related_name='choir_dues')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    date_paid = models.DateField()
    balance = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    month = models.CharField(max_length=25, choices=month_choices)
    year = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.choir_member
    
    def save(self, *args, **kwargs):
        self.balance = self.amount_due - self.amount_paid
        super().save(*args, **kwargs)

    def clean(self):
        if self.choir_member.church != self.church:
            raise ValidationError("Choir member does not belong to the specified church.")


    # def calculate_amount_paid(self):
    #     total_amount = ChoirDue.objects.aggregate()
    
    class Meta:
        verbose_name_plural = 'choir member dues'
