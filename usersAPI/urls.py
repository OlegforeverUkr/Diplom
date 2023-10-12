from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .token import TokenAuth
from . import views

router = DefaultRouter()
router.register(r'sessions', views.SessionViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'halls_cinema', views.HallViewSet)

app_name = "usersAPI"
urlpatterns = [
    path('', include(router.urls)),
    path('get_token/', TokenAuth.as_view()),
    path('movies/', views.MovieListView.as_view()),
    path('registration_API/', views.RegisterUserView.as_view()),
    path('buy_ticket_API/', views.BuyTicketView.as_view()),
    path('today_sessions/', views.TodaySessionsByTimeView.as_view()),
    path('total_tickets/', views.UserTicketsView.as_view()),
]
