from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0


class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
