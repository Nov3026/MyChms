from django.contrib import admin
from .models import ChoirDirectorAccount, ChoirMemberAccount,ChurchAccount

# Register your models here.
admin.site.register(ChoirDirectorAccount)
admin.site.register(ChoirMemberAccount)
admin.site.register(ChurchAccount)
