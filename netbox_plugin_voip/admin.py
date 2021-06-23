"""
from django.contrib import admin
import .models

@admin.register(models.MyModel1)
class MyModel1Admin(admin.ModelAdmin):
    fields = '__all__'
"""
from django.contrib import admin
from .models import DIDNumbers

@admin.register(DIDNumbers)
class DIDVoipAdmin(admin.ModelAdmin):
    list_display = ("did", "description","provider","route_option","tenant","called_party_mask")