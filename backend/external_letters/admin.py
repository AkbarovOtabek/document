from django.contrib import admin
from .models import ExternalLettersCategory, ExternalLetter


@admin.register(ExternalLettersCategory)
class ExternalLettersCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'time_create')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(ExternalLetter)
class ExternalLetterAdmin(admin.ModelAdmin):
    list_display = ('letter_number', 'internal_letter_number', 'executor',
                    'title', 'category', 'time_create')
    list_filter = ('category', 'executor')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'letter_number',
                     'internal_letter_number', 'executor', 'category')
    readonly_fields = ('time_create', 'updated')
