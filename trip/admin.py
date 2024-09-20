from django.contrib import admin

from trip.models import TrainType, Ticket, Journey, Crew, Route, Station, Order, Train

admin.site.register(TrainType)
admin.site.register(Train)
admin.site.register(Order)
admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(Journey)
admin.site.register(Ticket)
