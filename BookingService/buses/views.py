from copy import copy

from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render, redirect

from buses.models import BusSeatsScheme

from booking.models import Bus


schemes = {}

from django.template.defaulttags import register


@register.filter
def get(dictionary, key):
    try:
        if key not in dictionary:
            return dictionary.get(str(key))
        return dictionary.get(key)
    except:
        return None


def check_bus_dec(view_func):
    """ Decorator for checking bus scheme existence before all interactions """

    def wrapper(request, *args, **kwargs):
        print(args, kwargs, 'BUS_DEC_ENDPOINT')

        return view_func(request, *args, **kwargs)
        # If user is logged in
        # if request.user.is_authenticated:
        #     #
        #     ...
        #
        #     return view_func(request, *args, **kwargs)
        # elif request.path == "/":
        #     return view_func(request, *args, **kwargs)
        # else:
        #     return redirect('index')

    return wrapper



def edit_scheme(request, bid):
    """Add new bus to db"""
    scheme = BusSeatsScheme(bid)
    return render(request, 'scheme.html', {'scheme': scheme.scheme, 'busid': bid})


def add_row(request, bid):
    """Add new row to bus seat scheme"""
    scheme = BusSeatsScheme(bid)
    scheme.add_row()
    return redirect('edit-scheme', bid=bid)


def delete_row(request, bid, rowid):
    """Delete N  row from bus seat scheme"""
    scheme = BusSeatsScheme(bid)
    scheme.delete_row(rowid)
    return redirect('edit-scheme', bid=bid)


def add_row_space(request, bus_id):
    """Add space row to sitting scheme"""
    pass


def add_seat(request, bid, rowid):
    """Add seat to last row"""
    scheme = BusSeatsScheme(bid)
    scheme.add_seat(rowid)
    return redirect('edit-scheme', bid=bid)


def delete_seat(request, bid, rowid, seatid):
    """Add seat to last row"""
    scheme = BusSeatsScheme(bid)
    scheme.delete_seat(rowid, seatid)
    return redirect('edit-scheme', bid=bid)


def add_space(request, bid, rowid):
    """Add space to last row"""
    bid = int(bid)
    scheme = BusSeatsScheme(bid)
    scheme.add_space(rowid)
    return redirect('edit-scheme', bid=bid)


def add_seat_between(request, bid, rowid, seatid):
    scheme = BusSeatsScheme(bid)
    scheme.add_seat_after(rowid, seatid)
    return redirect('edit-scheme', bid=bid)


def add_space_between(request, bid, rowid, seatid):
    scheme = BusSeatsScheme(bid)
    scheme.add_space_after(rowid, seatid)
    return redirect('edit-scheme', bid=bid)


def set_row_n(request, bid, rowid):
    scheme = BusSeatsScheme(bid)
    print(request.POST.get('row-name'), request.POST)
    scheme.set_row_n(rowid, request.POST.get('row-name'))
    return redirect('edit-scheme', bid=bid)


def set_seat_n(request, bid, rowid, seatid):
    scheme = BusSeatsScheme(bid)
    scheme.set_seat_n(rowid, seatid, request.POST.get('seat-name'))
    return redirect('edit-scheme', bid=bid)
