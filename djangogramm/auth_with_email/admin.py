from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import Group as BaseGroup

from auth_with_email.models import User, Group


class UserAdmin(BaseUserAdmin):
    search_fields = ("email", "username", "full_name")
    ordering = ("username",)

    readonly_fields = ("avatar_image",)

    list_display = ("username", "email", "full_name", "registration_complete", "is_staff")

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal info", {"fields": ("full_name", "bio", "avatar_image", "avatar")}),
        ("Permissions", {"fields": (
                "registration_complete",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions"
            )
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")})
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "email", "password1", "password2")}),
    )


admin.site.unregister(BaseGroup)
admin.site.register(User, UserAdmin)
admin.site.register(Group)
