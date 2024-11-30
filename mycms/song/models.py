from django.db import models
from accounts.models import ChurchAccount

# Create your models here.
class ChoirSong(models.Model):
    church = models.ForeignKey(ChurchAccount,on_delete=models.CASCADE, related_name='choir_song')
    author = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200)
    song_content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Choirs songs'

