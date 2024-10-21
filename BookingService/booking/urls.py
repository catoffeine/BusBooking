from django.urls import path
from . import views

urlpatterns = [
    path(r'my-buses', views.my_buses_page, name='my-buses'),
    path(r'add-bus', views.add_bus, name='add_bus'),
    path('edit-bus/<bid>', views.edit_bus, name='edit-bus'),
    path('delete-bus/<bid>', views.delete_bus, name='delete-bus'),

    path(r'my-routes', views.my_routes_page, name='my-routes'),
    path(r'add-route', views.add_route, name='add-route'),
    path(r'edit-route/<rid>', views.edit_route, name='edit-route'),
    path(r'delete-route/<rid>', views.delete_route, name='delete-route'),

    path(r'my-trips', views.my_trips_page, name='my-trips'),
    path(r'add-trip', views.add_trip, name='add-trip'),
    path(r'view-trip/<tid>', views.view_trip, name='view-trip'),
    path(r'search-trips', views.search_trips, name='search-trips'),
    path(r'choose-seat/<tid>', views.choose_seat, name='choose-seat'),
    path(r'buy-ticket/<tid>/<seat>', views.buy_ticket, name='buy-ticket'),
    path(r'edit-trip/<tid>', views.edit_trip, name='edit-trip'),
    path(r'delete-trip/<tid>', views.delete_trip, name='delete-trip'),

    path(r'my-tickets', views.my_tickets_page, name='my-tickets'),
    path(r'view-ticket/<tcode>', views.view_ticket_page, name='view-ticket'),
    path(r'check-tickets/<tid>', views.check_trip_tickets, name='check-tickets'),
    path(r'check-ticket-data/<tid>/<data>', views.check_ticket_data, name='check-ticket'),
    path(r'return-ticket/<tcode>', views.return_ticket, name='return-ticket'),

]
