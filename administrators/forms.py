from .models import Ticket, Hall, Session, Movie
from django import forms
from django.core.exceptions import ValidationError

class BuyTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['ticket_date']


    def __init__(self, session, *args, **kwargs):
        super(BuyTicketForm, self).__init__(*args, **kwargs)
        self.fields['ticket_date'].widget = forms.SelectDateWidget()
        self.session = session


    def clean_ticket_date(self):
        ticket_date = self.cleaned_data['ticket_date']

        if ticket_date < self.session.date_showing_start or ticket_date > self.session.date_showing_end:
            raise ValidationError("Выбранная вами дата не входит в период показа сеанса.")

        return ticket_date


class HallForm(forms.ModelForm):
    class Meta:
        model = Hall
        fields = ['name_hall', 'size']


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = "__all__"


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['name_movie', 'duration_minutes', 'image_url']


class DateSelectionForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))