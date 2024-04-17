from django.contrib import admin
from .models import User, UserConfirmation
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', "phone", "email", "first_name"]
admin.site.register(User, UserAdmin)


class UserConfirmationAdmin(admin.ModelAdmin):
    list_display = ['code', "user", "verify_type", "expiration_time"]
admin.site.register(UserConfirmation, UserConfirmationAdmin)