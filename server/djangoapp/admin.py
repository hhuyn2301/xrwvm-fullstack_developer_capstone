"""Admin screens for car makes and models."""
from django.contrib import admin
from .models import CarMake, CarModel

@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ("name", "car_make", "type", "year", "dealer_id", "mileage")
    list_filter = ("car_make", "type", "year")
    search_fields = ("name", "car_make__name")
    list_select_related = ("car_make",)

admin.site.site_header = "Dealership Administration"
admin.site.site_title = "Dealership Admin"
admin.site.index_title = "Car catalogue and user management"
