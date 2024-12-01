from django.db import models
from accounts.models import ChurchAccount

# Create your models here.
class ChurchActivity(models.Model):
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()
    day = models.CharField(max_length=20)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.name}"
    

