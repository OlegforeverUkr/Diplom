from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and not request.user.is_staff:
            last_activity = request.session.get('last_activity', None)
            if last_activity and timezone.now().timestamp() - last_activity > 60:
                logout(request)
                return redirect('administrators:login')

            request.session['last_activity'] = timezone.now().timestamp()

        return response
