from django.contrib import admin
from .models import ChurchExpenditure

# Register your models here.
# admin.site.register(ChurchExpenditure)

@admin.register(ChurchExpenditure)
class ChurchExpenditureAdmin(admin.ModelAdmin):
    list_display = ('church','expenses_type','item',
                    'lrd_amount','usd_amount','descriptions','month','year')
    search_fields = ('expenses_type', 'year', 'month')
    list_filter = ('month', 'year', 'expenses_type')
