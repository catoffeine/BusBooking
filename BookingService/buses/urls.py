from django.urls import path
from . import views

urlpatterns = [
    path('edit-scheme/<bid>', views.edit_scheme, name='edit-scheme'),
    path('add-row/<bid>', views.add_row, name='add-row'),
    path('delete-row/<bid>/<rowid>', views.delete_row, name='delete-row'),
    path('add-seat/<bid>/<rowid>', views.add_seat, name='add-seat'),  # Add seat to end of row
    path('add-space/<bid>/<rowid>', views.add_space, name='add-space'),  # Add seat to end of row
    path('add-seat/<bid>/<rowid>/<seatid>', views.add_seat_between, name='add-seat-between'),  # Add seat between
    path('add-space/<bid>/<rowid>/<seatid>', views.add_space_between, name='add-space-between'),  # Add space between
    path('delete-seat/<bid>/<rowid>/<seatid>', views.delete_seat, name='delete-seat'),
    path('set-row-n/<bid>/<rowid>', views.set_row_n, name='set-row-n'),
    path('set-seat-n/<bid>/<rowid>/<seatid>', views.set_seat_n, name='set-seat-n')
]
