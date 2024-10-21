import random
import uuid
from datetime import datetime, timedelta
from os import path

import django.db.models
import qrcode
from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.conf.locale.ru import formats as ru_formats
from myauth.models import Driver, User

from myauth.models import Company


def declension(n, form_0, form_1, form_2):
    units = n % 10
    tens = (n // 10) % 10
    if tens == 1:
        return form_0
    if units in [0, 5, 6, 7, 8, 9]:
        return form_0
    if units == 1:
        return form_1
    if units in [2, 3, 4]:
        return form_2


class Bus(models.Model):
    id = models.AutoField(primary_key=True)
    license_plate = models.TextField()
    brand = models.TextField(blank=True, null=True)
    color = models.TextField(blank=True, null=True)
    sitting_scheme = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Автобус'
        verbose_name_plural = 'Автобусы'

    @admin.display(description='Схема мест')
    def edit_scheme_url(self):
        return mark_safe(f"<a href='/buses/edit-scheme/{self.id}' target='_blank'> Схема мест </a>")

    def __str__(self):
        return f'{self.color} {self.brand} {self.license_plate} #{self.id}'


class Route(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    stops = models.TextField(blank=True, null=True)
    verified = models.BooleanField(blank=True, null=True, default=False)
    owner = models.ForeignKey(User, on_delete=django.db.models.CASCADE)

    class Meta:
        verbose_name = 'Маршрут автобуса'
        verbose_name_plural = 'Маршруты автобусов'

    def __str__(self):
        return f'{self.name} #{self.id}'


class Trip(models.Model):
    id = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.RESTRICT, blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.RESTRICT, blank=True, null=True)
    driver = models.ForeignKey(Driver, on_delete=models.RESTRICT, blank=True, null=True)
    start_dt = models.DateTimeField(blank=True, null=True)
    ticket_price = models.IntegerField(blank=True, null=True)
    booked_seats = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Рейс'
        verbose_name_plural = 'Рейсы'

    @admin.display(description='Количество билетов')
    def available_tickets_count(self):
        tickets_count = random.randint(0, 10)  # ToDo: return tickets count
        color = 'green'
        if tickets_count < 5:
            color = 'orange'
        if tickets_count == 0:
            color = 'red'
        s = f"{declension(tickets_count, 'Осталось', 'Остался', 'Осталось')} {tickets_count} " \
            f"{declension(tickets_count, 'билетов', 'билет', 'билета')}"
        return mark_safe(f"<p style='color: {color}; margin: 0; padding: 0'>{s}</p>")

    def __str__(self):
        return f'{self.route.name} {self.start_dt} #{self.id}'


class Ticket(models.Model):

    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'

    id = models.AutoField(primary_key=True)
    ticket_code = models.CharField(max_length=100, blank=True, default=uuid.uuid4)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.CharField(max_length=100, blank=True, null=True)
    prev_seat = models.CharField(max_length=100, blank=True, null=True)
    bought_price = models.IntegerField(blank=True, null=True)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f'Билет на рейс {self.trip}, место {self.seat}'

    def get_qr(self):
        p = f"user_files/qrs/{self.ticket_code}.png"
        if not path.isfile(p):
            img = qrcode.make(self.ticket_code)
            img.save(p)
        return p

    @admin.display(description='QR-Код')
    def qr_html(self):
        return mark_safe(f'<a href="/{self.get_qr()}">Скачать</a>')

    def return_ticket(self):
        present = datetime.now()

        # # Если поездка ещё не началась
        # if present <= self.trip.start_dt - timedelta(days=2):
        #     # Без штрафа
        #     pass
        #
        # # Если до начала поездки менее 2х дней и более 2х часов
        # elif present <= self.trip.start_dt - timedelta(hours=2):
        #     # Штраф 5%
        #     pass
        #
        # # Если до начала поездки менее 2х часов
        # elif present < self.trip.start_dt:
        #     # Штраф 15%
        #     pass
        #
        # # Если поездка уже началась
        # else:
        #     # Обратитесь в тех. поддержку
        #     pass

        self.prev_seat = self.seat
        self.seat = ''
        self.is_returned = True



import json

from django.db import models

from booking.models import Bus


# class BusSeatsScheme:
#     def __init__(self, bid):
#         self.bid = bid
#
#         json_string = Bus.objects.get(id=self.bid).sitting_scheme
#         if json_string not in ('', None, ' '):
#             self.scheme = json.loads(json_string)
#         else:
#             self.scheme = {}
#         pass
#
#     def add_row(self):
#         """Adds row to the end"""
#         self.load()
#         last_n = self.rows_n
#         self.scheme[last_n + 1] = {'row_n': str(last_n), 'data': []}
#         self.save()
#
#     def add_seat(self, row_i):
#         """Add seat to the end of exact row"""
#         self.load()
#         print(row_i, self.scheme)
#         last_seat_n = self.seats_n_in_row(row_i)
#         self.scheme[row_i]['data'] += [{'multiplier': 1, 'seat_n': last_seat_n + 1}]
#         self.save()
#
#     def add_space(self, row_i):
#         """Add seat to the end of exact row"""
#         self.load()
#         self.scheme[row_i]['data'] += [{'space': True}]
#         self.save()
#
#     def add_seat_after(self, row_i, seat_id):
#         """Add seat after seat"""
#         self.load()
#         before_seats = self.scheme[row_i]['data'][:int(seat_id) - 1]
#         after_seats = self.scheme[row_i]['data'][int(seat_id) - 1:]
#         self.scheme[row_i]['data'] = before_seats + [{'multiplier': 1, 'seat_n': int(seat_id) + 1}] + after_seats
#         self.save()
#
#     def add_space_after(self, row_i, seat_id):
#         """Add space after seat"""
#         self.load()
#         before_seats = self.scheme[row_i]['data'][:int(seat_id) - 1]
#         after_seats = self.scheme[row_i]['data'][int(seat_id) - 1:]
#         self.scheme[row_i]['data'] = before_seats + [{'space': True}] + after_seats
#         self.save()
#
#     def delete_row(self, row_i):
#         """Delete row by its number"""
#         self.load()
#         self.scheme.pop(row_i)
#         self.save()
#
#     def delete_seat(self, row_i, seat_i):
#         """Delete seat by its coordinates"""
#         self.load()
#         self.scheme[row_i]['data'].pop(int(seat_i) - 1)
#         self.save()
#
#     def set_seat_n(self, row_i, seat_i, new_n):
#         """Change seat's seat_n by its coordinates"""
#         self.load()
#         self.scheme[row_i]['data'][int(seat_i) - 1]['seat_n'] = new_n
#         self.save()
#
#     def set_seat_multiplier(self, row_i, seat_i, multiplier):
#         """Change seat's seat_n by its coordinates"""
#         self.load()
#         self.scheme[row_i][seat_i]['multiplier'] = multiplier
#         self.save()
#
#     def set_row_n(self, row_i, new_n):
#         self.scheme[row_i]['row_n'] = new_n
#         self.save()
#
#     def seats_n_in_row(self, row_i, count_spaces=True):
#         """Return seats amount in exact row"""
#         row = self.scheme[str(row_i)]
#         sn = 0
#         for seat_json in row:
#             if count_spaces:
#                 sn += 1
#             elif not seat_json.get('space', False):
#                 sn += 1
#         return sn
#
#     def set_booked_tickets(self, booked_tickets):
#         print(booked_tickets)
#         print('TICKETS')
#         for ticket in booked_tickets:
#             if not ticket.is_returned:
#                 row_name, seat_name = ticket.seat.split('-')
#                 for i, row in self.scheme.items():
#                     if row.get('row_n') == row_name:
#                         r_i = i
#                         break
#
#                 for i, seat in enumerate(self.scheme[r_i]['data']):
#                     if seat.get('seat_n') == seat_name:
#                         self.scheme[r_i]['data'][i]['space'] = True
#                         break
#
#
#     @property
#     def rows_n(self):
#         """Get rows amount"""
#         try:
#             return len(self.scheme)
#         except ValueError:
#             return 0
#
#     @property
#     def seats_n(self):
#         """Get seats amount in bus"""
#         sn = 0
#         for row_i in self.scheme:
#             sn += self.seats_n_in_row(row_i)
#         return sn
#
#     @property
#     def exported_scheme(self):
#         return json.dumps(self.scheme)
#
#     def __repr__(self):
#         return str(self.scheme)
#
#     def __str__(self):
#         return self.__repr__()
#
#     def save(self):
#         b = Bus.objects.get(id=self.bid)
#         b.sitting_scheme = self.exported_scheme
#         b.save()
#
#     def load(self):
#         json_string = Bus.objects.get(id=self.bid).sitting_scheme
#         if json_string not in ('', None, ' '):
#             self.scheme = json.loads(json_string)
#         else:
#             self.scheme = {}


def get_driver_company(request):
    try:
        driver = Driver.objects.get(auth_profile=request.user)
        company = Company.objects.get(id=driver.company.id)
        return company
    except Exception as e:
        print('EXEPTION:', e)
        return None


def get_company_drivers(request):
    if request.user.role == 'driver':
        return Driver.objects.filter(auth_profile=request.user)
    company_profile = Company.objects.get(auth_profile=request.user)
    drivers = Driver.objects.filter(company=company_profile)
    return drivers


def get_available_buses(request):
    """Shows all connected buses"""
    queries = []
    if request.user.role == 'driver':
        company = get_driver_company(request)
        if company is not None:
            queries += [Q(owner=company.auth_profile)]
    if request.user.role == 'company':
        drivers = get_company_drivers(request)
        for driver in drivers:
            queries += Q(owner=driver.auth_profile)

    # Make one big query
    if len(queries):
        query = queries.pop()
        for item in queries:
            query |= item
        return Bus.objects.filter(Q(owner=request.user) | query)
    return Bus.objects.filter(owner=request.user)


def get_available_routes(request):
    """Shows all connected routes"""
    queries = []
    if request.user.role == 'driver':
        company = get_driver_company(request)
        if company is not None:
            queries += [Q(owner=company.auth_profile)]
    if request.user.role == 'company':
        drivers = get_company_drivers(request)
        for driver in drivers:
            queries += Q(owner=driver.auth_profile)

    # Make one big query
    if len(queries):
        query = queries.pop()
        for item in queries:
            query |= item
        return Route.objects.filter(Q(owner=request.user) | query)
    return Route.objects.filter(owner=request.user)


def convert_to_choices(data):
    return [(str(el), el) for el in data]
