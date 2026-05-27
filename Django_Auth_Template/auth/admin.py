from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
	model = UserProfile
	can_delete = False
	extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	inlines = [UserProfileInline]
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_verified', 'is_staff')
	list_filter = ('is_verified', 'is_staff', 'is_superuser', 'is_active', 'groups')
	search_fields = ('username', 'email', 'first_name', 'last_name')
	ordering = ('username',)

	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'is_verified')}),
		('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		('Important dates', {'fields': ('last_login', 'date_joined')}),
	)

	add_fieldsets = (
		(
			None,
			{
				'classes': ('wide',),
				'fields': ('username', 'email', 'phone', 'password1', 'password2', 'is_staff', 'is_superuser'),
			},
		),
	)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'country', 'city', 'date_of_birth', 'created_at')
	search_fields = ('user__username', 'user__email', 'country', 'city')
	list_filter = ('country', 'city')
