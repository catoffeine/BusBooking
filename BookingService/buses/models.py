import json

from django.db import models

from booking.models import Bus


class BusSeatsScheme:
    def __init__(self, bid):
        self.bid = bid

        json_string = Bus.objects.get(id=self.bid).sitting_scheme
        if json_string not in ('', None, ' '):
            self.scheme = json.loads(json_string)
        else:
            self.scheme = {}
        pass

    def add_row(self):
        """Adds row to the end"""
        self.load()
        last_n = self.rows_n
        self.scheme[last_n + 1] = {'row_n': str(last_n), 'data': []}
        self.save()

    def add_seat(self, row_i: int):
        """Add seat to the end of exact row"""
        self.load()
        row_i = int(row_i)
        last_seat_n = self.seats_n_in_row(row_i)
        self.scheme[row_i]['data'] += [{'multiplier': 1, 'seat_n': last_seat_n + 1}]
        self.save()

    def add_space(self, row_i: int):
        """Add seat to the end of exact row"""
        self.load()
        row_i = int(row_i)
        self.scheme[row_i]['data'] += [{'space': True}]
        self.save()

    def add_seat_after(self, row_i: int, seat_i: int):
        """Add seat after seat"""
        self.load()
        row_i, seat_i = int(row_i), int(seat_i)
        before_seats = self.scheme[row_i]['data'][:seat_i - 1]
        after_seats = self.scheme[row_i]['data'][seat_i - 1:]
        self.scheme[row_i]['data'] = before_seats + [{'multiplier': 1, 'seat_n': seat_i + 1}] + after_seats
        self.save()

    def add_space_after(self, row_i: int, seat_i: int):
        """Add space after seat"""
        self.load()
        row_i, seat_i = int(row_i), int(seat_i)
        before_seats = self.scheme[row_i]['data'][:seat_i - 1]
        after_seats = self.scheme[row_i]['data'][seat_i - 1:]
        self.scheme[row_i]['data'] = before_seats + [{'space': True}] + after_seats
        self.save()

    def delete_row(self, row_i: int):
        """Delete row by its number"""
        row_i = int(row_i)
        self.load()
        self.scheme.pop(row_i)
        self.save()

    def delete_seat(self, row_i: int, seat_i: int):
        """Delete seat by its coordinates"""
        row_i, seat_i = int(row_i), int(seat_i)
        self.load()
        self.scheme[row_i]['data'].pop(int(seat_i) - 1)
        self.save()

    def set_seat_n(self, row_i: int, seat_i: int, new_n: str):
        """Change seat's seat_n by its coordinates"""
        row_i, seat_i = int(row_i), int(seat_i)
        self.load()
        self.scheme[row_i]['data'][seat_i - 1]['seat_n'] = new_n
        self.save()

    def set_seat_multiplier(self, row_i: int, seat_i: int, multiplier: float):
        """Change seat's seat_n by its coordinates"""
        row_i, seat_i = int(row_i), int(seat_i)
        self.load()
        self.scheme[row_i][seat_i]['multiplier'] = multiplier
        self.save()

    def set_row_n(self, row_i: int, new_n: str):
        row_i = int(row_i)
        self.load()
        print(self.scheme[row_i])
        self.scheme[row_i]['row_n'] = new_n
        self.save()

    def seats_n_in_row(self, row_i: int, count_spaces=True):
        """Return seats amount in exact row"""
        row = self.scheme[row_i]
        sn = 0
        for seat_json in row:
            if count_spaces:
                sn += 1
            elif not seat_json.get('space', False):
                sn += 1
        return sn

    @property
    def rows_n(self):
        """Get rows amount"""
        self.load()
        try:
            return len(self.scheme)
        except ValueError:
            return 0

    @property
    def seats_n(self):
        """Get seats amount in bus"""
        self.load()
        sn = 0
        for row_i in self.scheme:
            sn += self.seats_n_in_row(row_i)
        return sn

    @property
    def exported_scheme(self):
        return json.dumps(self.scheme)

    def __repr__(self):
        return str(self.scheme)

    def __str__(self):
        return self.__repr__()

    def set_booked_tickets(self, booked_tickets):
        self.load()
        for ticket in booked_tickets:
            if not ticket.is_returned:
                row_name, seat_name = ticket.seat.split('-')
                for i, row in self.scheme.items():
                    if row.get('row_n') == row_name:
                        r_i = i
                        break
                for i, seat in enumerate(self.scheme[r_i]['data']):
                    if seat.get('seat_n') == seat_name:
                        self.scheme[r_i]['data'][i]['booked'] = True
                        break

    def save(self):
        b = Bus.objects.get(id=self.bid)
        b.sitting_scheme = self.exported_scheme
        b.save()

    def load(self):
        json_string = Bus.objects.get(id=self.bid).sitting_scheme
        if json_string not in ('', None, ' '):
            scheme = json.loads(json_string)
        else:
            scheme = {}
        self.scheme = {int(k): v for k, v in scheme.items()}
