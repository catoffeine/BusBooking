from django.contrib import admin

from django.db import models
from django.forms import TextInput, Textarea
from .models import Bus, Route, Trip, Ticket
from myauth.models import GET_VAR

admin.site.site_header = GET_VAR('admin-website-label')

style_overrides = {
    models.CharField: {'widget': TextInput(attrs={'size': '20'})},
    models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
}


class BusAdmin(admin.ModelAdmin):
    list_display = ('id', 'license_plate', 'brand', 'color', 'edit_scheme_url')
    search_fields = ['license_plate__icontains']
    formfield_overrides = style_overrides


class RouteAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name__icontains']
    formfield_overrides = style_overrides


class TripAdmin(admin.ModelAdmin):
    list_display = ('route', 'start_dt', 'bus', 'available_tickets_count',)
    search_fields = ['route__icontains']
    formfield_overrides = style_overrides


class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_code', 'trip', 'seat', 'qr_html')
    search_fields = ['ticket_id__icontains', 'trip__icontains']
    formfield_overrides = style_overrides


admin.site.register(Bus, BusAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(Ticket, TicketAdmin)
