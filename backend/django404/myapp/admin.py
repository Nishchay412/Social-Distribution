from django.contrib import admin
from .models import RemoteNode

@admin.register(RemoteNode)
class RemoteNodeAdmin(admin.ModelAdmin):
    list_display = ('host', 'username', 'is_active')
    # optionally fields for searching, filtering, etc.
