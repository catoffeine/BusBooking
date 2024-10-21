from django.forms import ModelForm, TextInput, Select, Form, DateField, CharField, Textarea

from booking.models import Bus, Route
from myauth.forms import txtw, txta

from booking.models import Trip

from myauth.models import Driver

from booking.models import get_company_drivers, get_available_buses

from booking.models import convert_to_choices

from booking.models import get_available_routes
from django_select2 import forms as s2forms

from booking.models import get_driver_company

from myauth.models import Company


class BusChangeForm(ModelForm):
    class Meta:
        model = Bus
        fields = ['license_plate', 'brand', 'color']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['license_plate'].widget = txtw('')
        self.fields['brand'].widget = txtw('')
        self.fields['color'].widget = txtw('')


class RouteChangeForm(ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'stops']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = txtw('ID')
        self.fields['stops'].widget = txta('введите названия остановок')


class SelectBusWidget(s2forms.Select2Widget):
    model = Bus
    search_fields = [
        "license_plate__icontains",
        "brand__icontains",
        "color__icontains",
    ]


class SelectRouteWidget(s2forms.Select2Widget):
    model = Route
    search_fields = [
        "name__icontains",
        "stops__icontains",
    ]


class SelectDriverWidget(s2forms.Select2Widget):
    model = Driver
    search_fields = [
        "name__icontains",
        "surname__icontains"
    ]


class TripChangeForm(ModelForm):
    class Meta:
        model = Trip
        fields = ['route', 'bus', 'driver', 'start_dt', 'ticket_price']
        widgets = {
            "route": SelectRouteWidget,
            "bus": SelectBusWidget,
            "driver": SelectDriverWidget,
            'ticket_price': txtw('Введите цену')
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.get('request')
        if 'request' in kwargs:
            kwargs.pop('request')

        super().__init__(*args, **kwargs)

        company_auth = request.user
        if request.user.role == 'driver':
            company = get_driver_company(request)
            if company is None:
                self.fields['route'].widget.queryset = Route.objects.filter(owner=request.user)
                self.fields['route'].queryset = Route.objects.filter(owner=request.user)
                self.fields['bus'].widget.queryset = Bus.objects.filter(owner=request.user)
                self.fields['bus'].queryset = Bus.objects.filter(owner=request.user)
            else:
                self.fields['route'].widget.queryset = Route.objects.filter(owner=company_auth)
                self.fields['route'].queryset = Route.objects.filter(owner=company_auth)
                self.fields['bus'].widget.queryset = Bus.objects.filter(owner=company_auth)
                self.fields['bus'].queryset = Bus.objects.filter(owner=company_auth)
        else:
            company = Company.objects.get(auth_profile=company_auth)
            self.fields['route'].widget.queryset = Route.objects.filter(owner=company_auth)
            self.fields['route'].queryset = Route.objects.filter(owner=company_auth)
            self.fields['bus'].widget.queryset = Bus.objects.filter(owner=company_auth)
            self.fields['bus'].queryset = Bus.objects.filter(owner=company_auth)
            self.fields['driver'].widget.queryset = Driver.objects.filter(company=company)
            self.fields['driver'].queryset = Driver.objects.filter(company=company)
        print('els', list(self.fields['route'].widget.queryset))


class TicketSearchForm(Form):
    date = DateField()
    from_f = CharField(max_length=100)
    to_f = CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = TextInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })

        self.fields['from_f'].widget = TextInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'role': 'combobox',
            'list': '',
            'name': 'departure_point',
            'autocomplete': 'off',
            'placeholder': 'Начните печатать...'
        })

        self.fields['to_f'].widget = TextInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'role': 'combobox',
            'list': '',
            'name': 'destination_point',
            'autocomplete': 'off',
            'placeholder': 'Начните печатать...'
        })
