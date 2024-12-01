from django.contrib import admin
from .models import ChoirDue

# Register your models here.
@admin.register(ChoirDue)
class ChoirDueAdmin(admin.ModelAdmin):
    list_display = ('church','choir_member','amount_due',
                    'amount_paid','date_paid','month','year')
    search_fields = ('choir_member__member__full_name', 'date_paid', 'balance')
    list_filter = ('month', 'year', 'balance')

