from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Import your custom User model

class CustomUserAdmin(UserAdmin):
    # ✅ Add "is_approved" to the fields displayed in the admin panel
    list_display = ("username", "email", "is_staff", "is_superuser", "is_approved")  
    list_filter = ("is_staff", "is_superuser", "is_approved")  # ✅ Add "is_approved" filter
    fieldsets = UserAdmin.fieldsets + (  # ✅ Add "is_approved" to the user edit form
        ("Approval Status", {"fields": ("is_approved",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (  # ✅ Add to user creation form
        ("Approval Status", {"fields": ("is_approved",)}),
    )

# ✅ Register the custom admin
admin.site.register(User, CustomUserAdmin)
