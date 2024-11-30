from django.db import models
from accounts.models import ChurchAccount, MemberRegistration
from django.core.validators import MinValueValidator
from choice.views import month_choices

# Create your models here.
class ChurchTithe(models.Model):
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE)
    member = models.ForeignKey(MemberRegistration, on_delete=models.CASCADE)
    usd_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True, validators=[MinValueValidator(0.00)])
    lrd_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True, validators=[MinValueValidator(0.00)])
    payment_date = models.DateField()
    month = models.CharField(max_length=25, choices=month_choices)
    year = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.member.full_name
    
    class Meta:
        unique_together = ('member', 'church')