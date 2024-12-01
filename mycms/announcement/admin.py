from django.contrib import admin
from .models import ChurchAnnouncement

# Register your models here.
# admin.site.register(ChurchAnnouncement)

@admin.register(ChurchAnnouncement)
class ChurchAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('church', 'author', 'title', 'content')
    search_fields = ('title', 'author')
