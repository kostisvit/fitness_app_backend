from django.contrib import admin

from .models import Sport, SportEvent


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(SportEvent)
class SportEventAdmin(admin.ModelAdmin):
    list_display = ('creator','title', 'sport', 'date', 'time', 'place','created', 'modified')
    search_fields = ('title','place' )
    list_filter = ('sport', 'date', 'creator')
