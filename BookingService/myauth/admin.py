import csv

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.forms import TextInput, Textarea
from django.db import models
from django.contrib.auth.models import Group
from django.http import HttpResponse

from .models import User as MyUser, GET_VAR, Config

from .models import Company, Client, Driver

style_overrides = {
    models.CharField: {'widget': TextInput(attrs={'size': '20'})},
    models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
}


@admin.action(description="Сформировать реестр")
def export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = [field.name for field in meta.fields]
    field_names.remove('passport_series')
    field_names.remove('passport_number')
    field_names.remove('auth_profile')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=PersonalDataRegistry.csv'
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])
    return response


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('email', 'docs_status', 'royalty_percent_adm')
    search_fields = ['name__icontains']
    formfield_overrides = style_overrides


class ClientAdmin(admin.ModelAdmin):
    list_display = ('fio', 'ph', 'em')
    search_fields = ['surname__icontains', 'name__icontains']
    formfield_overrides = style_overrides
    actions = [export_as_csv]


class DriverAdmin(admin.ModelAdmin):
    list_display = ('fio', 'docs_status', 'comp')
    search_fields = ['surname__icontains', 'name__icontains']
    formfield_overrides = style_overrides


admin.site.register(Company, CompanyAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Driver, DriverAdmin)


class MyUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'html_role')
    search_fields = ['email__icontains', 'phone__icontains', 'html_role__icontains']
    formfield_overrides = style_overrides


class ConfVarAdmin(admin.ModelAdmin):
    list_display = ('variable_name', 'value', 'description')
    formfield_overrides = style_overrides


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Config, ConfVarAdmin)

# Unregister unnecessary model
admin.site.unregister(Group)
