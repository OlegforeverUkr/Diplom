from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView
from django.db.models import Sum, F, Count, Q
from django.http import HttpResponseForbidden
from django.contrib import messages
from datetime import date, timedelta
from .models import Session, Ticket, Hall, Movie
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import BuyTicketForm, SessionForm, MovieForm, HallForm, DateSelectionForm
from .service import IsAdminOrStaff, hall_sold, session_sold




class UserRegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('administrators:login')


class UserLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('administrators:main')


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('administrators:login')


class SessionsListView(View):
    template_name = 'main_page.html'

    def get(self, request, *args, **kwargs):
        sort_by = request.GET.get('sort_by', 'time_start')
        
        today = date.today()
        today_sessions = Session.objects.filter(date_showing_start__lte=today, date_showing_end__gte=today).order_by(sort_by)

        tomorrow = today + timedelta(days=1)
        tomorrow_sessions = Session.objects.filter(date_showing_start__lte=tomorrow, date_showing_end__gte=tomorrow).order_by(sort_by)

        for session in today_sessions:
            session.available_tickets = session.hall.size - Ticket.objects.filter(ticket_session=session, ticket_date=today).count()

        for session in tomorrow_sessions:
            session.available_tickets = session.hall.size - Ticket.objects.filter(ticket_session=session, ticket_date=tomorrow).count()

        movies = Movie.objects.all()
        

        context = {
            'today_sessions': today_sessions,
            'tomorrow_sessions': tomorrow_sessions,
            'movies': movies,
        }

        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    template_name = 'user_profile.html'

    def get(self, request, *args, **kwargs):
        user_purchases = Ticket.objects.filter(buyer=request.user)
        total_spent = user_purchases.aggregate(total_spent=Sum(F('ticket_session__ticket_price')))['total_spent']

        context = {
            'user_purchases': user_purchases,
            'total_spent': total_spent or 0,
        }

        return render(request, self.template_name, context)




class BuyTicketView(View):
    template_name = 'buy_ticket.html'

    def get(self, request, session_id):
        session = Session.objects.get(pk=session_id)
        form = BuyTicketForm(session=session)
        return render(request, self.template_name, {'session': session, 'form': form})

    def post(self, request, session_id):
        session = Session.objects.get(pk=session_id)
        form = BuyTicketForm(session=session, data=request.POST)

        if form.is_valid():
            ticket_date = form.cleaned_data['ticket_date']
            if ticket_date < timezone.now().date():
                messages.info(request, "Выбранная вами дата уже прошла.")
                return redirect('administrators:buy_tiket', session_id=session.id)

            try:
                Ticket.objects.create(buyer=request.user, ticket_session=session, ticket_date=ticket_date)
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('administrators:buy_tiket', session_id=session.id)
            return redirect('administrators:main')

        return render(request, self.template_name, {'session': session, 'form': form})


class AdminCabinetView(IsAdminOrStaff, TemplateView):
    template_name = 'adminka.html'


class HallListView(IsAdminOrStaff, ListView):
    model = Hall
    template_name = 'manage_hall.html'
    context_object_name = 'halls'

    def post(self, request):
        hall_id = request.POST.get('hall_id')
        action = request.POST.get('action')

        if action == 'edit':
            return redirect(reverse_lazy('administrators:edit_halls', kwargs={'pk': hall_id}))
        
        return redirect(reverse_lazy('administrators:halls'))


class EditHallView(IsAdminOrStaff, UpdateView):
    model = Hall
    form_class = HallForm
    template_name = 'edit_hall.html'
    success_url = reverse_lazy('administrators:halls')

    def get(self, request, *args, **kwargs):
        hall = self.get_object()
        if hall_sold(hall):
            return HttpResponseForbidden("Cannot edit hall with sold tickets.")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        hall = self.get_object()
        if hall_sold(hall):
            return HttpResponseForbidden("Cannot edit hall with sold tickets.")
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs


class DeleteHallView(IsAdminOrStaff, DeleteView):
    model = Hall
    template_name = 'hall_delete.html'
    success_url = reverse_lazy('administrators:halls')

    def post(self, request, *args, **kwargs):
        hall = self.get_object()
        if hall_sold(hall):
            return HttpResponseForbidden("Cannot delete hall with sold tickets.")
        return super().post(request, *args, **kwargs)


class CreateHallView(IsAdminOrStaff, CreateView):
    model = Hall
    form_class = HallForm
    template_name = 'create_hall.html'
    success_url = reverse_lazy('administrators:halls')


class MovieListView(IsAdminOrStaff, ListView):
    model = Movie
    template_name = 'manage_movie.html'
    context_object_name = 'movies'

    def post(self, request):
        movie_id = request.POST.get('movie_id')
        action = request.POST.get('action')

        if action == 'edit':
            return redirect(reverse_lazy('administrators:edit_movie', kwargs={'pk': movie_id}))
        
        return redirect(reverse_lazy('administrators:movies'))


class EditMovieView(IsAdminOrStaff, UpdateView):
    model = Movie
    form_class = MovieForm
    template_name = 'edit_movie.html'
    success_url = reverse_lazy('administrators:movies')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs


class DeleteMovieView(IsAdminOrStaff, DeleteView):
    model = Movie
    template_name = 'movie_delete.html'
    success_url = reverse_lazy('administrators:movies')


class CreateMovieView(IsAdminOrStaff, CreateView):
    model = Movie
    form_class = MovieForm
    template_name = 'create_movie.html'
    success_url = reverse_lazy('administrators:movies')


class SessionsAdminListView(IsAdminOrStaff, ListView):
    model = Session
    template_name = 'manage_session.html'
    context_object_name = 'sessions'

    def sessions_with_ticket_counts(self):
        sessions_with_counts = Session.objects.annotate(ticket_count=Count('ticket'))
        return sessions_with_counts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sessions_with_counts = self.sessions_with_ticket_counts()
        context['sessions_with_counts'] = sessions_with_counts
        return context

    def post(self, request):
        session_id = request.POST.get('session_id')
        action = request.POST.get('action')

        if action == 'edit':
            return redirect(reverse_lazy('administrators:edit_session', kwargs={'pk': session_id}))
        
        return redirect(reverse_lazy('administrators:sessions'))


class EditSessionView(IsAdminOrStaff, UpdateView):
    model = Session
    form_class = SessionForm
    template_name = 'edit_session.html'
    success_url = reverse_lazy('administrators:sessions')

    def get(self, request, *args, **kwargs):
        session = self.get_object()
        if session_sold(session):
            return HttpResponseForbidden("Cannot edit session with sold tickets.")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        session = self.get_object()
        if session_sold(session):
            return HttpResponseForbidden("Cannot edit session with sold tickets.")
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs


class DeleteSessionView(IsAdminOrStaff, DeleteView):
    model = Session
    template_name = 'session_delete.html'
    success_url = reverse_lazy('administrators:sessions')

    def post(self, request, *args, **kwargs):
        session = self.get_object()
        if session_sold(session):
            return HttpResponseForbidden("Cannot delete session with sold tickets.")
        return super().post(request, *args, **kwargs)


class CreateSessionView(IsAdminOrStaff, CreateView):
    model = Session
    form_class = SessionForm
    template_name = 'create_session.html'
    success_url = reverse_lazy('administrators:sessions')


class MovieSessionsView(View):
    template_name = 'movie_sessions.html'

    def get(self, request, movie_id):
        try:
            movie = Movie.objects.get(pk=movie_id)
            sessions = movie.sessions.all()
        except Movie.DoesNotExist:
            raise Movie.DoesNotExist("Movie does not exist")

        return render(request, self.template_name, {'movie': movie, 'sessions': sessions})


class SessionsByDateView(View):
    template_name = 'sessions_by_date.html'

    def get(self, request, *args, **kwargs):
        form = DateSelectionForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = DateSelectionForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            sessions = Session.objects.filter(
                Q(date_showing_start__range=[start_date, end_date]) |
                Q(date_showing_end__range=[start_date, end_date]) |
                (Q(date_showing_start__lte=start_date) & Q(date_showing_end__gte=end_date))
            )

            return render(request, self.template_name, {'sessions': sessions, 'form': form})

        return render(request, self.template_name, {'form': form})






