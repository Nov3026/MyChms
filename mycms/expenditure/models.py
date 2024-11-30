from django.db import models
from accounts.models import ChurchAccount
from django.core.validators import MinValueValidator
from choice.views import month_choices, expense_types_choices


# Create your models here.
class ChurchExpenditure(models.Model):
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE)
    expenses_type = models.CharField(max_length=50, choices=expense_types_choices)
    item = models.CharField(max_length=200)
    lrd_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True, validators=[MinValueValidator(0.00)])
    usd_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True, validators=[MinValueValidator(0.00)])
    descriptions = models.CharField(max_length=255, blank=True, null=True)
    month = models.CharField(max_length=25, choices=month_choices)
    year = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.item
