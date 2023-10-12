from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from .serializers import SessionSerializer, TicketSerializer, HallSerializer, MovieSerializer
from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.response import Response
from administrators.models import Session, Ticket, Hall, Movie
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .permissions import get_session_permissions, IsAdminUserOrReadOnly
from datetime import datetime
from django.db.models import Q


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['ticket_price', 'time_start']
    ordering = ['time_start'] 

    def get_permissions(self):
        return get_session_permissions(self)

    def perform_destroy(self, instance):
        if Ticket.objects.filter(ticket_session=instance).exists():
            raise ValidationError("Нельзя удалить сеанс, для которого есть проданные билеты.")
        super().perform_destroy(instance)

    def perform_update(self, serializer):
        instance = serializer.instance
        if Ticket.objects.filter(ticket_session=instance).exists():
            raise ValidationError("Нельзя изменить сеанс, для которого есть проданные билеты.")
        super().perform_update(serializer)



class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Please provide username, password'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)

        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)


class BuyTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ticket_session_id = request.data.get('ticket_session_id')
        ticket_date = request.data.get('ticket_date')

        if not ticket_session_id or not ticket_date:
            return Response({'error': 'Please provide ticket_session_id and ticket_date'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ticket_session = Session.objects.get(id=ticket_session_id)
        except Session.DoesNotExist:
            return Response({'error': 'Ticket session not found'}, status=status.HTTP_404_NOT_FOUND)

        existing_ticket = Ticket.objects.filter(
            buyer=request.user,
            ticket_session=ticket_session,
            ticket_date=ticket_date
        ).first()

        if existing_ticket:
            return Response({'message':'Ypu already have ticket on this time'}, status=status.HTTP_400_BAD_REQUEST)

        ticket_data = {
            'buyer': request.user.id,
            'ticket_session': ticket_session.id,
            'ticket_date': ticket_date,
        }

        serializer = TicketSerializer(data=ticket_data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Ticket purchased successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class TodaySessionsByTimeView(APIView):
    serializer_class = SessionSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['ticket_price', 'time_start']
    ordering = ['time_start']

    def post(self, request, *args, **kwargs):
        start_time_input = request.data.get('start_time')
        end_time_input = request.data.get('end_time')
        hall_id_input = request.data.get('hall_id')
        date_input = request.data.get('date')

        start_time = datetime.strptime(start_time_input, '%H:%M:%S').time()
        end_time = datetime.strptime(end_time_input, '%H:%M:%S').time()

        queryset = Session.objects.filter(
            Q(time_start__gte=start_time, time_start__lt=end_time),
            Q(date_showing_start__lte=date_input, date_showing_end__gte=date_input)
        )

        if hall_id_input:
            queryset = queryset.filter(hall_id=hall_id_input)

        serializer = SessionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HallViewSet(viewsets.ModelViewSet):
    queryset = Hall.objects.all()
    serializer_class = HallSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def perform_destroy(self, instance):
        if Ticket.objects.filter(ticket_session__hall=instance).exists():
            raise ValidationError("Нельзя удалить зал, в котором есть проданные билеты.")
        super().perform_destroy(instance)

    def perform_update(self, serializer):
        instance = serializer.instance
        if Ticket.objects.filter(ticket_session__hall=instance).exists():
            raise ValidationError("Нельзя изменить зал, в котором есть проданные билеты.")
        super().perform_update(serializer)


class UserTicketsView(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        tickets = Ticket.objects.filter(buyer=user)
        serializer = TicketSerializer(tickets, many=True)
        total_spent = sum(ticket.ticket_session.ticket_price for ticket in tickets)
        response_data = {
            'tickets': serializer.data,
            'total_summ': total_spent,
        }
        return Response(response_data, status=status.HTTP_200_OK)
