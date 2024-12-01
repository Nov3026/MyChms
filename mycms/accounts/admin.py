from django.contrib import admin
from .models import ChoirDirectorAccount, ChoirMemberAccount,ChurchAccount

# Register your models here.
# admin.site.register(ChoirDirectorAccount)
# admin.site.register(ChoirMemberAccount)
# admin.site.register(ChurchAccount)

@admin.register(ChurchAccount)
class ChurchAccountAdmin(admin.ModelAdmin):
    list_display = ('church_name', 'phone_number', 'address', 'email','logo','status')
    readonly_fields = ('is_deleted', 'church_admin')
    search_fields = ('church_name', 'phone_number', 'address', 'email')

@admin.register(ChoirDirectorAccount)
class ChoirDirectorAccountAdmin(admin.ModelAdmin):
    list_display = ('member', 'church')
    search_fields = ('member__full_name', 'church__church_name','member__phone_number', 'member__email', 'member__address')

@admin.register(ChoirMemberAccount)
class ChoirMemberAccountAdmin(admin.ModelAdmin):
    list_display = ('member__full_name', 'church__church_name')
    search_fields = ('member__full_name', 'church__church_name')
