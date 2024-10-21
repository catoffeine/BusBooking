import json
from copy import copy
import datetime
import pytz

from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render, redirect

from myauth.views import check_everything

from booking.models import Bus

from myauth.forms import ClientChangeForm, DriverChangeForm, CompanyChangeForm
from myauth.models import Client, Driver, Company

from booking.models import Route

from booking.models import Trip
from typing import List

from .forms import BusChangeForm, RouteChangeForm, TripChangeForm, TicketSearchForm
from .models import get_driver_company, get_available_buses, get_company_drivers, Ticket
from buses.models import BusSeatsScheme


def UPOST(post, obj):
    """Updates request's POST dictionary with values from object, for update purposes"""
    post = copy(post)
    for k, v in model_to_dict(obj).items():
        if k not in post:
            post[k] = v
    return post


def find_suitable_trips(date, start_stop, final_stop):
    # Convert the date to a datetime object
    # start_stop, final_stop = start_stop.lower(), final_stop.lower()
    # search_date = date.date()

    # Perform the search based on the parameters
    start_stop = start_stop.strip().lower()
    final_stop = final_stop.strip().lower()
    date = datetime.datetime.combine(date, datetime.datetime.min.time())
    date = pytz.utc.localize(date)
    f = Trip.objects.filter
    trips = f(
        Q(start_dt__range=(datetime.datetime.combine(date, datetime.time.min),
                           datetime.datetime.combine(date, datetime.time.max))) &
        Q(route__stops__icontains=start_stop) &
        Q(route__stops__icontains=final_stop))
    trips = list(filter(lambda trip: trip.route.stops.find(start_stop) < trip.route.stops.find(final_stop), trips))
    return trips


def get_stops_list():
    routes = Route.objects.all()
    stops = [tuple(map(lambda stop: stop.strip().title(), x.stops.split(','))) for x in routes]
    s = set()
    for el in stops:
        s = s.union(set(el))
    print(s)
    return list(s)


"""BUSES"""


@check_everything
def my_buses_page(request):
    try:
        comp = get_driver_company(request)
        buses = get_available_buses(request)
    except Exception as e:
        print(e)
        raise e
    return render(request, 'my-buses.html', {'buses': buses})


@check_everything
def add_bus(request):
    bus = Bus()
    bus.owner = request.user
    bus.save()
    return redirect('edit-bus', bid=bus.id)


@check_everything
def edit_bus(request, bid):
    bus = Bus.objects.get(id=bid)
    form = BusChangeForm(instance=bus)
    if request.method == 'POST':
        form = BusChangeForm(UPOST(request.POST, bus), instance=bus)
        form.save()
    return render(request, 'edit-bus.html', {'form': form, 'label': 'Автобус', 'bid': bid})


@check_everything
def delete_bus(request, bid):
    Bus.objects.get(id=bid).delete()
    return redirect('my-buses')


"""ROUTES"""


@check_everything
def my_routes_page(request):
    try:
        comp = get_driver_company(request)
        if request.user.role == 'driver' and comp is not None:
            q = Q(owner=comp.auth_profile) | Q(owner=request.user)
        else:
            q = Q(owner=request.user)
        routes = Route.objects.filter(q)
    except Exception as e:
        routes = []
    return render(request, 'my-routes.html', {'routes': routes})


@check_everything
def add_route(request):
    r = Route()
    r.owner = request.user
    r.save()
    return redirect('edit-route', rid=r.id)


@check_everything
def edit_route(request, rid):
    route = Route.objects.get(id=rid)
    form = RouteChangeForm(instance=route)
    if request.method == 'POST':
        form = RouteChangeForm(UPOST(request.POST, route), instance=route)
        form.save()
    return render(request, 'edit-route.html', {'form': form, 'label': 'Маршрут', 'rid': rid})


@check_everything
def delete_route(request, rid):
    Route.objects.get(id=rid).delete()
    return redirect('my-routes')


"""TRIPS"""


@check_everything
def my_trips_page(request):
    try:
        if request.user.role == 'driver':
            q = Q(driver=Driver.objects.get(auth_profile=request.user))
        elif request.user.role == 'company':
            drivers = tuple(map(lambda x: x.auth_profile.id, get_company_drivers(request)))
            q = Q(driver__in=drivers)
        trips = Trip.objects.filter(q)
    except Exception as e:
        raise e
    return render(request, 'my-trips.html', {'trips': trips})


@check_everything
def add_trip(request):
    t = Trip()
    if request.user.role == 'driver':
        t.driver = Driver.objects.get(auth_profile=request.user)
    t.save()
    return redirect('edit-trip', tid=t.id)


@check_everything
def edit_trip(request, tid):
    trip = Trip.objects.get(id=tid)
    form = TripChangeForm(instance=trip, request=request)
    routes = Route.objects.all()
    buses = Bus.objects.all()
    if request.method == 'POST':
        form = TripChangeForm(UPOST(request.POST, trip), instance=trip, request=request)
        # form.data['start_dt'] = form.data['start_dt'].replace('/', '.')
        print()
        el = form.save()

    try:
        start_dt = trip.start_dt.strftime('%d.%m.%y %H:%M')
    except:
        start_dt = datetime.datetime.now().strftime('%d.%m.%y %H:%M')

    return render(request, 'edit-trip.html', {'form': form, 'label': 'Рейс', 'tid': tid,
                                              'routes': routes, 'buses': buses,
                                              'start_dt': start_dt})


@check_everything
def delete_trip(request, tid):
    Trip.objects.get(id=tid).delete()
    return redirect('my-trips')


@check_everything
def view_trip(request, tid):
    trip = Trip.objects.get(id=tid)
    return render(request, 'view-trip.html', {'trip': trip, 'tid': tid})


@check_everything
def choose_seat(request, tid):
    trip = Trip.objects.get(id=tid)
    scheme = BusSeatsScheme(trip.bus.id)
    try:
        booked_tickets = Ticket.objects.filter(trip__id=tid)
    except Exception as e:
        print(e)
        booked_seats = []
    scheme.set_booked_tickets(booked_tickets)
    return render(request, 'choose-seat.html', {'trip': trip, 'tid': tid, 'scheme': scheme.scheme})


@check_everything
def buy_ticket(request, tid, seat):
    t = Ticket()
    t.owner = request.user
    t.seat = seat
    t.trip = Trip.objects.get(id=tid)
    t.bought_price = t.trip.ticket_price
    t.save()
    return redirect('view-ticket', tcode=t.ticket_code)


@check_everything
def search_trips(request):
    stops = get_stops_list()
    if request.method == 'POST':
        form = TicketSearchForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            from_f = form.cleaned_data['from_f']
            to_f = form.cleaned_data['to_f']
            trips = find_suitable_trips(date, from_f, to_f)
            # trips = Trip.objects.all()

            return render(request, 'view-trips.html', {'trips': trips,
                                                       'from_f': from_f.capitalize(),
                                                       'to_f': to_f.capitalize(),
                                                       'date': date})
    else:
        form = TicketSearchForm()
    return render(request, 'search-tickets-form.html', {'form': form, 'stops': stops})


""" TICKETS """


@check_everything
def check_trip_tickets(request, tid):
    return render(request, 'check-tickets.html', {'tid': tid})


@check_everything
def check_ticket_data(request, tid, data):
    resp = {'data': 'Wrong ticket'}
    ticket = Ticket.objects.get(ticket_code=data)
    print(ticket.trip.id, tid, ticket.ticket_code)
    if ticket is not None:
        if str(ticket.trip.id) != str(tid):
            r = f'БИЛЕТ НА ДРУГОЙ РЕЙС {str(ticket.seat)} {str(ticket.trip)}'
        else:
            r = f"{str(ticket.seat)}"
        resp['data'] = r
    return HttpResponse(json.dumps(resp))


@check_everything
def my_tickets_page(request):
    owner = request.user
    tickets = Ticket.objects.filter(owner=owner)
    return render(request, 'my-tickets.html', {'tickets': tickets})


@check_everything
def view_ticket_page(request, tcode):
    owner = request.user
    ticket = Ticket.objects.get(Q(owner=owner) & Q(ticket_code=tcode))
    return render(request, 'view-ticket.html', {'ticket': ticket})


@check_everything
def return_ticket(request, tcode):
    owner = request.user
    ticket = Ticket.objects.get(Q(owner=owner) & Q(ticket_code=tcode))
    # ticket.is_returned = True
    ticket.return_ticket()
    ticket.save()
    return redirect('my-tickets')
