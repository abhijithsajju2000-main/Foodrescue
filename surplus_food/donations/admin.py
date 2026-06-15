from django.contrib import admin

from .models import FoodDonation, FoodClaim


admin.site.register(FoodDonation)

admin.site.register(FoodClaim)