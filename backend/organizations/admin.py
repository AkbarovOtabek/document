from django.contrib import admin
from .models import Category, Organization


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'time_create')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'phone',
                    'email', 'time_create', 'updated')
    list_filter = ('category', 'time_create')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description', 'address', 'phone', 'email')
    readonly_fields = ('time_create', 'updated')
