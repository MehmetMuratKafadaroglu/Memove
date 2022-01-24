from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_agent')
    list_filter = ('is_agent', )
    search_fields = ('email', )