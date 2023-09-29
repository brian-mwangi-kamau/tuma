from django.contrib import admin
from .models import CustomUser, PlatformAccount, Transaction, CharityList

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(PlatformAccount)
admin.site.register(CharityList)
admin.site.register(Transaction)