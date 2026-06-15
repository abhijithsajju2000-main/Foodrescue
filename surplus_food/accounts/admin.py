from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile

class ProfileAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'address', 'ngo_darpan_id', 'organization_pan', 'is_verified')}),
    )

admin.site.register(Profile, ProfileAdmin)