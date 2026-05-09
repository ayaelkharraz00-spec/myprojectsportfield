"""
reservations/admin.py  –  Register all models with the admin panel
"""
from django.contrib import admin
from .models import Sport, Terrain, Reservation


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display  = ['name', 'max_capacity']
    search_fields = ['name']


@admin.register(Terrain)
class TerrainAdmin(admin.ModelAdmin):
    list_display  = ['name', 'sport', 'surface_type', 'availability']
    list_filter   = ['sport', 'surface_type', 'availability']
    list_editable = ['availability']   # Toggle availability right from the list


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display  = ['user', 'terrain', 'date', 'start_time', 'duration', 'end_time_col']
    list_filter   = ['date', 'terrain__sport']
    search_fields = ['user__username', 'terrain__name']

    def end_time_col(self, obj):
        return obj.get_end_time().strftime('%H:%M')
    end_time_col.short_description = 'End Time'
