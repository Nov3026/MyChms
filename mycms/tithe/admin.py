from django.contrib import admin
from .models import ChurchTithe

# Register your models here.
# admin.site.register(ChurchTithe)

@admin.register(ChurchTithe)
class ChurchTitheAdmin(admin.ModelAdmin):
    list_display = ('church','member','usd_amount','lrd_amount','payment_date','month','year')
    list_filter = ('month', 'year')
    search_fields = ('member__full_name','usd_amount','lrd_amount')
    
