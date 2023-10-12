from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime
from django.contrib import messages




UserModel = get_user_model()

class Hall(models.Model):
    name_hall = models.CharField(max_length=50, unique=True)
    size = models.IntegerField()

    def __str__(self):
        return self.name_hall



class Movie(models.Model):
    name_movie = models.CharField(max_length=50)
    duration_minutes = models.IntegerField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name_movie

    @property
    def sessions(self):
        return Session.objects.filter(session_movie=self)



class Session(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    session_movie = models.ForeignKey(Movie, on_delete=models.CASCADE, default=None)

    name_session = models.CharField(max_length=100, default='Название сеанса', unique=True)
    ticket_price = models.DecimalField(max_digits=5, decimal_places=2)
    time_start = models.TimeField(default=None)
    time_end = models.TimeField(default=None, blank=True, null=True)
    date_showing_start = models.DateField(default=None)
    date_showing_end = models.DateField(default=None)

    class Meta:
        ordering = ['session_movie']


    def get_remaining_seats(self):
        sold_tickets = Ticket.objects.filter(ticket_session=self).count()
        remaining_seats = self.hall.size - sold_tickets
        return remaining_seats


    def save(self, *args, **kwargs):
        if not self.time_end or self.time_start < (datetime.combine(date.today(), self.time_start) + timedelta(minutes=self.session_movie.duration_minutes)).time():
            duration_minutes = self.session_movie.duration_minutes
            start_datetime = datetime.combine(date.today(), self.time_start)
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            self.time_end = end_datetime.time()

        if self.date_showing_end < self.date_showing_start:
            raise ValidationError('Дата окончания показа не может быть меньше даты начала показа.')

        sessions = Session.objects.filter(
            hall=self.hall,
            time_start__lt=self.time_end,
            time_end__gt=self.time_start,
            date_showing_start__lt=self.date_showing_end,
            date_showing_end__gt=self.date_showing_start
        ).exclude(pk=self.pk)
        
        if sessions.exists():
            raise ValidationError('Время уже занято в этом зале.')

        super().save(*args, **kwargs)


    def __str__(self) -> str:
        return self.name_session
    


class Ticket(models.Model):
    buyer = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    ticket_session = models.ForeignKey(Session, on_delete=models.CASCADE, default=None)
    ticket_date = models.DateField(default=timezone.now)


    def save(self, *args, **kwargs):
        exist_ticket = Ticket.objects.filter( 
            buyer=self.buyer, 
            ticket_session=self.ticket_session, 
            ticket_date=self.ticket_date 
            ).first()

        if exist_ticket:
            raise ValidationError("У вас уже есть билет на этот сеанс.")

        sold_tickets_count = Ticket.objects.filter(
            ticket_session=self.ticket_session,
            ticket_date=self.ticket_date
        ).count()
        
        if sold_tickets_count >= self.ticket_session.hall.size:
            raise ValidationError("Нет доступных мест на этот сеанс.")

        if not self.ticket_session.date_showing_start <= self.ticket_date <= self.ticket_session.date_showing_end:
            raise ValidationError("Выбранная вами дата не входит в период показа сеанса.")

        if self.ticket_date < timezone.now().date():
            raise ValidationError("Выбранная вами дата уже прошла.")

        super(Ticket, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Tiket for {self.buyer} on {self.ticket_session.session_movie}'
