from django.contrib import admin
from apps.accounts.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'created_at']
    search_fields = ['email', 'username']
    readonly_fields = ['created_at', 'updated_at']
