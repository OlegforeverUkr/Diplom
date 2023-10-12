from django.contrib import admin
from .models import Hall, Movie, Session, Ticket


class SessionAdmin(admin.ModelAdmin):
    list_display = ('name_session', 'hall', 'session_movie', 'date_and_time_start', 'ticket_price')

    def date_and_time_start(self, obj):
        return f"{obj.date_showing_start} Time -  {obj.time_start}"

    date_and_time_start.short_description = 'Date and Time Start'


admin.site.register(Session, SessionAdmin)
admin.site.register(Hall)
admin.site.register(Movie)
admin.site.register(Ticket)
