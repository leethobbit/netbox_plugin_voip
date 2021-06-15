from django.contrib import admin
from .models import DIDNumbers

"""
@admin.register(models.MyModel1)
class MyModel1Admin(admin.ModelAdmin):
    fields = '__all__'
"""
@admin.register(DIDNumbers)
class DIDNumberAdmin(admin.ModelAdmin):
    list_display = ("did","description","partition","route_option")

