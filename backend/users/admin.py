from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'access_level')
    search_fields = ('username', 'email', 'access_level')
    list_filter = ('username', 'email')


class TagAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, TagAdmin)
