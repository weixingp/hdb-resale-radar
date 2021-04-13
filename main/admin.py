from django.contrib import admin

# Register your models here.
from main.models import User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class UserAdmin(UserAdmin):

    fieldsets = (
        (None,
         {'fields': (
             'email',
             'password',
             # 'name',
             'last_login'
         )}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )

    # Reverse lookup full name from profile
    # def get_fullname(self, obj):
    #     return obj.profile.fullname

    # get_fullname.short_description = 'Full Name'
    # get_fullname.admin_order_field = 'profile__fullname'

    list_display = ('email', 'last_login')
    # list_select_related = ('profile',)

    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)