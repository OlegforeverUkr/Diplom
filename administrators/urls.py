from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()


app_name = "administrators"
urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('', views.SessionsListView.as_view(), name='main'),
    path('user-profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('buy-ticket/<int:session_id>/', views.BuyTicketView.as_view(), name='buy_tiket'),
    path('admin-cabinet/', views.AdminCabinetView.as_view(), name='adminka'),
    path('manage-halls/', views.HallListView.as_view(), name='halls'),
    path('edit-hall/<int:pk>/', views.EditHallView.as_view(), name='edit_halls'),
    path('delete-hall/<int:pk>/', views.DeleteHallView.as_view(), name='delete_hall'),
    path('create-hall/', views.CreateHallView.as_view(), name='create_hall'),
    path('manage-movies/', views.MovieListView.as_view(), name='movies'),
    path('edit-movie/<int:pk>/', views.EditMovieView.as_view(), name='edit_movie'),
    path('delete-movie/<int:pk>/', views.DeleteMovieView.as_view(), name='delete_movie'),
    path('create-movie/', views.CreateMovieView.as_view(), name='create_movie'),
    path('manage-sessions/', views.SessionsAdminListView.as_view(), name='sessions'),
    path('edit-session/<int:pk>/', views.EditSessionView.as_view(), name='edit_session'),
    path('delete-session/<int:pk>/', views.DeleteSessionView.as_view(), name='delete_session'),
    path('create-session/', views.CreateSessionView.as_view(), name='create_session'),
    path('movie-sessions/<int:movie_id>/', views.MovieSessionsView.as_view(), name='movie_sessions'),
    path('sessions-by-date/', views.SessionsByDateView.as_view(), name='sessions_by_date'),
]
