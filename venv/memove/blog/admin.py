from django.contrib import admin
from .models import Post, PropertyPlan, Pictures, Contact


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


@admin.register(PropertyPlan)
class PlanAdmin(admin.ModelAdmin):
    pass


@admin.register(Pictures)
class PlanAdmin(admin.ModelAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('head', 'name', 'email', 'date')
    prepopulated_fields = {'head': ('head',), 'name': ('name',), 'email': ('email',)}
    ordering = ('date',)
