from django.contrib import admin
from .models import ChoirSong

# # Register your models here.
# admin.site.register(ChoirSong)

@admin.register(ChoirSong)
class ChoirSongAdmin(admin.ModelAdmin):
    list_display = ('church','author','title','song_content',)
    search_fields = ('author','title')
    
