from django.db import models
from accounts.models import ChurchAccount


# Create your models here.
class ChurchAnnouncement(models.Model):
    church = models.ForeignKey(ChurchAccount, on_delete=models.CASCADE, related_name='church_announcements')
    author = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.author} - {self.title}"
    
    class Meta:
        verbose_name_plural = 'Church Announcements'
