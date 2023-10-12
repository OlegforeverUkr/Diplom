from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Ticket

class IsAdminOrStaff:
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect(reverse_lazy('usersapp:login'))
        
        return super().dispatch(request, *args, **kwargs)


def hall_sold(hall):
    return Ticket.objects.filter(ticket_session__hall=hall).exists()

def session_sold(session):
    return Ticket.objects.filter(ticket_session=session).exists()