from django.contrib import admin
from .models import ChurchActivity

# # Register your models here.
# admin.site.register(ChurchActivity)

@admin.register(ChurchActivity)
class ChurchActivityAdmin(admin.ModelAdmin):
    list_display = ('church','name','start_time',
                    'end_time','day',)
    search_fields = ('name',)
    
